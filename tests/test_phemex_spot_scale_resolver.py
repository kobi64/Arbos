import pytest

from exchanges.phemex_spot_scale_resolver import (
    PhemexSpotScaleResolver,
)


class FakeClient:
    def fetch_products(self):
        return {
            "code": 0,
            "data": {
                "currencies": [
                    {
                        "currency": "BTC",
                        "valueScale": 8,
                    },
                    {
                        "currency": "ABC",
                        "valueScale": 6,
                    },
                ],
                "products": [
                    {
                        "symbol": "sBTCUSDT",
                        "type": "Spot",
                        "baseCurrency": "BTC",
                        "quoteCurrency": "USDT",
                        "priceScale": 8,
                        "status": "Listed",
                    },
                    {
                        "symbol": "sABCUSDT",
                        "type": "Spot",
                        "baseCurrency": "ABC",
                        "quoteCurrency": "USDT",
                        "priceScale": 5,
                        "status": "Listed",
                    },
                    {
                        "symbol": "BTCUSDT",
                        "type": "PerpetualV2",
                        "baseCurrency": "BTC",
                        "quoteCurrency": "USDT",
                        "priceScale": 0,
                        "status": "Listed",
                    },
                ],
            },
        }


def test_resolves_btc_spot_scales():
    resolver = PhemexSpotScaleResolver(
        client=FakeClient(),
    )

    result = resolver.resolve(
        "BTC/USDT"
    )

    assert result == {
        "native_symbol": "sBTCUSDT",
        "price_scale": 8,
        "quantity_scale": 8,
    }


def test_resolves_market_specific_scales():
    resolver = PhemexSpotScaleResolver(
        client=FakeClient(),
    )

    result = resolver.resolve(
        "ABC/USDT"
    )

    assert result == {
        "native_symbol": "sABCUSDT",
        "price_scale": 5,
        "quantity_scale": 6,
    }


def test_perpetual_product_is_not_used():
    resolver = PhemexSpotScaleResolver(
        client=FakeClient(),
    )

    result = resolver.resolve(
        "BTCUSDT"
    )

    assert result[
        "native_symbol"
    ] == "sBTCUSDT"

    assert result[
        "price_scale"
    ] == 8


def test_unknown_symbol_fails_closed():
    resolver = PhemexSpotScaleResolver(
        client=FakeClient(),
    )

    with pytest.raises(
        RuntimeError,
        match="Phemex spot scale unavailable",
    ):
        resolver.resolve(
            "UNKNOWN/USDT"
        )


def test_client_is_required():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        PhemexSpotScaleResolver(
            client=None,
        )


def test_invalid_product_metadata_fails_closed():
    class InvalidClient:
        def fetch_products(self):
            return {
                "code": 0,
                "data": {},
            }

    resolver = PhemexSpotScaleResolver(
        client=InvalidClient(),
    )

    with pytest.raises(
        RuntimeError,
        match="Phemex spot scale unavailable",
    ):
        resolver.resolve(
            "BTC/USDT"
        )
