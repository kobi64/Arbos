import pytest

from exchanges.verified_raw_only_market_source import (
    VerifiedRawOnlyMarketSource,
)


class FakeExchange:
    def load_markets(self):
        return {
            "BTC/USDT": {
                "spot": True,
                "active": True,
            },
        }


class FakeNativeMarketSource:
    def fetch(self):
        return {
            "fetch_complete": True,
            "symbols": [
                "BTC/USDT",
                "COTI/USDT",
                "SUSPENDED/USDT",
            ],
            "markets": [
                {
                    "symbol": "BTC/USDT",
                    "status": "TRADING",
                    "order_types": [
                        "LIMIT",
                        "MARKET",
                    ],
                },
                {
                    "symbol": "COTI/USDT",
                    "status": "TRADING",
                    "order_types": [
                        "LIMIT",
                        "MARKET",
                    ],
                },
                {
                    "symbol": "SUSPENDED/USDT",
                    "status": "SUSPENDED",
                    "order_types": [
                        "LIMIT",
                        "MARKET",
                    ],
                },
            ],
        }


class FailedNativeMarketSource:
    def fetch(self):
        return {
            "fetch_complete": False,
            "symbols": [],
            "markets": [],
        }


def source():
    return VerifiedRawOnlyMarketSource(
        exchange_id="digifinex",
        exchange=FakeExchange(),
        native_market_source=(
            FakeNativeMarketSource()
        ),
    )


def test_verifies_trading_raw_only_market():
    assert source().is_verified(
        "COTI/USDT"
    ) is True


def test_does_not_classify_matched_market_as_raw_only():
    assert source().is_verified(
        "BTC/USDT"
    ) is False


def test_rejects_suspended_raw_only_market():
    assert source().is_verified(
        "SUSPENDED/USDT"
    ) is False


def test_unknown_market_is_not_verified():
    assert source().is_verified(
        "UNKNOWN/USDT"
    ) is False


def test_normalizes_symbol():
    assert source().is_verified(
        " coti/usdt "
    ) is True


def test_failed_native_catalogue_verifies_nothing():
    verifier = VerifiedRawOnlyMarketSource(
        exchange_id="digifinex",
        exchange=FakeExchange(),
        native_market_source=(
            FailedNativeMarketSource()
        ),
    )

    assert verifier.is_verified(
        "COTI/USDT"
    ) is False


def test_requires_exchange_id():
    with pytest.raises(
        ValueError,
        match="exchange_id is required",
    ):
        VerifiedRawOnlyMarketSource(
            exchange_id="",
            exchange=FakeExchange(),
            native_market_source=(
                FakeNativeMarketSource()
            ),
        )


def test_requires_exchange():
    with pytest.raises(
        ValueError,
        match="exchange is required",
    ):
        VerifiedRawOnlyMarketSource(
            exchange_id="digifinex",
            exchange=None,
            native_market_source=(
                FakeNativeMarketSource()
            ),
        )


def test_requires_native_market_source():
    with pytest.raises(
        ValueError,
        match="native_market_source is required",
    ):
        VerifiedRawOnlyMarketSource(
            exchange_id="digifinex",
            exchange=FakeExchange(),
            native_market_source=None,
        )
