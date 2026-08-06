"""
ArbOS™
EX-121
Exchange Triangle Route Discovery
"""


class ExchangeTriangleRouteDiscovery:
    def discover(self, markets, quote_asset, bridge_asset):
        if quote_asset is None or not str(quote_asset).strip():
            raise ValueError("quote_asset is required")

        if bridge_asset is None or not str(bridge_asset).strip():
            raise ValueError("bridge_asset is required")

        quote_asset = str(quote_asset).strip().upper()
        bridge_asset = str(bridge_asset).strip().upper()

        spot_symbols = {
            symbol
            for symbol, market in markets.items()
            if market.get("spot", False)
        }

        bridge_symbol = f"{bridge_asset}/{quote_asset}"

        if bridge_symbol not in spot_symbols:
            return []

        routes = []

        for symbol in sorted(spot_symbols):
            suffix = f"/{bridge_asset}"

            if not symbol.endswith(suffix):
                continue

            alt_asset = symbol[: -len(suffix)]

            if alt_asset in {quote_asset, bridge_asset}:
                continue

            quote_symbol = f"{alt_asset}/{quote_asset}"

            if quote_symbol not in spot_symbols:
                continue

            routes.append({
                "route_id": (
                    f"{quote_asset}-{bridge_asset}-"
                    f"{alt_asset}-{quote_asset}"
                ),
                "legs": [
                    {"symbol": bridge_symbol, "side": "buy"},
                    {"symbol": symbol, "side": "buy"},
                    {"symbol": quote_symbol, "side": "sell"},
                ],
            })

        return routes
