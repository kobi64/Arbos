"""
ArbOS™
EX-146
Multi-Exchange Public Paper Verification
"""


class MultiExchangePublicPaperVerification:
    def __init__(
        self,
        multi_coin_scanner,
    ):
        self._multi_coin_scanner = multi_coin_scanner

    def scan(
        self,
        exchange_pairs,
        coin_assets,
        starting_usdt_value,
        source_fee_rate,
        destination_fee_rate,
        max_slippage_percent,
    ):
        if not exchange_pairs:
            raise ValueError(
                "exchange_pairs are required"
            )

        results = []
        failures = []

        for pair in exchange_pairs:
            source_exchange_id = pair[0]
            destination_exchange_id = pair[1]

            try:
                result = self._multi_coin_scanner.scan(
                    source_exchange_id=source_exchange_id,
                    destination_exchange_id=destination_exchange_id,
                    coin_assets=coin_assets,
                    starting_usdt_value=starting_usdt_value,
                    source_fee_rate=source_fee_rate,
                    destination_fee_rate=destination_fee_rate,
                    max_slippage_percent=max_slippage_percent,
                )

                best_result = result.get(
                    "best_result"
                )

                if best_result is None:
                    failures.append({
                        "source_exchange": (
                            source_exchange_id
                        ),
                        "destination_exchange": (
                            destination_exchange_id
                        ),
                        "reason": "no_best_result",
                    })
                    continue

                record = dict(best_result)

                record.setdefault(
                    "source_exchange",
                    source_exchange_id,
                )
                record.setdefault(
                    "destination_exchange",
                    destination_exchange_id,
                )

                results.append(record)

            except Exception as exc:
                failures.append({
                    "source_exchange": (
                        source_exchange_id
                    ),
                    "destination_exchange": (
                        destination_exchange_id
                    ),
                    "reason": (
                        "exchange_pair_scan_failed"
                    ),
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
            "pairs_scanned": len(exchange_pairs),
            "successful_pairs": len(results),
            "failed_pairs": len(failures),
            "best_result": best_result,
            "ranked_results": ranked_results,
            "failures": failures,
            "paper_only": True,
            "live_order_submitted": False,
        }
