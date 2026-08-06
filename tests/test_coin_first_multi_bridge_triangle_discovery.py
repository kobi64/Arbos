import pytest

from core.coin_first_multi_bridge_triangle_discovery import (
    CoinFirstMultiBridgeTriangleDiscovery,
)


def sample_markets():
    return {
        "COINX/USDT": {
            "spot": True,
            "active": True,
        },
        "COINX/BTC": {
            "spot": True,
            "active": True,
        },
        "BTC/USDT": {
            "spot": True,
            "active": True,
        },
        "COINX/ETH": {
            "spot": True,
            "active": True,
        },
        "ETH/USDT": {
            "spot": True,
            "active": True,
        },
        "COINX/SOL": {
            "spot": True,
            "active": True,
        },
        "SOL/USDT": {
            "spot": True,
            "active": True,
        },
    }


def test_discovers_all_coin_first_internal_bridge_routes():
    discovery = CoinFirstMultiBridgeTriangleDiscovery()

    routes = discovery.discover(
        markets=sample_markets(),
        quote_asset="USDT",
        coin_asset="COINX",
    )

    route_ids = {
        route["route_id"]
        for route in routes
    }

    assert route_ids == {
        "USDT-COINX-BTC-USDT",
        "USDT-COINX-ETH-USDT",
        "USDT-COINX-SOL-USDT",
    }


def test_coin_is_bought_first_then_sold_into_bridge():
    discovery = CoinFirstMultiBridgeTriangleDiscovery()

    routes = discovery.discover(
        markets=sample_markets(),
        quote_asset="USDT",
        coin_asset="COINX",
    )

    btc_route = next(
        route
        for route in routes
        if route["bridge_asset"] == "BTC"
    )

    assert btc_route["legs"] == [
        {
            "symbol": "COINX/USDT",
            "side": "buy",
        },
        {
            "symbol": "COINX/BTC",
            "side": "sell",
        },
        {
            "symbol": "BTC/USDT",
            "side": "sell",
        },
    ]
