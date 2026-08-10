"""
ArbOS™
EX-177
Exchange Network Identity & Completeness Validator

Determines whether source and destination exchange network
records contain sufficient evidence to identify the same
blockchain network safely.

A matching display/network name alone is not sufficient when
stronger identity fields conflict or are unavailable.

Results:
- VERIFIED
- INCOMPATIBLE
- UNVERIFIED

UNVERIFIED and INCOMPATIBLE networks must not be treated as
transfer-executable.

This module performs validation only.
It never transfers assets or submits exchange orders.
"""


class ExchangeNetworkIdentityValidator:
    def validate(
        self,
        coin,
        source_exchange,
        destination_exchange,
        source_network,
        destination_network,
    ):
        coin = self._required(
            coin,
            "coin",
        ).upper()

        source_exchange = self._required(
            source_exchange,
            "source_exchange",
        ).lower()

        destination_exchange = self._required(
            destination_exchange,
            "destination_exchange",
        ).lower()

        if source_network is None:
            raise ValueError(
                "source_network is required"
            )

        if destination_network is None:
            raise ValueError(
                "destination_network is required"
            )

        source = self._normalize(
            source_network
        )
        destination = self._normalize(
            destination_network
        )

        if source["withdraw_enabled"] is False:
            return self._result(
                coin,
                source_exchange,
                destination_exchange,
                source,
                destination,
                status="INCOMPATIBLE",
                reason="source_withdrawal_disabled",
            )

        if destination["deposit_enabled"] is False:
            return self._result(
                coin,
                source_exchange,
                destination_exchange,
                source,
                destination,
                status="INCOMPATIBLE",
                reason="destination_deposit_disabled",
            )

        source_contract = source[
            "contract_address"
        ]
        destination_contract = destination[
            "contract_address"
        ]

        if source_contract and destination_contract:
            if (
                source_contract.lower()
                != destination_contract.lower()
            ):
                return self._result(
                    coin,
                    source_exchange,
                    destination_exchange,
                    source,
                    destination,
                    status="INCOMPATIBLE",
                    reason="contract_address_mismatch",
                )

            return self._result(
                coin,
                source_exchange,
                destination_exchange,
                source,
                destination,
                status="VERIFIED",
                reason="matching_contract_address",
            )

        source_chain_id = source["chain_id"]
        destination_chain_id = destination[
            "chain_id"
        ]

        if source_chain_id and destination_chain_id:
            if (
                source_chain_id.lower()
                != destination_chain_id.lower()
            ):
                return self._result(
                    coin,
                    source_exchange,
                    destination_exchange,
                    source,
                    destination,
                    status="INCOMPATIBLE",
                    reason="chain_id_mismatch",
                )

            return self._result(
                coin,
                source_exchange,
                destination_exchange,
                source,
                destination,
                status="VERIFIED",
                reason="matching_chain_id",
            )

        source_name = source["network_name"]
        destination_name = destination[
            "network_name"
        ]

        if (
            source_name
            and destination_name
            and source_name != destination_name
        ):
            return self._result(
                coin,
                source_exchange,
                destination_exchange,
                source,
                destination,
                status="INCOMPATIBLE",
                reason="network_name_mismatch",
            )

        # Matching names alone are intentionally not
        # sufficient proof when chain identity is absent.
        return self._result(
            coin,
            source_exchange,
            destination_exchange,
            source,
            destination,
            status="UNVERIFIED",
            reason="insufficient_network_identity",
        )

    @staticmethod
    def _normalize(network):
        if not isinstance(network, dict):
            raise ValueError(
                "network record must be a dictionary"
            )

        def text(key):
            value = network.get(key)

            if value is None:
                return None

            value = str(value).strip()

            return value or None

        network_name = (
            text("network_name")
            or text("network")
            or text("chain_name")
            or text("chain")
        )

        chain_id = (
            text("chain_id")
            or text("id")
        )

        contract_address = (
            text("contract_address")
            or text("contractAddress")
        )

        return {
            "network_name": (
                network_name.upper()
                if network_name
                else None
            ),
            "chain_id": chain_id,
            "contract_address": contract_address,
            "deposit_enabled": network.get(
                "deposit_enabled",
                network.get(
                    "deposit",
                    None,
                ),
            ),
            "withdraw_enabled": network.get(
                "withdraw_enabled",
                network.get(
                    "withdraw",
                    None,
                ),
            ),
        }

    @staticmethod
    def _required(value, name):
        if value is None or not str(value).strip():
            raise ValueError(
                f"{name} is required"
            )

        return str(value).strip()

    @staticmethod
    def _result(
        coin,
        source_exchange,
        destination_exchange,
        source,
        destination,
        status,
        reason,
    ):
        verified = status == "VERIFIED"

        return {
            "coin": coin,
            "source_exchange": source_exchange,
            "destination_exchange": (
                destination_exchange
            ),
            "source_network": source,
            "destination_network": destination,
            "network_match": status,
            "reason": reason,
            "verified": verified,
            "execution_allowed": verified,
            "live_transfer_submitted": False,
            "live_order_submitted": False,
        }
