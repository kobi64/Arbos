from exchanges.digifinex_native_market_source import (
    DigiFinexNativeMarketSource,
)


class FakeExchange:
    def publicSpotGetMarketSymbols(self):
        return {
            "symbol_list": [
                {
                    "symbol": "BTC_USDT",
                    "base_asset": "BTC",
                    "quote_asset": "USDT",
                    "status": "TRADING",
                    "order_types": ["LIMIT", "MARKET"],
                    "minimum_amount": 0.0001,
                    "minimum_value": 2,
                    "price_precision": 2,
                    "amount_precision": 7,
                    "zone": "MAIN",
                },
                {
                    "symbol": "COTI_USDT",
                    "base_asset": "COTI",
                    "quote_asset": "USDT",
                    "status": "TRADING",
                    "order_types": ["LIMIT", "MARKET"],
                    "minimum_amount": 1,
                    "minimum_value": 2,
                    "price_precision": 6,
                    "amount_precision": 2,
                    "zone": "INNOVATE",
                },
            ]
        }


class FirstMethodFailsExchange:
    def publicSpotGetMarketSymbols(self):
        raise RuntimeError("endpoint unavailable")

    def public_spot_get_market_symbols(self):
        return {
            "symbol_list": [
                {
                    "symbol": "COTI_USDT",
                    "base_asset": "COTI",
                    "quote_asset": "USDT",
                    "status": "TRADING",
                },
            ]
        }


class EmptyExchange:
    def publicSpotGetMarketSymbols(self):
        return {"symbol_list": []}


def test_fetches_native_market_catalogue():
    result = DigiFinexNativeMarketSource(
        FakeExchange()
    ).fetch()

    assert result["fetch_complete"] is True
    assert result["market_count"] == 2
    assert "BTC/USDT" in result["symbols"]
    assert "COTI/USDT" in result["symbols"]


def test_preserves_native_market_metadata():
    result = DigiFinexNativeMarketSource(
        FakeExchange()
    ).fetch()

    markets = {
        item["symbol"]: item
        for item in result["markets"]
    }

    coti = markets["COTI/USDT"]

    assert coti["status"] == "TRADING"
    assert "MARKET" in coti["order_types"]
    assert coti["price_precision"] == 6
    assert coti["minimum_value"] == 2


def test_falls_back_when_first_endpoint_fails():
    result = DigiFinexNativeMarketSource(
        FirstMethodFailsExchange()
    ).fetch()

    assert result["fetch_complete"] is True
    assert result["method"] == (
        "public_spot_get_market_symbols"
    )
    assert "COTI/USDT" in result["symbols"]
    assert len(result["errors"]) == 1


def test_empty_catalogue_is_not_accepted():
    result = DigiFinexNativeMarketSource(
        EmptyExchange()
    ).fetch()

    assert result["fetch_complete"] is False
    assert result["market_count"] == 0


def test_missing_exchange_is_rejected():
    try:
        DigiFinexNativeMarketSource(None)
        assert False
    except ValueError as exc:
        assert str(exc) == "exchange is required"


def test_native_source_never_submits_live_order():
    result = DigiFinexNativeMarketSource(
        FakeExchange()
    ).fetch()

    assert result["live_order_submitted"] is False
