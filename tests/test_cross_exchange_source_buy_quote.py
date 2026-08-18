import pytest

from core.cross_exchange_source_buy_quote import (
    CrossExchangeSourceBuyQuote,
)


class FakeDepthScanner:
    def __init__(self):
        self.route = None
        self.starting_value = None
        self.fee_rate = None
        self.max_slippage_percent = None

    def scan_route(
        self,
        route,
        starting_value,
        fee_rate,
        max_slippage_percent,
    ):
        self.route = route
        self.starting_value = starting_value
        self.fee_rate = fee_rate
        self.max_slippage_percent = (
            max_slippage_percent
        )

        return {
            "route_id": route["route_id"],
            "filled": True,
            "net_final_value": 25.0,
            "legs": [
                {
                    "leg_number": 1,
                    "symbol": "ALT/USDT",
                    "side": "buy",
                    "average_price": 4.0,
                    "slippage_percent": 0.1,
                    "fee_rate": fee_rate,
                    "net_output_amount": 25.0,
                },
            ],
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_quotes_source_buy_using_alt_usdt_pair():
    scanner = FakeDepthScanner()

    result = CrossExchangeSourceBuyQuote(
        depth_scanner=scanner
    ).quote(
        coin_asset="ALT",
        starting_usdt_value=100.0,
        source_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert scanner.route == {
        "route_id": "SOURCE-BUY-ALT",
        "legs": [
            {
                "symbol": "ALT/USDT",
                "side": "buy",
            },
        ],
    }

    assert result["filled"] is True
    assert result["coin_asset"] == "ALT"
    assert result["coin_amount"] == 25.0
    assert result["starting_usdt_value"] == 100.0


def test_passes_source_fee_and_slippage_limit():
    scanner = FakeDepthScanner()

    CrossExchangeSourceBuyQuote(
        depth_scanner=scanner
    ).quote(
        coin_asset="ALT",
        starting_usdt_value=100.0,
        source_fee_rate=0.002,
        max_slippage_percent=0.75,
    )

    assert scanner.fee_rate == 0.002
    assert (
        scanner.max_slippage_percent
        == 0.75
    )


def test_rejected_source_buy_remains_rejected():
    class RejectedScanner:
        def scan_route(
            self,
            route,
            starting_value,
            fee_rate,
            max_slippage_percent,
        ):
            return {
                "route_id": route["route_id"],
                "filled": False,
                "reason": "slippage_exceeded",
                "legs": [],
                "paper_only": True,
                "live_order_submitted": False,
            }

    result = CrossExchangeSourceBuyQuote(
        depth_scanner=RejectedScanner()
    ).quote(
        coin_asset="ALT",
        starting_usdt_value=100.0,
        source_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["filled"] is False
    assert result["coin_amount"] is None
    assert result["reason"] == "slippage_exceeded"


def test_requires_coin_asset():
    with pytest.raises(
        ValueError,
        match="coin_asset is required",
    ):
        CrossExchangeSourceBuyQuote(
            depth_scanner=FakeDepthScanner()
        ).quote(
            coin_asset="",
            starting_usdt_value=100.0,
            source_fee_rate=0.001,
            max_slippage_percent=0.5,
        )


def test_requires_positive_starting_value():
    with pytest.raises(
        ValueError,
        match="starting_usdt_value must be positive",
    ):
        CrossExchangeSourceBuyQuote(
            depth_scanner=FakeDepthScanner()
        ).quote(
            coin_asset="ALT",
            starting_usdt_value=0,
            source_fee_rate=0.001,
            max_slippage_percent=0.5,
        )


def test_source_buy_is_paper_only():
    result = CrossExchangeSourceBuyQuote(
        depth_scanner=FakeDepthScanner()
    ).quote(
        coin_asset="ALT",
        starting_usdt_value=100.0,
        source_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False


def test_unfilled_source_buy_preserves_coin_amount_as_unknown():
    class UnfilledScanner:
        def scan_route(self, **kwargs):
            return {
                "filled": False,
                "reason": "insufficient_depth",
            }

    quote = CrossExchangeSourceBuyQuote(
        depth_scanner=UnfilledScanner(),
    )

    result = quote.quote(
        coin_asset="BTC",
        starting_usdt_value=100.0,
        source_fee_rate=0.001,
        max_slippage_percent=1.0,
    )

    assert result["filled"] is False
    assert result["coin_amount"] is None
    assert result["live_order_submitted"] is False
