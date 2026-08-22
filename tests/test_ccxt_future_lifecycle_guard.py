import asyncio

import pytest

from ccxt.async_support.base.ws.future import Future

from core.ccxt_future_lifecycle_guard import (
    ccxt_future_lifecycle_guard_installed,
    install_ccxt_future_lifecycle_guard,
)


def test_guard_installs():
    result = (
        install_ccxt_future_lifecycle_guard()
    )

    assert (
        result["installed"] is True
        or result["already_installed"] is True
    )

    assert (
        ccxt_future_lifecycle_guard_installed()
        is True
    )


def test_guard_is_idempotent():
    install_ccxt_future_lifecycle_guard()

    result = (
        install_ccxt_future_lifecycle_guard()
    )

    assert result == {
        "installed": False,
        "already_installed": True,
    }


def test_awaited_future_still_raises_original_exception():
    async def exercise():
        install_ccxt_future_lifecycle_guard()

        future = Future()

        future.set_exception(
            RuntimeError(
                "simulated failure"
            )
        )

        with pytest.raises(
            RuntimeError,
            match="simulated failure",
        ):
            await future

    asyncio.run(exercise())


def test_reject_still_raises_original_exception_when_awaited():
    async def exercise():
        install_ccxt_future_lifecycle_guard()

        future = Future()

        future.reject(
            RuntimeError(
                "rejected failure"
            )
        )

        with pytest.raises(
            RuntimeError,
            match="rejected failure",
        ):
            await future

    asyncio.run(exercise())


def test_unawaited_set_exception_is_retrieved():
    messages = []

    async def exercise():
        install_ccxt_future_lifecycle_guard()

        loop = asyncio.get_running_loop()

        previous_handler = (
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
            future = Future()

            future.set_exception(
                RuntimeError(
                    "background failure"
                )
            )

            await asyncio.sleep(0)
            await asyncio.sleep(0)

            assert future.done()

        finally:
            loop.set_exception_handler(
                previous_handler
            )

    asyncio.run(exercise())

    assert not any(
        "Future exception was never retrieved"
        in message
        for message in messages
    )


def test_unawaited_rejected_future_is_retrieved():
    messages = []

    async def exercise():
        install_ccxt_future_lifecycle_guard()

        loop = asyncio.get_running_loop()

        previous_handler = (
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
            future = Future()

            future.reject(
                RuntimeError(
                    "background rejection"
                )
            )

            await asyncio.sleep(0)
            await asyncio.sleep(0)

            assert future.done()

        finally:
            loop.set_exception_handler(
                previous_handler
            )

    asyncio.run(exercise())

    assert not any(
        "Future exception was never retrieved"
        in message
        for message in messages
    )
