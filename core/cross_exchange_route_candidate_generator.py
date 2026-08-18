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
        source_network_metadata=None,
        destination_network_metadata=None,
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

        source_network_metadata = (
            source_network_metadata
            or {}
        )

        destination_network_metadata = (
            destination_network_metadata
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

        source_direct_metadata = (
            source_network_metadata.get(
                coin_asset,
                {},
            )
            or {}
        )

        destination_direct_metadata = (
            destination_network_metadata.get(
                coin_asset,
                {},
            )
            or {}
        )

        source_transfer_available = (
            source_direct_metadata.get(
                "transfer_verification_available"
            )
        )

        destination_transfer_available = (
            destination_direct_metadata.get(
                "transfer_verification_available"
            )
        )

        transfer_verification_unavailable = (
            source_transfer_available is False
            or destination_transfer_available is False
        )

        if transfer_verification_unavailable:
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
                "network": None,
                "withdraw_fee": None,
                "transfer_amount": None,
                "pre_transfer_amount": float(
                    coin_amount
                ),
                "executable": False,
                "reason": (
                    "transfer_verification_unavailable"
                ),
                "transfer_verification_available": False,
                "source_network_metadata_reason": (
                    source_direct_metadata.get(
                        "network_metadata_reason"
                    )
                ),
                "destination_network_metadata_reason": (
                    destination_direct_metadata.get(
                        "network_metadata_reason"
                    )
                ),
                "network_identity": None,
                "source_network": None,
                "destination_network": None,
                "legacy_reason": None,
                "network_identity_result": None,
            })

        elif direct_source and direct_destination:
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

            direct_result = self._diagnose_network_mismatch(
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
                    "withdraw_fee"
                ),
                "transfer_amount": direct_result.get(
                    "net_amount"
                ),
                "pre_transfer_amount": float(
                    coin_amount
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
                "feasibility_diagnostics": (
                    direct_result.get(
                        "feasibility_diagnostics"
                    )
                ),
                "source_network": direct_result.get(
                    "source_network"
                ),
                "destination_network": direct_result.get(
                    "destination_network"
                ),
                "legacy_reason": direct_result.get(
                    "legacy_reason"
                ),
                "network_identity_result": (
                    direct_result.get(
                        "network_identity_result"
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

            source_bridge_metadata = (
                source_network_metadata.get(
                    bridge_asset,
                    {},
                )
                or {}
            )

            destination_bridge_metadata = (
                destination_network_metadata.get(
                    bridge_asset,
                    {},
                )
                or {}
            )

            source_transfer_available = (
                source_bridge_metadata.get(
                    "transfer_verification_available"
                )
            )

            destination_transfer_available = (
                destination_bridge_metadata.get(
                    "transfer_verification_available"
                )
            )

            transfer_verification_unavailable = (
                source_transfer_available is False
                or destination_transfer_available is False
            )

            if transfer_verification_unavailable:
                transfer_result = {
                    "executable": False,
                    "network": None,
                    "withdraw_fee": None,
                    "net_amount": None,
                    "reason": (
                        "transfer_verification_unavailable"
                    ),
                    "transfer_verification_available": False,
                    "source_network_metadata_reason": (
                        source_bridge_metadata.get(
                            "network_metadata_reason"
                        )
                    ),
                    "destination_network_metadata_reason": (
                        destination_bridge_metadata.get(
                            "network_metadata_reason"
                        )
                    ),
                }

            else:
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
                    "withdraw_fee"
                ),
                "transfer_amount": transfer_result.get(
                    "net_amount"
                ),
                "pre_transfer_amount": float(
                    quoted_amount
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
                "transfer_verification_available": (
                    transfer_result.get(
                        "transfer_verification_available"
                    )
                ),
                "source_network_metadata_reason": (
                    transfer_result.get(
                        "source_network_metadata_reason"
                    )
                ),
                "destination_network_metadata_reason": (
                    transfer_result.get(
                        "destination_network_metadata_reason"
                    )
                ),
                "network_identity": (
                    transfer_result.get(
                        "network_identity"
                    )
                ),
                "feasibility_diagnostics": (
                    transfer_result.get(
                        "feasibility_diagnostics"
                    )
                ),
            })

        return candidates

    def _diagnose_network_mismatch(
        self,
        transfer_asset,
        source_exchange,
        destination_exchange,
        transfer_result,
        source_identity_records,
        destination_identity_records,
    ):
        result = dict(transfer_result)

        if not self._require_verified_identity:
            return result

        if result.get("reason") != "no_compatible_network":
            return result

        if (
            not source_identity_records
            or not destination_identity_records
        ):
            return result

        for source_record in source_identity_records:
            if source_record.get("withdraw") is False:
                continue

            for destination_record in (
                destination_identity_records
            ):
                if destination_record.get("deposit") is False:
                    continue

                source_chain_id = str(
                    source_record.get(
                        "chain_id",
                        "",
                    )
                    or ""
                ).strip()

                destination_chain_id = str(
                    destination_record.get(
                        "chain_id",
                        "",
                    )
                    or ""
                ).strip()

                source_contract = str(
                    source_record.get(
                        "contract_address",
                        "",
                    )
                    or ""
                ).strip()

                destination_contract = str(
                    destination_record.get(
                        "contract_address",
                        "",
                    )
                    or ""
                ).strip()

                source_has_identity = bool(
                    source_chain_id
                    or source_contract
                )

                destination_has_identity = bool(
                    destination_chain_id
                    or destination_contract
                )

                # EX-180:
                # If one exchange provides strong network
                # identity and the other does not, differing
                # display names are not enough evidence to
                # declare the networks incompatible.
                #
                # Keep execution blocked, but classify the
                # relationship as UNVERIFIED for audit.
                if (
                    source_has_identity
                    != destination_has_identity
                ):
                    source_name = str(
                        source_record.get(
                            "network",
                            source_record.get(
                                "network_name",
                                "",
                            ),
                        )
                    ).strip().upper()

                    destination_name = str(
                        destination_record.get(
                            "network",
                            destination_record.get(
                                "network_name",
                                "",
                            ),
                        )
                    ).strip().upper()

                    result["legacy_reason"] = (
                        "no_compatible_network"
                    )
                    result["reason"] = (
                        "network_identity_unverified"
                    )
                    result["network_identity"] = (
                        "UNVERIFIED"
                    )
                    result["source_network"] = (
                        source_name or None
                    )
                    result["destination_network"] = (
                        destination_name or None
                    )

                    result[
                        "network_identity_result"
                    ] = {
                        "coin": str(
                            transfer_asset
                        ).strip().upper(),
                        "source_exchange": (
                            source_exchange
                        ),
                        "destination_exchange": (
                            destination_exchange
                        ),
                        "source_network": {
                            "network_name": (
                                source_name or None
                            ),
                            "chain_id": (
                                source_chain_id or None
                            ),
                            "contract_address": (
                                source_contract or None
                            ),
                        },
                        "destination_network": {
                            "network_name": (
                                destination_name or None
                            ),
                            "chain_id": (
                                destination_chain_id
                                or None
                            ),
                            "contract_address": (
                                destination_contract
                                or None
                            ),
                        },
                        "network_match": (
                            "UNVERIFIED"
                        ),
                        "reason": (
                            "incomplete_network_identity"
                        ),
                        "verified": False,
                        "execution_allowed": False,
                        "live_transfer_submitted": False,
                        "live_order_submitted": False,
                    }

                    return result

                # When both sides contain strong identity,
                # let EX-177 determine VERIFIED versus
                # INCOMPATIBLE.
                if (
                    source_has_identity
                    and destination_has_identity
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

                    if (
                        identity.get(
                            "network_match"
                        )
                        == "UNVERIFIED"
                    ):
                        result["legacy_reason"] = (
                            "no_compatible_network"
                        )
                        result["reason"] = (
                            "network_identity_unverified"
                        )
                        result[
                            "network_identity"
                        ] = "UNVERIFIED"
                        result[
                            "network_identity_result"
                        ] = identity

                        return result

        return result

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
