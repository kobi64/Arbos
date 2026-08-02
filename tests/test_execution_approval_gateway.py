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

    result = gateway.approve(
        proposal_id="TRADE-001"
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

    result = gateway.modify(
        proposal_id="TRADE-003",
        new_amount=500,
    )

    assert result["amount"] == 500


def test_approval_history_recorded():
    gateway = ExecutionApprovalGateway()

    gateway.approve(
        proposal_id="TRADE-004"
    )

    history = gateway.get_history()

    assert len(history) == 2


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
