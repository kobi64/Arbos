"""
ArbOS™
EX-211
External Arbitrage Signal Correlator

Correlates third-party arbitrage signals that refer to the
same directional cross-exchange opportunity.

Correlation identity:
coin + buy_exchange + sell_exchange

Preserves:
- first source
- all contributing sources
- signal count
- source count

Paper-safe infrastructure only.
No authentication.
No transfers.
No live orders.
"""

from copy import deepcopy


class ExternalArbitrageSignalCorrelator:
    def __init__(self):
        self._opportunities = {}

    def correlate(
        self,
        signal,
    ):
        if signal is None:
            raise ValueError(
                "signal is required"
            )

        source = str(
            signal.get(
                "source",
                "",
            )
            or ""
        ).strip().lower()

        if not source:
            raise ValueError(
                "source is required"
            )

        source_signal_id = str(
            signal.get(
                "source_signal_id",
                "",
            )
            or ""
        ).strip()

        if not source_signal_id:
            raise ValueError(
                "source_signal_id is required"
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

        opportunity_key = (
            f"{coin}:"
            f"{buy_exchange}:"
            f"{sell_exchange}"
        )

        record = self._opportunities.get(
            opportunity_key
        )

        if record is None:
            record = {
                "opportunity_key": (
                    opportunity_key
                ),
                "coin": coin,
                "buy_exchange": (
                    buy_exchange
                ),
                "sell_exchange": (
                    sell_exchange
                ),
                "first_source": source,
                "sources": [],
                "signals": [],
                "source_count": 0,
                "signal_count": 0,
            }

            self._opportunities[
                opportunity_key
            ] = record

        if source not in record[
            "sources"
        ]:
            record["sources"].append(
                source
            )

        record["signals"].append({
            "source": source,
            "source_signal_id": (
                source_signal_id
            ),
            "reported_spread_percent": (
                signal.get(
                    "reported_spread_percent"
                )
            ),
            "reported_status": (
                signal.get(
                    "reported_status"
                )
            ),
        })

        record[
            "source_count"
        ] = len(
            record["sources"]
        )

        record[
            "signal_count"
        ] = len(
            record["signals"]
        )

        return {
            **deepcopy(record),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def get(
        self,
        opportunity_key,
    ):
        record = self._opportunities.get(
            opportunity_key
        )

        if record is None:
            return None

        return deepcopy(
            record
        )
