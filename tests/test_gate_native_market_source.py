from exchanges.gate_native_market_source import (
    GateNativeMarketSource,
)


class FakeExchange:
    def publicSpotGetCurrencyPairs(self):
        return [
            {
                "id": "BTC_USDT",
                "base": "BTC",
                "quote": "USDT",
                "trade_status": "tradable",
                "min_base_amount": "0.0001",
                "min_quote_amount": "1",
                "amount_precision": 6,
                "precision": 2,
            },
            {
                "id": "OLD_USDT",
                "base": "OLD",
                "quote": "USDT",
                "trade_status": "untradable",
                "min_base_amount": "1",
                "min_quote_amount": "1",
                "amount_precision": 2,
                "precision": 4,
            },
        ]


class FailedExchange:
    def publicSpotGetCurrencyPairs(self):
        raise RuntimeError(
            "native catalogue unavailable"
        )


def test_fetches_gate_native_catalogue():
    result = GateNativeMarketSource(
        FakeExchange()
    ).fetch()

    assert result["fetch_complete"] is True
    assert result["exchange_id"] == "gate"

    assert result["symbols"] == [
        "BTC/USDT",
        "OLD/USDT",
    ]


def test_normalizes_gate_market_status():
    result = GateNativeMarketSource(
        FakeExchange()
    ).fetch()

    markets = result["markets"]

    assert markets[0]["symbol"] == "BTC/USDT"
    assert markets[0]["status"] == "TRADING"

    assert markets[1]["symbol"] == "OLD/USDT"
    assert markets[1]["status"] == "SUSPENDED"


def test_preserves_gate_market_metadata():
    result = GateNativeMarketSource(
        FakeExchange()
    ).fetch()

    market = result["markets"][0]

    assert market["minimum_amount"] == "0.0001"
    assert market["minimum_value"] == "1"
    assert market["amount_precision"] == 6
    assert market["price_precision"] == 2

    assert market["order_types"] == [
        "LIMIT",
        "MARKET",
    ]

    assert market["raw"]["id"] == "BTC_USDT"


def test_gate_native_failure_is_fail_closed():
    result = GateNativeMarketSource(
        FailedExchange()
    ).fetch()

    assert result["fetch_complete"] is False
    assert result["symbols"] == []
    assert result["markets"] == []


def test_requires_exchange():
    try:
        GateNativeMarketSource(None)
        assert False
    except ValueError as exc:
        assert str(exc) == "exchange is required"
