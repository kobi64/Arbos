"""
ArbOS™
EX-216
External Venue Alias Registry

Canonicalizes external exchange names into ArbOS™
exchange identifiers.

This prevents false coverage gaps caused by different
source naming conventions.

Examples:
- gate / gate.io -> gateio
- huobi / huobiglobal -> htx

Paper-safe utility only.
No live orders.
"""


class ExternalVenueAliasRegistry:
    DEFAULT_ALIASES = {
        "gate": "gateio",
        "gate.io": "gateio",
        "gateio": "gateio",

        "huobi": "htx",
        "huobiglobal": "htx",
        "huobi global": "htx",
        "htx": "htx",
    }

    def __init__(
        self,
        aliases=None,
    ):
        merged = dict(
            self.DEFAULT_ALIASES
        )

        if aliases:
            for alias, canonical in (
                aliases.items()
            ):
                alias_key = str(
                    alias
                    or ""
                ).strip().lower()

                canonical_value = str(
                    canonical
                    or ""
                ).strip().lower()

                if alias_key:
                    merged[
                        alias_key
                    ] = canonical_value

        self._aliases = merged

    def canonicalize(
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

        return self._aliases.get(
            exchange,
            exchange,
        )
