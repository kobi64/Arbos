import asyncio

from core.dynamic_feed_capacity_orchestrator import (
    DynamicFeedCapacityOrchestrator,
)


class FakeManager:
    def __init__(
        self,
        health,
    ):
        self._health = health
        self.applied = []

    def health_snapshot(self):
        return dict(
            self._health
        )

    async def apply_symbol_rotation(
        self,
        active_symbols,
    ):
        self.applied.append(
            list(active_symbols)
        )

        return {
            "updated": True,
            "active_symbols": list(
                active_symbols
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }


class FakeCapacityController:
    def __init__(
        self,
        decision,
    ):
        self._decision = decision
        self.calls = []

    def decide(
        self,
        current_capacity,
        health_snapshot,
    ):
        self.calls.append({
            "current_capacity": (
                current_capacity
            ),
            "health_snapshot": dict(
                health_snapshot
            ),
        })

        return dict(
            self._decision
        )


class FakeApplicationPlanner:
    def __init__(
        self,
        plan,
    ):
        self._plan = plan
        self.calls = []

    def plan(
        self,
        active_symbols,
        overflow_symbols,
        target_capacity,
    ):
        self.calls.append({
            "active_symbols": list(
                active_symbols
            ),
            "overflow_symbols": list(
                overflow_symbols
            ),
            "target_capacity": (
                target_capacity
            ),
        })

        return dict(
            self._plan
        )


def test_orchestrator_applies_scale_down_plan():
    manager = FakeManager({
        "unhealthy_symbol_count": 2,
    })

    controller = FakeCapacityController({
        "action": "scale_down",
        "current_capacity": 4,
        "target_capacity": 3,
        "capacity_change": -1,
    })

    planner = FakeApplicationPlanner({
        "action": "scale_down",
        "changed": True,
        "active_symbols": [
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
        ],
        "overflow_symbols": [
            "XRP/USDT",
            "ADA/USDT",
        ],
        "demoted_symbols": [
            "XRP/USDT",
        ],
        "promoted_symbols": [],
    })

    orchestrator = DynamicFeedCapacityOrchestrator(
        manager=manager,
        capacity_controller=controller,
        application_planner=planner,
        active_symbols=[
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
            "XRP/USDT",
        ],
        overflow_symbols=[
            "ADA/USDT",
        ],
    )

    result = asyncio.run(
        orchestrator.rebalance()
    )

    assert manager.applied == [[
        "BTC/USDT",
        "ETH/USDT",
        "SOL/USDT",
    ]]

    assert result["action"] == "scale_down"

    assert result["active_symbols"] == [
        "BTC/USDT",
        "ETH/USDT",
        "SOL/USDT",
    ]

    assert result["overflow_symbols"] == [
        "XRP/USDT",
        "ADA/USDT",
    ]


def test_orchestrator_applies_scale_up_plan():
    manager = FakeManager({
        "unhealthy_symbol_count": 0,
    })

    controller = FakeCapacityController({
        "action": "scale_up",
        "current_capacity": 2,
        "target_capacity": 3,
        "capacity_change": 1,
    })

    planner = FakeApplicationPlanner({
        "action": "scale_up",
        "changed": True,
        "active_symbols": [
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
        ],
        "overflow_symbols": [
            "XRP/USDT",
        ],
        "demoted_symbols": [],
        "promoted_symbols": [
            "SOL/USDT",
        ],
    })

    orchestrator = DynamicFeedCapacityOrchestrator(
        manager=manager,
        capacity_controller=controller,
        application_planner=planner,
        active_symbols=[
            "BTC/USDT",
            "ETH/USDT",
        ],
        overflow_symbols=[
            "SOL/USDT",
            "XRP/USDT",
        ],
    )

    result = asyncio.run(
        orchestrator.rebalance()
    )

    assert manager.applied == [[
        "BTC/USDT",
        "ETH/USDT",
        "SOL/USDT",
    ]]

    assert result[
        "active_symbols"
    ] == [
        "BTC/USDT",
        "ETH/USDT",
        "SOL/USDT",
    ]


def test_hold_decision_does_not_touch_manager():
    manager = FakeManager({
        "unhealthy_symbol_count": 0,
    })

    controller = FakeCapacityController({
        "action": "hold",
        "current_capacity": 2,
        "target_capacity": 2,
        "capacity_change": 0,
    })

    planner = FakeApplicationPlanner({
        "action": "hold",
        "changed": False,
        "active_symbols": [
            "BTC/USDT",
            "ETH/USDT",
        ],
        "overflow_symbols": [
            "SOL/USDT",
        ],
        "demoted_symbols": [],
        "promoted_symbols": [],
    })

    orchestrator = DynamicFeedCapacityOrchestrator(
        manager=manager,
        capacity_controller=controller,
        application_planner=planner,
        active_symbols=[
            "BTC/USDT",
            "ETH/USDT",
        ],
        overflow_symbols=[
            "SOL/USDT",
        ],
    )

    result = asyncio.run(
        orchestrator.rebalance()
    )

    assert manager.applied == []

    assert result["action"] == "hold"


def test_orchestrator_updates_internal_symbol_state():
    manager = FakeManager({
        "unhealthy_symbol_count": 0,
    })

    controller = FakeCapacityController({
        "action": "scale_up",
        "current_capacity": 1,
        "target_capacity": 2,
        "capacity_change": 1,
    })

    planner = FakeApplicationPlanner({
        "action": "scale_up",
        "changed": True,
        "active_symbols": [
            "BTC/USDT",
            "ETH/USDT",
        ],
        "overflow_symbols": [
            "SOL/USDT",
        ],
        "demoted_symbols": [],
        "promoted_symbols": [
            "ETH/USDT",
        ],
    })

    orchestrator = DynamicFeedCapacityOrchestrator(
        manager=manager,
        capacity_controller=controller,
        application_planner=planner,
        active_symbols=[
            "BTC/USDT",
        ],
        overflow_symbols=[
            "ETH/USDT",
            "SOL/USDT",
        ],
    )

    asyncio.run(
        orchestrator.rebalance()
    )

    assert orchestrator.active_symbols == [
        "BTC/USDT",
        "ETH/USDT",
    ]

    assert orchestrator.overflow_symbols == [
        "SOL/USDT",
    ]


def test_orchestrator_is_paper_safe():
    manager = FakeManager({
        "unhealthy_symbol_count": 0,
    })

    controller = FakeCapacityController({
        "action": "hold",
        "current_capacity": 1,
        "target_capacity": 1,
        "capacity_change": 0,
    })

    planner = FakeApplicationPlanner({
        "action": "hold",
        "changed": False,
        "active_symbols": [
            "BTC/USDT",
        ],
        "overflow_symbols": [],
        "demoted_symbols": [],
        "promoted_symbols": [],
    })

    orchestrator = DynamicFeedCapacityOrchestrator(
        manager=manager,
        capacity_controller=controller,
        application_planner=planner,
        active_symbols=[
            "BTC/USDT",
        ],
        overflow_symbols=[],
    )

    result = asyncio.run(
        orchestrator.rebalance()
    )

    assert result["paper_only"] is True
    assert result[
        "live_order_submitted"
    ] is False
