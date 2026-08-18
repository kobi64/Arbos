import pytest

from exchanges.execution_approval_gateway import ExecutionApprovalGateway


def test_create_approval_gateway():
    gateway = ExecutionApprovalGateway()

    assert gateway is not None


def test_create_trade_proposal():
    gateway = ExecutionApprovalGateway()

    proposal = gateway.create_proposal(
        route="USDT-TOKEN-BTC-USDT",
        amount=1000,
        expected_profit=18.50,
        fees=0.75,
        risk="low",
    )

    assert proposal["route"] == "USDT-TOKEN-BTC-USDT"


def test_calculate_net_profit():
    gateway = ExecutionApprovalGateway()

    proposal = gateway.create_proposal(
        route="ROUTE-001",
        amount=1000,
        expected_profit=20,
        fees=2,
        risk="low",
    )

    assert proposal["net_profit"] == 18


def test_approve_trade():
    gateway = ExecutionApprovalGateway()
    proposal = _pending_proposal(gateway)

    result = gateway.approve(
        proposal_id=proposal["proposal_id"]
    )

    assert result["approved"] is True


def test_reject_trade():
    gateway = ExecutionApprovalGateway()

    result = gateway.reject(
        proposal_id="TRADE-002",
        reason="Risk too high",
    )

    assert result["approved"] is False


def test_modify_trade():
    gateway = ExecutionApprovalGateway()
    proposal = _pending_proposal(gateway)

    result = gateway.modify(
        proposal_id=proposal["proposal_id"],
        new_amount=500,
    )

    assert result["amount"] == 500


def test_approval_history_recorded():
    gateway = ExecutionApprovalGateway()
    proposal = _pending_proposal(gateway)

    gateway.approve(
        proposal_id=proposal["proposal_id"]
    )

    history = gateway.get_history()

    assert len(history) == 3
    assert history[-1]["action"] == "trade_approved"


def test_proposal_contains_risk_information():
    gateway = ExecutionApprovalGateway()

    proposal = gateway.create_proposal(
        route="ROUTE-005",
        amount=1000,
        expected_profit=15,
        fees=1,
        risk="medium",
    )

    assert proposal["risk"] == "medium"


@pytest.mark.parametrize(
    "amount",
    [
        None,
        "bad",
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
        0.0,
        -1.0,
    ],
)
def test_create_proposal_requires_positive_finite_amount(
    amount,
):
    gateway = ExecutionApprovalGateway()

    with pytest.raises(
        ValueError,
        match="amount must be a positive finite number",
    ):
        gateway.create_proposal(
            route="ROUTE-001",
            amount=amount,
            expected_profit=10.0,
            fees=1.0,
            risk="low",
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("expected_profit", None),
        ("expected_profit", "bad"),
        ("expected_profit", float("nan")),
        ("expected_profit", float("inf")),
        ("expected_profit", float("-inf")),
        ("expected_profit", True),
        ("fees", None),
        ("fees", "bad"),
        ("fees", float("nan")),
        ("fees", float("inf")),
        ("fees", float("-inf")),
        ("fees", True),
        ("fees", -0.01),
    ],
)
def test_create_proposal_rejects_invalid_economics(
    field,
    value,
):
    gateway = ExecutionApprovalGateway()

    kwargs = {
        "route": "ROUTE-001",
        "amount": 100.0,
        "expected_profit": 10.0,
        "fees": 1.0,
        "risk": "low",
    }
    kwargs[field] = value

    requirement = (
        "finite non-negative number"
        if field == "fees"
        else "finite number"
    )

    with pytest.raises(
        ValueError,
        match=f"{field} must be a {requirement}",
    ):
        gateway.create_proposal(**kwargs)


@pytest.mark.parametrize(
    "expected_profit,fees",
    [
        (0.0, 0.0),
        (-1.0, 0.0),
        (1.0, 1.0),
        (1.0, 2.0),
    ],
)
def test_non_positive_net_profit_cannot_create_proposal(
    expected_profit,
    fees,
):
    gateway = ExecutionApprovalGateway()

    with pytest.raises(
        ValueError,
        match="net_profit must be positive",
    ):
        gateway.create_proposal(
            route="ROUTE-001",
            amount=100.0,
            expected_profit=expected_profit,
            fees=fees,
            risk="low",
        )


@pytest.mark.parametrize(
    "new_amount",
    [
        None,
        "bad",
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
        0.0,
        -1.0,
    ],
)
def test_modify_requires_positive_finite_amount(
    new_amount,
):
    gateway = ExecutionApprovalGateway()

    with pytest.raises(
        ValueError,
        match="new_amount must be a positive finite number",
    ):
        gateway.modify(
            proposal_id="TRADE-001",
            new_amount=new_amount,
        )


def test_numeric_string_proposal_values_remain_supported():
    gateway = ExecutionApprovalGateway()

    proposal = gateway.create_proposal(
        route="ROUTE-001",
        amount="100",
        expected_profit="10",
        fees="1.5",
        risk="low",
    )

    assert proposal["amount"] == 100.0
    assert proposal["expected_profit"] == 10.0
    assert proposal["fees"] == 1.5
    assert proposal["net_profit"] == 8.5


