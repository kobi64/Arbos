"""
ArbOS™
EX-373
CCXT Async Spawn Lifecycle Guard

Compatibility guard for CCXT async_support / CCXT Pro spawned
background tasks.

Purpose:
- handle cancelled spawned asyncio Tasks safely;
- retrieve spawned Task exceptions;
- retrieve exceptions from CCXT wrapper Futures so asyncio does
  not emit "Future exception was never retrieved";
- retain ownership of active spawned Tasks;
- explicitly drain/cancel spawned Tasks before exchange shutdown;
- preserve Future completion semantics for callers that await the
  returned Future.

The installed CCXT package is not modified.

No authentication.
No transfers.
No order submission.
"""

import asyncio
from types import MethodType

from ccxt.async_support.base.ws.future import Future


def install_ccxt_spawn_lifecycle_guard(exchange):
    """
    Replace one exchange instance's spawn() implementation with
    cancellation-safe lifecycle handling and explicit task ownership.

    The installed CCXT package is not modified.
    """

    if exchange is None:
        raise ValueError("exchange is required")

    if getattr(
        exchange,
        "_arbos_spawn_lifecycle_guard_installed",
        False,
    ):
        return exchange

    original_spawn = getattr(
        exchange,
        "spawn",
        None,
    )

    if original_spawn is None:
        raise ValueError(
            "exchange does not provide spawn"
        )

    exchange._arbos_original_spawn = (
        original_spawn
    )

    exchange._arbos_spawn_tasks = set()

    def guarded_spawn(
        self,
        method,
        *args,
    ):
        future = Future()

        task = (
            self.asyncio_loop.create_task(
                method(*args)
            )
        )

        self._arbos_spawn_tasks.add(
            task
        )

        def task_completed(
            asyncio_future,
        ):
            self._arbos_spawn_tasks.discard(
                asyncio_future
            )

            if asyncio_future.cancelled():
                if not future.done():
                    future.cancel()

                return

            try:
                exception = (
                    asyncio_future.exception()
                )

            except asyncio.CancelledError:
                if not future.done():
                    future.cancel()

                return

            if exception is None:
                if not future.done():
                    future.resolve(
                        asyncio_future.result()
                    )

            else:
                if not future.done():
                    future.reject(
                        exception
                    )

        def wrapper_future_completed(
            completed_future,
        ):
            if completed_future.cancelled():
                return

            try:
                completed_future.exception()

            except asyncio.CancelledError:
                pass

            except Exception:
                # Retrieving the exception is intentional.
                #
                # A later await of the same Future still preserves
                # its normal exception semantics.
                pass

        task.add_done_callback(
            task_completed
        )

        future.add_done_callback(
            wrapper_future_completed
        )

        return future

    async def drain_spawn_tasks(
        self,
        cancel=True,
    ):
        """
        Drain all currently active Tasks created through CCXT spawn().

        This must run before exchange.close() so a background snapshot
        cannot recreate an aiohttp ClientSession during shutdown.
        """

        tasks = list(
            getattr(
                self,
                "_arbos_spawn_tasks",
                set(),
            )
        )

        if cancel:
            for task in tasks:
                if not task.done():
                    task.cancel()

        results = []

        if tasks:
            results = list(
                await asyncio.gather(
                    *tasks,
                    return_exceptions=True,
                )
            )

        # Run completion callbacks before exchange.close().
        await asyncio.sleep(0)

        active_tasks = set(
            getattr(
                self,
                "_arbos_spawn_tasks",
                set(),
            )
        )

        # Completed tasks should already have removed themselves through
        # task_completed(), but explicitly discard the drained snapshot
        # for deterministic shutdown accounting.
        for task in tasks:
            active_tasks.discard(
                task
            )

        self._arbos_spawn_tasks = (
            active_tasks
        )

        cancelled_task_count = sum(
            1
            for result in results
            if isinstance(
                result,
                asyncio.CancelledError,
            )
        )

        task_error_count = sum(
            1
            for result in results
            if isinstance(
                result,
                BaseException,
            )
            and not isinstance(
                result,
                asyncio.CancelledError,
            )
        )

        return {
            "task_count": len(tasks),
            "cancelled_task_count": (
                cancelled_task_count
            ),
            "task_error_count": (
                task_error_count
            ),
            "remaining_task_count": len(
                self._arbos_spawn_tasks
            ),
        }

    exchange.spawn = MethodType(
        guarded_spawn,
        exchange,
    )

    exchange.drain_spawn_tasks = MethodType(
        drain_spawn_tasks,
        exchange,
    )

    exchange._arbos_spawn_lifecycle_guard_installed = (
        True
    )

    return exchange
