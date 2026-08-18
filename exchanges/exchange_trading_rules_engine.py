"""
ArbOS™
EX-094
Exchange Trading Rules Engine
"""

import math


class ExchangeTradingRulesEngine:
    @staticmethod
    def _positive_number(value, name):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"{name} must be positive"
            )

        if not math.isfinite(value) or value <= 0:
            raise ValueError(
                f"{name} must be positive"
            )

        return value

    @staticmethod
    def _non_negative_number(value, name):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"{name} must be non-negative"
            )

        if not math.isfinite(value) or value < 0:
            raise ValueError(
                f"{name} must be non-negative"
            )

        return value

    def validate(self, quantity, price, rules):
        quantity = self._positive_number(
            quantity,
            "quantity",
        )
        price = self._positive_number(
            price,
            "price",
        )

        min_quantity = self._non_negative_number(
            rules["min_quantity"],
            "min_quantity",
        )
        max_quantity = self._positive_number(
            rules["max_quantity"],
            "max_quantity",
        )
        quantity_step = self._positive_number(
            rules["quantity_step"],
            "quantity_step",
        )
        price_tick = self._positive_number(
            rules["price_tick"],
            "price_tick",
        )
        min_notional = self._non_negative_number(
            rules["min_notional"],
            "min_notional",
        )

        if max_quantity < min_quantity:
            raise ValueError(
                "max_quantity must be greater than or "
                "equal to min_quantity"
            )

        if quantity < min_quantity:
            return {
                "valid": False,
                "reason": "below_min_quantity",
            }

        if quantity > max_quantity:
            return {
                "valid": False,
                "reason": "above_max_quantity",
            }

        if (
            abs(
                round(quantity / quantity_step)
                * quantity_step
                - quantity
            )
            > 1e-12
        ):
            return {
                "valid": False,
                "reason": "invalid_quantity_step",
            }

        if (
            abs(
                round(price / price_tick)
                * price_tick
                - price
            )
            > 1e-12
        ):
            return {
                "valid": False,
                "reason": "invalid_price_tick",
            }

        if quantity * price < min_notional:
            return {
                "valid": False,
                "reason": "below_min_notional",
            }

        return {
            "valid": True,
            "reason": None,
        }
