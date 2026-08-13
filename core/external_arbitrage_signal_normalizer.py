"""
ArbOS™
EX-211
External Arbitrage Signal Normalizer

Normalizes third-party arbitrage signals into a common
ArbOS™ external-opportunity contract.

External reports are treated as leads only.
They are never trusted as executable without ArbOS™
independent verification.

Paper-safe infrastructure only.
No authentication.
No transfers.
No live orders.
"""

from copy import deepcopy


class ExternalArbitrageSignalNormalizer:
    def normalize(
        self,
        source,
        signal,
    ):
        source = str(
            source
            or ""
        ).strip().lower()

        if not source:
            raise ValueError(
                "source is required"
            )

        if signal is None:
            raise ValueError(
                "signal is required"
            )

        signal_id = str(
            signal.get(
                "signal_id",
                "",
            )
            or ""
        ).strip()

        if not signal_id:
            raise ValueError(
                "signal_id is required"
            )

        coin = str(
            signal.get(
                "coin",
                "",
            )
            or ""
        ).strip().upper()

        if not coin:
            raise ValueError(
                "coin is required"
            )

        buy_exchange = str(
            signal.get(
                "buy_exchange",
                "",
            )
            or ""
        ).strip().lower()

        if not buy_exchange:
            raise ValueError(
                "buy_exchange is required"
            )

        sell_exchange = str(
            signal.get(
                "sell_exchange",
                "",
            )
            or ""
        ).strip().lower()

        if not sell_exchange:
            raise ValueError(
                "sell_exchange is required"
            )

        buy_price = signal.get(
            "buy_price"
        )

        sell_price = signal.get(
            "sell_price"
        )

        spread_percent = signal.get(
            "spread_percent"
        )

        status = str(
            signal.get(
                "status",
                "",
            )
            or ""
        ).strip().lower()

        observed_at = signal.get(
            "observed_at"
        )

        return {
            "source": source,
            "source_signal_id": signal_id,
            "signal_key": (
                f"{source}:{signal_id}"
            ),
            "coin": coin,
            "buy_exchange": (
                buy_exchange
            ),
            "sell_exchange": (
                sell_exchange
            ),
            "buy_price": (
                float(buy_price)
                if buy_price is not None
                else None
            ),
            "sell_price": (
                float(sell_price)
                if sell_price is not None
                else None
            ),
            "reported_spread_percent": (
                float(spread_percent)
                if spread_percent is not None
                else None
            ),
            "reported_status": status,
            "observed_at": (
                float(observed_at)
                if observed_at is not None
                else None
            ),
            "raw": deepcopy(
                signal
            ),

            # External sources are leads only.
            "externally_reported": True,
            "arbos_verified": False,
            "executable": False,
            "verification_required": True,

            "paper_only": True,
            "live_order_submitted": False,
        }
