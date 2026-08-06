import pytest

from core.exchange_triangle_route_discovery import (
    ExchangeTriangleRouteDiscovery,
)


def sample_markets():
    return {
        "BTC/USDT": {"spot": True},
        "ETH/BTC": {"spot": True},
        "ETH/USDT": {"spot": True},
        "SOL/BTC": {"spot": True},
        "SOL/USDT": {"spot": True},
        "ADA/USDT": {"spot": True},
    }


def test_discovers_supported_btc_triangles():
    discovery = ExchangeTriangleRouteDiscovery()

    routes = discovery.discover(
        markets=sample_markets(),
        quote_asset="USDT",
        bridge_asset="BTC",
    )

    route_ids = {route["route_id"] for route in routes}

    assert "USDT-BTC-ETH-USDT" in route_ids
    assert "USDT-BTC-SOL-USDT" in route_ids
    assert "USDT-BTC-ADA-USDT" not in route_ids


def test_missing_quote_asset_is_rejected():
    discovery = ExchangeTriangleRouteDiscovery()

    with pytest.raises(ValueError, match="quote_asset is required"):
        discovery.discover(
            markets=sample_markets(),
            quote_asset="",
            bridge_asset="BTC",
        )


def test_missing_bridge_asset_is_rejected():
    discovery = ExchangeTriangleRouteDiscovery()

    with pytest.raises(ValueError, match="bridge_asset is required"):
        discovery.discover(
            markets=sample_markets(),
            quote_asset="USDT",
            bridge_asset="",
        )


def test_ignores_non_spot_markets():
    markets = sample_markets()
    markets["XRP/BTC"] = {"spot": False}
    markets["XRP/USDT"] = {"spot": True}

    discovery = ExchangeTriangleRouteDiscovery()

    routes = discovery.discover(
        markets=markets,
        quote_asset="USDT",
        bridge_asset="BTC",
    )

    route_ids = {route["route_id"] for route in routes}

    assert "USDT-BTC-XRP-USDT" not in route_ids