def test_numeric_string_modified_amount_remains_supported():
    gateway = ExecutionApprovalGateway()
    proposal = _pending_proposal(gateway)

    result = gateway.modify(
        proposal_id=proposal["proposal_id"],
        new_amount="250.5",
    )

    assert result["amount"] == 250.5


def _pending_proposal(gateway):
    return gateway.create_proposal(
        route="ROUTE-STATE-001",
        amount=100.0,
        expected_profit=10.0,
        fees=1.0,
        risk="low",
    )


def test_created_proposal_has_authoritative_proposal_id():
    gateway = ExecutionApprovalGateway()

    proposal = _pending_proposal(gateway)

    assert proposal["proposal_id"]
    assert proposal["status"] == "pending"


def test_created_proposal_ids_are_unique():
    gateway = ExecutionApprovalGateway()

    first = _pending_proposal(gateway)
    second = _pending_proposal(gateway)

    assert first["proposal_id"] != second["proposal_id"]


def test_unknown_proposal_cannot_be_approved():
    gateway = ExecutionApprovalGateway()

    result = gateway.approve("UNKNOWN")

    assert result["approved"] is False
    assert result["status"] == "not_found"
    assert result["proposal_id"] == "UNKNOWN"


def test_unknown_proposal_cannot_be_rejected():
    gateway = ExecutionApprovalGateway()

    result = gateway.reject(
        "UNKNOWN",
        reason="no longer wanted",
    )

    assert result["approved"] is False
    assert result["status"] == "not_found"
    assert result["proposal_id"] == "UNKNOWN"


def test_unknown_proposal_cannot_be_modified():
    gateway = ExecutionApprovalGateway()

    result = gateway.modify(
        "UNKNOWN",
        new_amount=250.0,
    )

    assert result["status"] == "not_found"
    assert result["proposal_id"] == "UNKNOWN"


def test_pending_proposal_can_be_approved_once():
    gateway = ExecutionApprovalGateway()
    proposal = _pending_proposal(gateway)

    result = gateway.approve(
        proposal["proposal_id"]
    )

    assert result["approved"] is True
    assert result["status"] == "approved"


def test_approved_proposal_cannot_be_approved_again():
    gateway = ExecutionApprovalGateway()
    proposal = _pending_proposal(gateway)
    proposal_id = proposal["proposal_id"]

    gateway.approve(proposal_id)
    result = gateway.approve(proposal_id)

    assert result["approved"] is False
    assert result["status"] == "not_pending"


def test_rejected_proposal_cannot_later_be_approved():
    gateway = ExecutionApprovalGateway()
    proposal = _pending_proposal(gateway)
    proposal_id = proposal["proposal_id"]

    gateway.reject(
        proposal_id,
        reason="risk changed",
    )
    result = gateway.approve(proposal_id)

    assert result["approved"] is False
    assert result["status"] == "not_pending"


def test_approved_proposal_cannot_later_be_rejected():
    gateway = ExecutionApprovalGateway()
    proposal = _pending_proposal(gateway)
    proposal_id = proposal["proposal_id"]

    gateway.approve(proposal_id)
    result = gateway.reject(
        proposal_id,
        reason="too late",
    )

    assert result["approved"] is False
    assert result["status"] == "not_pending"


def test_pending_proposal_can_be_modified():
    gateway = ExecutionApprovalGateway()
    proposal = _pending_proposal(gateway)

    result = gateway.modify(
        proposal["proposal_id"],
        new_amount=250.0,
    )

    assert result["status"] == "modified"
    assert result["amount"] == 250.0


def test_modification_updates_authoritative_pending_amount():
    gateway = ExecutionApprovalGateway()
    proposal = _pending_proposal(gateway)
    proposal_id = proposal["proposal_id"]

    gateway.modify(
        proposal_id,
        new_amount=250.0,
    )

    result = gateway.approve(proposal_id)

    assert result["approved"] is True
    assert result["proposal"]["amount"] == 250.0


def test_approved_proposal_cannot_be_modified():
    gateway = ExecutionApprovalGateway()
    proposal = _pending_proposal(gateway)
    proposal_id = proposal["proposal_id"]

    gateway.approve(proposal_id)

    result = gateway.modify(
        proposal_id,
        new_amount=250.0,
    )

    assert result["status"] == "not_pending"


def test_rejected_proposal_cannot_be_modified():
    gateway = ExecutionApprovalGateway()
    proposal = _pending_proposal(gateway)
    proposal_id = proposal["proposal_id"]

    gateway.reject(
        proposal_id,
        reason="risk changed",
    )

    result = gateway.modify(
        proposal_id,
        new_amount=250.0,
    )

    assert result["status"] == "not_pending"


def test_rejection_reason_is_preserved_in_terminal_state():
    gateway = ExecutionApprovalGateway()
    proposal = _pending_proposal(gateway)

    result = gateway.reject(
        proposal["proposal_id"],
        reason="liquidity deteriorated",
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "liquidity deteriorated"
