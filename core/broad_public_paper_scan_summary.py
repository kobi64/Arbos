"""
ArbOS™
EX-256
Broad Public Paper Scan Opportunity Summary

Builds a concise operator-facing summary from broad public
paper scan results.

Presentation/reporting only.
No authentication.
No transfers.
No live orders.
"""

from core.broad_public_paper_scan_failure_diagnostics import (
    BroadPublicPaperScanFailureDiagnostics,
)


class BroadPublicPaperScanSummary:
    def build(
        self,
        scan_result,
        top_limit=10,
    ):
        if scan_result is None:
            raise ValueError(
                "scan_result is required"
            )

        if (
            not isinstance(top_limit, int)
            or isinstance(top_limit, bool)
            or top_limit <= 0
        ):
            raise ValueError(
                "top_limit must be positive"
            )

        ranked_routes = list(
            scan_result.get(
                "ranked_routes",
                [],
            )
            or []
        )

        rejected_routes = list(
            scan_result.get(
                "rejected_routes",
                [],
            )
            or []
        )

        executable_routes = [
            dict(route)
            for route in ranked_routes
            if route.get(
                "executable",
                False,
            )
            is True
        ]

        profitable_routes = [
            route
            for route in executable_routes
            if self._profit_percent(route) > 0
        ]

        unprofitable_routes = [
            route
            for route in executable_routes
            if self._profit_percent(route) <= 0
        ]

        profitable_routes.sort(
            key=self._profit_percent,
            reverse=True,
        )

        unprofitable_routes.sort(
            key=self._profit_percent,
            reverse=True,
        )

        rejection_reasons = {}

        for route in rejected_routes:
            reason = (
                route.get("reason")
                or "unknown"
            )

            rejection_reasons[reason] = (
                rejection_reasons.get(
                    reason,
                    0,
                )
                + 1
            )

        best_route = (
            profitable_routes[0]
            if profitable_routes
            else (
                executable_routes[0]
                if executable_routes
                else None
            )
        )

        diagnostics = (
            BroadPublicPaperScanFailureDiagnostics()
            .build(
                scan_result
            )
        )

        return {
            "diagnostics": diagnostics,
            "route_count": scan_result.get(
                "route_count",
                len(ranked_routes),
            ),
            "executable_route_count": len(
                executable_routes
            ),
            "profitable_route_count": len(
                profitable_routes
            ),
            "unprofitable_route_count": len(
                unprofitable_routes
            ),
            "rejected_route_count": (
                scan_result.get(
                    "rejected_count",
                    len(rejected_routes),
                )
            ),
            "internal_route_count": (
                scan_result.get(
                    "internal_route_count",
                    0,
                )
            ),
            "cross_exchange_route_count": (
                scan_result.get(
                    "cross_exchange_route_count",
                    0,
                )
            ),
            "successful_internal_scans": (
                scan_result.get(
                    "successful_internal_scans",
                    0,
                )
            ),
            "successful_cross_exchange_scans": (
                scan_result.get(
                    "successful_cross_exchange_scans",
                    0,
                )
            ),
            "unique_coin_count": (
                scan_result.get(
                    "unique_coin_count",
                    0,
                )
            ),
            "unique_coin_assets": list(
                scan_result.get(
                    "unique_coin_assets",
                    [],
                )
                or []
            ),
            "best_route": (
                self._compact_route(
                    best_route
                )
                if best_route is not None
                else None
            ),
            "top_profitable_routes": [
                self._compact_route(route)
                for route in (
                    profitable_routes[
                        :top_limit
                    ]
                )
            ],
            "top_unprofitable_routes": [
                self._compact_route(route)
                for route in (
                    unprofitable_routes[
                        :top_limit
                    ]
                )
            ],
            "rejection_reasons": dict(
                sorted(
                    rejection_reasons.items()
                )
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    @staticmethod
    def _profit_percent(route):
        value = route.get(
            "net_profit_percent",
            float("-inf"),
        )

        try:
            return float(value)
        except (
            TypeError,
            ValueError,
        ):
            return float("-inf")

    @staticmethod
    def _compact_route(route):
        return {
            "route_id": route.get(
                "route_id"
            ),
            "route_type": route.get(
                "route_type"
            ),
            "coin_asset": route.get(
                "coin_asset"
            ),
            "source_exchange": route.get(
                "source_exchange"
            ),
            "destination_exchange": (
                route.get(
                    "destination_exchange"
                )
            ),
            "net_profit": route.get(
                "net_profit"
            ),
            "net_profit_percent": (
                route.get(
                    "net_profit_percent"
                )
            ),
            "max_leg_slippage_percent": (
                route.get(
                    "max_leg_slippage_percent"
                )
            ),
            "executable": route.get(
                "executable",
                False,
            ),
        }
