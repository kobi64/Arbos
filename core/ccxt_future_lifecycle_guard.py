"""
ArbOS™
EX-373
CCXT Future Lifecycle Guard

Compatibility guard for CCXT async_support / CCXT Pro Future
objects.

Purpose:
- retrieve exceptions from completed CCXT Futures;
- prevent asyncio "Future exception was never retrieved" warnings
  when CCXT background subscription work loses its consumer;
- preserve normal Future result / exception semantics for callers
  that later await the same Future.

The installed CCXT package is not modified.

No authentication.
No transfers.
No order submission.
"""

import asyncio

from ccxt.async_support.base.ws.future import Future


_INSTALLED = False
_ORIGINAL_SET_EXCEPTION = None


def _retrieve_completed_exception(
    completed_future,
):
    if completed_future.cancelled():
        return

    try:
        completed_future.exception()

    except asyncio.CancelledError:
        pass

    except Exception:
        # Calling exception() marks the exception as retrieved.
        #
        # This does NOT remove the exception from the Future.
        # A later `await future` still raises the same exception.
        pass


def install_ccxt_future_lifecycle_guard():
    """
    Install one process-wide guard for CCXT's Future subclass.

    Idempotent.

    The guard observes exceptions after CCXT completes a Future,
    including Futures created outside exchange.spawn().
    """

    global _INSTALLED
    global _ORIGINAL_SET_EXCEPTION

    if _INSTALLED:
        return {
            "installed": False,
            "already_installed": True,
        }

    _ORIGINAL_SET_EXCEPTION = (
        Future.set_exception
    )

    def guarded_set_exception(
        self,
        exception,
    ):
        result = _ORIGINAL_SET_EXCEPTION(
            self,
            exception,
        )

        self.add_done_callback(
            _retrieve_completed_exception
        )

        return result

    Future.set_exception = (
        guarded_set_exception
    )

    _INSTALLED = True

    return {
        "installed": True,
        "already_installed": False,
    }


def ccxt_future_lifecycle_guard_installed():
    return _INSTALLED
