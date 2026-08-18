"""
ArbOS™
EX-089
Fee-Aware Live Route Valuation
"""

import math


class FeeAwareLiveRouteValuation:
    def __init__(self, market_data_provider):
        self._provider = market_data_provider

    @staticmethod
    def _positive_finite_number(value, error_message):
        try:
            number = float(value)
        except (TypeError, ValueError):
            raise ValueError(error_message)

        if not math.isfinite(number) or number <= 0:
            raise ValueError(error_message)

        return number

    @staticmethod
    def _fee_rate(value):
        try:
            fee_rate = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                "fee_rate must be non-negative"
            )

        if not math.isfinite(fee_rate) or fee_rate < 0:
            raise ValueError(
                "fee_rate must be non-negative"
            )

        if fee_rate > 1:
            raise ValueError(
                "fee_rate must be between 0 and 1"
            )

        return fee_rate

    def evaluate(self, route, starting_value):
        if route is None:
            raise ValueError("route is required")

        starting_value = self._positive_finite_number(
            starting_value,
            "starting_value must be positive",
        )

        amount = starting_value
        valued_legs = []

        for index, leg in enumerate(
            route.get("legs") or [],
            start=1,
        ):
            symbol = leg.get("symbol")
            side = str(
                leg.get("side", "")
            ).strip().lower()

            fee_rate = self._fee_rate(
                leg.get("fee_rate", 0.0)
            )

            if side == "buy":
                raw_price = self._provider.get_ask(
                    symbol
                )
            elif side == "sell":
                raw_price = self._provider.get_bid(
                    symbol
                )
            else:
                raise ValueError("invalid side")

            price = self._positive_finite_number(
                raw_price,
                "market price unavailable",
            )

            if side == "buy":
                gross_output = amount / price
            else:
                gross_output = amount * price

            fee_amount = gross_output * fee_rate
            net_output = gross_output - fee_amount

            if (
                not math.isfinite(gross_output)
                or not math.isfinite(fee_amount)
                or not math.isfinite(net_output)
                or gross_output < 0
                or fee_amount < 0
                or net_output < 0
            ):
                raise ValueError(
                    "valuation result invalid"
                )

            valued_legs.append(
                {
                    "leg_number": index,
                    "symbol": symbol,
                    "side": side,
                    "input_amount": amount,
                    "price": price,
                    "gross_output_amount": (
                        gross_output
                    ),
                    "fee_rate": fee_rate,
                    "fee_amount": fee_amount,
                    "net_output_amount": (
                        net_output
                    ),
                }
            )

            amount = net_output

        fee_multiplier = 1.0

        for leg in valued_legs:
            fee_multiplier *= (
                1.0 - leg["fee_rate"]
            )

        total_fee_rate_effect = (
            1.0 - fee_multiplier
        )

        if (
            not math.isfinite(amount)
            or amount < 0
            or not math.isfinite(
                total_fee_rate_effect
            )
            or total_fee_rate_effect < 0
            or total_fee_rate_effect > 1
        ):
            raise ValueError(
                "valuation result invalid"
            )

        return {
            "route_id": str(
                route.get("route_id", "")
            ).strip(),
            "starting_value": starting_value,
            "gross_final_value": amount,
            "total_fee_rate_effect": (
                total_fee_rate_effect
            ),
            "legs": valued_legs,
        }
