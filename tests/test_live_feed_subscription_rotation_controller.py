import asyncio

from core.live_feed_subscription_rotation_controller import (
    LiveFeedSubscriptionRotationController,
)


class FakeManager:
    def __init__(self):
        self.applied = []

    def health_snapshot(self):
        return {
            "unhealthy_symbols": [
                "ETH/USDT",
            ],
        }

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


class FakePlanner:
    def __init__(self):
        self.calls = []

    def plan(
        self,
        active_symbols,
        unhealthy_symbols,
        overflow_symbols,
    ):
        self.calls.append({
            "active_symbols": list(
                active_symbols
            ),
            "unhealthy_symbols": list(
                unhealthy_symbols
            ),
            "overflow_symbols": list(
                overflow_symbols
            ),
        })

        return {
            "rotation_required": True,
            "removed_symbols": [
                "ETH/USDT",
            ],
            "promoted_symbols": [
                "XRP/USDT",
            ],
            "active_symbols": [
                "BTC/USDT",
                "SOL/USDT",
                "XRP/USDT",
            ],
            "overflow_symbols": [
                "ADA/USDT",
            ],
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_controller_plans_and_applies_rotation():
    manager = FakeManager()
    planner = FakePlanner()

    controller = (
        LiveFeedSubscriptionRotationController(
            manager=manager,
            planner=planner,
            active_symbols=[
                "BTC/USDT",
                "ETH/USDT",
                "SOL/USDT",
            ],
            overflow_symbols=[
                "XRP/USDT",
                "ADA/USDT",
            ],
        )
    )

    result = asyncio.run(
        controller.rebalance()
    )

    assert planner.calls[0][
        "unhealthy_symbols"
    ] == [
        "ETH/USDT",
    ]

    assert manager.applied == [[
        "BTC/USDT",
        "SOL/USDT",
        "XRP/USDT",
    ]]

    assert result[
        "removed_symbols"
    ] == [
        "ETH/USDT",
    ]

    assert result[
        "promoted_symbols"
    ] == [
        "XRP/USDT",
    ]

    assert result[
        "active_symbols"
    ] == [
        "BTC/USDT",
        "SOL/USDT",
        "XRP/USDT",
    ]

    assert result[
        "overflow_symbols"
    ] == [
        "ADA/USDT",
    ]


def test_no_rotation_does_not_restart_manager():
    class HealthyManager(FakeManager):
        def health_snapshot(self):
            return {
                "unhealthy_symbols": [],
            }

    class NoRotationPlanner(FakePlanner):
        def plan(
            self,
            active_symbols,
            unhealthy_symbols,
            overflow_symbols,
        ):
            return {
                "rotation_required": False,
                "removed_symbols": [],
                "promoted_symbols": [],
                "active_symbols": list(
                    active_symbols
                ),
                "overflow_symbols": list(
                    overflow_symbols
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

    manager = HealthyManager()

    controller = (
        LiveFeedSubscriptionRotationController(
            manager=manager,
            planner=NoRotationPlanner(),
            active_symbols=[
                "BTC/USDT",
            ],
            overflow_symbols=[
                "ETH/USDT",
            ],
        )
    )

    result = asyncio.run(
        controller.rebalance()
    )

    assert result[
        "rotation_required"
    ] is False

    assert manager.applied == []
