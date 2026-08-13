"""
ArbOS™
EX-213
Finder Spot Intelligence Adapter

Adapts Finder public landing-ticker rows into the generic
ArbOS™ external intelligence contract.

Initial scope:
- plain USDT spot-style cross-exchange intelligence only
- external source is a lead only
- ArbOS™ independently verifies executability

No authentication.
No transfers.
No live orders.
"""

from copy import deepcopy
import hashlib
import json


class FinderSpotIntelligenceAdapter:
    def adapt(
        self,
        row,
        observed_at,
    ):
        if row is None:
            raise ValueError(
                "row is required"
            )

        token = str(
            row.get(
                "token",
                "",
            )
            or ""
        ).strip().upper()

        if not token:
            raise ValueError(
                "token is required"
            )

        buy_exchange = str(
            row.get(
                "buyEx",
                "",
            )
            or ""
        ).strip().lower()

        if not buy_exchange:
            raise ValueError(
                "buyEx is required"
            )

        sell_exchange = str(
            row.get(
                "sellEx",
                "",
            )
            or ""
        ).strip().lower()

        if not sell_exchange:
            raise ValueError(
                "sellEx is required"
            )

        quote = str(
            row.get(
                "quote",
                "",
            )
            or ""
        ).strip().upper()

        if quote != "USDT":
            raise ValueError(
                "quote must be USDT"
            )

        buy_price = row.get(
            "buyP"
        )

        sell_price = row.get(
            "sellP"
        )

        spread = row.get(
            "spread"
        )

        fingerprint_payload = {
            "token": token,
            "quote": quote,
            "buy_exchange": (
                buy_exchange
            ),
            "sell_exchange": (
                sell_exchange
            ),
            "buy_price": buy_price,
            "sell_price": sell_price,
            "spread": spread,
            "profit": row.get(
                "profit"
            ),
            "classification": row.get(
                "cls"
            ),
        }

        fingerprint_json = json.dumps(
            fingerprint_payload,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
        )

        digest = hashlib.sha256(
            fingerprint_json.encode(
                "utf-8"
            )
        ).hexdigest()[:20]

        signal_id = (
            f"finder-{digest}"
        )

        return {
            "signal_id": signal_id,
            "coin": token,
            "quote": quote,
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
            "spread_percent": (
                float(spread)
                if spread is not None
                else None
            ),
            "status": (
                "reported_high_spread"
                if (
                    spread is not None
                    and float(spread) > 0
                )
                else "reported"
            ),
            "reported_profit": (
                float(
                    row.get(
                        "profit"
                    )
                )
                if row.get(
                    "profit"
                )
                is not None
                else None
            ),
            "reported_classification": str(
                row.get(
                    "cls",
                    "",
                )
                or ""
            ).strip().lower(),
            "observed_at": float(
                observed_at
            ),
            "raw": deepcopy(
                row
            ),

            # Finder is external intelligence only.
            "arbos_verified": False,
            "executable": False,
            "verification_required": True,

            "paper_only": True,
            "live_order_submitted": False,
        }
