"""
ArbOS™

EX-352
100-Coin Feed Capacity Readiness

Maps a globally selected coin universe to per-exchange
USDT symbols and verifies that every required exchange
subscription set fits its configured feed-capacity profile.

Planning only.
No authentication.
No transfers.
No live orders.
"""

from core.live_feed_subscription_batch_planner import (
    LiveFeedSubscriptionBatchPlanner,
)


class HundredCoinFeedCapacityReadiness:
    def evaluate(
        self,
        exchange_selected_assets,
        capacity_profiles,
    ):
        if not isinstance(
            exchange_selected_assets,
            dict,
        ):
            raise ValueError(
                "exchange_selected_assets are required"
            )

        if capacity_profiles is None:
            raise ValueError(
                "capacity_profiles are required"
            )

        plans = {}
        failures = []
        total_required_symbols = 0
        total_selected_symbols = 0
        total_overflow_symbols = 0

        for exchange_id, assets in (
            exchange_selected_assets.items()
        ):
            exchange_id = str(
                exchange_id
                or ""
            ).strip().lower()

            if not exchange_id:
                continue

            symbols = []
            seen = set()

            for asset in assets or []:
                asset = str(
                    asset
                    or ""
                ).strip().upper()

                if not asset:
                    continue

                symbol = f"{asset}/USDT"

                if symbol in seen:
                    continue

                seen.add(symbol)
                symbols.append(symbol)

            if not symbols:
                continue

            total_required_symbols += len(
                symbols
            )

            profile = capacity_profiles.get(
                exchange_id
            )

            if profile is None:
                failures.append({
                    "exchange_id": exchange_id,
                    "reason": (
                        "capacity_profile_unavailable"
                    ),
                    "required_symbol_count": len(
                        symbols
                    ),
                })
                continue

            planner = (
                LiveFeedSubscriptionBatchPlanner
                .from_profile(profile)
            )

            plan = planner.plan(
                exchange_id=exchange_id,
                symbols=symbols,
            )

            plans[exchange_id] = plan

            selected_count = int(
                plan.get(
                    "selected_symbol_count",
                    0,
                )
                or 0
            )

            overflow_count = int(
                plan.get(
                    "overflow_symbol_count",
                    0,
                )
                or 0
            )

            total_selected_symbols += (
                selected_count
            )
            total_overflow_symbols += (
                overflow_count
            )

            if overflow_count:
                failures.append({
                    "exchange_id": exchange_id,
                    "reason": (
                        "feed_capacity_exceeded"
                    ),
                    "required_symbol_count": len(
                        symbols
                    ),
                    "selected_symbol_count": (
                        selected_count
                    ),
                    "overflow_symbol_count": (
                        overflow_count
                    ),
                    "overflow_symbols": list(
                        plan.get(
                            "overflow_symbols",
                            [],
                        )
                    ),
                })

        if not plans and not failures:
            raise ValueError(
                "no exchange symbols are available"
            )

        ready = (
            not failures
            and total_required_symbols
            == total_selected_symbols
            and total_overflow_symbols == 0
        )

        if ready:
            reason = None
        elif any(
            item["reason"]
            == "capacity_profile_unavailable"
            for item in failures
        ):
            reason = (
                "capacity_profile_unavailable"
            )
        else:
            reason = (
                "feed_capacity_exceeded"
            )

        return {
            "readiness": (
                "PASS"
                if ready
                else "FAIL"
            ),
            "ready": ready,
            "reason": reason,
            "exchange_plans": plans,
            "failure_count": len(
                failures
            ),
            "failures": failures,
            "planned_exchange_count": len(
                plans
            ),
            "total_required_symbol_count": (
                total_required_symbols
            ),
            "total_selected_symbol_count": (
                total_selected_symbols
            ),
            "total_overflow_symbol_count": (
                total_overflow_symbols
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
