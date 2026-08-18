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


@pytest.mark.parametrize(
    "trade_amount",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_request_rejects_invalid_numeric_trade_amount(
    trade_amount,
):
    with pytest.raises(
        ValueError,
        match="invalid trade amount",
    ):
        ManualApproval.request(
            asset="BTC",
            trade_amount=trade_amount,
            route="ExchangeA -> ExchangeB",
            expected_profit=25.0,
            net_profit=18.0,
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("expected_profit", None),
        ("expected_profit", "not-a-number"),
        ("expected_profit", float("nan")),
        ("expected_profit", float("inf")),
        ("expected_profit", float("-inf")),
        ("net_profit", None),
        ("net_profit", "not-a-number"),
        ("net_profit", float("nan")),
        ("net_profit", float("inf")),
        ("net_profit", float("-inf")),
    ],
)
def test_request_rejects_invalid_numeric_profit(
    field,
    value,
):
    kwargs = {
        "asset": "BTC",
        "trade_amount": 1000.0,
        "route": "ExchangeA -> ExchangeB",
        "expected_profit": 25.0,
        "net_profit": 18.0,
    }
    kwargs[field] = value

    with pytest.raises(
        ValueError,
        match="profit must be a finite non-negative number",
    ):
        ManualApproval.request(**kwargs)


def test_request_rejects_boolean_trade_amount():
    with pytest.raises(
        ValueError,
        match="invalid trade amount",
    ):
        ManualApproval.request(
            asset="BTC",
            trade_amount=True,
            route="ExchangeA -> ExchangeB",
            expected_profit=25.0,
            net_profit=18.0,
        )


@pytest.mark.parametrize(
    "field",
    [
        "expected_profit",
        "net_profit",
    ],
)
def test_request_rejects_boolean_profit(field):
    kwargs = {
        "asset": "BTC",
        "trade_amount": 1000.0,
        "route": "ExchangeA -> ExchangeB",
        "expected_profit": 25.0,
        "net_profit": 18.0,
    }
    kwargs[field] = True

    with pytest.raises(
        ValueError,
        match="profit must be a finite non-negative number",
    ):
        ManualApproval.request(**kwargs)
