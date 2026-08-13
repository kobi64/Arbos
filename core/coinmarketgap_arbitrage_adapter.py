"""
ArbOS™
EX-211
CoinMarketGap Arbitrage Adapter

Adapts CoinMarketGap opportunity rows into the generic
ArbOS™ external arbitrage signal contract.

CoinMarketGap's exploitable flag is preserved as an external
claim only. ArbOS™ must independently verify executability.

Paper-safe infrastructure only.
No authentication.
No transfers.
No live orders.
"""

from copy import deepcopy
import hashlib
import json


class CoinMarketGapArbitrageAdapter:
    def adapt(
        self,
        row,
        observed_at,
    ):
        if row is None:
            raise ValueError(
                "row is required"
            )

        ticker = str(
            row.get(
                "internal_ticker",
                "",
            )
            or ""
        ).strip().upper()

        if not ticker:
            raise ValueError(
                "internal_ticker is required"
            )

        buy_exchange = str(
            row.get(
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
            row.get(
                "sell_exchange",
                "",
            )
            or ""
        ).strip().lower()

        if not sell_exchange:
            raise ValueError(
                "sell_exchange is required"
            )

        stable = str(
            row.get(
                "stable",
                "",
            )
            or ""
        ).strip().upper()

        ask_price = row.get(
            "ask_price"
        )

        bid_price = row.get(
            "bid_price"
        )

        profit_pct = row.get(
            "profit_pct"
        )

        exploitable = (
            row.get(
                "exploitable"
            )
            is True
        )

        fingerprint_payload = {
            "project_id": row.get(
                "project_id"
            ),
            "ticker": ticker,
            "stable": stable,
            "buy_exchange": (
                buy_exchange
            ),
            "sell_exchange": (
                sell_exchange
            ),
            "ask_price": (
                ask_price
            ),
            "bid_price": (
                bid_price
            ),
            "avg_buy": row.get(
                "avg_buy"
            ),
            "avg_sell": row.get(
                "avg_sell"
            ),
            "qty": row.get(
                "qty"
            ),
            "profit": row.get(
                "profit"
            ),
            "profit_pct": (
                profit_pct
            ),
            "exploitable": (
                exploitable
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
            f"cmg-{digest}"
        )

        return {
            "signal_id": signal_id,
            "coin": ticker,
            "buy_exchange": (
                buy_exchange
            ),
            "sell_exchange": (
                sell_exchange
            ),
            "buy_price": (
                float(ask_price)
                if ask_price is not None
                else None
            ),
            "sell_price": (
                float(bid_price)
                if bid_price is not None
                else None
            ),
            "stable": stable,
            "spread_percent": (
                float(profit_pct) * 100.0
                if profit_pct is not None
                else None
            ),
            "status": (
                "exploitable"
                if exploitable
                else "not_exploitable"
            ),
            "externally_exploitable": (
                exploitable
            ),
            "observed_at": (
                float(observed_at)
            ),
            "reported_quantity": (
                float(
                    row.get(
                        "qty"
                    )
                )
                if row.get(
                    "qty"
                )
                is not None
                else None
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
            "reported_cost": (
                float(
                    row.get(
                        "cost"
                    )
                )
                if row.get(
                    "cost"
                )
                is not None
                else None
            ),
            "reported_revenue": (
                float(
                    row.get(
                        "revenue"
                    )
                )
                if row.get(
                    "revenue"
                )
                is not None
                else None
            ),
            "avg_buy": (
                float(
                    row.get(
                        "avg_buy"
                    )
                )
                if row.get(
                    "avg_buy"
                )
                is not None
                else None
            ),
            "avg_sell": (
                float(
                    row.get(
                        "avg_sell"
                    )
                )
                if row.get(
                    "avg_sell"
                )
                is not None
                else None
            ),
            "buy_url": row.get(
                "buy_url"
            ),
            "sell_url": row.get(
                "sell_url"
            ),
            "raw": deepcopy(
                row
            ),

            # External source is a lead only.
            "arbos_verified": False,
            "executable": False,
            "verification_required": True,

            "paper_only": True,
            "live_order_submitted": False,
        }
