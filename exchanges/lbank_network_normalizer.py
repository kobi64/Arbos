"""
ArbOS™
EX-221
LBank Network Normalizer

Normalizes LBank public asset/network metadata into
canonical ArbOS™ network records.

Preserves:
- deposit / withdrawal state
- withdrawal fee
- minimum withdrawal
- minimum deposit
- contract address
- memo/tag requirement

Unknown networks fail closed.

Read-only.
No transfers.
No live orders.
"""


class LBankNetworkNormalizer:
    _ALIASES = {
        "erc20": "ETH",
        "ethereum": "ETH",

        "bep20(bsc)": "BSC",
        "bep20": "BSC",
        "bsc": "BSC",

        "trc20": "TRX",
        "tron": "TRX",

        "polygon": "POLYGON",
        "matic": "POLYGON",

        "arbitrum one": "ARBITRUM",
        "arbitrum": "ARBITRUM",

        "solana": "SOL",
        "sol": "SOL",

        "c-chain": "AVAXC",
        "avax c-chain": "AVAXC",
        "avaxc": "AVAXC",

        "terra classic": "LUNC",
        "lunc": "LUNC",

        "omni": "OMNI",

        "ton": "TON",
        "toncoin": "TONCOIN",

        "near": "NEAR",

        "klay": "KLAYTN",
        "klaytn": "KLAYTN",

        "plasma": "PLASMA",
    }

    def normalize_network_name(
        self,
        value,
    ):
        value = str(
            value
            or ""
        ).strip().lower()

        if not value:
            return None

        return self._ALIASES.get(
            value
        )

    def normalize_record(
        self,
        record,
    ):
        if not isinstance(
            record,
            dict,
        ):
            return None

        asset = str(
            record.get(
                "assetCode",
                "",
            )
            or ""
        ).strip().upper()

        raw_network = str(
            record.get(
                "chainName",
                "",
            )
            or ""
        ).strip()

        if (
            not asset
            or not raw_network
        ):
            return None

        network = (
            self.normalize_network_name(
                raw_network
            )
        )

        if network is None:
            return None

        fee = record.get(
            "assetFee"
        )

        if not isinstance(
            fee,
            dict,
        ):
            fee = {}

        contract = record.get(
            "contractInfo"
        )

        if contract is not None:
            contract = str(
                contract
            ).strip() or None

        return {
            "asset": asset,
            "network": network,
            "raw_network": (
                raw_network
            ),
            "deposit_enabled": (
                record.get(
                    "canDeposit"
                )
                is True
            ),
            "withdraw_enabled": (
                record.get(
                    "canDraw"
                )
                is True
            ),
            "station_withdraw_enabled": (
                record.get(
                    "canStationDraw"
                )
                is True
            ),
            "contract_address": (
                contract
            ),
            "memo_required": (
                record.get(
                    "hasMemo"
                )
                is True
            ),
            "withdraw_fee": (
                self._float_or_none(
                    fee.get(
                        "feeAmt"
                    )
                )
            ),
            "min_withdraw": (
                self._float_or_none(
                    fee.get(
                        "minAmt"
                    )
                )
            ),
            "min_deposit": (
                self._float_or_zero(
                    fee.get(
                        "minDepositAmt"
                    )
                )
            ),
        }

    @staticmethod
    def _float_or_none(
        value,
    ):
        if value in (
            None,
            "",
        ):
            return None

        return float(
            value
        )

    @staticmethod
    def _float_or_zero(
        value,
    ):
        if value in (
            None,
            "",
        ):
            return 0.0

        return max(
            0.0,
            float(
                value
            ),
        )
