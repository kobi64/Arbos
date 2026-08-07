from core.public_live_multi_path_verification_runner import (
    PublicLiveMultiPathVerificationRunner,
)


class FakeBootstrap:
    def create(self, exchange_id):
        return {"exchange_id": exchange_id}


class FakePipelineFactory:
    def __init__(self):
        self.calls = []

    def build(self, source_exchange, destination_exchange):
        self.calls.append(
            (source_exchange, destination_exchange)
        )
        return FakeScanner()


class FakeScanner:
    def scan(self, **kwargs):
        return {
            "best_route": {
                "route_id": "DIRECT-COINX",
                "net_profit_percent": 3.2,
            },
            "ranked_routes": [],
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_builds_public_exchanges_and_runs_paper_only_scan():
    factory = FakePipelineFactory()

    runner = PublicLiveMultiPathVerificationRunner(
        bootstrap=FakeBootstrap(),
        pipeline_factory=factory,
    )

    result = runner.run(
        source_exchange_id="kucoin",
        destination_exchange_id="gate",
        scan_kwargs={
            "coin_asset": "COINX",
        },
    )

    assert factory.calls == [
        (
            {"exchange_id": "kucoin"},
            {"exchange_id": "gate"},
        )
    ]

    assert result["best_route"]["route_id"] == "DIRECT-COINX"
    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False
