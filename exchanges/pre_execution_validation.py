"""
ArbOS™
EX-065
Pre-Execution Validation Pipeline
"""

import math


class PreExecutionValidationPipeline:
    VALID_SIDES = {"buy", "sell"}
    VALID_ORDER_TYPES = {"market", "limit"}

    def validate(self, order):
        if order is None:
            raise ValueError("order is required")

        reasons = []

        symbol = order.get("symbol")
        side = order.get("side")
        order_type = order.get("order_type")
        quantity = order.get("quantity")
        price = order.get("price")

        if symbol is None or not str(symbol).strip():
            reasons.append("MISSING_SYMBOL")
        else:
            symbol = str(symbol).strip().upper()

            if (
                symbol.count("/") != 1
                or any(not part for part in symbol.split("/"))
            ):
                reasons.append("INVALID_SYMBOL_FORMAT")

        if str(side).strip().lower() not in self.VALID_SIDES:
            reasons.append("INVALID_SIDE")

        normalized_order_type = str(order_type).strip().lower()

        if normalized_order_type not in self.VALID_ORDER_TYPES:
            reasons.append("INVALID_ORDER_TYPE")

        if isinstance(quantity, bool):
            valid_quantity = False
        else:
            try:
                normalized_quantity = float(quantity)
                valid_quantity = (
                    math.isfinite(normalized_quantity)
                    and normalized_quantity > 0
                )
            except (TypeError, ValueError, OverflowError):
                valid_quantity = False

        if not valid_quantity:
            reasons.append("INVALID_QUANTITY")

        if normalized_order_type == "limit":
            if isinstance(price, bool):
                valid_price = False
            else:
                try:
                    normalized_price = float(price)
                    valid_price = (
                        math.isfinite(normalized_price)
                        and normalized_price > 0
                    )
                except (TypeError, ValueError, OverflowError):
                    valid_price = False

            if not valid_price:
                reasons.append("LIMIT_PRICE_REQUIRED")

        return {
            "valid": len(reasons) == 0,
            "reasons": reasons,
        }
