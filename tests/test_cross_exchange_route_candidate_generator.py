import pytest
from core.cross_exchange_route_candidate_generator import (
    CrossExchangeRouteCandidateGenerator,
)


class FakeTransferEvaluator:
    def evaluate(
        self,
        amount,
        source_networks,
        destination_networks,
    ):
        asset = source_networks[0]["asset"]

        if asset == "COINX":
            return {
                "executable": True,
                "network": "ARBITRUM",
                "withdraw_fee": 2.0,
                "net_amount": amount - 2.0,
                "reason": "ok",
            }

        if asset == "BTC":
            return {
                "executable": True,
                "network": "BTC",
                "withdraw_fee": 0.0001,
                "net_amount": amount - 0.0001,
                "reason": "ok",
            }

        return {
            "executable": False,
            "network": None,
            "withdraw_fee": 0.0,
            "net_amount": 0.0,
            "reason": "no_compatible_network",
        }


def test_generates_direct_coin_transfer_candidate():
    generator = CrossExchangeRouteCandidateGenerator(
        transfer_evaluator=FakeTransferEvaluator(),
    )

    candidates = generator.generate(
        source_exchange="exchange-a",
        destination_exchange="exchange-b",
        coin_asset="COINX",
        coin_amount=100.0,
        source_networks={
            "COINX": [{"asset": "COINX"}],
        },
        destination_networks={
            "COINX": [{"asset": "COINX"}],
        },
        bridge_quotes={},
    )

    assert len(candidates) == 1

    candidate = candidates[0]

    assert candidate["route_type"] == "direct_cross_exchange"
    assert candidate["transfer_asset"] == "COINX"
    assert candidate["network"] == "ARBITRUM"
    assert candidate["transfer_amount"] == 98.0
    assert candidate["executable"] is True


def test_generates_bridge_transfer_candidates_for_all_available_bridges():
    generator = CrossExchangeRouteCandidateGenerator(
        transfer_evaluator=FakeTransferEvaluator(),
    )

    candidates = generator.generate(
        source_exchange="exchange-a",
        destination_exchange="exchange-b",
        coin_asset="COINX",
        coin_amount=100.0,
        source_networks={
            "COINX": [{"asset": "COINX"}],
            "BTC": [{"asset": "BTC"}],
            "ETH": [{"asset": "ETH"}],
        },
        destination_networks={
            "COINX": [{"asset": "COINX"}],
            "BTC": [{"asset": "BTC"}],
            "ETH": [{"asset": "ETH"}],
        },
        bridge_quotes={
            "BTC": {
                "output_amount": 0.0025,
                "method": "spot",
            },
            "ETH": {
                "output_amount": 0.05,
                "method": "spot",
            },
        },
    )

    route_types = [
        candidate["route_type"]
        for candidate in candidates
    ]

    assert route_types.count("direct_cross_exchange") == 1
    assert route_types.count("bridge_cross_exchange") == 2

    btc = next(
        candidate
        for candidate in candidates
        if candidate["transfer_asset"] == "BTC"
    )

    assert btc["conversion_asset"] == "BTC"
    assert btc["conversion_method"] == "spot"
    assert btc["transfer_amount"] == pytest.approx(0.0024)
    assert btc["executable"] is True


def test_keeps_infeasible_bridge_candidate_for_audit():
    generator = CrossExchangeRouteCandidateGenerator(
        transfer_evaluator=FakeTransferEvaluator(),
    )

    candidates = generator.generate(
        source_exchange="exchange-a",
        destination_exchange="exchange-b",
        coin_asset="COINX",
        coin_amount=100.0,
        source_networks={
            "ETH": [{"asset": "ETH"}],
        },
        destination_networks={
            "ETH": [{"asset": "ETH"}],
        },
        bridge_quotes={
            "ETH": {
                "output_amount": 0.05,
                "method": "convert_swap",
            },
        },
    )

    assert len(candidates) == 1
    assert candidates[0]["transfer_asset"] == "ETH"
    assert candidates[0]["executable"] is False
    assert candidates[0]["reason"] == "no_compatible_network"


def test_does_not_invent_bridge_without_quote():
    generator = CrossExchangeRouteCandidateGenerator(
        transfer_evaluator=FakeTransferEvaluator(),
    )

    candidates = generator.generate(
        source_exchange="exchange-a",
        destination_exchange="exchange-b",
        coin_asset="COINX",
        coin_amount=100.0,
        source_networks={
            "BTC": [{"asset": "BTC"}],
        },
        destination_networks={
            "BTC": [{"asset": "BTC"}],
        },
        bridge_quotes={},
    )

    assert candidates == []


