from exchanges.kucoin_native_market_source import (
    KuCoinNativeMarketSource,
)


class FakeExchange:
    def publicGetSymbols(self):
        return {
            "code": "200000",
            "data": [
                {
                    "symbol": "COTI-USDT",
                    "baseCurrency": "COTI",
                    "quoteCurrency": "USDT",
                    "enableTrading": True,
                },
                {
                    "symbol": "ABC-USDT",
                    "baseCurrency": "ABC",
                    "quoteCurrency": "USDT",
                    "enableTrading": False,
                },
            ],
        }


class FailedExchange:
    def publicGetSymbols(self):
        raise RuntimeError("native failure")


def test_fetches_native_market_catalogue():
    result = KuCoinNativeMarketSource(
        FakeExchange()
    ).fetch()

    assert result["fetch_complete"] is True
    assert result["symbols"] == [
        "COTI/USDT",
        "ABC/USDT",
    ]


def test_normalizes_native_market_records():
    result = KuCoinNativeMarketSource(
        FakeExchange()
    ).fetch()

    markets = result["markets"]

    assert markets[0]["symbol"] == "COTI/USDT"
    assert markets[0]["status"] == "TRADING"
    assert markets[1]["symbol"] == "ABC/USDT"
    assert markets[1]["status"] == "SUSPENDED"


def test_preserves_raw_market_metadata():
    result = KuCoinNativeMarketSource(
        FakeExchange()
    ).fetch()

    market = result["markets"][0]

    assert market["raw"]["symbol"] == "COTI-USDT"
    assert market["raw"]["enableTrading"] is True


def test_failed_native_fetch_is_fail_closed():
    result = KuCoinNativeMarketSource(
        FailedExchange()
    ).fetch()

    assert result["fetch_complete"] is False
    assert result["symbols"] == []
    assert result["markets"] == []


def test_requires_exchange():
    try:
        KuCoinNativeMarketSource(None)
        assert False
    except ValueError as exc:
        assert str(exc) == "exchange is required"
