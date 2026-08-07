"""
ArbOS™
EX-136
Cross-Exchange Route Candidate Generator
"""


class CrossExchangeRouteCandidateGenerator:
    def __init__(self, transfer_evaluator):
        self._transfer_evaluator = transfer_evaluator

    def generate(
        self,
        source_exchange,
        destination_exchange,
        coin_asset,
        coin_amount,
        source_networks,
        destination_networks,
        bridge_quotes,
    ):
        candidates = []

        coin_asset = str(coin_asset).strip().upper()

        direct_source = source_networks.get(
            coin_asset,
            [],
        )
        direct_destination = destination_networks.get(
            coin_asset,
            [],
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

            candidates.append({
                "route_id": (
                    f"DIRECT-{source_exchange}-"
                    f"{coin_asset}-{destination_exchange}"
                ),
                "route_type": "direct_cross_exchange",
                "source_exchange": source_exchange,
                "destination_exchange": destination_exchange,
                "coin_asset": coin_asset,
                "transfer_asset": coin_asset,
                "conversion_asset": None,
                "conversion_method": None,
                "network": direct_result.get("network"),
                "withdraw_fee": direct_result.get(
                    "withdraw_fee",
                    0.0,
                ),
                "transfer_amount": direct_result.get(
                    "net_amount",
                    0.0,
                ),
                "executable": bool(
                    direct_result.get("executable")
                ),
                "reason": direct_result.get(
                    "reason",
                    "",
                ),
            })

        for bridge_asset, quote in bridge_quotes.items():
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

            transfer = self._transfer_evaluator.evaluate(
                amount=quoted_amount,
                source_networks=source_bridge_networks,
                destination_networks=destination_bridge_networks,
            )

            transfer_result = (
                transfer
                if isinstance(transfer, dict)
                else transfer.__dict__
            )

            candidates.append({
                "route_id": (
                    f"BRIDGE-{source_exchange}-"
                    f"{coin_asset}-{bridge_asset}-"
                    f"{destination_exchange}"
                ),
                "route_type": "bridge_cross_exchange",
                "source_exchange": source_exchange,
                "destination_exchange": destination_exchange,
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
            })

        return candidates
