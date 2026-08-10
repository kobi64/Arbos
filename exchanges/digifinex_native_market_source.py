"""
ArbOS™
EX-176
DigiFinex Native Market Source

Retrieves DigiFinex's native/raw public spot-market catalogue
independently of CCXT's normalized load_markets() result.

This is market-discovery infrastructure only.
It never authenticates or submits exchange orders.
"""


class DigiFinexNativeMarketSource:
    METHOD_CANDIDATES = (
        "publicSpotGetMarketSymbols",
        "public_spot_get_market_symbols",
        "publicSpotGetSpotSymbols",
        "public_spot_get_spot_symbols",
        "publicSpotGetMarkets",
        "public_spot_get_markets",
    )

    def __init__(self, exchange):
        if exchange is None:
            raise ValueError("exchange is required")

        self._exchange = exchange

    def fetch(self):
        errors = []

        for method_name in self.METHOD_CANDIDATES:
            method = getattr(
                self._exchange,
                method_name,
                None,
            )

            if not callable(method):
                continue

            try:
                response = method()
            except Exception as exc:
                errors.append({
                    "method": method_name,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                })
                continue

            markets = self._extract_markets(
                response
            )

            if not markets:
                errors.append({
                    "method": method_name,
                    "error_type": (
                        "EmptyMarketCatalogue"
                    ),
                    "error": (
                        "native market catalogue empty"
                    ),
                })
                continue

            return {
                "exchange_id": "digifinex",
                "source": "native_raw_api",
                "method": method_name,
                "markets": markets,
                "symbols": [
                    market["symbol"]
                    for market in markets
                ],
                "market_count": len(markets),
                "errors": errors,
                "fetch_complete": True,
                "live_order_submitted": False,
            }

        return {
            "exchange_id": "digifinex",
            "source": "native_raw_api",
            "method": None,
            "markets": [],
            "symbols": [],
            "market_count": 0,
            "errors": errors,
            "fetch_complete": False,
            "live_order_submitted": False,
        }

    @staticmethod
    def _extract_markets(response):
        if not isinstance(response, dict):
            return []

        raw_markets = (
            response.get("symbol_list")
            or response.get("data")
            or response.get("symbols")
            or []
        )

        if isinstance(raw_markets, dict):
            raw_markets = (
                raw_markets.get("symbol_list")
                or raw_markets.get("symbols")
                or raw_markets.get("data")
                or []
            )

        if not isinstance(raw_markets, list):
            return []

        results = []

        for market in raw_markets:
            if not isinstance(market, dict):
                continue

            base = str(
                market.get("base_asset", "")
            ).strip().upper()

            quote = str(
                market.get("quote_asset", "")
            ).strip().upper()

            raw_symbol = str(
                market.get("symbol", "")
            ).strip().upper()

            if base and quote:
                symbol = f"{base}/{quote}"
            elif raw_symbol:
                symbol = (
                    raw_symbol
                    .replace("_", "/")
                    .replace("-", "/")
                )
            else:
                continue

            parts = [
                part.strip()
                for part in symbol.split("/")
                if part.strip()
            ]

            if len(parts) != 2:
                continue

            symbol = (
                f"{parts[0]}/{parts[1]}"
            )

            results.append({
                "symbol": symbol,
                "raw_symbol": raw_symbol,
                "base_asset": (
                    base or parts[0]
                ),
                "quote_asset": (
                    quote or parts[1]
                ),
                "status": market.get(
                    "status"
                ),
                "order_types": market.get(
                    "order_types"
                ),
                "minimum_amount": market.get(
                    "minimum_amount"
                ),
                "minimum_value": market.get(
                    "minimum_value"
                ),
                "price_precision": market.get(
                    "price_precision"
                ),
                "amount_precision": market.get(
                    "amount_precision"
                ),
                "zone": market.get("zone"),
            })

        unique = {}

        for market in results:
            unique[market["symbol"]] = market

        return [
            unique[symbol]
            for symbol in sorted(unique)
        ]
