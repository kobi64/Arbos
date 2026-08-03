"""
ArbOS™
EX-056
Exchange Execution Safety Gate
"""


class ExchangeExecutionSafetyGate:
    RULES = [
        ("exchange_healthy", "EXCHANGE_UNHEALTHY"),
        ("market_data_fresh", "STALE_MARKET_DATA"),
        ("sufficient_balance", "INSUFFICIENT_BALANCE"),
        ("valid_order_size", "INVALID_ORDER_SIZE"),
        ("network_supported", "NETWORK_UNSUPPORTED"),
        ("reconciliation_clear", "RECONCILIATION_REQUIRED"),
    ]

    def evaluate(self, context):
        if context is None:
            raise ValueError("context is required")

        reasons = []

        for field, failure_reason in self.RULES:
            if field not in context:
                reasons.append(f"MISSING_{field.upper()}")
                continue

            if context[field] is not True:
                reasons.append(failure_reason)

        return {
            "allowed": len(reasons) == 0,
            "reasons": reasons,
        }
