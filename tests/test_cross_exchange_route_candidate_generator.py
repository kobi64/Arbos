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
