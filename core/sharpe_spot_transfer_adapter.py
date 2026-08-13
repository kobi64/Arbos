"""
ArbOS™
EX-212
Sharpe Spot Transfer Adapter

Adapts Sharpe CEX spot-transfer arbitrage rows into
the generic ArbOS™ external intelligence contract.

SPOT TRANSFER ONLY.

External source claims are never treated as proof of
executability. ArbOS™ must independently verify them.

Paper-safe infrastructure only.
No authentication.
No transfers.
No live orders.
"""

from copy import deepcopy
import hashlib
import json


class SharpeSpotTransferAdapter:
    def adapt(
        self,
        row,
        observed_at,
    ):
        if row is None:
            raise ValueError(
                "row is required"
            )

        symbol = str(
            row.get(
                "symbol",
                "",
            )
            or ""
        ).strip().upper()

        if not symbol:
            raise ValueError(
                "symbol is required"
            )

        buy_exchange = str(
            row.get(
                "buyExchange",
                "",
            )
            or ""
        ).strip().lower()

        if not buy_exchange:
            raise ValueError(
                "buyExchange is required"
            )

        sell_exchange = str(
            row.get(
                "sellExchange",
                "",
            )
            or ""
        ).strip().lower()

        if not sell_exchange:
            raise ValueError(
                "sellExchange is required"
            )

        buy_ask = row.get(
            "buyAsk"
        )

        sell_bid = row.get(
            "sellBid"
        )

        net_profit_pct = row.get(
            "netProfitPct"
        )

        fingerprint_payload = {
            "symbol": symbol,
            "buy_exchange": (
                buy_exchange
            ),
            "sell_exchange": (
                sell_exchange
            ),
            "network": row.get(
                "network"
            ),
            "buy_ask": buy_ask,
            "sell_bid": sell_bid,
            "net_profit_usd": row.get(
                "netProfitUsd"
            ),
            "net_profit_pct": (
                net_profit_pct
            ),
            "gross_spread_pct": row.get(
                "grossSpreadPct"
            ),
            "withdrawal_fee": row.get(
                "withdrawalFee"
            ),
            "buy_withdraw_enabled": row.get(
                "buyWithdrawEnabled"
            ),
            "sell_deposit_enabled": row.get(
                "sellDepositEnabled"
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
            f"sharpe-{digest}"
        )

        return {
            "signal_id": signal_id,
            "coin": symbol,
            "buy_exchange": (
                buy_exchange
            ),
            "sell_exchange": (
                sell_exchange
            ),
            "buy_price": (
                float(buy_ask)
                if buy_ask is not None
                else None
            ),
            "sell_price": (
                float(sell_bid)
                if sell_bid is not None
                else None
            ),
            "network": row.get(
                "network"
            ),
            "spread_percent": (
                float(net_profit_pct)
                if net_profit_pct is not None
                else None
            ),
            "status": (
                "reported_profitable"
                if (
                    net_profit_pct is not None
                    and float(net_profit_pct) > 0
                )
                else "reported"
            ),
            "observed_at": float(
                observed_at
            ),
            "reported_profit": (
                float(
                    row.get(
                        "netProfitUsd"
                    )
                )
                if row.get(
                    "netProfitUsd"
                )
                is not None
                else None
            ),
            "reported_gross_spread_percent": (
                float(
                    row.get(
                        "grossSpreadPct"
                    )
                )
                if row.get(
                    "grossSpreadPct"
                )
                is not None
                else None
            ),
            "reported_withdrawal_fee": (
                float(
                    row.get(
                        "withdrawalFee"
                    )
                )
                if row.get(
                    "withdrawalFee"
                )
                is not None
                else None
            ),
            "reported_depth_usd": (
                float(
                    row.get(
                        "depthUsd"
                    )
                )
                if row.get(
                    "depthUsd"
                )
                is not None
                else None
            ),
            "reported_slippage_percent": (
                float(
                    row.get(
                        "slippagePct"
                    )
                )
                if row.get(
                    "slippagePct"
                )
                is not None
                else None
            ),
            "reported_transfer_eta_seconds": (
                float(
                    row.get(
                        "transferEtaSeconds"
                    )
                )
                if row.get(
                    "transferEtaSeconds"
                )
                is not None
                else None
            ),
            "reported_buy_withdraw_enabled": (
                row.get(
                    "buyWithdrawEnabled"
                )
            ),
            "reported_sell_deposit_enabled": (
                row.get(
                    "sellDepositEnabled"
                )
            ),
            "source_updated_at": row.get(
                "updatedAt"
            ),
            "raw": deepcopy(
                row
            ),

            # External source is intelligence only.
            "arbos_verified": False,
            "executable": False,
            "verification_required": True,

            "paper_only": True,
            "live_order_submitted": False,
        }
