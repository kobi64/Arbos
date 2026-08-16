"""
ArbOS™
EX-219
MEXC Network Normalizer

Normalizes MEXC Spot V3 per-network metadata into
canonical ArbOS™ network identifiers while preserving
raw identity evidence.

Read-only utility.
No authentication changes.
No transfers.
No live orders.
"""


class MexcNetworkNormalizer:
    NETWORK_ALIASES = {
        "TRX": "TRC20",
        "TRON": "TRC20",
        "TRC20": "TRC20",

        "ETH": "ERC20",
        "ETHEREUM": "ERC20",
        "ERC20": "ERC20",

        "BEP20(BSC)": "BSC",
        "BSC": "BSC",
        "BEP20": "BSC",

        "SOL": "SOL",
        "SOLANA": "SOL",

        "ARBITRUM": "ARBITRUM",
        "ARB": "ARBITRUM",

        "MATIC": "POLYGON",
        "POLYGON": "POLYGON",

        "AVAX_CCHAIN": "AVAXC",
        "AVAX-C": "AVAXC",
        "AVAXC": "AVAXC",
    }

    def normalize(
        self,
        network_data,
    ):
        raw_network = str(
            network_data.get(
                "network",
                "",
            )
            or ""
        ).strip()

        lookup = raw_network.upper()

        if not lookup:
            raise ValueError(
                "network is required"
            )

        network = self.NETWORK_ALIASES.get(
            lookup,
            lookup,
        )

        withdraw_fee = network_data.get(
            "withdrawFee"
        )

        withdraw_min = network_data.get(
            "withdrawMin"
        )

        confirmations = network_data.get(
            "minConfirm"
        )

        contract_address = network_data.get(
            "contract"
        )

        if contract_address is not None:
            contract_address = str(
                contract_address
            ).strip() or None

        return {
            "network": network,
            "raw_network": raw_network,
            "deposit_enabled": bool(
                network_data.get(
                    "depositEnable",
                    False,
                )
            ),
            "withdraw_enabled": bool(
                network_data.get(
                    "withdrawEnable",
                    False,
                )
            ),
            "withdraw_fee": (
                float(
                    withdraw_fee
                )
                if withdraw_fee not in (
                    None,
                    "",
                )
                else None
            ),
            "min_withdraw": (
                max(
                    0.0,
                    float(
                        withdraw_min
                    ),
                )
                if withdraw_min not in (
                    None,
                    "",
                )
                else None
            ),
            "confirmations": (
                int(
                    confirmations
                )
                if confirmations not in (
                    None,
                    "",
                )
                else None
            ),
            "contract_address": (
                contract_address
            ),
        }
