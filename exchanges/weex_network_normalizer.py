"""
ArbOS™
EX-217
WEEX Network Normalizer

Maps WEEX human-readable network names into
canonical ArbOS™ network identifiers.

Unknown networks are preserved in normalized uppercase
form rather than guessed.

Paper-safe utility only.
No live orders.
"""


class WeexNetworkNormalizer:
    ALIASES = {
        "tron (trc20)": "TRC20",
        "ethereum (eth)": "ERC20",
        "bnb smart chain (bsc)": "BSC",
        "arbitrum one (arb)": "ARBITRUM",
        "solana (sol)": "SOL",
        "polygon pos (matic)": "POLYGON",
        "optimism (op)": "OPTIMISM",
        "avalanche c-chain (avax-c)": "AVAXC",
        "the open network (ton)": "TON",
    }

    def normalize(
        self,
        network,
    ):
        value = str(
            network
            or ""
        ).strip()

        if not value:
            raise ValueError(
                "network is required"
            )

        key = value.lower()

        if key in self.ALIASES:
            return self.ALIASES[
                key
            ]

        return value.upper()
