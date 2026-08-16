"""
ArbOS™
EX-232
Phemex Network Metadata Adapter

Normalizes Phemex public chain-setting metadata into the
standard ArbOS™ network metadata representation.

Important:
- public Phemex chain settings provide network identity/status
- they do not verify deposit/withdraw enablement separately
- they do not provide withdrawal fees, minimums, or confirmations
- therefore transfer verification remains unavailable

Read-only.
No authentication.
No transfers.
No live orders.
"""


class PhemexNetworkMetadataAdapter:
    def __init__(
        self,
        client,
    ):
        if client is None:
            raise ValueError(
                "client is required"
            )

        self._client = client

    @staticmethod
    def _normalize_coin(
        coin,
    ):
        coin = str(
            coin
            or ""
        ).strip().upper()

        if not coin:
            raise ValueError(
                "coin is required"
            )

        return coin

    def describe_networks(
        self,
        coin,
    ):
        coin = self._normalize_coin(
            coin
        )

        try:
            payload = (
                self._client
                .fetch_networks(
                    coin
                )
            )

        except Exception as exc:
            return {
                "coin": coin,
                "network_metadata_available": False,
                "network_metadata_reason": (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
                "transfer_verification_available": False,
                "networks": [],
                "paper_only": True,
                "live_order_submitted": False,
                "live_transfer_submitted": False,
            }

        if not isinstance(
            payload,
            dict,
        ):
            return self._failed_result(
                coin,
                "invalid_response",
            )

        if payload.get(
            "code"
        ) != 0:
            return self._failed_result(
                coin,
                payload.get(
                    "msg",
                    "network_metadata_unavailable",
                ),
            )

        data = payload.get(
            "data"
        )

        if not isinstance(
            data,
            dict,
        ):
            return self._failed_result(
                coin,
                "invalid_network_metadata",
            )

        raw_networks = data.get(
            coin
        )

        if not isinstance(
            raw_networks,
            list,
        ):
            return self._failed_result(
                coin,
                "currency_networks_unavailable",
            )

        networks = []

        for raw in raw_networks:
            if not isinstance(
                raw,
                dict,
            ):
                continue

            network = str(
                raw.get(
                    "chainName",
                    "",
                )
                or ""
            ).strip().upper()

            if not network:
                continue

            in_use = (
                raw.get(
                    "inUse"
                )
                is True
            )

            permanently_closed = (
                raw.get(
                    "permanentlyClosed"
                )
                in (
                    1,
                    True,
                )
            )

            operational = (
                in_use
                and not permanently_closed
            )

            networks.append({
                "network": network,
                "display_name": raw.get(
                    "displayName"
                ),
                "display_network": raw.get(
                    "displayNetwork"
                ),
                "chain_id": raw.get(
                    "chainId"
                ),
                "chain_tx_url": raw.get(
                    "chainTxUrl"
                ),
                "in_use": in_use,
                "permanently_closed": (
                    permanently_closed
                ),
                "operational": operational,

                # Intentionally unknown from the
                # public Phemex chain-settings endpoint.
                "deposit_enabled": None,
                "withdraw_enabled": None,
                "minimum_deposit": None,
                "minimum_withdrawal": None,
                "withdraw_fee": None,
                "confirmations": None,

                "raw": raw,
            })

        return {
            "coin": coin,
            "network_metadata_available": True,
            "network_metadata_reason": None,
            "transfer_verification_available": False,
            "networks": networks,
            "paper_only": True,
            "live_order_submitted": False,
            "live_transfer_submitted": False,
        }

    @staticmethod
    def _failed_result(
        coin,
        reason,
    ):
        return {
            "coin": coin,
            "network_metadata_available": False,
            "network_metadata_reason": reason,
            "transfer_verification_available": False,
            "networks": [],
            "paper_only": True,
            "live_order_submitted": False,
            "live_transfer_submitted": False,
        }

    def get_networks(
        self,
        coin,
    ):
        return self.describe_networks(
            coin
        ).get(
            "networks",
            [],
        )
