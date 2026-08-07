"""
ArbOS™
EX-144
Multi-Coin Public Paper Verification
"""


class MultiCoinPublicPaperVerification:
    def __init__(
        self,
        verification_runner,
    ):
        self._verification_runner = verification_runner

    def scan(
        self,
        source_exchange_id,
        destination_exchange_id,
        coin_assets,
        starting_usdt_value,
        source_fee_rate,
        destination_fee_rate,
        max_slippage_percent,
    ):
        if not coin_assets:
            raise ValueError(
                "coin_assets are required"
            )

        results = []
        failures = []

        for coin_asset in coin_assets:
            coin = str(
                coin_asset
            ).strip().upper()

            try:
                result = self._verification_runner.run(
                    source_exchange_id=source_exchange_id,
                    destination_exchange_id=destination_exchange_id,
                    prepare_kwargs={
                        "coin_asset": coin,
                        "starting_usdt_value": (
                            starting_usdt_value
                        ),
                        "source_fee_rate": (
                            source_fee_rate
                        ),
                        "destination_fee_rate": (
                            destination_fee_rate
                        ),
                        "max_slippage_percent": (
                            max_slippage_percent
                        ),
                    },
                )

                best_route = result.get(
                    "best_route"
                )

                if best_route is None:
                    failures.append({
                        "coin_asset": coin,
                        "reason": "no_best_route",
                    })
                    continue

                record = dict(best_route)

                if "coin_asset" not in record:
                    record["coin_asset"] = coin

                results.append(record)

            except Exception as exc:
                failures.append({
                    "coin_asset": coin,
                    "reason": "coin_scan_failed",
                    "error": (
                        f"{type(exc).__name__}: {exc}"
                    ),
                })

        ranked_results = sorted(
            results,
            key=lambda item: (
                item.get(
                    "net_profit_percent",
                    float("-inf"),
                ),
                item.get(
                    "net_profit",
                    float("-inf"),
                ),
            ),
            reverse=True,
        )

        best_result = (
            ranked_results[0]
            if ranked_results
            else None
        )

        return {
            "source_exchange_id": (
                source_exchange_id
            ),
            "destination_exchange_id": (
                destination_exchange_id
            ),
            "coins_scanned": len(
                coin_assets
            ),
            "successful_scans": len(
                results
            ),
            "failed_scans": len(
                failures
            ),
            "best_result": best_result,
            "ranked_results": ranked_results,
            "failures": failures,
            "paper_only": True,
            "live_order_submitted": False,
        }
