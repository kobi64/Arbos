"""
ArbOS™
EX-204
Route Dependency Registry

Central source of truth for registered arbitrage routes
and the market dependencies that affect them.

Stores complete route definitions and derives:

- route -> dependent markets
- market -> affected routes

Reads are copy-safe.

Paper-safe infrastructure only.
No authentication.
No transfers.
No live orders.
"""

from copy import deepcopy


class RouteDependencyRegistry:
    def __init__(self):
        self._routes = {}
        self._route_markets = {}
        self._market_routes = {}

    def register(
        self,
        route,
    ):
        if route is None:
            raise ValueError(
                "route is required"
            )

        route_id = str(
            route.get(
                "route_id",
                "",
            )
            or ""
        ).strip()

        if not route_id:
            raise ValueError(
                "route_id is required"
            )

        if route_id in self._routes:
            raise ValueError(
                "route_id already registered"
            )

        exchange_id = str(
            route.get(
                "exchange_id",
                "",
            )
            or ""
        ).strip().lower()

        if not exchange_id:
            raise ValueError(
                "exchange_id is required"
            )

        legs = (
            route.get(
                "legs"
            )
            or []
        )

        if not legs:
            raise ValueError(
                "route legs are required"
            )

        normalized_route = deepcopy(
            route
        )

        normalized_route[
            "route_id"
        ] = route_id

        normalized_route[
            "exchange_id"
        ] = exchange_id

        normalized_legs = []
        market_dependencies = set()

        for leg in legs:
            normalized_leg = deepcopy(
                leg
            )

            symbol = str(
                normalized_leg.get(
                    "symbol",
                    "",
                )
                or ""
            ).strip().upper()

            if not symbol:
                raise ValueError(
                    "leg symbol is required"
                )

            normalized_leg[
                "symbol"
            ] = symbol

            leg_exchange_id = str(
                normalized_leg.get(
                    "exchange_id",
                    exchange_id,
                )
                or exchange_id
            ).strip().lower()

            if not leg_exchange_id:
                raise ValueError(
                    "leg exchange_id is required"
                )

            normalized_leg[
                "exchange_id"
            ] = leg_exchange_id

            normalized_legs.append(
                normalized_leg
            )

            market_dependencies.add(
                (
                    leg_exchange_id,
                    symbol,
                )
            )

        normalized_route[
            "legs"
        ] = normalized_legs

        self._routes[
            route_id
        ] = normalized_route

        self._route_markets[
            route_id
        ] = market_dependencies

        for market_key in market_dependencies:
            self._market_routes.setdefault(
                market_key,
                set(),
            ).add(
                route_id
            )

        return {
            "registered": True,
            "route_id": route_id,
            "market_count": len(
                market_dependencies
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def get(
        self,
        route_id,
    ):
        route_id = str(
            route_id
            or ""
        ).strip()

        route = self._routes.get(
            route_id
        )

        if route is None:
            return None

        return deepcopy(
            route
        )

    def markets_for_route(
        self,
        route_id,
    ):
        route_id = str(
            route_id
            or ""
        ).strip()

        return sorted(
            self._route_markets.get(
                route_id,
                set(),
            )
        )

    def routes_for_market(
        self,
        exchange_id,
        symbol,
    ):
        key = self._normalize_market_key(
            exchange_id=exchange_id,
            symbol=symbol,
        )

        return sorted(
            self._market_routes.get(
                key,
                set(),
            )
        )

    def route_count(
        self,
    ):
        return len(
            self._routes
        )

    @staticmethod
    def _normalize_market_key(
        exchange_id,
        symbol,
    ):
        exchange_id = str(
            exchange_id
            or ""
        ).strip().lower()

        symbol = str(
            symbol
            or ""
        ).strip().upper()

        if not exchange_id:
            raise ValueError(
                "exchange_id is required"
            )

        if not symbol:
            raise ValueError(
                "symbol is required"
            )

        return (
            exchange_id,
            symbol,
        )
