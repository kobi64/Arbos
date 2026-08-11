from exchanges.exchange_market_alias_reconciler import (
    ExchangeMarketAliasReconciler,
)


def test_reconciles_native_id_alias():
    ccxt_markets = {
        "BSV/USDT": {
            "id": "BCHSV-USDT",
            "symbol": "BSV/USDT",
            "spot": True,
            "active": True,
        },
    }

    native_markets = [
        {
            "symbol": "BCHSV/USDT",
            "status": "TRADING",
            "raw": {
                "symbol": "BCHSV-USDT",
            },
        },
    ]

    result = ExchangeMarketAliasReconciler().reconcile(
        ccxt_markets=ccxt_markets,
        native_markets=native_markets,
    )

    assert result["alias_match_count"] == 1

    assert result["alias_matches"] == [
        {
            "ccxt_symbol": "BSV/USDT",
            "native_symbol": "BCHSV/USDT",
            "native_market_id": "BCHSV-USDT",
        },
    ]


def test_reconciles_multiple_known_aliases():
    ccxt_markets = {
        "APTOSLAUNCHTOKEN/USDT": {
            "id": "ALT-USDT",
            "spot": True,
            "active": True,
        },
        "VAIOT/USDT": {
            "id": "VAI-USDT",
            "spot": True,
            "active": True,
        },
        "WAXP/USDT": {
            "id": "WAX-USDT",
            "spot": True,
            "active": True,
        },
    }

    native_markets = [
        {
            "symbol": "ALT/USDT",
            "raw": {
                "symbol": "ALT-USDT",
            },
        },
        {
            "symbol": "VAI/USDT",
            "raw": {
                "symbol": "VAI-USDT",
            },
        },
        {
            "symbol": "WAX/USDT",
            "raw": {
                "symbol": "WAX-USDT",
            },
        },
    ]

    result = ExchangeMarketAliasReconciler().reconcile(
        ccxt_markets=ccxt_markets,
        native_markets=native_markets,
    )

    assert result["alias_match_count"] == 3


def test_same_normalized_symbol_is_not_alias():
    ccxt_markets = {
        "BTC/USDT": {
            "id": "BTC-USDT",
            "spot": True,
            "active": True,
        },
    }

    native_markets = [
        {
            "symbol": "BTC/USDT",
            "raw": {
                "symbol": "BTC-USDT",
            },
        },
    ]

    result = ExchangeMarketAliasReconciler().reconcile(
        ccxt_markets=ccxt_markets,
        native_markets=native_markets,
    )

    assert result["alias_match_count"] == 0
    assert result["alias_matches"] == []


def test_different_native_ids_do_not_match():
    ccxt_markets = {
        "AAA/USDT": {
            "id": "AAA-USDT",
            "spot": True,
            "active": True,
        },
    }

    native_markets = [
        {
            "symbol": "BBB/USDT",
            "raw": {
                "symbol": "BBB-USDT",
            },
        },
    ]

    result = ExchangeMarketAliasReconciler().reconcile(
        ccxt_markets=ccxt_markets,
        native_markets=native_markets,
    )

    assert result["alias_match_count"] == 0


def test_inactive_ccxt_market_is_not_alias_candidate():
    ccxt_markets = {
        "BSV/USDT": {
            "id": "BCHSV-USDT",
            "spot": True,
            "active": False,
        },
    }

    native_markets = [
        {
            "symbol": "BCHSV/USDT",
            "raw": {
                "symbol": "BCHSV-USDT",
            },
        },
    ]

    result = ExchangeMarketAliasReconciler().reconcile(
        ccxt_markets=ccxt_markets,
        native_markets=native_markets,
    )

    assert result["alias_match_count"] == 0


def test_derivative_market_is_not_alias_candidate():
    ccxt_markets = {
        "BSV/USDT:USDT": {
            "id": "BCHSV-USDT",
            "spot": False,
            "active": True,
        },
    }

    native_markets = [
        {
            "symbol": "BCHSV/USDT",
            "raw": {
                "symbol": "BCHSV-USDT",
            },
        },
    ]

    result = ExchangeMarketAliasReconciler().reconcile(
        ccxt_markets=ccxt_markets,
        native_markets=native_markets,
    )

    assert result["alias_match_count"] == 0


def test_reconciliation_is_research_only():
    result = ExchangeMarketAliasReconciler().reconcile(
        ccxt_markets={},
        native_markets=[],
    )

    assert result["reconciliation_complete"] is True
    assert result["live_order_submitted"] is False
