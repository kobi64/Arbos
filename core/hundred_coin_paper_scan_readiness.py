"""
ArbOS™

EX-352
100-Coin Paper Scan Readiness

Builds a globally bounded paper-scan universe from discovered
exchange coin universes and evaluates whether the requested
coin set is suitable for a controlled broad public paper test.

This component:
- does not authenticate
- does not transfer assets
- does not submit orders
- does not execute live trades
"""


class HundredCoinPaperScanReadiness:
    def evaluate(
        self,
        exchange_coin_assets,
        requested_coin_count=100,
        minimum_exchange_coverage=2,
    ):
        if not isinstance(
            exchange_coin_assets,
            dict,
        ):
            raise ValueError(
                "exchange_coin_assets are required"
            )

        if (
            not isinstance(
                requested_coin_count,
                int,
            )
            or isinstance(
                requested_coin_count,
                bool,
            )
            or requested_coin_count <= 0
        ):
            raise ValueError(
                "requested_coin_count must be positive"
            )

        if (
            not isinstance(
                minimum_exchange_coverage,
                int,
            )
            or isinstance(
                minimum_exchange_coverage,
                bool,
            )
            or minimum_exchange_coverage < 2
        ):
            raise ValueError(
                "minimum_exchange_coverage must be at least 2"
            )

        normalized = {}

        for exchange_id, coins in (
            exchange_coin_assets.items()
        ):
            exchange_id = str(
                exchange_id
                or ""
            ).strip().lower()

            if not exchange_id:
                continue

            normalized[exchange_id] = {
                str(coin)
                .strip()
                .upper()
                for coin in (
                    coins or []
                )
                if str(coin).strip()
            }

        if len(normalized) < 2:
            raise ValueError(
                "at least two exchanges are required"
            )

        coverage = {}

        for exchange_id, coins in (
            normalized.items()
        ):
            for coin in coins:
                coverage.setdefault(
                    coin,
                    [],
                ).append(
                    exchange_id
                )

        coverage_records = []

        for coin, exchanges in (
            coverage.items()
        ):
            exchange_ids = sorted(
                set(exchanges)
            )

            coverage_records.append({
                "coin_asset": coin,
                "exchange_ids": (
                    exchange_ids
                ),
                "exchange_count": len(
                    exchange_ids
                ),
            })

        coverage_records.sort(
            key=lambda item: (
                -item["exchange_count"],
                item["coin_asset"],
            )
        )

        eligible = [
            item
            for item in coverage_records
            if item["exchange_count"]
            >= minimum_exchange_coverage
        ]

        selected = eligible[
            :requested_coin_count
        ]

        selected_coin_assets = [
            item["coin_asset"]
            for item in selected
        ]

        selected_set = set(
            selected_coin_assets
        )

        exchange_selected_assets = {
            exchange_id: sorted(
                coins & selected_set
            )
            for exchange_id, coins in (
                normalized.items()
            )
        }

        rejected = [
            item
            for item in coverage_records
            if item["exchange_count"]
            < minimum_exchange_coverage
        ]

        selected_count = len(
            selected_coin_assets
        )

        ready = (
            selected_count
            == requested_coin_count
        )

        if ready:
            reason = None
        else:
            reason = (
                "insufficient_cross_exchange_coin_coverage"
            )

        return {
            "readiness": (
                "PASS"
                if ready
                else "FAIL"
            ),
            "ready": ready,
            "reason": reason,
            "requested_coin_count": (
                requested_coin_count
            ),
            "selected_coin_count": (
                selected_count
            ),
            "selected_coin_assets": (
                selected_coin_assets
            ),
            "eligible_coin_count": len(
                eligible
            ),
            "rejected_coin_count": len(
                rejected
            ),
            "coverage_records": (
                coverage_records
            ),
            "rejected_coins": rejected,
            "exchange_selected_assets": (
                exchange_selected_assets
            ),
            "exchange_count": len(
                normalized
            ),
            "minimum_exchange_coverage": (
                minimum_exchange_coverage
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
