from core.cross_exchange_route_candidate_generator import (
    CrossExchangeRouteCandidateGenerator,
)
from exchanges.exchange_network_identity_validator import (
    ExchangeNetworkIdentityValidator,
)


class NoCompatibleTransferEvaluator:
    @staticmethod
    def evaluate(
        amount,
        source_networks,
        destination_networks,
    ):
        return {
            "executable": False,
            "network": None,
            "withdraw_fee": 0.0,
            "net_amount": 0.0,
            "reason": "no_compatible_network",
        }


def strict_generator():
    return CrossExchangeRouteCandidateGenerator(
        transfer_evaluator=(
            NoCompatibleTransferEvaluator
        ),
        identity_validator=(
            ExchangeNetworkIdentityValidator()
        ),
        require_verified_identity=True,
    )


def test_real_coti_shape_is_classified_unverified():
    candidates = strict_generator().generate(
        source_exchange="kucoin",
        destination_exchange="digifinex",
        coin_asset="COTI",
        coin_amount=9500.0,
        source_networks={
            "COTI": [
                {
                    "network": "COTIEVM",
                },
            ],
        },
        destination_networks={
            "COTI": [
                {
                    "network": "COTI",
                },
            ],
        },
        source_network_identity_records={
            "COTI": [
                {
                    "coin": "COTI",
                    "network": "COTIEVM",
                    "network_name": "COTIEVM",
                    "chain_id": "cotievm",
                    "contract_address": None,
                    "deposit": True,
                    "withdraw": True,
                    "withdraw_fee": 150.0,
                },
            ],
        },
        destination_network_identity_records={
            "COTI": [
                {
                    "coin": "COTI",
                    "network": "COTI",
                    "network_name": "COTI",
                    "chain_id": None,
                    "contract_address": None,
                    "deposit": True,
                    "withdraw": True,
                    "withdraw_fee": 0.0006,
                },
            ],
        },
        bridge_quotes={},
    )

    assert len(candidates) == 1

    candidate = candidates[0]

    assert candidate["executable"] is False
    assert candidate["reason"] == (
        "network_identity_unverified"
    )
    assert candidate["legacy_reason"] == (
        "no_compatible_network"
    )
    assert candidate["network_identity"] == (
        "UNVERIFIED"
    )
    assert candidate["source_network"] == (
        "COTIEVM"
    )
    assert candidate["destination_network"] == (
        "COTI"
    )

    identity = candidate[
        "network_identity_result"
    ]

    assert identity["network_match"] == (
        "UNVERIFIED"
    )
    assert identity["execution_allowed"] is False


def test_true_identity_conflict_stays_legacy_blocked():
    candidates = strict_generator().generate(
        source_exchange="a",
        destination_exchange="b",
        coin_asset="TOKEN",
        coin_amount=1000.0,
        source_networks={
            "TOKEN": [
                {
                    "network": "CHAIN-A",
                },
            ],
        },
        destination_networks={
            "TOKEN": [
                {
                    "network": "CHAIN-B",
                },
            ],
        },
        source_network_identity_records={
            "TOKEN": [
                {
                    "network": "CHAIN-A",
                    "chain_id": "chain-a",
                    "withdraw": True,
                },
            ],
        },
        destination_network_identity_records={
            "TOKEN": [
                {
                    "network": "CHAIN-B",
                    "chain_id": "chain-b",
                    "deposit": True,
                },
            ],
        },
        bridge_quotes={},
    )

    candidate = candidates[0]

    assert candidate["executable"] is False
    assert candidate["reason"] == (
        "no_compatible_network"
    )


def test_blocked_coti_preserves_pre_transfer_amount():
    candidates = strict_generator().generate(
        source_exchange="kucoin",
        destination_exchange="digifinex",
        coin_asset="COTI",
        coin_amount=9500.0,
        source_networks={
            "COTI": [
                {"network": "COTIEVM"},
            ],
        },
        destination_networks={
            "COTI": [
                {"network": "COTI"},
            ],
        },
        source_network_identity_records={
            "COTI": [
                {
                    "coin": "COTI",
                    "network": "COTIEVM",
                    "network_name": "COTIEVM",
                    "chain_id": "cotievm",
                    "contract_address": None,
                    "deposit": True,
                    "withdraw": True,
                    "withdraw_fee": 150.0,
                },
            ],
        },
        destination_network_identity_records={
            "COTI": [
                {
                    "coin": "COTI",
                    "network": "COTI",
                    "network_name": "COTI",
                    "chain_id": None,
                    "contract_address": None,
                    "deposit": True,
                    "withdraw": True,
                    "withdraw_fee": 0.0006,
                },
            ],
        },
        bridge_quotes={},
    )

    candidate = candidates[0]

    assert candidate["executable"] is False
    assert candidate["transfer_amount"] == 0.0
    assert candidate["pre_transfer_amount"] == 9500.0
    assert candidate["reason"] == (
        "network_identity_unverified"
    )
