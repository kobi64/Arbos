"""
ArbOS™
EX-132
Coin-First Multi-Bridge Triangle Discovery
"""


class CoinFirstMultiBridgeTriangleDiscovery:
    def discover(
        self,
        markets,
        quote_asset,
        coin_asset,
    ):
        if quote_asset is None or not str(quote_asset).strip():
            raise ValueError("quote_asset is required")

        if coin_asset is None or not str(coin_asset).strip():
            raise ValueError("coin_asset is required")

        quote_asset = str(quote_asset).strip().upper()
        coin_asset = str(coin_asset).strip().upper()

        spot_symbols = {
            symbol
            for symbol, market in markets.items()
            if market.get("spot", False)
            and market.get("active", True) is not False
        }

        coin_quote_symbol = f"{coin_asset}/{quote_asset}"

        if coin_quote_symbol not in spot_symbols:
            return []

        routes = []

        prefix = f"{coin_asset}/"

        for symbol in sorted(spot_symbols):
            if not symbol.startswith(prefix):
                continue

            bridge_asset = symbol[len(prefix):]

            if bridge_asset in {coin_asset, quote_asset}:
                continue

            bridge_quote_symbol = f"{bridge_asset}/{quote_asset}"

            if bridge_quote_symbol not in spot_symbols:
                continue

            routes.append({
                "route_id": (
                    f"{quote_asset}-{coin_asset}-"
                    f"{bridge_asset}-{quote_asset}"
                ),
                "coin_asset": coin_asset,
                "bridge_asset": bridge_asset,
                "quote_asset": quote_asset,
                "direction": "coin_first",
                "legs": [
                    {
                        "symbol": coin_quote_symbol,
                        "side": "buy",
                    },
                    {
                        "symbol": symbol,
                        "side": "sell",
                    },
                    {
                        "symbol": bridge_quote_symbol,
                        "side": "sell",
                    },
                ],
            })

            routes.append({
                "route_id": (
                    f"{quote_asset}-{bridge_asset}-"
                    f"{coin_asset}-{quote_asset}"
                ),
                "coin_asset": coin_asset,
                "bridge_asset": bridge_asset,
                "quote_asset": quote_asset,
                "direction": "bridge_first",
                "legs": [
                    {
                        "symbol": bridge_quote_symbol,
                        "side": "buy",
                    },
                    {
                        "symbol": symbol,
                        "side": "buy",
                    },
                    {
                        "symbol": coin_quote_symbol,
                        "side": "sell",
                    },
                ],
            })

        return routes
