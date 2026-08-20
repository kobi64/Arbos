import asyncio
import json

import aiohttp

from exchanges.htx_native_bbo_feed import (
    HTXNativeBBOFeed,
)


class FakeIntake:
    def __init__(self):
        self.snapshots = []

    def submit(
        self,
        snapshot,
    ):
        self.snapshots.append(
            snapshot
        )

        return {
            "accepted": True
        }


class Message:
    def __init__(
        self,
        payload,
    ):
        self.type = (
            aiohttp.WSMsgType.TEXT
        )

        self.data = (
            json.dumps(
                payload
            )
        )


class FakeWebSocket:
    def __init__(
        self,
        messages,
    ):
        self._messages = list(
            messages
        )

        self.sent = []

    async def send_json(
        self,
        payload,
    ):
        self.sent.append(
            payload
        )

    async def receive(
        self,
    ):
        if self._messages:
            return self._messages.pop(
                0
            )

        await asyncio.sleep(
            0.001
        )

        return Message({
            "ping": 123,
        })

    async def __aenter__(
        self,
    ):
        return self

    async def __aexit__(
        self,
        *args,
    ):
        return False


class ConnectContext:
    def __init__(
        self,
        websocket,
    ):
        self._websocket = (
            websocket
        )

    async def __aenter__(
        self,
    ):
        return self._websocket

    async def __aexit__(
        self,
        *args,
    ):
        return False


class FakeSession:
    def __init__(
        self,
        websocket,
    ):
        self._websocket = (
            websocket
        )

    def ws_connect(
        self,
        *args,
        **kwargs,
    ):
        return ConnectContext(
            self._websocket
        )

    async def __aenter__(
        self,
    ):
        return self

    async def __aexit__(
        self,
        *args,
    ):
        return False


def test_normalizes_native_htx_bbo():
    intake = FakeIntake()

    feed = HTXNativeBBOFeed(
        intake_service=intake,
        symbols=[
            "BTC/USDT"
        ],
    )

    snapshot = feed._normalize_bbo(
        {
            "ch": (
                "market."
                "btcusdt"
                ".bbo"
            ),
            "ts": 1000,
            "tick": {
                "bid": 69999.0,
                "ask": 70000.0,
                "bidSize": 1.5,
                "askSize": 2.5,
                "ts": 1000,
            },
        },
        {
            "btcusdt": (
                "BTC/USDT"
            ),
        },
    )

    assert snapshot[
        "exchange_id"
    ] == "htx"

    assert snapshot[
        "symbol"
    ] == "BTC/USDT"

    assert snapshot[
        "best_bid"
    ] == 69999.0

    assert snapshot[
        "best_ask"
    ] == 70000.0

    assert snapshot[
        "bids"
    ] == [
        [
            69999.0,
            1.5,
        ]
    ]

    assert snapshot[
        "asks"
    ] == [
        [
            70000.0,
            2.5,
        ]
    ]


def test_rejects_locked_or_crossed_bbo():
    feed = HTXNativeBBOFeed(
        intake_service=(
            FakeIntake()
        ),
        symbols=[
            "BTC/USDT"
        ],
    )

    result = feed._normalize_bbo(
        {
            "ch": (
                "market."
                "btcusdt"
                ".bbo"
            ),
            "tick": {
                "bid": 100.0,
                "ask": 100.0,
            },
        },
        {
            "btcusdt": (
                "BTC/USDT"
            ),
        },
    )

    assert result is None


def test_feed_submits_bbo_into_intake():
    intake = FakeIntake()

    websocket = FakeWebSocket([
        Message({
            "status": "ok",
            "subbed": (
                "market."
                "btcusdt"
                ".bbo"
            ),
        }),
        Message({
            "ch": (
                "market."
                "btcusdt"
                ".bbo"
            ),
            "ts": 1000,
            "tick": {
                "bid": 69999.0,
                "ask": 70000.0,
                "bidSize": 1.0,
                "askSize": 2.0,
                "ts": 1000,
            },
        }),
    ])

    feed = HTXNativeBBOFeed(
        intake_service=intake,
        symbols=[
            "BTC/USDT"
        ],
        session_factory=(
            lambda: FakeSession(
                websocket
            )
        ),
    )

    result = asyncio.run(
        feed.run_once(
            duration_seconds=0.02
        )
    )

    assert result[
        "subscription_acks"
    ] == 1

    assert (
        result[
            "received_symbol_count"
        ]
        == 1
    )

    assert len(
        intake.snapshots
    ) == 1

    assert (
        intake.snapshots[
            0
        ][
            "source"
        ]
        == "htx_native_bbo"
    )


def test_missing_quiet_symbol_does_not_fail_feed():
    intake = FakeIntake()

    websocket = FakeWebSocket([
        Message({
            "status": "ok",
            "subbed": (
                "market."
                "btcusdt"
                ".bbo"
            ),
        }),
        Message({
            "status": "ok",
            "subbed": (
                "market."
                "aceusdt"
                ".bbo"
            ),
        }),
        Message({
            "ch": (
                "market."
                "btcusdt"
                ".bbo"
            ),
            "ts": 1000,
            "tick": {
                "bid": 69999.0,
                "ask": 70000.0,
                "bidSize": 1.0,
                "askSize": 1.0,
            },
        }),
    ])

    feed = HTXNativeBBOFeed(
        intake_service=intake,
        symbols=[
            "BTC/USDT",
            "ACE/USDT",
        ],
        session_factory=(
            lambda: FakeSession(
                websocket
            )
        ),
    )

    result = asyncio.run(
        feed.run_once(
            duration_seconds=0.02
        )
    )

    assert (
        result[
            "received_symbol_count"
        ]
        == 1
    )

    assert (
        result[
            "missing_symbols"
        ]
        == [
            "ACE/USDT"
        ]
    )

    assert result[
        "paper_only"
    ] is True

    assert (
        result[
            "live_order_submitted"
        ]
        is False
    )


def test_missing_dependencies_are_rejected():
    try:
        HTXNativeBBOFeed(
            intake_service=None,
            symbols=[
                "BTC/USDT"
            ],
        )

        assert False

    except ValueError as exc:
        assert (
            str(exc)
            == "intake_service is required"
        )
