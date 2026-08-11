"""
ArbOS™
EX-197
Unified Multi-Exchange Public Paper Scanner

Runs the existing public live-paper verification pipeline across
every ordered exchange pair and every overlapping coin universe.

Preserves all returned internal and cross-exchange routes and
ranks them globally by net paper profitability.

Paper only.
No authentication.
No transfers.
No live orders.
"""


class UnifiedMultiExchangePublicPaperScanner:
    def __init__(
        self,
        verification_runner,
    ):
        if verification_runner is None:
            raise ValueError(
                "verification_runner is required"
            )

        self._verification_runner = (
            verification_runner
        )

    def scan(
        self,
        exchange_coin_assets,
        fee_rates,
        starting_usdt_value,
        max_slippage_percent,
    ):
        if exchange_coin_assets is None:
            raise ValueError(
                "exchange_coin_assets is required"
            )

        exchange_ids = sorted(
            exchange_coin_assets.keys()
        )

        if len(exchange_ids) < 2:
            raise ValueError(
                "at least two exchanges are required"
            )

        if starting_usdt_value <= 0:
            raise ValueError(
                "starting_usdt_value must be positive"
            )

        all_routes = []
        failures = []

        ordered_exchange_pair_count = 0
        coin_pair_scans = 0
        successful_coin_scans = 0
        failed_coin_scans = 0

        for source_exchange_id in exchange_ids:
            source_coins = {
                str(coin).strip().upper()
                for coin in (
                    exchange_coin_assets.get(
                        source_exchange_id,
                        set(),
                    )
                    or set()
                )
                if str(coin).strip()
            }

            for destination_exchange_id in exchange_ids:
                if (
                    source_exchange_id
                    == destination_exchange_id
                ):
                    continue

                ordered_exchange_pair_count += 1

                destination_coins = {
                    str(coin).strip().upper()
                    for coin in (
                        exchange_coin_assets.get(
                            destination_exchange_id,
                            set(),
                        )
                        or set()
                    )
                    if str(coin).strip()
                }

                common_coins = sorted(
                    source_coins
                    & destination_coins
                )

                for coin_asset in common_coins:
                    coin_pair_scans += 1

                    try:
                        source_fee_rate = float(
                            fee_rates[
                                source_exchange_id
                            ]
                        )

                        destination_fee_rate = float(
                            fee_rates[
                                destination_exchange_id
                            ]
                        )

                        result = (
                            self._verification_runner.run(
                                source_exchange_id=(
                                    source_exchange_id
                                ),
                                destination_exchange_id=(
                                    destination_exchange_id
                                ),
                                prepare_kwargs={
                                    "coin_asset": (
                                        coin_asset
                                    ),
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
                        )

                        successful_coin_scans += 1

                        for route in result.get(
                            "ranked_routes",
                            [],
                        ):
                            record = dict(route)

                            record.setdefault(
                                "coin_asset",
                                coin_asset,
                            )

                            record.setdefault(
                                "source_exchange",
                                source_exchange_id,
                            )

                            record.setdefault(
                                "destination_exchange",
                                destination_exchange_id,
                            )

                            record[
                                "paper_only"
                            ] = True

                            record[
                                "live_order_submitted"
                            ] = False

                            all_routes.append(
                                record
                            )

                    except Exception as exc:
                        failed_coin_scans += 1

                        failures.append({
                            "source_exchange_id": (
                                source_exchange_id
                            ),
                            "destination_exchange_id": (
                                destination_exchange_id
                            ),
                            "coin_asset": coin_asset,
                            "reason": (
                                "coin_scan_failed"
                            ),
                            "error": (
                                f"{type(exc).__name__}: "
                                f"{exc}"
                            ),
                        })

        ranked_routes = sorted(
            all_routes,
            key=lambda item: (
                float(
                    item.get(
                        "net_profit_percent",
                        float("-inf"),
                    )
                    or float("-inf")
                ),
                float(
                    item.get(
                        "net_profit",
                        float("-inf"),
                    )
                    or float("-inf")
                ),
            ),
            reverse=True,
        )

        best_route = (
            ranked_routes[0]
            if ranked_routes
            else None
        )

        executable_routes = [
            route
            for route in ranked_routes
            if route.get(
                "executable"
            ) is True
        ]

        profitable_routes = [
            route
            for route in executable_routes
            if float(
                route.get(
                    "net_profit_percent",
                    0.0,
                )
                or 0.0
            ) > 0.0
        ]

        return {
            "exchange_count": len(
                exchange_ids
            ),
            "ordered_exchange_pair_count": (
                ordered_exchange_pair_count
            ),
            "coin_pair_scans": (
                coin_pair_scans
            ),
            "successful_coin_scans": (
                successful_coin_scans
            ),
            "failed_coin_scans": (
                failed_coin_scans
            ),
            "route_count": len(
                ranked_routes
            ),
            "executable_route_count": len(
                executable_routes
            ),
            "profitable_route_count": len(
                profitable_routes
            ),
            "best_route": best_route,
            "ranked_routes": ranked_routes,
            "failures": failures,
            "paper_only": True,
            "live_order_submitted": False,
        }
