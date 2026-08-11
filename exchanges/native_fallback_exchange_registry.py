"""
ArbOS™
EX-183
Native Fallback Exchange Registry

Stores exchange-specific builders for verified native
public market-data fallback providers.

The registry contains no exchange-specific transport logic.
It only maps normalized exchange IDs to provider builders.

Public market-data infrastructure only.
No authentication.
No transfers.
No live orders.
"""


class NativeFallbackExchangeRegistry:
    def __init__(self):
        self._builders = {}

    def register(
        self,
        exchange_id,
        builder,
    ):
        exchange_id = self._normalize_exchange_id(
            exchange_id
        )

        if builder is None:
            raise ValueError(
                "builder is required"
            )

        if not callable(builder):
            raise ValueError(
                "builder must be callable"
            )

        self._builders[
            exchange_id
        ] = builder

    def has(
        self,
        exchange_id,
    ):
        if exchange_id is None:
            return False

        exchange_id = str(
            exchange_id
        ).strip().lower()

        if not exchange_id:
            return False

        return exchange_id in self._builders

    def build(
        self,
        exchange_id,
        exchange,
    ):
        if exchange_id is None:
            return None

        exchange_id = str(
            exchange_id
        ).strip().lower()

        if not exchange_id:
            return None

        builder = self._builders.get(
            exchange_id
        )

        if builder is None:
            return None

        return builder(
            exchange
        )

    @staticmethod
    def _normalize_exchange_id(
        exchange_id,
    ):
        if exchange_id is None:
            raise ValueError(
                "exchange_id is required"
            )

        exchange_id = str(
            exchange_id
        ).strip().lower()

        if not exchange_id:
            raise ValueError(
                "exchange_id is required"
            )

        return exchange_id
