"""
ArbOS™
EX-136 / EX-178
Cross-Exchange Route Candidate Generator

EX-178 adds optional strict blockchain-network identity
enforcement for live-paper cross-exchange routes.

Legacy callers remain backward-compatible.

When strict identity enforcement is enabled, a transfer route
must pass both:
- existing transfer feasibility
- EX-177 network identity verification

Unverified routes remain visible for audit and opportunity
monitoring but are not executable.
"""


class CrossExchangeRouteCandidateGenerator:
    def __init__(
        self,
        transfer_evaluator,
        identity_validator=None,
        require_verified_identity=False,
    ):
        self._transfer_evaluator = transfer_evaluator
        self._identity_validator = identity_validator
        self._require_verified_identity = bool(
            require_verified_identity
        )

        if (
            self._require_verified_identity
            and self._identity_validator is None
        ):
            raise ValueError(
                "identity_validator is required "
                "when verified identity is required"
            )

    def generate(
        self,
        source_exchange,
        destination_exchange,
        coin_asset,
        coin_amount,
        source_networks,
        destination_networks,
        bridge_quotes,
        source_network_identity_records=None,
        destination_network_identity_records=None,
    ):
        candidates = []

        coin_asset = str(
            coin_asset
        ).strip().upper()

        source_network_identity_records = (
            source_network_identity_records
            or {}
        )

        destination_network_identity_records = (
            destination_network_identity_records
            or {}
        )

        direct_source = source_networks.get(
            coin_asset,
            [],
        )

        direct_destination = (
            destination_networks.get(
                coin_asset,
                [],
            )
        )

        if direct_source and direct_destination:
            direct = self._transfer_evaluator.evaluate(
                amount=coin_amount,
                source_networks=direct_source,
                destination_networks=direct_destination,
            )

            direct_result = (
                direct
                if isinstance(direct, dict)
                else direct.__dict__
            )

            direct_result = self._enforce_identity(
                transfer_asset=coin_asset,
                source_exchange=source_exchange,
                destination_exchange=destination_exchange,
                transfer_result=direct_result,
                source_identity_records=(
                    source_network_identity_records.get(
                        coin_asset,
                        [],
                    )
                ),
                destination_identity_records=(
                    destination_network_identity_records.get(
                        coin_asset,
                        [],
                    )
                ),
            )

            candidates.append({
                "route_id": (
                    f"DIRECT-{source_exchange}-"
                    f"{coin_asset}-{destination_exchange}"
                ),
                "route_type": (
                    "direct_cross_exchange"
                ),
                "source_exchange": source_exchange,
                "destination_exchange": (
                    destination_exchange
                ),
                "coin_asset": coin_asset,
                "transfer_asset": coin_asset,
                "conversion_asset": None,
                "conversion_method": None,
                "network": direct_result.get(
                    "network"
                ),
                "withdraw_fee": direct_result.get(
                    "withdraw_fee",
                    0.0,
                ),
                "transfer_amount": direct_result.get(
                    "net_amount",
                    0.0,
                ),
                "executable": bool(
                    direct_result.get(
                        "executable"
                    )
                ),
                "reason": direct_result.get(
                    "reason",
                    "",
                ),
                "network_identity": (
                    direct_result.get(
                        "network_identity"
                    )
                ),
            })

        for bridge_asset, quote in (
            bridge_quotes.items()
        ):
            bridge_asset = str(
                bridge_asset
            ).strip().upper()

            source_bridge_networks = (
                source_networks.get(
                    bridge_asset,
                    [],
                )
            )

            destination_bridge_networks = (
                destination_networks.get(
                    bridge_asset,
                    [],
                )
            )

            quoted_amount = float(
                quote.get(
                    "output_amount",
                    0.0,
                )
            )

            if not source_bridge_networks:
                continue

            if not destination_bridge_networks:
                continue

            transfer = (
                self._transfer_evaluator.evaluate(
                    amount=quoted_amount,
                    source_networks=(
                        source_bridge_networks
                    ),
                    destination_networks=(
                        destination_bridge_networks
                    ),
                )
            )

            transfer_result = (
                transfer
                if isinstance(transfer, dict)
                else transfer.__dict__
            )

            transfer_result = self._enforce_identity(
                transfer_asset=bridge_asset,
                source_exchange=source_exchange,
                destination_exchange=destination_exchange,
                transfer_result=transfer_result,
                source_identity_records=(
                    source_network_identity_records.get(
                        bridge_asset,
                        [],
                    )
                ),
                destination_identity_records=(
                    destination_network_identity_records.get(
                        bridge_asset,
                        [],
                    )
                ),
            )

            candidates.append({
                "route_id": (
                    f"BRIDGE-{source_exchange}-"
                    f"{coin_asset}-{bridge_asset}-"
                    f"{destination_exchange}"
                ),
                "route_type": (
                    "bridge_cross_exchange"
                ),
                "source_exchange": source_exchange,
                "destination_exchange": (
                    destination_exchange
                ),
                "coin_asset": coin_asset,
                "transfer_asset": bridge_asset,
                "conversion_asset": bridge_asset,
                "conversion_method": quote.get(
                    "method"
                ),
                "quoted_conversion_amount": (
                    quoted_amount
                ),
                "network": transfer_result.get(
                    "network"
                ),
                "withdraw_fee": transfer_result.get(
                    "withdraw_fee",
                    0.0,
                ),
                "transfer_amount": transfer_result.get(
                    "net_amount",
                    0.0,
                ),
                "executable": bool(
                    transfer_result.get(
                        "executable"
                    )
                ),
                "reason": transfer_result.get(
                    "reason",
                    "",
                ),
                "network_identity": (
                    transfer_result.get(
                        "network_identity"
                    )
                ),
            })

        return candidates

    def _enforce_identity(
        self,
        transfer_asset,
        source_exchange,
        destination_exchange,
        transfer_result,
        source_identity_records,
        destination_identity_records,
    ):
        result = dict(
            transfer_result
        )

        if not self._require_verified_identity:
            return result

        if result.get("executable") is not True:
            return result

        selected_network = str(
            result.get(
                "network",
                "",
            )
        ).strip().upper()

        if not selected_network:
            result["executable"] = False
            result["reason"] = (
                "network_identity_unavailable"
            )
            result["network_identity"] = (
                "UNVERIFIED"
            )
            return result

        source_matches = [
            record
            for record in source_identity_records
            if str(
                record.get(
                    "network",
                    record.get(
                        "network_name",
                        "",
                    ),
                )
            ).strip().upper()
            == selected_network
        ]

        destination_matches = [
            record
            for record in destination_identity_records
            if str(
                record.get(
                    "network",
                    record.get(
                        "network_name",
                        "",
                    ),
                )
            ).strip().upper()
            == selected_network
        ]

        if not source_matches or not destination_matches:
            result["executable"] = False
            result["reason"] = (
                "network_identity_unavailable"
            )
            result["network_identity"] = (
                "UNVERIFIED"
            )
            return result

        identity_results = []

        for source_record in source_matches:
            for destination_record in (
                destination_matches
            ):
                identity = (
                    self._identity_validator.validate(
                        coin=transfer_asset,
                        source_exchange=(
                            source_exchange
                        ),
                        destination_exchange=(
                            destination_exchange
                        ),
                        source_network=(
                            source_record
                        ),
                        destination_network=(
                            destination_record
                        ),
                    )
                )

                identity_results.append(
                    identity
                )

                if (
                    identity.get(
                        "execution_allowed"
                    )
                    is True
                ):
                    result[
                        "network_identity"
                    ] = "VERIFIED"

                    result[
                        "network_identity_result"
                    ] = identity

                    return result

        incompatible = any(
            item.get("network_match")
            == "INCOMPATIBLE"
            for item in identity_results
        )

        result["executable"] = False

        if incompatible:
            result["reason"] = (
                "network_identity_incompatible"
            )
            result["network_identity"] = (
                "INCOMPATIBLE"
            )
        else:
            result["reason"] = (
                "network_identity_unverified"
            )
            result["network_identity"] = (
                "UNVERIFIED"
            )

        if identity_results:
            result[
                "network_identity_result"
            ] = identity_results[0]

        return result
