import pytest

from core.bridge_conversion_quote_engine import (
    BridgeConversionQuoteEngine,
)


class FakeSpotQuoteProvider:
    def __init__(self, available=True, output_amount=0.0025):
        self.available = available
        self.output_amount = output_amount
        self.calls = []

    def quote(
        self,
        from_asset,
        to_asset,
        amount,
    ):
        self.calls.append({
            "from_asset": from_asset,
            "to_asset": to_asset,
            "amount": amount,
        })

        if not self.available:
            return None

        return {
            "method": "spot",
            "from_asset": from_asset,
            "to_asset": to_asset,
            "input_amount": amount,
            "output_amount": self.output_amount,
        }


class FakeConvertQuoteProvider:
    def __init__(self, available=True, output_amount=0.0024):
        self.available = available
        self.output_amount = output_amount
        self.calls = []

    def quote(
        self,
        from_asset,
        to_asset,
        amount,
    ):
        self.calls.append({
            "from_asset": from_asset,
            "to_asset": to_asset,
            "amount": amount,
        })

        if not self.available:
            return None

        return {
            "method": "convert_swap",
            "from_asset": from_asset,
            "to_asset": to_asset,
            "input_amount": amount,
            "output_amount": self.output_amount,
        }


def test_prefers_spot_quote_when_available():
    spot = FakeSpotQuoteProvider(
        available=True,
        output_amount=0.0025,
    )
    convert = FakeConvertQuoteProvider(
        available=True,
        output_amount=0.0024,
    )

    engine = BridgeConversionQuoteEngine(
        spot_quote_provider=spot,
        convert_quote_provider=convert,
    )

    result = engine.quote(
        from_asset="COINX",
        to_asset="BTC",
        amount=1000.0,
    )

    assert result["method"] == "spot"
    assert result["output_amount"] == 0.0025
    assert len(spot.calls) == 1
    assert len(convert.calls) == 0


def test_falls_back_to_convert_swap_when_spot_unavailable():
    spot = FakeSpotQuoteProvider(
        available=False,
    )
    convert = FakeConvertQuoteProvider(
        available=True,
        output_amount=0.0024,
    )

    engine = BridgeConversionQuoteEngine(
        spot_quote_provider=spot,
        convert_quote_provider=convert,
    )

    result = engine.quote(
        from_asset="COINX",
        to_asset="BTC",
        amount=1000.0,
    )

    assert result["method"] == "convert_swap"
    assert result["output_amount"] == 0.0024
    assert len(spot.calls) == 1
    assert len(convert.calls) == 1


def test_rejects_when_no_conversion_quote_is_available():
    engine = BridgeConversionQuoteEngine(
        spot_quote_provider=FakeSpotQuoteProvider(
            available=False,
        ),
        convert_quote_provider=FakeConvertQuoteProvider(
            available=False,
        ),
    )

    result = engine.quote(
        from_asset="COINX",
        to_asset="BTC",
        amount=1000.0,
    )

    assert result["available"] is False
    assert result["reason"] == "conversion_quote_unavailable"


def test_unavailable_conversion_quote_preserves_output_as_unknown():
    class NoQuoteProvider:
        def quote(self, **kwargs):
            return None

    engine = BridgeConversionQuoteEngine(
        spot_quote_provider=NoQuoteProvider(),
        convert_quote_provider=NoQuoteProvider(),
    )

    result = engine.quote(
        from_asset="USDT",
        to_asset="USDC",
        amount=100.0,
    )

    assert result["available"] is False
    assert result["input_amount"] == 100.0
    assert result["output_amount"] is None
    assert result["reason"] == "conversion_quote_unavailable"