def test_direct_route_remains_visible_when_transfer_verification_unavailable():
    generator = CrossExchangeRouteCandidateGenerator(
        transfer_evaluator=FakeTransferEvaluator(),
    )

    candidates = generator.generate(
        source_exchange="weex",
        destination_exchange="gateio",
        coin_asset="FIR",
        coin_amount=100000.0,
        source_networks={
            "FIR": [],
        },
        destination_networks={
            "FIR": [
                {"asset": "FIR"},
            ],
        },
        bridge_quotes={},
        source_network_metadata={
            "FIR": {
                "network_metadata_available": False,
                "network_metadata_reason": (
                    "empty_network_list"
                ),
                "transfer_verification_available": False,
            },
        },
        destination_network_metadata={
            "FIR": {
                "network_metadata_available": True,
                "network_metadata_reason": None,
                "transfer_verification_available": True,
            },
        },
    )

    assert len(candidates) == 1

    candidate = candidates[0]

    assert candidate[
        "route_type"
    ] == "direct_cross_exchange"

    assert candidate[
        "executable"
    ] is False

    assert candidate[
        "reason"
    ] == "transfer_verification_unavailable"

    assert candidate[
        "transfer_verification_available"
    ] is False

    assert candidate[
        "source_network_metadata_reason"
    ] == "empty_network_list"


def test_verified_empty_networks_keep_no_compatible_network_semantics():
    class NoNetworkEvaluator:
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

    generator = CrossExchangeRouteCandidateGenerator(
        transfer_evaluator=NoNetworkEvaluator(),
    )

    candidates = generator.generate(
        source_exchange="a",
        destination_exchange="b",
        coin_asset="COINX",
        coin_amount=100.0,
        source_networks={
            "COINX": [
                {"asset": "COINX"},
            ],
        },
        destination_networks={
            "COINX": [
                {"asset": "COINX"},
            ],
        },
        bridge_quotes={},
        source_network_metadata={
            "COINX": {
                "network_metadata_available": True,
                "transfer_verification_available": True,
            },
        },
        destination_network_metadata={
            "COINX": {
                "network_metadata_available": True,
                "transfer_verification_available": True,
            },
        },
    )

    assert len(candidates) == 1
    assert candidates[0][
        "reason"
    ] == "no_compatible_network"


def test_unavailable_transfer_verification_does_not_invent_zero_fee():
    generator = CrossExchangeRouteCandidateGenerator(
        transfer_evaluator=FakeTransferEvaluator(),
    )

    candidates = generator.generate(
        source_exchange="weex",
        destination_exchange="gateio",
        coin_asset="FIR",
        coin_amount=100000.0,
        source_networks={
            "FIR": [],
        },
        destination_networks={
            "FIR": [
                {"asset": "FIR"},
            ],
        },
        bridge_quotes={},
        source_network_metadata={
            "FIR": {
                "network_metadata_available": False,
                "network_metadata_reason": (
                    "empty_network_list"
                ),
                "transfer_verification_available": False,
            },
        },
        destination_network_metadata={
            "FIR": {
                "network_metadata_available": True,
                "network_metadata_reason": None,
                "transfer_verification_available": True,
            },
        },
    )

    assert len(candidates) == 1

    candidate = candidates[0]

    assert candidate["executable"] is False
    assert candidate["network"] is None
    assert candidate["withdraw_fee"] is None
    assert candidate["reason"] == (
        "transfer_verification_unavailable"
    )


def test_missing_evaluator_withdraw_fee_is_not_invented_as_zero():
    class MissingFeeEvaluator:
        @staticmethod
        def evaluate(
            amount,
            source_networks,
            destination_networks,
        ):
            return {
                "executable": False,
                "network": None,
                "net_amount": 0.0,
                "reason": "withdrawal_fee_unknown",
            }

    generator = CrossExchangeRouteCandidateGenerator(
        transfer_evaluator=MissingFeeEvaluator(),
    )

    candidates = generator.generate(
        source_exchange="exchange-a",
        destination_exchange="exchange-b",
        coin_asset="COINX",
        coin_amount=100.0,
        source_networks={
            "COINX": [
                {"asset": "COINX"},
            ],
        },
        destination_networks={
            "COINX": [
                {"asset": "COINX"},
            ],
        },
        bridge_quotes={},
    )

    assert len(candidates) == 1

    candidate = candidates[0]

    assert candidate["executable"] is False
    assert candidate["withdraw_fee"] is None
    assert candidate["reason"] == (
        "withdrawal_fee_unknown"
    )


def test_bridge_missing_evaluator_withdraw_fee_is_not_invented_as_zero():
    class MissingBridgeFeeEvaluator:
        @staticmethod
        def evaluate(
            amount,
            source_networks,
            destination_networks,
        ):
            return {
                "executable": False,
                "network": None,
                "net_amount": 0.0,
                "reason": "withdrawal_fee_unknown",
            }

    generator = CrossExchangeRouteCandidateGenerator(
        transfer_evaluator=MissingBridgeFeeEvaluator(),
    )

    candidates = generator.generate(
        source_exchange="exchange-a",
        destination_exchange="exchange-b",
        coin_asset="COINX",
        coin_amount=100.0,
        source_networks={
            "BTC": [
                {"asset": "BTC"},
            ],
        },
        destination_networks={
            "BTC": [
                {"asset": "BTC"},
            ],
        },
        bridge_quotes={
            "BTC": {
                "output_amount": 0.0025,
                "method": "spot",
            },
        },
    )

    assert len(candidates) == 1

    candidate = candidates[0]

    assert candidate["route_type"] == (
        "bridge_cross_exchange"
    )
    assert candidate["executable"] is False
    assert candidate["withdraw_fee"] is None
    assert candidate["reason"] == (
        "withdrawal_fee_unknown"
    )
