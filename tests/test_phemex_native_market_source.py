from exchanges.phemex_native_market_source import (
    PhemexNativeMarketSource,
)


class FakePhemexExchange:
    def publicGetProducts(self):
        return {
            "code": 0,
            "data": {
                "products": [
                    {
                        "symbol": "sBTCUSDT",
                        "type": "Spot",
                        "baseCurrency": "BTC",
                        "quoteCurrency": "USDT",
                        "status": "Listed",
                        "priceScale": 8,
                        "pricePrecision": 2,
                        "baseQtyPrecision": 6,
                        "minOrderValue": "1 USDT",
                        "defaultMakerFee": "0.001",
                        "defaultTakerFee": "0.001",
                    },
                    {
                        "symbol": "BTCUSDT",
                        "type": "PerpetualV2",
                        "baseCurrency": "BTC",
                        "quoteCurrency": "USDT",
                        "status": "Listed",
                    },
                ],
                "perpProductsV2": [
                    {
                        "symbol": "BTCUSDT",
                        "type": "PerpetualV2",
                        "baseCurrency": "BTC",
                        "quoteCurrency": "USDT",
                        "status": "Listed",
                    },
                ],
            },
        }


def test_fetch_normalizes_phemex_spot_market():
    result = PhemexNativeMarketSource(
        FakePhemexExchange()
    ).fetch()

    assert result["exchange_id"] == "phemex"
    assert result["fetch_complete"] is True
    assert result["market_count"] == 1
    assert result["symbols"] == ["BTC/USDT"]

    market = result["markets"][0]

    assert market["symbol"] == "BTC/USDT"
    assert market["native_symbol"] == "sBTCUSDT"
    assert market["status"] == "TRADING"
    assert market["price_scale"] == 8
    assert market["price_precision"] == 2
    assert market["amount_precision"] == 6
    assert market["maker_fee_rate"] == "0.001"
    assert market["taker_fee_rate"] == "0.001"


def test_perpetual_contract_is_not_exposed_as_spot():
    result = PhemexNativeMarketSource(
        FakePhemexExchange()
    ).fetch()

    assert result["market_count"] == 1

    native_symbols = [
        market["native_symbol"]
        for market in result["markets"]
    ]

    assert "BTCUSDT" not in native_symbols
    assert "sBTCUSDT" in native_symbols


def test_non_listed_spot_market_is_suspended():
    class Exchange:
        def publicGetProducts(self):
            return {
                "code": 0,
                "data": {
                    "products": [
                        {
                            "symbol": "sABCUSDT",
                            "type": "Spot",
                            "baseCurrency": "ABC",
                            "quoteCurrency": "USDT",
                            "status": "Delisted",
                            "priceScale": 8,
                        },
                    ],
                },
            }

    result = PhemexNativeMarketSource(
        Exchange()
    ).fetch()

    assert result["markets"][0]["status"] == "SUSPENDED"


def test_failed_exchange_call_returns_safe_result():
    class Exchange:
        def publicGetProducts(self):
            raise RuntimeError("offline")

    result = PhemexNativeMarketSource(
        Exchange()
    ).fetch()

    assert result == {
        "exchange_id": "phemex",
        "fetch_complete": False,
        "symbols": [],
        "markets": [],
        "market_count": 0,
        "live_order_submitted": False,
    }


def test_invalid_payload_returns_safe_result():
    class Exchange:
        def publicGetProducts(self):
            return []

    result = PhemexNativeMarketSource(
        Exchange()
    ).fetch()

    assert result["fetch_complete"] is False
    assert result["market_count"] == 0


def test_live_order_is_never_submitted():
    result = PhemexNativeMarketSource(
        FakePhemexExchange()
    ).fetch()

    assert result["live_order_submitted"] is False
