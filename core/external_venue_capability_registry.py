"""
ArbOS™
EX-216
External Venue Capability Registry

Classifies exchange support for external intelligence routes.

Coverage levels:
- full
- partial
- intelligence_only
- unsupported

A route is fully verifiable only when both exchanges
have full verification capability.

No live orders.
"""


class ExternalVenueCapabilityRegistry:
    def __init__(
        self,
        capabilities,
        alias_registry=None,
    ):
        self._alias_registry = (
            alias_registry
        )

        self._capabilities = {
            str(exchange).strip().lower(): dict(
                values
            )
            for exchange, values in (
                capabilities
                or {}
            ).items()
        }

    def classify_exchange(
        self,
        exchange,
    ):
        exchange = str(
            exchange
            or ""
        ).strip().lower()

        if not exchange:
            raise ValueError(
                "exchange is required"
            )

        if (
            self._alias_registry
            is not None
        ):
            exchange = (
                self._alias_registry
                .canonicalize(
                    exchange
                )
            )

        capability = self._capabilities.get(
            exchange
        )

        if capability is None:
            return {
                "exchange": exchange,
                "known_exchange": False,
                "coverage": "unsupported",
                "full_verification_available": False,
                "capabilities": {},
                "paper_only": True,
                "live_order_submitted": False,
            }

        market_data = bool(
            capability.get(
                "market_data",
                False,
            )
        )

        order_books = bool(
            capability.get(
                "order_books",
                False,
            )
        )

        networks = bool(
            capability.get(
                "networks",
                False,
            )
        )

        transfer_metadata = bool(
            capability.get(
                "transfer_metadata",
                False,
            )
        )

        verification = bool(
            capability.get(
                "verification",
                False,
            )
        )

        full = all([
            market_data,
            order_books,
            networks,
            transfer_metadata,
            verification,
        ])

        any_capability = any([
            market_data,
            order_books,
            networks,
            transfer_metadata,
            verification,
        ])

        if full:
            coverage = "full"
        elif any_capability:
            coverage = "partial"
        else:
            coverage = "intelligence_only"

        return {
            "exchange": exchange,
            "known_exchange": True,
            "coverage": coverage,
            "full_verification_available": full,
            "capabilities": {
                "market_data": market_data,
                "order_books": order_books,
                "networks": networks,
                "transfer_metadata": transfer_metadata,
                "verification": verification,
            },
            "paper_only": True,
            "live_order_submitted": False,
        }

    def classify_route(
        self,
        buy_exchange,
        sell_exchange,
    ):
        buy_exchange = str(
            buy_exchange
            or ""
        ).strip().lower()

        sell_exchange = str(
            sell_exchange
            or ""
        ).strip().lower()

        if not buy_exchange:
            raise ValueError(
                "buy exchange is required"
            )

        if not sell_exchange:
            raise ValueError(
                "sell exchange is required"
            )

        if (
            self._alias_registry
            is not None
        ):
            buy_exchange = (
                self._alias_registry
                .canonicalize(
                    buy_exchange
                )
            )

            sell_exchange = (
                self._alias_registry
                .canonicalize(
                    sell_exchange
                )
            )

        if buy_exchange == sell_exchange:
            raise ValueError(
                "buy and sell exchanges must be distinct"
            )

        buy = self.classify_exchange(
            buy_exchange
        )

        sell = self.classify_exchange(
            sell_exchange
        )

        unsupported_exchanges = []

        if buy[
            "coverage"
        ] == "unsupported":
            unsupported_exchanges.append(
                buy_exchange
            )

        if sell[
            "coverage"
        ] == "unsupported":
            unsupported_exchanges.append(
                sell_exchange
            )

        full = (
            buy[
                "full_verification_available"
            ]
            and sell[
                "full_verification_available"
            ]
        )

        if full:
            coverage = "full"
        elif unsupported_exchanges:
            coverage = "unsupported"
        elif (
            buy["coverage"]
            == "intelligence_only"
            or sell["coverage"]
            == "intelligence_only"
        ):
            coverage = "intelligence_only"
        else:
            coverage = "partial"

        return {
            "buy_exchange": buy_exchange,
            "sell_exchange": sell_exchange,
            "coverage": coverage,
            "full_verification_available": full,
            "unsupported_exchanges": (
                unsupported_exchanges
            ),
            "buy_capability": buy,
            "sell_capability": sell,
            "paper_only": True,
            "live_order_submitted": False,
        }
