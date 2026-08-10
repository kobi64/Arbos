"""
ArbOS™
EX-176
Verified Exchange Market Registry

Builds a trusted exchange-market registry from:
- CCXT normalized markets
- native/raw exchange markets
- EX-176 completeness comparison

RAW_ONLY markets are not automatically trusted.
They must be explicitly tradable in native metadata.

This module performs market verification only.
It never submits exchange orders.
"""


class VerifiedExchangeMarketRegistry:
    def build(
        self,
        exchange_id,
        comparison_result,
        native_markets,
    ):
        if exchange_id is None or not str(exchange_id).strip():
            raise ValueError("exchange_id is required")

        if comparison_result is None:
            raise ValueError(
                "comparison_result is required"
            )

        if native_markets is None:
            raise ValueError(
                "native_markets is required"
            )

        exchange_id = str(
            exchange_id
        ).strip().lower()

        native_by_symbol = {
            str(item.get("symbol", "")).strip().upper(): item
            for item in native_markets
            if isinstance(item, dict)
            and str(item.get("symbol", "")).strip()
        }

        verified = []
        rejected = []

        for record in comparison_result.get(
            "markets",
            [],
        ):
            symbol = str(
                record.get("symbol", "")
            ).strip().upper()

            status = record.get("status")

            if not symbol:
                continue

            if status == "MATCHED":
                verified.append({
                    "exchange_id": exchange_id,
                    "symbol": symbol,
                    "source": "MATCHED",
                    "verified": True,
                    "reason": "matched_catalogues",
                })
                continue

            if status == "RAW_ONLY":
                native = native_by_symbol.get(
                    symbol
                )

                if native is None:
                    rejected.append({
                        "exchange_id": exchange_id,
                        "symbol": symbol,
                        "source": "RAW_ONLY",
                        "verified": False,
                        "reason": (
                            "native_metadata_required"
                        ),
                    })
                    continue

                native_status = str(
                    native.get(
                        "status",
                        "",
                    )
                ).strip().upper()

                order_types = [
                    str(value).strip().upper()
                    for value in (
                        native.get(
                            "order_types"
                        )
                        or []
                    )
                ]

                tradable = (
                    native_status == "TRADING"
                    and bool(order_types)
                )

                if tradable:
                    verified.append({
                        "exchange_id": exchange_id,
                        "symbol": symbol,
                        "source": "RAW_ONLY",
                        "verified": True,
                        "reason": (
                            "native_market_trading"
                        ),
                        "native_status": (
                            native_status
                        ),
                        "order_types": (
                            order_types
                        ),
                        "minimum_amount": (
                            native.get(
                                "minimum_amount"
                            )
                        ),
                        "minimum_value": (
                            native.get(
                                "minimum_value"
                            )
                        ),
                        "price_precision": (
                            native.get(
                                "price_precision"
                            )
                        ),
                        "amount_precision": (
                            native.get(
                                "amount_precision"
                            )
                        ),
                    })
                else:
                    rejected.append({
                        "exchange_id": exchange_id,
                        "symbol": symbol,
                        "source": "RAW_ONLY",
                        "verified": False,
                        "reason": (
                            "native_market_not_tradable"
                        ),
                        "native_status": (
                            native_status
                        ),
                        "order_types": (
                            order_types
                        ),
                    })

                continue

            rejected.append({
                "exchange_id": exchange_id,
                "symbol": symbol,
                "source": status,
                "verified": False,
                "reason": (
                    "ccxt_only_requires_review"
                    if status == "CCXT_ONLY"
                    else "unsupported_market_status"
                ),
            })

        return {
            "exchange_id": exchange_id,
            "verified_markets": verified,
            "rejected_markets": rejected,
            "verified_count": len(verified),
            "rejected_count": len(rejected),
            "registry_complete": True,
            "live_order_submitted": False,
        }
