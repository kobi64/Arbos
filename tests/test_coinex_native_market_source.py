from exchanges.coinex_native_market_source import (
    CoinExNativeMarketSource,
)


class FakeExchange:
    def publicGetSpotMarket(self):
        return {
            "code": 0,
            "data": [
                {
                    "base_ccy": "BTC",
                    "base_ccy_precision": 8,
                    "delisted_at": 0,
                    "is_amm_available": True,
                    "is_api_trading_available": True,
                    "is_margin_available": False,
                    "is_pre_market_trading_available": False,
                    "maker_fee_rate": "0.002",
                    "market": "BTCUSDT",
                    "min_amount": "0.0001",
                    "quote_ccy": "USDT",
                    "quote_ccy_precision": 2,
                    "status": "online",
                    "taker_fee_rate": "0.002",
                },
                {
                    "base_ccy": "HALT",
                    "base_ccy_precision": 8,
                    "delisted_at": 0,
                    "is_amm_available": False,
                    "is_api_trading_available": False,
                    "is_margin_available": False,
                    "is_pre_market_trading_available": False,
                    "maker_fee_rate": "0.003",
                    "market": "HALTUSDT",
                    "min_amount": "10",
                    "quote_ccy": "USDT",
                    "quote_ccy_precision": 6,
                    "status": "offline",
                    "taker_fee_rate": "0.003",
                },
            ],
        }


class FailedExchange:
    def publicGetSpotMarket(self):
        raise RuntimeError(
            "native catalogue unavailable"
        )


def test_fetches_coinex_native_catalogue():
    result = CoinExNativeMarketSource(
        FakeExchange()
    ).fetch()

    assert result["fetch_complete"] is True
    assert result["exchange_id"] == "coinex"

    assert result["symbols"] == [
        "BTC/USDT",
        "HALT/USDT",
    ]


def test_normalizes_coinex_status():
    result = CoinExNativeMarketSource(
        FakeExchange()
    ).fetch()

    markets = result["markets"]

    assert markets[0]["status"] == "TRADING"
    assert markets[1]["status"] == "SUSPENDED"


def test_preserves_coinex_market_metadata():
    result = CoinExNativeMarketSource(
        FakeExchange()
    ).fetch()

    market = result["markets"][0]

    assert market["minimum_amount"] == "0.0001"
    assert market["price_precision"] == 2
    assert market["amount_precision"] == 8

    assert market[
        "api_trading_available"
    ] is True

    assert market[
        "maker_fee_rate"
    ] == "0.002"

    assert market[
        "taker_fee_rate"
    ] == "0.002"

    assert market[
        "native_symbol"
    ] == "BTCUSDT"

    assert market[
        "raw"
    ]["market"] == "BTCUSDT"


def test_failed_native_fetch_is_fail_closed():
    result = CoinExNativeMarketSource(
        FailedExchange()
    ).fetch()

    assert result["fetch_complete"] is False
    assert result["symbols"] == []
    assert result["markets"] == []


def test_requires_exchange():
    try:
        CoinExNativeMarketSource(None)
        assert False
    except ValueError as exc:
        assert str(exc) == "exchange is required"


def test_source_is_paper_safe():
    result = CoinExNativeMarketSource(
        FakeExchange()
    ).fetch()

    assert result[
        "live_order_submitted"
    ] is False
