import pytest

from exchanges.manual_approval import ManualApproval


def test_trade_requires_manual_approval():
    result = ManualApproval.request(
        asset="BTC",
        trade_amount=1000.0,
        route="ExchangeA -> ExchangeB",
        expected_profit=25.0,
        net_profit=18.0,
    )

    assert result["approved"] is False
    assert result["status"] == "awaiting_approval"


def test_approval_accepts_valid_trade():
    result = ManualApproval.approve(
        approval_id="ARB-001"
    )

    assert result["approved"] is True
    assert result["status"] == "approved"


def test_rejection_blocks_trade():
    result = ManualApproval.reject(
        approval_id="ARB-002",
        reason="profit_margin_too_low",
    )

    assert result["approved"] is False
    assert result["status"] == "rejected"
    assert result["reason"] == "profit_margin_too_low"


def test_approval_request_contains_trade_summary():
    result = ManualApproval.request(
        asset="ETH",
        trade_amount=2000.0,
        route="ExchangeA -> ExchangeB",
        expected_profit=50.0,
        net_profit=40.0,
    )

    assert "trade_summary" in result
    assert result["trade_summary"]["asset"] == "ETH"


def test_rejects_invalid_trade_amount():
    with pytest.raises(ValueError):
        ManualApproval.request(
            asset="BTC",
            trade_amount=0,
            route="ExchangeA -> ExchangeB",
            expected_profit=25.0,
            net_profit=18.0,
        )


def test_rejects_missing_asset():
    with pytest.raises(ValueError):
        ManualApproval.request(
            asset="",
            trade_amount=1000.0,
            route="ExchangeA -> ExchangeB",
            expected_profit=25.0,
            net_profit=18.0,
        )


def test_rejects_negative_profit():
    with pytest.raises(ValueError):
        ManualApproval.request(
            asset="BTC",
            trade_amount=1000.0,
            route="ExchangeA -> ExchangeB",
            expected_profit=-5.0,
            net_profit=-10.0,
        )


def test_cannot_approve_unknown_request():
    result = ManualApproval.approve(
        approval_id="UNKNOWN"
    )

    assert result["approved"] is False
    assert result["status"] == "not_found"
