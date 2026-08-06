"""
ArbOS™
EX-126
CEX Discovery Pipeline Coordinator
"""


class CEXDiscoveryPipelineCoordinator:
    def __init__(self, market_loader, auto_scanner):
        self._market_loader = market_loader
        self._auto_scanner = auto_scanner

    def run(
        self,
        quote_asset,
        bridge_asset,
        starting_value,
        max_slippage_percent,
        fee_type="taker",
    ):
        loaded = self._market_loader.load()

        exchange_markets = loaded.get("markets", {})
        failures = loaded.get("failures", {})

        results = self._auto_scanner.scan(
            exchange_markets=exchange_markets,
            quote_asset=quote_asset,
            bridge_asset=bridge_asset,
            starting_value=starting_value,
            max_slippage_percent=max_slippage_percent,
            fee_type=fee_type,
        )

        return {
            "results": results,
            "market_load_failures": failures,
        }
