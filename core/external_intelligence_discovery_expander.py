"""
ArbOS™
EX-211
External Intelligence Discovery Expander

Uses an external arbitrage lead to trigger ArbOS™'s
existing unified public-paper discovery across the
referenced exchanges and coin.

The external source acts only as a trigger.
All discovered routes remain ArbOS™ native discoveries.

Paper-safe infrastructure only.
No authentication.
No transfers.
No live orders.
"""


class ExternalIntelligenceDiscoveryExpander:
    def __init__(
        self,
        scanner,
        market_support=None,
    ):
        if scanner is None:
            raise ValueError(
                "scanner is required"
            )

        self._scanner = scanner
        self._market_support = (
            market_support
        )

    def expand(
        self,
        candidate,
        fee_rates,
        starting_usdt_value,
        max_slippage_percent,
    ):
        if candidate is None:
            raise ValueError(
                "candidate is required"
            )

        coin = str(
            candidate.get(
                "coin",
                "",
            )
            or ""
        ).strip().upper()

        if not coin:
            raise ValueError(
                "coin is required"
            )

        buy_exchange = str(
            candidate.get(
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
            candidate.get(
                "sell_exchange",
                "",
            )
            or ""
        ).strip().lower()

        if not sell_exchange:
            raise ValueError(
                "sell_exchange is required"
            )

        if buy_exchange == sell_exchange:
            raise ValueError(
                "distinct exchanges are required"
            )

        opportunity_key = str(
            candidate.get(
                "opportunity_key",
                "",
            )
            or ""
        ).strip()

        source = str(
            candidate.get(
                "source",
                "",
            )
            or ""
        ).strip().lower()

        source_signal_id = str(
            candidate.get(
                "source_signal_id",
                "",
            )
            or ""
        ).strip()

        result = self._scanner.scan(
            exchange_coin_assets={
                buy_exchange: {
                    coin,
                },
                sell_exchange: {
                    coin,
                },
            },
            fee_rates=fee_rates,
            starting_usdt_value=float(
                starting_usdt_value
            ),
            max_slippage_percent=float(
                max_slippage_percent
            ),
        )

        ranked_routes = []

        for route in (
            result.get(
                "ranked_routes"
            )
            or []
        ):
            record = dict(
                route
            )

            record[
                "trigger_source"
            ] = source

            record[
                "trigger_signal_id"
            ] = source_signal_id

            record[
                "trigger_opportunity_key"
            ] = opportunity_key

            record[
                "discovery_source"
            ] = "arbos_native"

            record[
                "paper_only"
            ] = True

            record[
                "live_order_submitted"
            ] = False

            ranked_routes.append(
                record
            )

        best_route = result.get(
            "best_route"
        )

        if isinstance(
            best_route,
            dict,
        ):
            best_route = dict(
                best_route
            )

            best_route[
                "trigger_source"
            ] = source

            best_route[
                "trigger_signal_id"
            ] = source_signal_id

            best_route[
                "trigger_opportunity_key"
            ] = opportunity_key

            best_route[
                "discovery_source"
            ] = "arbos_native"

            best_route[
                "paper_only"
            ] = True

            best_route[
                "live_order_submitted"
            ] = False

        return {
            **result,
            "discovery_complete": True,
            "best_route": best_route,
            "ranked_routes": ranked_routes,
            "trigger_source": source,
            "trigger_signal_id": (
                source_signal_id
            ),
            "trigger_opportunity_key": (
                opportunity_key
            ),
            "trigger_coin": coin,
            "paper_only": True,
            "live_order_submitted": False,
        }

    def expand_across_exchanges(
        self,
        candidate,
        exchange_ids,
        fee_rates,
        starting_usdt_value,
        max_slippage_percent,
    ):
        if candidate is None:
            raise ValueError(
                "candidate is required"
            )

        coin = str(
            candidate.get(
                "coin",
                "",
            )
            or ""
        ).strip().upper()

        if not coin:
            raise ValueError(
                "coin is required"
            )

        normalized_exchanges = []
        seen = set()

        for exchange_id in (
            exchange_ids
            or []
        ):
            value = str(
                exchange_id
                or ""
            ).strip().lower()

            if not value:
                continue

            if value in seen:
                continue

            seen.add(
                value
            )

            normalized_exchanges.append(
                value
            )

        if len(
            normalized_exchanges
        ) < 2:
            raise ValueError(
                "at least two exchanges are required"
            )

        skipped_exchanges = []

        if (
            self._market_support
            is not None
        ):
            supported_exchanges = []

            for exchange_id in (
                normalized_exchanges
            ):
                supported = (
                    self._market_support
                    .supports(
                        exchange_id=(
                            exchange_id
                        ),
                        coin=coin,
                    )
                )

                if supported:
                    supported_exchanges.append(
                        exchange_id
                    )
                else:
                    skipped_exchanges.append(
                        exchange_id
                    )

            normalized_exchanges = (
                supported_exchanges
            )

            if len(
                normalized_exchanges
            ) < 2:
                raise ValueError(
                    "at least two supported "
                    "exchanges are required"
                )

        normalized_fee_rates = {}

        for exchange_id in (
            normalized_exchanges
        ):
            if (
                exchange_id
                not in fee_rates
            ):
                raise ValueError(
                    f"fee rate is required for "
                    f"{exchange_id}"
                )

            normalized_fee_rates[
                exchange_id
            ] = float(
                fee_rates[
                    exchange_id
                ]
            )

        opportunity_key = str(
            candidate.get(
                "opportunity_key",
                "",
            )
            or ""
        ).strip()

        source = str(
            candidate.get(
                "source",
                "",
            )
            or ""
        ).strip().lower()

        source_signal_id = str(
            candidate.get(
                "source_signal_id",
                "",
            )
            or ""
        ).strip()

        exchange_coin_assets = {
            exchange_id: {
                coin,
            }
            for exchange_id
            in normalized_exchanges
        }

        result = self._scanner.scan(
            exchange_coin_assets=(
                exchange_coin_assets
            ),
            fee_rates=(
                normalized_fee_rates
            ),
            starting_usdt_value=float(
                starting_usdt_value
            ),
            max_slippage_percent=float(
                max_slippage_percent
            ),
        )

        ranked_routes = []

        for route in (
            result.get(
                "ranked_routes"
            )
            or []
        ):
            record = dict(
                route
            )

            record[
                "trigger_source"
            ] = source

            record[
                "trigger_signal_id"
            ] = source_signal_id

            record[
                "trigger_opportunity_key"
            ] = opportunity_key

            record[
                "discovery_source"
            ] = "arbos_native"

            record[
                "paper_only"
            ] = True

            record[
                "live_order_submitted"
            ] = False

            ranked_routes.append(
                record
            )

        best_route = result.get(
            "best_route"
        )

        if isinstance(
            best_route,
            dict,
        ):
            best_route = dict(
                best_route
            )

            best_route[
                "trigger_source"
            ] = source

            best_route[
                "trigger_signal_id"
            ] = source_signal_id

            best_route[
                "trigger_opportunity_key"
            ] = opportunity_key

            best_route[
                "discovery_source"
            ] = "arbos_native"

            best_route[
                "paper_only"
            ] = True

            best_route[
                "live_order_submitted"
            ] = False

        return {
            **result,
            "discovery_complete": True,
            "best_route": best_route,
            "ranked_routes": (
                ranked_routes
            ),
            "trigger_source": source,
            "trigger_signal_id": (
                source_signal_id
            ),
            "trigger_opportunity_key": (
                opportunity_key
            ),
            "trigger_coin": coin,
            "expanded_exchanges": list(
                normalized_exchanges
            ),
            "expanded_exchange_count": len(
                normalized_exchanges
            ),
            "skipped_exchanges": list(
                skipped_exchanges
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
