import asyncio

import pytest

from core.ccxt_spawn_lifecycle_guard import (
    install_ccxt_spawn_lifecycle_guard,
)


class FakeExchange:
    def __init__(self):
        self.asyncio_loop = None

    def spawn(self, method, *args):
        raise AssertionError(
            "original spawn should be replaced"
        )


def test_guard_requires_exchange():
    with pytest.raises(
        ValueError,
        match="exchange is required",
    ):
        install_ccxt_spawn_lifecycle_guard(
            None
        )


def test_guard_is_idempotent():
    exchange = FakeExchange()

    install_ccxt_spawn_lifecycle_guard(
        exchange
    )

    first_spawn = exchange.spawn

    install_ccxt_spawn_lifecycle_guard(
        exchange
    )

    assert exchange.spawn == first_spawn
    assert (
        exchange
        ._arbos_spawn_lifecycle_guard_installed
        is True
    )


def test_guard_resolves_successful_spawn():
    async def exercise():
        exchange = FakeExchange()
        exchange.asyncio_loop = (
            asyncio.get_running_loop()
        )

        install_ccxt_spawn_lifecycle_guard(
            exchange
        )

        async def work():
            await asyncio.sleep(0)
            return 123

        result = await exchange.spawn(
            work
        )

        assert result == 123

    asyncio.run(exercise())


def test_guard_preserves_spawn_exception():
    async def exercise():
        exchange = FakeExchange()
        exchange.asyncio_loop = (
            asyncio.get_running_loop()
        )

        install_ccxt_spawn_lifecycle_guard(
            exchange
        )

        async def work():
            await asyncio.sleep(0)
            raise RuntimeError(
                "simulated failure"
            )

        with pytest.raises(
            RuntimeError,
            match="simulated failure",
        ):
            await exchange.spawn(
                work
            )

    asyncio.run(exercise())


def test_guard_handles_cancelled_spawn_without_callback_error():
    async def exercise():
        exchange = FakeExchange()
        exchange.asyncio_loop = (
            asyncio.get_running_loop()
        )

        install_ccxt_spawn_lifecycle_guard(
            exchange
        )

        started = asyncio.Event()

        async def work():
            started.set()
            await asyncio.sleep(3600)

        future = exchange.spawn(
            work
        )

        await started.wait()

        current = [
            task
            for task
            in asyncio.all_tasks()
            if task is not asyncio.current_task()
        ]

        for task in current:
            task.cancel()

        await asyncio.gather(
            *current,
            return_exceptions=True,
        )

        await asyncio.sleep(0)

        assert future.cancelled()

    asyncio.run(exercise())


def test_unawaited_failed_wrapper_future_is_retrieved():
    messages = []

    async def exercise():
        loop = asyncio.get_running_loop()

        old_handler = (
            loop.get_exception_handler()
        )

        def handler(
            loop,
            context,
        ):
            messages.append(
                context.get(
                    "message",
                    ""
                )
            )

        loop.set_exception_handler(
            handler
        )

        try:
            exchange = FakeExchange()
            exchange.asyncio_loop = loop

            install_ccxt_spawn_lifecycle_guard(
                exchange
            )

            async def work():
                raise RuntimeError(
                    "background failure"
                )

            exchange.spawn(
                work
            )

            await asyncio.sleep(0)
            await asyncio.sleep(0)

        finally:
            loop.set_exception_handler(
                old_handler
            )

    asyncio.run(exercise())

    assert not any(
        "Future exception was never retrieved"
        in message
        for message in messages
    )


def test_guard_tracks_active_spawn_task():
    async def exercise():
        exchange = FakeExchange()
        exchange.asyncio_loop = (
            asyncio.get_running_loop()
        )

        install_ccxt_spawn_lifecycle_guard(
            exchange
        )

        started = asyncio.Event()
        release = asyncio.Event()

        async def work():
            started.set()
            await release.wait()
            return 123

        future = exchange.spawn(
            work
        )

        await started.wait()

        assert len(
            exchange._arbos_spawn_tasks
        ) == 1

        release.set()

        assert await future == 123

        await asyncio.sleep(0)

        assert (
            exchange._arbos_spawn_tasks
            == set()
        )

    asyncio.run(exercise())


def test_guard_drains_active_spawn_tasks():
    async def exercise():
        exchange = FakeExchange()
        exchange.asyncio_loop = (
            asyncio.get_running_loop()
        )

        install_ccxt_spawn_lifecycle_guard(
            exchange
        )

        started = asyncio.Event()

        async def work():
            started.set()
            await asyncio.sleep(
                3600
            )

        future = exchange.spawn(
            work
        )

        await started.wait()

        assert len(
            exchange._arbos_spawn_tasks
        ) == 1

        result = await (
            exchange.drain_spawn_tasks(
                cancel=True,
            )
        )

        assert result[
            "task_count"
        ] == 1

        assert result[
            "cancelled_task_count"
        ] == 1

        assert result[
            "task_error_count"
        ] == 0

        assert result[
            "remaining_task_count"
        ] == 0

        assert (
            exchange._arbos_spawn_tasks
            == set()
        )

        assert future.cancelled()

    asyncio.run(exercise())
