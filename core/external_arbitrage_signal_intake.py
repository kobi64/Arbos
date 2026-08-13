"""
ArbOS™
EX-211
External Arbitrage Signal Intake

Accepts normalized third-party arbitrage signals,
deduplicates them by signal_key, and preserves the rule
that external signals must be independently verified
before they can ever be considered executable.

Paper-safe infrastructure only.
No authentication.
No transfers.
No live orders.
"""

from copy import deepcopy


class ExternalArbitrageSignalIntake:
    def __init__(self):
        self._seen_signal_keys = set()

        self._received = 0
        self._accepted = 0
        self._duplicates = 0

    def submit(
        self,
        signal,
    ):
        self._received += 1

        if signal is None:
            raise ValueError(
                "signal is required"
            )

        signal_key = str(
            signal.get(
                "signal_key",
                "",
            )
            or ""
        ).strip()

        if not signal_key:
            raise ValueError(
                "signal_key is required"
            )

        if signal_key in self._seen_signal_keys:
            self._duplicates += 1

            return {
                "accepted": False,
                "reason": (
                    "duplicate_external_signal"
                ),
                "signal_key": signal_key,
                "paper_only": True,
                "live_order_submitted": False,
            }

        self._seen_signal_keys.add(
            signal_key
        )

        self._accepted += 1

        normalized = deepcopy(
            signal
        )

        normalized[
            "arbos_verified"
        ] = False

        normalized[
            "executable"
        ] = False

        normalized[
            "verification_required"
        ] = True

        return {
            **normalized,
            "accepted": True,
            "reason": None,
            "signal_key": signal_key,
            "arbos_verified": False,
            "executable": False,
            "verification_required": True,
            "paper_only": True,
            "live_order_submitted": False,
        }

    def statistics(
        self,
    ):
        return {
            "received": (
                self._received
            ),
            "accepted": (
                self._accepted
            ),
            "duplicates": (
                self._duplicates
            ),
        }
