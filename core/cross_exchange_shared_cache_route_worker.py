"""
ArbOS™
EX-353
Cross-Exchange Shared Cache Route Worker

Evaluates cross-exchange market opportunities using only
already-populated shared live-market cache snapshots.

No exchange API request is made during route evaluation.

This complements the EX-203 internal-route worker and preserves
the EX-200 -> EX-205 event-driven architecture:

market update
    -> shared cache
    -> dependency dispatcher
    -> coalesced work queue
    -> worker pool
    -> route evaluation

Paper/public-data infrastructure only.
No authentication.
No transfers.
No live orders.
"""

from copy import deepcopy


class CrossExchangeSharedCacheRouteWorker:
    def __init__(
        self,
        market_cache,
        route_registry,
    ):
        if market_cache is None:
            raise ValueError(
                "market_cache is required"
            )

        if route_registry is None:
            raise ValueError(
                "route_registry is required"
            )

        self._market_cache = market_cache
        self._route_registry = route_registry

    def _snapshot(
        self,
        exchange_id,
        symbol,
    ):
        result = (
            self._market_cache
            .get_with_freshness(
                exchange_id=str(
                    exchange_id
                ).strip().lower(),
                symbol=str(
                    symbol
                ).strip().upper(),
            )
        )

        snapshot = result.get(
            "snapshot"
        )

        if snapshot is None:
            return {
                "ready": False,
                "reason": (
                    "market_snapshot_unavailable"
                ),
                "exchange_id": exchange_id,
                "symbol": symbol,
            }

        freshness = result.get(
            "freshness"
        )

        if (
            freshness is not None
            and freshness.get("fresh")
            is False
        ):
            return {
                "ready": False,
                "reason": freshness.get(
                    "reason",
                    "market_data_stale",
                ),
                "exchange_id": exchange_id,
                "symbol": symbol,
            }

        return {
            "ready": True,
            "snapshot": deepcopy(
                snapshot
            ),
        }

    @staticmethod
    def _best_ask(snapshot):
        try:
            price = float(
                snapshot["asks"][0][0]
            )
        except (
            TypeError,
            ValueError,
            KeyError,
            IndexError,
        ):
            raise ValueError(
                "source ask unavailable"
            )

        if price <= 0:
            raise ValueError(
                "source ask must be positive"
            )

        return price

    @staticmethod
    def _best_bid(snapshot):
        try:
            price = float(
                snapshot["bids"][0][0]
            )
        except (
            TypeError,
            ValueError,
            KeyError,
            IndexError,
        ):
            raise ValueError(
                "destination bid unavailable"
            )

        if price <= 0:
            raise ValueError(
                "destination bid must be positive"
            )

        return price

    def evaluate(
        self,
        route_id,
    ):
        route = self._route_registry.get(
            route_id
        )

        if route is None:
            return {
                "processed": True,
                "route_id": route_id,
                "filled": False,
                "reason": (
                    "route_not_registered"
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        source_exchange = str(
            route.get(
                "source_exchange",
                "",
            )
        ).strip().lower()

        destination_exchange = str(
            route.get(
                "destination_exchange",
                "",
            )
        ).strip().lower()

        symbol = str(
            route.get(
                "symbol",
                "",
            )
        ).strip().upper()

        starting_value = float(
            route.get(
                "starting_value",
                0.0,
            )
        )

        source_fee_rate = float(
            route.get(
                "source_fee_rate",
                0.0,
            )
        )

        destination_fee_rate = float(
            route.get(
                "destination_fee_rate",
                0.0,
            )
        )

        if not source_exchange:
            raise ValueError(
                "source_exchange is required"
            )

        if not destination_exchange:
            raise ValueError(
                "destination_exchange is required"
            )

        if not symbol:
            raise ValueError(
                "symbol is required"
            )

        if starting_value <= 0:
            raise ValueError(
                "starting_value must be positive"
            )

        source = self._snapshot(
            source_exchange,
            symbol,
        )

        if source.get("ready") is not True:
            return {
                "processed": True,
                "route_id": route_id,
                "filled": False,
                **{
                    key: value
                    for key, value
                    in source.items()
                    if key != "ready"
                },
                "paper_only": True,
                "live_order_submitted": False,
            }

        destination = self._snapshot(
            destination_exchange,
            symbol,
        )

        if (
            destination.get("ready")
            is not True
        ):
            return {
                "processed": True,
                "route_id": route_id,
                "filled": False,
                **{
                    key: value
                    for key, value
                    in destination.items()
                    if key != "ready"
                },
                "paper_only": True,
                "live_order_submitted": False,
            }

        source_ask = self._best_ask(
            source["snapshot"]
        )

        destination_bid = self._best_bid(
            destination["snapshot"]
        )

        gross_coin_amount = (
            starting_value
            / source_ask
        )

        source_fee_amount = (
            gross_coin_amount
            * source_fee_rate
        )

        net_coin_amount = (
            gross_coin_amount
            - source_fee_amount
        )

        gross_final_value = (
            net_coin_amount
            * destination_bid
        )

        destination_fee_amount = (
            gross_final_value
            * destination_fee_rate
        )

        net_final_value = (
            gross_final_value
            - destination_fee_amount
        )

        net_profit = (
            net_final_value
            - starting_value
        )

        net_profit_percent = (
            net_profit
            / starting_value
            * 100.0
        )

        return {
            "processed": True,
            "route_id": route_id,
            "route_type": (
                "cross_exchange"
            ),
            "source_exchange": (
                source_exchange
            ),
            "destination_exchange": (
                destination_exchange
            ),
            "symbol": symbol,
            "filled": True,
            "starting_value": (
                starting_value
            ),
            "source_ask": source_ask,
            "destination_bid": (
                destination_bid
            ),
            "gross_coin_amount": (
                gross_coin_amount
            ),
            "net_coin_amount": (
                net_coin_amount
            ),
            "source_fee_amount": (
                source_fee_amount
            ),
            "destination_fee_amount": (
                destination_fee_amount
            ),
            "gross_final_value": (
                gross_final_value
            ),
            "net_final_value": (
                net_final_value
            ),
            "net_profit": net_profit,
            "net_profit_percent": (
                net_profit_percent
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
