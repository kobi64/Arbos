"""
ArbOS™

EX-352
100-Coin Public Paper Scan Harness

Orchestrates a controlled broad public-market paper scan.

Authoritative sequence:

discovered exchange universes
    -> globally bounded coin universe
    -> cross-exchange coverage gate
    -> feed-capacity gate
    -> exact approved universe
    -> existing broad paper scanner

The harness does not authenticate, transfer assets,
or submit live orders.
"""

from core.hundred_coin_paper_scan_readiness import (
    HundredCoinPaperScanReadiness,
)
from core.hundred_coin_feed_capacity_readiness import (
    HundredCoinFeedCapacityReadiness,
)


class HundredCoinPublicPaperScanHarness:
    def __init__(
        self,
        scanner,
        capacity_profiles,
        universe_readiness=None,
        capacity_readiness=None,
    ):
        if scanner is None:
            raise ValueError(
                "scanner is required"
            )

        if capacity_profiles is None:
            raise ValueError(
                "capacity_profiles are required"
            )

        self._scanner = scanner
        self._capacity_profiles = (
            capacity_profiles
        )

        self._universe_readiness = (
            universe_readiness
            or HundredCoinPaperScanReadiness()
        )

        self._capacity_readiness = (
            capacity_readiness
            or HundredCoinFeedCapacityReadiness()
        )

    def run(
        self,
        exchange_coin_assets,
        fee_rates,
        starting_usdt_value,
        max_slippage_percent,
        requested_coin_count=100,
        minimum_exchange_coverage=2,
    ):
        if fee_rates is None:
            raise ValueError(
                "fee_rates are required"
            )

        if starting_usdt_value <= 0:
            raise ValueError(
                "starting_usdt_value must be positive"
            )

        universe = (
            self._universe_readiness.evaluate(
                exchange_coin_assets=(
                    exchange_coin_assets
                ),
                requested_coin_count=(
                    requested_coin_count
                ),
                minimum_exchange_coverage=(
                    minimum_exchange_coverage
                ),
            )
        )

        if not universe.get(
            "ready",
            False,
        ):
            return self._blocked(
                reason=(
                    universe.get("reason")
                    or "universe_readiness_failed"
                ),
                universe_readiness=universe,
                capacity_readiness=None,
            )

        approved_assets = {
            exchange_id: set(
                assets or []
            )
            for exchange_id, assets in (
                universe.get(
                    "exchange_selected_assets",
                    {},
                ).items()
            )
            if assets
        }

        if len(approved_assets) < 2:
            return self._blocked(
                reason=(
                    "insufficient_approved_exchanges"
                ),
                universe_readiness=universe,
                capacity_readiness=None,
            )

        for exchange_id in approved_assets:
            if exchange_id not in fee_rates:
                raise ValueError(
                    "fee rate is required "
                    f"for exchange: {exchange_id}"
                )

        capacity = (
            self._capacity_readiness.evaluate(
                exchange_selected_assets=(
                    approved_assets
                ),
                capacity_profiles=(
                    self._capacity_profiles
                ),
            )
        )

        if not capacity.get(
            "ready",
            False,
        ):
            return self._blocked(
                reason=(
                    capacity.get("reason")
                    or "feed_capacity_readiness_failed"
                ),
                universe_readiness=universe,
                capacity_readiness=capacity,
            )

        scanner_result = (
            self._scanner.scan(
                exchange_coin_assets=(
                    approved_assets
                ),
                fee_rates=fee_rates,
                starting_usdt_value=(
                    starting_usdt_value
                ),
                max_slippage_percent=(
                    max_slippage_percent
                ),
            )
        )

        if scanner_result.get(
            "live_order_submitted",
            False,
        ):
            return {
                "harness_ready": False,
                "scan_executed": True,
                "readiness": "FAIL",
                "reason": (
                    "live_order_submission_detected"
                ),
                "requested_coin_count": (
                    requested_coin_count
                ),
                "approved_coin_count": (
                    universe[
                        "selected_coin_count"
                    ]
                ),
                "approved_coin_assets": list(
                    universe[
                        "selected_coin_assets"
                    ]
                ),
                "exchange_coin_assets": (
                    approved_assets
                ),
                "universe_readiness": (
                    universe
                ),
                "capacity_readiness": (
                    capacity
                ),
                "scanner_result": (
                    scanner_result
                ),
                "paper_only": True,
                "live_order_submitted": True,
            }

        return {
            "harness_ready": True,
            "scan_executed": True,
            "readiness": "PASS",
            "reason": None,
            "requested_coin_count": (
                requested_coin_count
            ),
            "approved_coin_count": (
                universe[
                    "selected_coin_count"
                ]
            ),
            "approved_coin_assets": list(
                universe[
                    "selected_coin_assets"
                ]
            ),
            "exchange_coin_assets": (
                approved_assets
            ),
            "universe_readiness": universe,
            "capacity_readiness": capacity,
            "scanner_result": (
                scanner_result
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    @staticmethod
    def _blocked(
        reason,
        universe_readiness,
        capacity_readiness,
    ):
        return {
            "harness_ready": False,
            "scan_executed": False,
            "readiness": "FAIL",
            "reason": reason,
            "universe_readiness": (
                universe_readiness
            ),
            "capacity_readiness": (
                capacity_readiness
            ),
            "scanner_result": None,
            "paper_only": True,
            "live_order_submitted": False,
        }
