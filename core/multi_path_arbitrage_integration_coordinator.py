"""
ArbOS™
EX-138
Multi-Path Arbitrage Integration Coordinator
"""


class MultiPathArbitrageIntegrationCoordinator:
    def __init__(
        self,
        cross_exchange_generator,
        cross_exchange_valuation,
        evaluator,
    ):
        self._cross_exchange_generator = cross_exchange_generator
        self._cross_exchange_valuation = cross_exchange_valuation
        self._evaluator = evaluator

    def evaluate(
        self,
        internal_routes,
        cross_exchange_generate_kwargs,
        starting_usdt_value,
        destination_fee_rate,
        max_slippage_percent,
    ):
        candidates = []

        for route in internal_routes:
            if route.get("filled") is not True:
                continue

            candidates.append({
                **route,
                "route_type": route.get(
                    "route_type",
                    "internal_triangle",
                ),
                "executable": True,
            })

        cross_exchange_candidates = (
            self._cross_exchange_generator.generate(
                **cross_exchange_generate_kwargs
            )
        )

        valued_cross_exchange = []

        for candidate in cross_exchange_candidates:
            valued = self._cross_exchange_valuation.evaluate(
                candidate=candidate,
                starting_usdt_value=starting_usdt_value,
                destination_fee_rate=destination_fee_rate,
                max_slippage_percent=max_slippage_percent,
            )

            valued_cross_exchange.append(
                valued
            )

        candidates.extend(
            valued_cross_exchange
        )

        result = self._evaluator.evaluate(
            candidates
        )

        return {
            "best_route": result["best_route"],
            "ranked_routes": result["ranked_routes"],
            "executable_count": result["executable_count"],
            "best_internal": result.get(
                "best_internal"
            ),
            "best_cross_exchange": result.get(
                "best_cross_exchange"
            ),
            "ranked_internal": result.get(
                "ranked_internal",
                [],
            ),
            "ranked_cross_exchange": result.get(
                "ranked_cross_exchange",
                [],
            ),
            "internal_candidate_count": sum(
                1
                for candidate in candidates
                if candidate.get("route_type")
                == "internal_triangle"
                and candidate.get("executable") is True
            ),
            "cross_exchange_candidate_count": len(
                valued_cross_exchange
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
