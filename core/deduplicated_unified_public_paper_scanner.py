"""
ArbOS™
EX-199
Deduplicated Unified Public Paper Scanner

Runs internal arbitrage scans once per exchange/coin and
cross-exchange scans separately across ordered exchange pairs.

This avoids recalculating the same internal routes once for every
destination exchange while preserving full cross-exchange coverage.

Paper only.
No authentication.
No transfers.
No live orders.
"""

from core.multi_path_arbitrage_route_evaluator import (
    MultiPathArbitrageRouteEvaluator,
)


class DeduplicatedUnifiedPublicPaperScanner:
    def __init__(
        self,
        bootstrap,
        pipeline_factory,
        input_preparer_factory,
        evaluator=None,
    ):
        if bootstrap is None:
            raise ValueError(
                "bootstrap is required"
            )

        if pipeline_factory is None:
            raise ValueError(
                "pipeline_factory is required"
            )

        if input_preparer_factory is None:
            raise ValueError(
                "input_preparer_factory is required"
            )

        self._bootstrap = bootstrap
        self._pipeline_factory = (
            pipeline_factory
        )
        self._input_preparer_factory = (
            input_preparer_factory
        )
        self._evaluator = (
            evaluator
            if evaluator is not None
            else MultiPathArbitrageRouteEvaluator()
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

        exchanges = {
            exchange_id: (
                self._bootstrap.create(
                    exchange_id
                )
            )
            for exchange_id in exchange_ids
        }

        internal_routes = []
        cross_exchange_routes = []
        rejected_routes = []
        failures = []

        internal_coin_scans = 0
        successful_internal_scans = 0
        failed_internal_scans = 0

        cross_exchange_coin_scans = 0
        successful_cross_exchange_scans = 0
        failed_cross_exchange_scans = 0

        ordered_exchange_pair_count = 0

        #
        # PHASE A
        # Internal routes:
        # each exchange / coin exactly once.
        #
        for exchange_id in exchange_ids:
            coins = sorted({
                str(coin).strip().upper()
                for coin in (
                    exchange_coin_assets.get(
                        exchange_id,
                        set(),
                    )
                    or set()
                )
                if str(coin).strip()
            })

            exchange = exchanges[
                exchange_id
            ]

            scanner = (
                self._pipeline_factory
                .build_internal(
                    exchange=exchange
                )
            )

            markets = exchange.load_markets()

            fee_rate = float(
                fee_rates[
                    exchange_id
                ]
            )

            for coin_asset in coins:
                internal_coin_scans += 1

                try:
                    result = scanner.scan(
                        markets=markets,
                        quote_asset="USDT",
                        coin_asset=coin_asset,
                        starting_value=(
                            starting_usdt_value
                        ),
                        fee_rate=fee_rate,
                        max_slippage_percent=(
                            max_slippage_percent
                        ),
                    )

                    successful_internal_scans += 1

                    for route in result.get(
                        "ranked_routes",
                        [],
                    ):
                        record = dict(route)

                        record.setdefault(
                            "route_type",
                            "internal_triangle",
                        )

                        record.setdefault(
                            "coin_asset",
                            coin_asset,
                        )

                        record.setdefault(
                            "source_exchange",
                            exchange_id,
                        )

                        record[
                            "executable"
                        ] = True

                        record[
                            "paper_only"
                        ] = True

                        record[
                            "live_order_submitted"
                        ] = False

                        internal_routes.append(
                            record
                        )

                except Exception as exc:
                    failed_internal_scans += 1

                    failures.append({
                        "phase": "internal",
                        "exchange_id": (
                            exchange_id
                        ),
                        "coin_asset": coin_asset,
                        "reason": (
                            "internal_coin_scan_failed"
                        ),
                        "error": (
                            f"{type(exc).__name__}: "
                            f"{exc}"
                        ),
                    })

        #
        # PHASE B
        # Cross-exchange routes:
        # every ordered source -> destination pair
        # and every overlapping coin.
        #
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

            source_exchange = exchanges[
                source_exchange_id
            ]

            source_fee_rate = float(
                fee_rates[
                    source_exchange_id
                ]
            )

            for destination_exchange_id in exchange_ids:
                if (
                    source_exchange_id
                    == destination_exchange_id
                ):
                    continue

                ordered_exchange_pair_count += 1

                destination_exchange = exchanges[
                    destination_exchange_id
                ]

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

                destination_fee_rate = float(
                    fee_rates[
                        destination_exchange_id
                    ]
                )

                coordinator = (
                    self._pipeline_factory
                    .build_cross_exchange(
                        destination_exchange=(
                            destination_exchange
                        )
                    )
                )

                for coin_asset in common_coins:
                    cross_exchange_coin_scans += 1

                    try:
                        preparer = (
                            self._input_preparer_factory(
                                source_exchange=(
                                    source_exchange
                                ),
                                destination_exchange=(
                                    destination_exchange
                                ),
                            )
                        )

                        prepared = preparer.prepare(
                            source_exchange_id=(
                                source_exchange_id
                            ),
                            destination_exchange_id=(
                                destination_exchange_id
                            ),
                            coin_asset=coin_asset,
                            starting_usdt_value=(
                                starting_usdt_value
                            ),
                            source_fee_rate=(
                                source_fee_rate
                            ),
                            max_slippage_percent=(
                                max_slippage_percent
                            ),
                        )

                        if prepared.get(
                            "prepare_complete",
                            True,
                        ) is not True:
                            failed_cross_exchange_scans += 1

                            failures.append({
                                "phase": (
                                    "cross_exchange"
                                ),
                                "source_exchange_id": (
                                    source_exchange_id
                                ),
                                "destination_exchange_id": (
                                    destination_exchange_id
                                ),
                                "coin_asset": coin_asset,
                                "reason": prepared.get(
                                    "reason",
                                    "preparation_failed",
                                ),
                            })

                            continue

                        result = coordinator.evaluate(
                            internal_routes=[],
                            cross_exchange_generate_kwargs={
                                "source_exchange": (
                                    source_exchange_id
                                ),
                                "destination_exchange": (
                                    destination_exchange_id
                                ),
                                "coin_asset": (
                                    prepared[
                                        "coin_asset"
                                    ]
                                ),
                                "coin_amount": (
                                    prepared[
                                        "coin_amount"
                                    ]
                                ),
                                "source_networks": (
                                    prepared[
                                        "source_networks"
                                    ]
                                ),
                                "destination_networks": (
                                    prepared[
                                        "destination_networks"
                                    ]
                                ),
                                "source_network_metadata": (
                                    prepared.get(
                                        "source_network_metadata",
                                        {},
                                    )
                                ),
                                "destination_network_metadata": (
                                    prepared.get(
                                        "destination_network_metadata",
                                        {},
                                    )
                                ),
                                "bridge_quotes": (
                                    prepared[
                                        "bridge_quotes"
                                    ]
                                ),
                                "source_network_identity_records": (
                                    prepared.get(
                                        "source_network_identity_records",
                                        {},
                                    )
                                ),
                                "destination_network_identity_records": (
                                    prepared.get(
                                        "destination_network_identity_records",
                                        {},
                                    )
                                ),
                            },
                            starting_usdt_value=(
                                starting_usdt_value
                            ),
                            destination_fee_rate=(
                                destination_fee_rate
                            ),
                            max_slippage_percent=(
                                max_slippage_percent
                            ),
                        )

                        successful_cross_exchange_scans += 1

                        for route in result.get(
                            "ranked_cross_exchange",
                            result.get(
                                "ranked_routes",
                                [],
                            ),
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

                            cross_exchange_routes.append(
                                record
                            )

                        for route in result.get(
                            "rejected_cross_exchange",
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

                            rejected_routes.append(
                                record
                            )

                    except Exception as exc:
                        failed_cross_exchange_scans += 1

                        failures.append({
                            "phase": (
                                "cross_exchange"
                            ),
                            "source_exchange_id": (
                                source_exchange_id
                            ),
                            "destination_exchange_id": (
                                destination_exchange_id
                            ),
                            "coin_asset": coin_asset,
                            "reason": (
                                "cross_exchange_coin_scan_failed"
                            ),
                            "error": (
                                f"{type(exc).__name__}: "
                                f"{exc}"
                            ),
                        })

        candidates = (
            internal_routes
            + cross_exchange_routes
            + rejected_routes
        )

        ranked = self._evaluator.evaluate(
            candidates
        )

        return {
            **ranked,
            "exchange_count": len(
                exchange_ids
            ),
            "ordered_exchange_pair_count": (
                ordered_exchange_pair_count
            ),
            "internal_coin_scans": (
                internal_coin_scans
            ),
            "successful_internal_scans": (
                successful_internal_scans
            ),
            "failed_internal_scans": (
                failed_internal_scans
            ),
            "cross_exchange_coin_scans": (
                cross_exchange_coin_scans
            ),
            "successful_cross_exchange_scans": (
                successful_cross_exchange_scans
            ),
            "failed_cross_exchange_scans": (
                failed_cross_exchange_scans
            ),
            "internal_route_count": len(
                internal_routes
            ),
            "cross_exchange_route_count": len(
                cross_exchange_routes
            ),
            "route_count": len(
                ranked.get(
                    "ranked_routes",
                    [],
                )
            ),
            "failure_count": len(
                failures
            ),
            "failures": failures,
            "paper_only": True,
            "live_order_submitted": False,
        }
