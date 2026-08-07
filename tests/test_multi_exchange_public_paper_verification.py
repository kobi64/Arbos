import pytest

from core.multi_exchange_public_paper_verification import (
    MultiExchangePublicPaperVerification,
)


class FakeMultiCoinScanner:
    def __init__(self):
        self.calls = []

    def scan(
        self,
        source_exchange_id,
        destination_exchange_id,
        coin_assets,
        starting_usdt_value,
        source_fee_rate,
        destination_fee_rate,
        max_slippage_percent,
    ):
        self.calls.append(
            (
                source_exchange_id,
                destination_exchange_id,
            )
        )

        profits = {
            ("kucoin", "gate"): 0.40,
            ("gate", "kucoin"): 0.15,
            ("kucoin", "kraken"): -0.20,
        }

        profit = profits[
            (
                source_exchange_id,
                destination_exchange_id,
            )
        ]

        return {
            "best_result": {
                "route_id": (
                    f"BEST-{source_exchange_id}-"
                    f"{destination_exchange_id}"
                ),
                "source_exchange": source_exchange_id,
                "destination_exchange": destination_exchange_id,
                "coin_asset": "ETH",
                "net_profit": profit,
                "net_profit_percent": profit,
            },
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_scans_exchange_pairs_and_ranks_best_results():
    scanner = FakeMultiCoinScanner()

    coordinator = MultiExchangePublicPaperVerification(
        multi_coin_scanner=scanner,
    )

    result = coordinator.scan(
        exchange_pairs=[
            ("kucoin", "gate"),
            ("gate", "kucoin"),
            ("kucoin", "kraken"),
        ],
        coin_assets=["ETH", "SOL"],
        starting_usdt_value=100.0,
        source_fee_rate=0.001,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False

    assert result["pairs_scanned"] == 3
    assert result["successful_pairs"] == 3
    assert result["failed_pairs"] == 0

    assert [
        item["source_exchange"]
        for item in result["ranked_results"]
    ] == ["kucoin", "gate", "kucoin"]

    assert result["best_result"]["source_exchange"] == "kucoin"
    assert result["best_result"]["destination_exchange"] == "gate"
    assert result["best_result"]["net_profit_percent"] == 0.40


def test_pair_failure_does_not_stop_other_pairs():
    class PartiallyFailingScanner(FakeMultiCoinScanner):
        def scan(self, **kwargs):
            if (
                kwargs["source_exchange_id"] == "gate"
                and kwargs["destination_exchange_id"] == "kucoin"
            ):
                raise RuntimeError("exchange pair unavailable")

            return super().scan(**kwargs)

    coordinator = MultiExchangePublicPaperVerification(
        multi_coin_scanner=PartiallyFailingScanner(),
    )

    result = coordinator.scan(
        exchange_pairs=[
            ("kucoin", "gate"),
            ("gate", "kucoin"),
        ],
        coin_assets=["ETH"],
        starting_usdt_value=100.0,
        source_fee_rate=0.001,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["successful_pairs"] == 1
    assert result["failed_pairs"] == 1

    failure = result["failures"][0]

    assert failure["source_exchange"] == "gate"
    assert failure["destination_exchange"] == "kucoin"
    assert failure["reason"] == "exchange_pair_scan_failed"
    assert "RuntimeError" in failure["error"]


def test_empty_exchange_pairs_are_rejected():
    coordinator = MultiExchangePublicPaperVerification(
        multi_coin_scanner=FakeMultiCoinScanner(),
    )

    with pytest.raises(
        ValueError,
        match="exchange_pairs are required",
    ):
        coordinator.scan(
            exchange_pairs=[],
            coin_assets=["ETH"],
            starting_usdt_value=100.0,
            source_fee_rate=0.001,
            destination_fee_rate=0.001,
            max_slippage_percent=0.5,
        )
