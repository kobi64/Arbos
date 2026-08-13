import pytest

from core.coinmarketgap_arbitrage_adapter import (
    CoinMarketGapArbitrageAdapter,
)


def coti_row():
    return {
        "project_id": "coti",
        "internal_ticker": "COTI",
        "stable": "USDT",
        "buy_exchange": "kucoin",
        "sell_exchange": "digifinex",
        "qty": 358403.15,
        "ask_price": 0.00995,
        "bid_price": 0.01149,
        "avg_buy": 0.0101402111,
        "avg_sell": 0.0114241365,
        "cost": 3634.2836069,
        "revenue": 4094.4464971,
        "profit": 458.6703902,
        "profit_pct": 0.1262065485,
        "internal_coin_name": "COTI",
        "buy_url": "https://www.kucoin.com/trade/COTI-USDT",
        "sell_url": "https://www.digifinex.com/en-ww/trade/USDT/COTI",
        "exploitable": True,
    }


def test_adapts_coinmarketgap_row():
    adapter = CoinMarketGapArbitrageAdapter()

    result = adapter.adapt(
        coti_row(),
        observed_at=1000.0,
    )

    assert result["coin"] == "COTI"
    assert result["buy_exchange"] == "kucoin"
    assert result["sell_exchange"] == "digifinex"

    assert result["buy_price"] == 0.00995
    assert result["sell_price"] == 0.01149

    assert result["stable"] == "USDT"

    assert result["observed_at"] == 1000.0


def test_converts_fractional_profit_pct_to_percent():
    adapter = CoinMarketGapArbitrageAdapter()

    result = adapter.adapt(
        coti_row(),
        observed_at=1000.0,
    )

    assert result[
        "spread_percent"
    ] == pytest.approx(
        12.62065485
    )


def test_preserves_exploitable_status():
    adapter = CoinMarketGapArbitrageAdapter()

    result = adapter.adapt(
        coti_row(),
        observed_at=1000.0,
    )

    assert result[
        "status"
    ] == "exploitable"

    assert result[
        "externally_exploitable"
    ] is True


def test_false_exploitable_status_is_preserved():
    adapter = CoinMarketGapArbitrageAdapter()

    row = coti_row()
    row["exploitable"] = False

    result = adapter.adapt(
        row,
        observed_at=1000.0,
    )

    assert result[
        "status"
    ] == "not_exploitable"

    assert result[
        "externally_exploitable"
    ] is False


def test_generates_stable_source_signal_id():
    adapter = CoinMarketGapArbitrageAdapter()

    first = adapter.adapt(
        coti_row(),
        observed_at=1000.0,
    )

    second = adapter.adapt(
        coti_row(),
        observed_at=2000.0,
    )

    assert first[
        "signal_id"
    ] == second[
        "signal_id"
    ]


def test_changed_market_data_changes_signal_id():
    adapter = CoinMarketGapArbitrageAdapter()

    first = adapter.adapt(
        coti_row(),
        observed_at=1000.0,
    )

    row = coti_row()
    row["bid_price"] = 0.01160

    second = adapter.adapt(
        row,
        observed_at=1001.0,
    )

    assert first[
        "signal_id"
    ] != second[
        "signal_id"
    ]


def test_preserves_reported_trade_economics():
    adapter = CoinMarketGapArbitrageAdapter()

    result = adapter.adapt(
        coti_row(),
        observed_at=1000.0,
    )

    assert result[
        "reported_quantity"
    ] == pytest.approx(
        358403.15
    )

    assert result[
        "reported_profit"
    ] == pytest.approx(
        458.6703902
    )

    assert result[
        "reported_cost"
    ] == pytest.approx(
        3634.2836069
    )

    assert result[
        "reported_revenue"
    ] == pytest.approx(
        4094.4464971
    )


def test_preserves_raw_row_copy():
    adapter = CoinMarketGapArbitrageAdapter()

    row = coti_row()

    result = adapter.adapt(
        row,
        observed_at=1000.0,
    )

    row["internal_ticker"] = "CHANGED"

    assert result[
        "raw"
    ][
        "internal_ticker"
    ] == "COTI"


def test_required_fields_are_validated():
    adapter = CoinMarketGapArbitrageAdapter()

    row = coti_row()
    row["internal_ticker"] = ""

    with pytest.raises(
        ValueError,
        match="internal_ticker is required",
    ):
        adapter.adapt(
            row,
            observed_at=1000.0,
        )


def test_adapter_does_not_trust_exploitable_flag():
    adapter = CoinMarketGapArbitrageAdapter()

    result = adapter.adapt(
        coti_row(),
        observed_at=1000.0,
    )

    assert result[
        "externally_exploitable"
    ] is True

    assert result[
        "arbos_verified"
    ] is False

    assert result[
        "executable"
    ] is False

    assert result[
        "verification_required"
    ] is True


def test_adapter_is_paper_safe():
    adapter = CoinMarketGapArbitrageAdapter()

    result = adapter.adapt(
        coti_row(),
        observed_at=1000.0,
    )

    assert result["paper_only"] is True
    assert result[
        "live_order_submitted"
    ] is False
