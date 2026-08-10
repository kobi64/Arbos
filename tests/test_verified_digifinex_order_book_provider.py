import pytest

from exchanges.verified_digifinex_order_book_provider import (
    VerifiedDigiFinexOrderBookProvider,
)


class FakeExchange:
    def load_markets(self):
        return {
            "BTC/USDT": {
                "spot": True,
                "active": True,
            },
        }

    def fetch_order_book(
        self,
        symbol,
        limit=None,
    ):
        if symbol == "BTC/USDT":
            return {
                "bids": [[50000.0, 1.0]],
                "asks": [[50001.0, 1.0]],
            }

        raise ValueError("unknown symbol")

    def publicSpotGetMarketSymbols(self):
        return {
            "symbol_list": [
                {
                    "symbol": "BTC_USDT",
                    "base_asset": "BTC",
                    "quote_asset": "USDT",
                    "status": "TRADING",
                    "order_types": [
                        "LIMIT",
                        "MARKET",
                    ],
                },
                {
                    "symbol": "COTI_USDT",
                    "base_asset": "COTI",
                    "quote_asset": "USDT",
                    "status": "TRADING",
                    "order_types": [
                        "LIMIT",
                        "MARKET",
                    ],
                    "minimum_value": 2,
                },
            ],
        }

    def publicSpotGetOrderBook(
        self,
        params,
    ):
        assert params["symbol"] == (
            "coti_usdt"
        )

        return {
            "code": 0,
            "asks": [
                [0.01164, 1000],
                [0.01155, 2000],
            ],
            "bids": [
                [0.01142, 1000],
                [0.01141, 2000],
            ],
            "date": 123,
        }


def test_uses_normal_ccxt_market_when_available():
    provider = (
        VerifiedDigiFinexOrderBookProvider(
            FakeExchange()
        )
    )

    result = provider.snapshot(
        "BTC/USDT"
    )

    assert result["best_bid"] == 50000.0
    assert result["market_source"] == (
        "CCXT_NORMALIZED"
    )


def test_uses_native_depth_for_verified_raw_only_market():
    provider = (
        VerifiedDigiFinexOrderBookProvider(
            FakeExchange()
        )
    )

    result = provider.snapshot(
        "COTI/USDT"
    )

    assert result["market_verified"] is True

    assert result["market_source"] == (
        "VERIFIED_RAW_ONLY_DIGIFINEX_NATIVE"
    )

    assert result["best_bid"] == 0.01142
    assert result["best_ask"] == 0.01155


def test_unverified_raw_market_is_not_allowed():
    class SuspendedExchange(FakeExchange):
        def publicSpotGetMarketSymbols(self):
            result = super().publicSpotGetMarketSymbols()

            result["symbol_list"][1][
                "status"
            ] = "SUSPENDED"

            return result

    provider = (
        VerifiedDigiFinexOrderBookProvider(
            SuspendedExchange()
        )
    )

    with pytest.raises(Exception):
        provider.snapshot("COTI/USDT")


def test_missing_exchange_is_rejected():
    with pytest.raises(
        ValueError,
        match="exchange is required",
    ):
        VerifiedDigiFinexOrderBookProvider(
            None
        )
