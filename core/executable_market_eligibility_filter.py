"""
ArbOS™
EX-128
Executable Market Eligibility Filter
"""


class ExecutableMarketEligibilityFilter:
    def filter(self, markets):
        if markets is None:
            raise ValueError("markets are required")

        return {
            symbol: market
            for symbol, market in markets.items()
            if (
                market.get("spot", False) is True
                and market.get("active", False) is True
            )
        }
