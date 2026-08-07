import pytest

from core.multi_coin_public_paper_verification import (
    MultiCoinPublicPaperVerification,
)


class FakeVerificationRunner:
    def __init__(self):
        self.calls = []

    def run(
        self,
        source_exchange_id,
        destination_exchange_id,
        prepare_kwargs,
    ):
        coin = prepare_kwargs["coin_asset"]

        self.calls.append({
            "source_exchange_id": source_exchange_id,
            "destination_exchange_id": destination_exchange_id,
            "prepare_kwargs": dict(prepare_kwargs),
        })

        profits = {
            "ETH": -0.30,
            "SOL": 0.75,
            "XRP": 0.20,
        }

        profit = profits[coin]

        return {
            "best_route": {
                "route_id": f"BEST-{coin}",
                "coin_asset": coin,
                "executable": True,
                "net_profit": profit,
                "net_profit_percent": profit,
            },
            "ranked_routes": [],
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_scans_multiple_coins_and_ranks_best_results():
    runner = FakeVerificationRunner()

    scanner = MultiCoinPublicPaperVerification(
        verification_runner=runner,
    )

    result = scanner.scan(
        source_exchange_id="kucoin",
        destination_exchange_id="gate",
        coin_assets=["ETH", "SOL", "XRP"],
        starting_usdt_value=100.0,
        source_fee_rate=0.001,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False

    assert result["coins_scanned"] == 3
    assert result["successful_scans"] == 3
    assert result["failed_scans"] == 0

    assert [
        item["coin_asset"]
        for item in result["ranked_results"]
    ] == ["SOL", "XRP", "ETH"]

    assert result["best_result"]["coin_asset"] == "SOL"
    assert result["best_result"]["net_profit_percent"] == 0.75

    assert len(runner.calls) == 3


def test_one_coin_failure_does_not_stop_batch():
    class PartiallyFailingRunner(FakeVerificationRunner):
        def run(
            self,
            source_exchange_id,
            destination_exchange_id,
            prepare_kwargs,
        ):
            if prepare_kwargs["coin_asset"] == "SOL":
                raise RuntimeError("temporary market failure")

            return super().run(
                source_exchange_id=source_exchange_id,
                destination_exchange_id=destination_exchange_id,
                prepare_kwargs=prepare_kwargs,
            )

    scanner = MultiCoinPublicPaperVerification(
        verification_runner=PartiallyFailingRunner(),
    )

    result = scanner.scan(
        source_exchange_id="kucoin",
        destination_exchange_id="gate",
        coin_assets=["ETH", "SOL", "XRP"],
        starting_usdt_value=100.0,
        source_fee_rate=0.001,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["coins_scanned"] == 3
    assert result["successful_scans"] == 2
    assert result["failed_scans"] == 1

    failure = result["failures"][0]

    assert failure["coin_asset"] == "SOL"
    assert failure["reason"] == "coin_scan_failed"
    assert "RuntimeError" in failure["error"]

    assert result["best_result"]["coin_asset"] == "XRP"
    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False


def test_empty_coin_list_is_rejected():
    scanner = MultiCoinPublicPaperVerification(
        verification_runner=FakeVerificationRunner(),
    )

    with pytest.raises(
        ValueError,
        match="coin_assets are required",
    ):
        scanner.scan(
            source_exchange_id="kucoin",
            destination_exchange_id="gate",
            coin_assets=[],
            starting_usdt_value=100.0,
            source_fee_rate=0.001,
            destination_fee_rate=0.001,
            max_slippage_percent=0.5,
        )
