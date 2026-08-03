"""
ArbOS™
EX-066
Dry-Run Execution Adapter
"""


class DryRunExecutionAdapter:
    def execute(self, order):
        if order is None:
            raise ValueError("order is required")

        quantity = order.get("quantity")
        reference_price = order.get("reference_price")
        side = str(order.get("side", "")).strip().lower()
        order_type = str(order.get("order_type", "")).strip().lower()

        try:
            quantity = float(quantity)
        except (TypeError, ValueError):
            quantity = 0.0

        if quantity <= 0:
            raise ValueError("quantity must be positive")

        try:
            reference_price = float(reference_price)
        except (TypeError, ValueError):
            raise ValueError("reference_price is required")

        if reference_price <= 0:
            raise ValueError("reference_price is required")

        status = "FILLED"
        filled_quantity = quantity
        average_price = reference_price

        if order_type == "limit":
            try:
                limit_price = float(order.get("limit_price"))
            except (TypeError, ValueError):
                limit_price = None

            if side == "buy":
                fillable = limit_price is not None and limit_price >= reference_price
            elif side == "sell":
                fillable = limit_price is not None and limit_price <= reference_price
            else:
                fillable = False

            if not fillable:
                status = "OPEN"
                filled_quantity = 0.0
                average_price = None

        notional = filled_quantity * average_price if average_price is not None else 0.0

        return {
            "status": status,
            "simulated": True,
            "filled_quantity": filled_quantity,
            "average_price": average_price,
            "notional": notional,
        }
