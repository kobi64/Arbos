import pytest

from core.finder_spot_intelligence_adapter import (
    FinderSpotIntelligenceAdapter,
)


def finder_row():
    return {
        "token": "LUNC",
        "quote": "USDT",
        "buyEx": "Poloniex",
        "sellEx": "Kucoin",
        "buyP": 0.00003936,
        "sellP": 0.00004928,
        "spread": 24.8763,
        "profit": 49.331,
        "cls": "veryhigh",
    }


def test_adapts_finder_row():
    adapter = FinderSpotIntelligenceAdapter()

    result = adapter.adapt(
        finder_row(),
        observed_at=1000.0,
    )

    assert result["coin"] == "LUNC"
    assert result["buy_exchange"] == "poloniex"
    assert result["sell_exchange"] == "kucoin"
    assert result["buy_price"] == pytest.approx(
        0.00003936
    )
    assert result["sell_price"] == pytest.approx(
        0.00004928
    )
    assert result["observed_at"] == 1000.0


def test_preserves_reported_spread_and_profit():
    adapter = FinderSpotIntelligenceAdapter()

    result = adapter.adapt(
        finder_row(),
        observed_at=1000.0,
    )

    assert result[
        "spread_percent"
    ] == pytest.approx(
        24.8763
    )

    assert result[
        "reported_profit"
    ] == pytest.approx(
        49.331
    )

    assert result[
        "reported_classification"
    ] == "veryhigh"


def test_quote_is_preserved():
    adapter = FinderSpotIntelligenceAdapter()

    result = adapter.adapt(
        finder_row(),
        observed_at=1000.0,
    )

    assert result["quote"] == "USDT"


def test_generates_stable_signal_id():
    adapter = FinderSpotIntelligenceAdapter()

    first = adapter.adapt(
        finder_row(),
        observed_at=1000.0,
    )

    second = adapter.adapt(
        finder_row(),
        observed_at=2000.0,
    )

    assert first[
        "signal_id"
    ] == second[
        "signal_id"
    ]


def test_changed_market_data_changes_signal_id():
    adapter = FinderSpotIntelligenceAdapter()

    first = adapter.adapt(
        finder_row(),
        observed_at=1000.0,
    )

    row = finder_row()
    row["sellP"] = 0.000051

    second = adapter.adapt(
        row,
        observed_at=1001.0,
    )

    assert first[
        "signal_id"
    ] != second[
        "signal_id"
    ]


def test_required_token_is_validated():
    adapter = FinderSpotIntelligenceAdapter()

    row = finder_row()
    row["token"] = ""

    with pytest.raises(
        ValueError,
        match="token is required",
    ):
        adapter.adapt(
            row,
            observed_at=1000.0,
        )


def test_required_buy_exchange_is_validated():
    adapter = FinderSpotIntelligenceAdapter()

    row = finder_row()
    row["buyEx"] = ""

    with pytest.raises(
        ValueError,
        match="buyEx is required",
    ):
        adapter.adapt(
            row,
            observed_at=1000.0,
        )


def test_required_sell_exchange_is_validated():
    adapter = FinderSpotIntelligenceAdapter()

    row = finder_row()
    row["sellEx"] = ""

    with pytest.raises(
        ValueError,
        match="sellEx is required",
    ):
        adapter.adapt(
            row,
            observed_at=1000.0,
        )


def test_adapter_never_marks_finder_signal_verified():
    adapter = FinderSpotIntelligenceAdapter()

    result = adapter.adapt(
        finder_row(),
        observed_at=1000.0,
    )

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
    adapter = FinderSpotIntelligenceAdapter()

    result = adapter.adapt(
        finder_row(),
        observed_at=1000.0,
    )

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False
