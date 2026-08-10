import pytest

from exchanges.verified_native_order_book_provider import (
    VerifiedNativeOrderBookProvider,
)


class FakeNormalProvider:
    def snapshot(self, symbol, limit=None):
        if symbol == "BTC/USDT":
            return {
                "symbol": symbol,
                "best_bid": 50000.0,
                "best_ask": 50001.0,
            }

        raise ValueError("normalized market unavailable")


class FakeNativeProvider:
    def snapshot(self, symbol, limit=None):
        if symbol != "COTI/USDT":
            raise ValueError("native market unavailable")

        return {
            "symbol": symbol,
            "best_bid": 0.01142,
            "best_ask": 0.01155,
        }


class FakeVerifiedMarketSource:
    def is_verified(self, symbol):
        return symbol == "COTI/USDT"


def build_provider():
    return VerifiedNativeOrderBookProvider(
        exchange_id="digifinex",
        normal_provider=FakeNormalProvider(),
        native_provider=FakeNativeProvider(),
        verified_market_source=FakeVerifiedMarketSource(),
    )


def test_uses_normal_provider_when_market_is_available():
    provider = build_provider()

    result = provider.snapshot("BTC/USDT")

    assert result["best_bid"] == 50000.0
    assert result["market_source"] == "CCXT_NORMALIZED"


def test_uses_native_provider_for_verified_raw_only_market():
    provider = build_provider()

    result = provider.snapshot("COTI/USDT")

    assert result["best_bid"] == 0.01142
    assert result["best_ask"] == 0.01155
    assert result["market_verified"] is True
    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False

    assert result["market_source"] == (
        "VERIFIED_RAW_ONLY_DIGIFINEX_NATIVE"
    )


def test_unverified_native_market_is_blocked():
    provider = build_provider()

    with pytest.raises(ValueError):
        provider.snapshot("UNKNOWN/USDT")


def test_requires_exchange_id():
    with pytest.raises(
        ValueError,
        match="exchange_id is required",
    ):
        VerifiedNativeOrderBookProvider(
            exchange_id="",
            normal_provider=FakeNormalProvider(),
            native_provider=FakeNativeProvider(),
            verified_market_source=FakeVerifiedMarketSource(),
        )


def test_requires_all_providers():
    with pytest.raises(
        ValueError,
        match="normal_provider is required",
    ):
        VerifiedNativeOrderBookProvider(
            exchange_id="digifinex",
            normal_provider=None,
            native_provider=FakeNativeProvider(),
            verified_market_source=FakeVerifiedMarketSource(),
        )


def test_normalizes_symbol_and_exchange_id():
    provider = VerifiedNativeOrderBookProvider(
        exchange_id=" DigiFinex ",
        normal_provider=FakeNormalProvider(),
        native_provider=FakeNativeProvider(),
        verified_market_source=FakeVerifiedMarketSource(),
    )

    result = provider.snapshot(" coti/usdt ")

    assert result["symbol"] == "COTI/USDT"

    assert result["market_source"] == (
        "VERIFIED_RAW_ONLY_DIGIFINEX_NATIVE"
    )
