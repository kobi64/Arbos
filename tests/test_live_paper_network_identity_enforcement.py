from core.cross_exchange_route_candidate_generator import (
    CrossExchangeRouteCandidateGenerator,
)
from exchanges.exchange_network_identity_validator import (
    ExchangeNetworkIdentityValidator,
)


class FakeTransferEvaluator:
    @staticmethod
    def evaluate(
        amount,
        source_networks,
        destination_networks,
    ):
        return {
            "executable": True,
            "network": "COTI",
            "withdraw_fee": 150.0,
            "net_amount": amount - 150.0,
            "reason": "ok",
        }


def strict_generator():
    return CrossExchangeRouteCandidateGenerator(
        transfer_evaluator=FakeTransferEvaluator,
        identity_validator=(
            ExchangeNetworkIdentityValidator()
        ),
        require_verified_identity=True,
    )


def test_verified_identity_remains_executable():
    candidates = strict_generator().generate(
        source_exchange="kucoin",
        destination_exchange="digifinex",
        coin_asset="COTI",
        coin_amount=1000.0,
        source_networks={
            "COTI": [{"network": "COTI"}],
        },
        destination_networks={
            "COTI": [{"network": "COTI"}],
        },
        source_network_identity_records={
            "COTI": [
                {
                    "network": "COTI",
                    "chain_id": "cotievm",
                    "withdraw": True,
                },
            ],
        },
        destination_network_identity_records={
            "COTI": [
                {
                    "network": "COTI",
                    "chain_id": "cotievm",
                    "deposit": True,
                },
            ],
        },
        bridge_quotes={},
    )

    assert len(candidates) == 1

    candidate = candidates[0]

    assert candidate["executable"] is True
    assert (
        candidate["network_identity"]
        == "VERIFIED"
    )
    assert candidate["reason"] == "ok"


def test_coti_live_shape_is_blocked_as_unverified():
    candidates = strict_generator().generate(
        source_exchange="kucoin",
        destination_exchange="digifinex",
        coin_asset="COTI",
        coin_amount=1000.0,
        source_networks={
            "COTI": [{"network": "COTI"}],
        },
        destination_networks={
            "COTI": [{"network": "COTI"}],
        },
        source_network_identity_records={
            "COTI": [
                {
                    "network": "COTI",
                    "chain_id": "cotievm",
                    "withdraw": True,
                },
            ],
        },
        destination_network_identity_records={
            "COTI": [
                {
                    "network": "COTI",
                    "chain_id": None,
                    "deposit": True,
                },
            ],
        },
        bridge_quotes={},
    )

    candidate = candidates[0]

    assert candidate["executable"] is False
    assert (
        candidate["network_identity"]
        == "UNVERIFIED"
    )
    assert candidate["reason"] == (
        "network_identity_unverified"
    )


def test_missing_identity_is_blocked():
    candidates = strict_generator().generate(
        source_exchange="a",
        destination_exchange="b",
        coin_asset="COTI",
        coin_amount=1000.0,
        source_networks={
            "COTI": [{"network": "COTI"}],
        },
        destination_networks={
            "COTI": [{"network": "COTI"}],
        },
        source_network_identity_records={},
        destination_network_identity_records={},
        bridge_quotes={},
    )

    candidate = candidates[0]

    assert candidate["executable"] is False
    assert candidate["reason"] == (
        "network_identity_unavailable"
    )


def test_conflicting_identity_is_blocked():
    candidates = strict_generator().generate(
        source_exchange="a",
        destination_exchange="b",
        coin_asset="COTI",
        coin_amount=1000.0,
        source_networks={
            "COTI": [{"network": "COTI"}],
        },
        destination_networks={
            "COTI": [{"network": "COTI"}],
        },
        source_network_identity_records={
            "COTI": [
                {
                    "network": "COTI",
                    "chain_id": "cotievm",
                },
            ],
        },
        destination_network_identity_records={
            "COTI": [
                {
                    "network": "COTI",
                    "chain_id": "different-chain",
                },
            ],
        },
        bridge_quotes={},
    )

    candidate = candidates[0]

    assert candidate["executable"] is False
    assert (
        candidate["network_identity"]
        == "INCOMPATIBLE"
    )
    assert candidate["reason"] == (
        "network_identity_incompatible"
    )


def test_legacy_generator_remains_backward_compatible():
    generator = (
        CrossExchangeRouteCandidateGenerator(
            transfer_evaluator=(
                FakeTransferEvaluator
            ),
        )
    )

    candidates = generator.generate(
        source_exchange="a",
        destination_exchange="b",
        coin_asset="COTI",
        coin_amount=1000.0,
        source_networks={
            "COTI": [{"network": "COTI"}],
        },
        destination_networks={
            "COTI": [{"network": "COTI"}],
        },
        bridge_quotes={},
    )

    assert candidates[0]["executable"] is True


def test_strict_mode_requires_validator():
    try:
        CrossExchangeRouteCandidateGenerator(
            transfer_evaluator=(
                FakeTransferEvaluator
            ),
            require_verified_identity=True,
        )
        assert False
    except ValueError as exc:
        assert (
            "identity_validator is required"
            in str(exc)
        )
