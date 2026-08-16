import pytest

from core.cross_exchange_route_valuation import (
    CrossExchangeRouteValuation,
)


class FakeDestinationScanner:
    def __init__(self):
        self.calls = []

    def scan_route(
        self,
        route,
        starting_value,
        fee_rate,
        max_slippage_percent,
    ):
        self.calls.append({
            "route": route,
            "starting_value": starting_value,
            "fee_rate": fee_rate,
            "max_slippage_percent": max_slippage_percent,
        })

        symbol = route["legs"][0]["symbol"]

        final_values = {
            "COINX/USDT": 104.0,
            "BTC/USDT": 103.0,
        }

        return {
            "route_id": route["route_id"],
            "filled": True,
            "net_final_value": final_values[symbol],
            "max_leg_slippage_percent": 0.1,
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_values_direct_cross_exchange_candidate_to_final_usdt():
    valuation = CrossExchangeRouteValuation(
        destination_scanner=FakeDestinationScanner(),
    )

    candidate = {
        "route_id": "DIRECT-A-COINX-B",
        "route_type": "direct_cross_exchange",
        "transfer_asset": "COINX",
        "transfer_amount": 98.0,
        "executable": True,
    }

    result = valuation.evaluate(
        candidate=candidate,
        starting_usdt_value=100.0,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["executable"] is True
    assert result["net_final_value"] == 104.0
    assert result["net_profit"] == 4.0
    assert result["net_profit_percent"] == 4.0


def test_values_bridge_candidate_using_bridge_usdt_market():
    scanner = FakeDestinationScanner()

    valuation = CrossExchangeRouteValuation(
        destination_scanner=scanner,
    )

    candidate = {
        "route_id": "BRIDGE-A-COINX-BTC-B",
        "route_type": "bridge_cross_exchange",
        "transfer_asset": "BTC",
        "transfer_amount": 0.0024,
        "executable": True,
    }

    result = valuation.evaluate(
        candidate=candidate,
        starting_usdt_value=100.0,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["net_final_value"] == 103.0
    assert result["net_profit_percent"] == 3.0

    leg = scanner.calls[0]["route"]["legs"][0]

    assert leg == {
        "symbol": "BTC/USDT",
        "side": "sell",
    }


def test_rejects_candidate_that_is_already_non_executable():
    valuation = CrossExchangeRouteValuation(
        destination_scanner=FakeDestinationScanner(),
    )

    candidate = {
        "route_id": "FAILED",
        "route_type": "direct_cross_exchange",
        "transfer_asset": "COINX",
        "transfer_amount": 0.0,
        "executable": False,
        "reason": "no_compatible_network",
    }

    result = valuation.evaluate(
        candidate=candidate,
        starting_usdt_value=100.0,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["executable"] is False
    assert result["reason"] == "no_compatible_network"


def test_direct_destination_result_does_not_expose_mixed_unit_pnl():
    class MixedUnitDestinationScanner:
        def scan_route(
            self,
            route,
            starting_value,
            fee_rate,
            max_slippage_percent,
        ):
            return {
                "route_id": route["route_id"],
                "filled": True,
                "starting_value": starting_value,
                "net_final_value": 99.5,
                "net_profit": 99.447,
                "net_profit_percent": 190000.0,
                "paper_only": True,
                "live_order_submitted": False,
            }

    valuation = CrossExchangeRouteValuation(
        destination_scanner=MixedUnitDestinationScanner(),
    )

    candidate = {
        "route_id": "DIRECT-ETH",
        "route_type": "direct_cross_exchange",
        "transfer_asset": "ETH",
        "transfer_amount": 0.053,
        "executable": True,
    }

    result = valuation.evaluate(
        candidate=candidate,
        starting_usdt_value=100.0,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["net_profit"] == -0.5
    assert result["net_profit_percent"] == -0.5

    destination = result["destination_result"]

    assert "net_profit" not in destination
    assert "net_profit_percent" not in destination
    assert destination["input_asset"] == "ETH"
    assert destination["output_asset"] == "USDT"
    assert destination["pnl_comparable"] is False


def test_destination_result_strips_scanner_mixed_unit_pnl():
    class MixedUnitDestinationScanner:
        def scan_route(
            self,
            route,
            starting_value,
            fee_rate,
            max_slippage_percent,
        ):
            return {
                "route_id": route["route_id"],
                "filled": True,
                "starting_value": starting_value,
                "net_final_value": 99.5,
                "net_profit": 99.447,
                "net_profit_percent": 190000.0,
                "paper_only": True,
                "live_order_submitted": False,
            }

    valuation = CrossExchangeRouteValuation(
        destination_scanner=MixedUnitDestinationScanner(),
    )

    candidate = {
        "route_id": "DIRECT-ETH",
        "route_type": "direct_cross_exchange",
        "transfer_asset": "ETH",
        "transfer_amount": 0.053,
        "executable": True,
    }

    result = valuation.evaluate(
        candidate=candidate,
        starting_usdt_value=100.0,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["net_profit"] == -0.5
    assert result["net_profit_percent"] == -0.5

    destination = result["destination_result"]

    assert "net_profit" not in destination
    assert "net_profit_percent" not in destination
    assert destination["input_asset"] == "ETH"
    assert destination["output_asset"] == "USDT"
    assert destination["pnl_comparable"] is False


def test_values_blocked_candidate_for_research_only():
    scanner = FakeDestinationScanner()

    valuation = CrossExchangeRouteValuation(
        destination_scanner=scanner,
    )

    candidate = {
        "route_id": "DIRECT-kucoin-COTI-digifinex",
        "route_type": "direct_cross_exchange",
        "transfer_asset": "COINX",
        "pre_transfer_amount": 98.0,
        "transfer_amount": 0.0,
        "executable": False,
        "reason": "network_identity_unverified",
    }

    result = valuation.evaluate(
        candidate=candidate,
        starting_usdt_value=100.0,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["executable"] is False
    assert result["reason"] == (
        "network_identity_unverified"
    )

    assert result["valuation_only"] is True
    assert (
        result["paper_market_value_available"]
        is True
    )

    assert (
        result["hypothetical_transfer_amount"]
        == 98.0
    )

    assert result["hypothetical_final_value"] == 104.0
    assert result["hypothetical_profit"] == 4.0
    assert (
        result["hypothetical_profit_percent"]
        == 4.0
    )

    assert result["transfer_verified"] is False


def test_blocked_candidate_without_pre_transfer_amount_is_not_valued():
    scanner = FakeDestinationScanner()

    valuation = CrossExchangeRouteValuation(
        destination_scanner=scanner,
    )

    candidate = {
        "route_id": "FAILED",
        "route_type": "direct_cross_exchange",
        "transfer_asset": "COINX",
        "transfer_amount": 0.0,
        "executable": False,
        "reason": "no_compatible_network",
    }

    result = valuation.evaluate(
        candidate=candidate,
        starting_usdt_value=100.0,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["executable"] is False
    assert result["valuation_only"] is False
    assert (
        result["paper_market_value_available"]
        is False
    )

    assert scanner.calls == []


def test_destination_market_exception_blocks_executable_route_cleanly():
    class MissingDestinationMarketScanner:
        def scan_route(
            self,
            route,
            starting_value,
            fee_rate,
            max_slippage_percent,
        ):
            raise ValueError(
                "destination symbol unavailable"
            )

    valuation = CrossExchangeRouteValuation(
        destination_scanner=(
            MissingDestinationMarketScanner()
        ),
    )

    candidate = {
        "route_id": "DIRECT-kucoin-BNB-htx",
        "route_type": "direct_cross_exchange",
        "transfer_asset": "BNB",
        "transfer_amount": 1.0,
        "executable": True,
    }

    result = valuation.evaluate(
        candidate=candidate,
        starting_usdt_value=100.0,
        destination_fee_rate=0.002,
        max_slippage_percent=0.5,
    )

    assert result["executable"] is False
    assert result["reason"] == (
        "destination_market_unavailable"
    )
    assert result["destination_result"] is None
    assert (
        "ValueError"
        in result["destination_error"]
    )
    assert result["paper_only"] is True
    assert (
        result["live_order_submitted"]
        is False
    )


def test_destination_market_exception_does_not_break_research_valuation():
    class MissingDestinationMarketScanner:
        def scan_route(
            self,
            route,
            starting_value,
            fee_rate,
            max_slippage_percent,
        ):
            raise ValueError(
                "destination symbol unavailable"
            )

    valuation = CrossExchangeRouteValuation(
        destination_scanner=(
            MissingDestinationMarketScanner()
        ),
    )

    candidate = {
        "route_id": (
            "DIRECT-kucoin-COTI-htx"
        ),
        "route_type": (
            "direct_cross_exchange"
        ),
        "transfer_asset": "COTI",
        "pre_transfer_amount": 25.0,
        "transfer_amount": 0.0,
        "executable": False,
        "reason": (
            "network_identity_unverified"
        ),
    }

    result = valuation.evaluate(
        candidate=candidate,
        starting_usdt_value=100.0,
        destination_fee_rate=0.002,
        max_slippage_percent=0.5,
    )

    assert result["executable"] is False
    assert result["reason"] == (
        "network_identity_unverified"
    )
    assert result["valuation_only"] is True
    assert (
        result["paper_market_value_available"]
        is False
    )
    assert (
        "ValueError"
        in result["destination_error"]
    )
    assert result["paper_only"] is True
    assert (
        result["live_order_submitted"]
        is False
    )


def test_executable_candidate_with_unknown_transfer_amount_fails_closed():
    scanner = FakeDestinationScanner()

    valuation = CrossExchangeRouteValuation(
        destination_scanner=scanner,
    )

    candidate = {
        "route_id": "DIRECT-A-COINX-B",
        "route_type": "direct_cross_exchange",
        "transfer_asset": "COINX",
        "transfer_amount": None,
        "executable": True,
    }

    with pytest.raises(
        ValueError,
        match="transfer_amount is required",
    ):
        valuation.evaluate(
            candidate=candidate,
            starting_usdt_value=100.0,
            destination_fee_rate=0.001,
            max_slippage_percent=0.5,
        )

    assert scanner.calls == []
