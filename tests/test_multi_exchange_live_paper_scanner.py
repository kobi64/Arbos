import pytest

from core.multi_exchange_live_paper_scanner import (
    MultiExchangeLivePaperScanner,
)


class FakeExchangeScanner:
    def __init__(self):
        self.calls = []

    def scan_route(
        self,
        exchange_id,
        route,
        starting_value,
        max_slippage_percent,
        fee_type="taker",
    ):
        self.calls.append(exchange_id)

        profits = {
            "kraken": -1.2,
            "kucoin": -0.8,
            "gate": -1.0,
        }

        return {
            "exchange_id": exchange_id,
            "route_id": route["route_id"],
            "filled": True,
            "net_profit_percent": profits[exchange_id],
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_scans_multiple_exchanges_and_ranks_results():
    exchange_scanner = FakeExchangeScanner()
    scanner = MultiExchangeLivePaperScanner(exchange_scanner)

    route = {
        "route_id": "USDT-BTC-SOL-USDT",
        "legs": [],
    }

    results = scanner.scan(
        exchange_ids=["kraken", "kucoin", "gate"],
        route=route,
        starting_value=100.0,
        max_slippage_percent=0.5,
    )

    assert len(results) == 3
    assert results[0]["exchange_id"] == "kucoin"
    assert results[1]["exchange_id"] == "gate"
    assert results[2]["exchange_id"] == "kraken"
    assert all(result["paper_only"] is True for result in results)
    assert all(
        result["live_order_submitted"] is False
        for result in results
    )


def test_exchange_failure_does_not_stop_other_results():
    class PartiallyFailingScanner(FakeExchangeScanner):
        def scan_route(
            self,
            exchange_id,
            route,
            starting_value,
            max_slippage_percent,
            fee_type="taker",
        ):
            if exchange_id == "gate":
                raise RuntimeError("temporary exchange failure")

            return super().scan_route(
                exchange_id=exchange_id,
                route=route,
                starting_value=starting_value,
                max_slippage_percent=max_slippage_percent,
                fee_type=fee_type,
            )

    scanner = MultiExchangeLivePaperScanner(
        PartiallyFailingScanner()
    )

    results = scanner.scan(
        exchange_ids=["kraken", "kucoin", "gate"],
        route={"route_id": "ROUTE-002", "legs": []},
        starting_value=100.0,
        max_slippage_percent=0.5,
    )

    assert len(results) == 3
    failed = next(
        result for result in results
        if result["exchange_id"] == "gate"
    )
    assert failed["filled"] is False
    assert failed["reason"] == "exchange_scan_failed"


def test_empty_exchange_list_is_rejected():
    scanner = MultiExchangeLivePaperScanner(FakeExchangeScanner())

    with pytest.raises(ValueError, match="exchange_ids are required"):
        scanner.scan(
            exchange_ids=[],
            route={"route_id": "ROUTE-003", "legs": []},
            starting_value=100.0,
            max_slippage_percent=0.5,
        )
