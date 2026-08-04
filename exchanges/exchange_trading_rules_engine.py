"""
ArbOS™
EX-094
Exchange Trading Rules Engine
"""


class ExchangeTradingRulesEngine:
    def validate(self, quantity, price, rules):
        try:
            quantity = float(quantity)
        except (TypeError, ValueError):
            quantity = 0.0

        try:
            price = float(price)
        except (TypeError, ValueError):
            price = 0.0

        if quantity <= 0:
            raise ValueError("quantity must be positive")

        if price <= 0:
            raise ValueError("price must be positive")

        min_quantity = float(rules["min_quantity"])
        max_quantity = float(rules["max_quantity"])
        quantity_step = float(rules["quantity_step"])
        price_tick = float(rules["price_tick"])
        min_notional = float(rules["min_notional"])

        if quantity < min_quantity:
            return {"valid": False, "reason": "below_min_quantity"}

        if quantity > max_quantity:
            return {"valid": False, "reason": "above_max_quantity"}

        if abs(round(quantity / quantity_step) * quantity_step - quantity) > 1e-12:
            return {"valid": False, "reason": "invalid_quantity_step"}

        if abs(round(price / price_tick) * price_tick - price) > 1e-12:
            return {"valid": False, "reason": "invalid_price_tick"}

        if quantity * price < min_notional:
            return {"valid": False, "reason": "below_min_notional"}

        return {
            "valid": True,
            "reason": None,
        }
