"""
ArbOS™
EX-118
Dynamic Exchange Fee Resolver
"""

import math


class DynamicExchangeFeeResolver:
    def __init__(self, fee_config):
        self._fee_config = {}

        for exchange_id, fees in fee_config.items():
            if (
                "maker" not in fees
                or "taker" not in fees
                or fees["maker"] is None
                or fees["taker"] is None
            ):
                raise ValueError(
                    "maker and taker fee rates are required"
                )

            try:
                maker = float(fees["maker"])
                taker = float(fees["taker"])
            except (TypeError, ValueError):
                raise ValueError(
                    "fee rates must be finite non-negative numbers"
                )

            if (
                not math.isfinite(maker)
                or not math.isfinite(taker)
                or maker < 0
                or taker < 0
            ):
                raise ValueError(
                    "fee rates must be finite non-negative numbers"
                )

            self._fee_config[str(exchange_id).strip().lower()] = {
                "maker": maker,
                "taker": taker,
            }

    def resolve(self, exchange_id, fee_type="taker"):
        exchange_id = str(exchange_id).strip().lower()
        fee_type = str(fee_type).strip().lower()

        if fee_type not in {"maker", "taker"}:
            raise ValueError("invalid fee_type")

        fees = self._fee_config.get(exchange_id)

        if fees is None:
            raise ValueError("exchange fee configuration not found")

        return {
            "exchange_id": exchange_id,
            "fee_type": fee_type,
            "fee_rate": fees[fee_type],
        }
