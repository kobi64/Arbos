"""
ArbOS™
EX-218
Poloniex Network Normalizer

Normalizes Poloniex per-network currency metadata into
canonical ArbOS™ network identifiers while preserving
raw identity evidence.

Read-only utility.
No authentication.
No transfers.
No live orders.
"""


class PoloniexNetworkNormalizer:
    NETWORK_ALIASES = {
        "TRX": "TRC20",
        "TRON": "TRC20",
        "TRC20": "TRC20",

        "ETH": "ERC20",
        "ETHEREUM": "ERC20",
        "ERC20": "ERC20",

        "BSC": "BSC",
        "BEP20": "BSC",

        "SOL": "SOL",
        "SOLANA": "SOL",

        "ARBITRUM": "ARBITRUM",
        "ARB": "ARBITRUM",

        "MATIC": "POLYGON",
        "POLYGON": "POLYGON",

        "AVAXC": "AVAXC",
        "AVAX-C": "AVAXC",
    }

    def normalize(
        self,
        network_data,
    ):
        raw_network = str(
            network_data.get(
                "blockchain",
                "",
            )
            or ""
        ).strip()

        network_name = str(
            network_data.get(
                "name",
                "",
            )
            or ""
        ).strip()

        lookup = (
            raw_network
            or network_name
        ).upper()

        network = self.NETWORK_ALIASES.get(
            lookup,
            lookup,
        )

        if not network:
            raise ValueError(
                "network is required"
            )

        withdraw_fee = (
            network_data.get(
                "withdrawFee"
            )
        )

        withdraw_min = (
            network_data.get(
                "withdrawMin"
            )
        )

        confirmations = (
            network_data.get(
                "minConfirm"
            )
        )

        contract_address = (
            network_data.get(
                "contractAddress"
            )
        )

        if contract_address is not None:
            contract_address = str(
                contract_address
            ).strip() or None

        return {
            "network": network,
            "raw_network": (
                raw_network
                or None
            ),
            "network_name": (
                network_name
                or None
            ),
            "deposit_enabled": bool(
                network_data.get(
                    "depositEnable",
                    False,
                )
            ),
            "withdraw_enabled": bool(
                network_data.get(
                    "withdrawalEnable",
                    False,
                )
            ),
            "withdraw_fee": (
                float(
                    withdraw_fee
                )
                if withdraw_fee
                not in (
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
                if withdraw_min
                not in (
                    None,
                    "",
                )
                else None
            ),
            "confirmations": (
                int(
                    confirmations
                )
                if confirmations
                not in (
                    None,
                    "",
                )
                else None
            ),
            "contract_address": (
                contract_address
            ),
        }
