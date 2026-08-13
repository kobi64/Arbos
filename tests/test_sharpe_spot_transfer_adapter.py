import pytest

from core.sharpe_spot_transfer_adapter import (
    SharpeSpotTransferAdapter,
)


def sharpe_row():
    return {
        "symbol": "COTI",
        "buyExchange": "KuCoin",
        "sellExchange": "Bitget",
        "network": "ERC20",
        "buyAsk": 0.0100,
        "sellBid": 0.0112,
        "netProfitUsd": 31.50,
        "netProfitPct": 10.5,
        "grossSpreadPct": 12.0,
        "withdrawalFee": 5.0,
        "buyWithdrawEnabled": True,
        "sellDepositEnabled": True,
        "depthUsd": 25000.0,
        "slippagePct": 0.25,
        "transferEtaSeconds": 180,
        "updatedAt": "2026-08-13T12:39:17.702Z",
    }


def test_adapts_sharpe_spot_transfer_row():
    adapter = SharpeSpotTransferAdapter()

    result = adapter.adapt(
        sharpe_row(),
        observed_at=1000.0,
    )

    assert result["coin"] == "COTI"
    assert result["buy_exchange"] == "kucoin"
    assert result["sell_exchange"] == "bitget"
    assert result["buy_price"] == 0.0100
    assert result["sell_price"] == 0.0112
    assert result["network"] == "ERC20"
    assert result["observed_at"] == 1000.0


def test_preserves_reported_profit_metrics():
    adapter = SharpeSpotTransferAdapter()

    result = adapter.adapt(
        sharpe_row(),
        observed_at=1000.0,
    )

    assert result[
        "reported_profit"
    ] == 31.50

    assert result[
        "spread_percent"
    ] == 10.5

    assert result[
        "reported_gross_spread_percent"
    ] == 12.0


def test_preserves_transfer_and_liquidity_metadata():
    adapter = SharpeSpotTransferAdapter()

    result = adapter.adapt(
        sharpe_row(),
        observed_at=1000.0,
    )

    assert result[
        "reported_withdrawal_fee"
    ] == 5.0

    assert result[
        "reported_depth_usd"
    ] == 25000.0

    assert result[
        "reported_slippage_percent"
    ] == 0.25

    assert result[
        "reported_transfer_eta_seconds"
    ] == 180


def test_preserves_deposit_withdraw_status():
    adapter = SharpeSpotTransferAdapter()

    result = adapter.adapt(
        sharpe_row(),
        observed_at=1000.0,
    )

    assert result[
        "reported_buy_withdraw_enabled"
    ] is True

    assert result[
        "reported_sell_deposit_enabled"
    ] is True


def test_generates_stable_signal_id():
    adapter = SharpeSpotTransferAdapter()

    first = adapter.adapt(
        sharpe_row(),
        observed_at=1000.0,
    )

    second = adapter.adapt(
        sharpe_row(),
        observed_at=2000.0,
    )

    assert first[
        "signal_id"
    ] == second[
        "signal_id"
    ]


def test_changed_market_data_changes_signal_id():
    adapter = SharpeSpotTransferAdapter()

    first = adapter.adapt(
        sharpe_row(),
        observed_at=1000.0,
    )

    row = sharpe_row()
    row["sellBid"] = 0.0115

    second = adapter.adapt(
        row,
        observed_at=1001.0,
    )

    assert first[
        "signal_id"
    ] != second[
        "signal_id"
    ]


def test_missing_optional_fields_are_tolerated():
    adapter = SharpeSpotTransferAdapter()

    row = {
        "symbol": "COTI",
        "buyExchange": "KuCoin",
        "sellExchange": "Bitget",
        "buyAsk": 0.0100,
        "sellBid": 0.0112,
        "netProfitPct": 10.5,
    }

    result = adapter.adapt(
        row,
        observed_at=1000.0,
    )

    assert result["coin"] == "COTI"
    assert result[
        "reported_depth_usd"
    ] is None

    assert result[
        "reported_transfer_eta_seconds"
    ] is None


def test_required_symbol_is_validated():
    adapter = SharpeSpotTransferAdapter()

    row = sharpe_row()
    row["symbol"] = ""

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        adapter.adapt(
            row,
            observed_at=1000.0,
        )


def test_required_exchanges_are_validated():
    adapter = SharpeSpotTransferAdapter()

    row = sharpe_row()
    row["buyExchange"] = ""

    with pytest.raises(
        ValueError,
        match="buyExchange is required",
    ):
        adapter.adapt(
            row,
            observed_at=1000.0,
        )


def test_adapter_never_marks_sharpe_signal_verified():
    adapter = SharpeSpotTransferAdapter()

    result = adapter.adapt(
        sharpe_row(),
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
    adapter = SharpeSpotTransferAdapter()

    result = adapter.adapt(
        sharpe_row(),
        observed_at=1000.0,
    )

    assert result["paper_only"] is True
    assert result[
        "live_order_submitted"
    ] is False
