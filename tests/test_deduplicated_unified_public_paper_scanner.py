from core.deduplicated_unified_public_paper_scanner import (
    DeduplicatedUnifiedPublicPaperScanner,
)


class FakeInternalScanner:
    def __init__(self, exchange_id, calls):
        self.exchange_id = exchange_id
        self.calls = calls

    def scan(
        self,
        markets,
        quote_asset,
        coin_asset,
        starting_value,
        fee_rate,
        max_slippage_percent,
    ):
        self.calls.append(
            (
                self.exchange_id,
                coin_asset,
            )
        )

        return {
            "ranked_routes": [
                {
                    "route_id": (
                        f"INTERNAL-{self.exchange_id}-"
                        f"{coin_asset}"
                    ),
                    "route_type": (
                        "internal_triangle"
                    ),
                    "coin_asset": coin_asset,
                    "source_exchange": (
                        self.exchange_id
                    ),
                    "executable": True,
                    "filled": True,
                    "net_profit": 0.1,
                    "net_profit_percent": 0.1,
                },
            ],
            "paper_only": True,
            "live_order_submitted": False,
        }


class FakeCrossCoordinator:
    def __init__(self, destination_id, calls):
        self.destination_id = destination_id
        self.calls = calls

    def evaluate(
        self,
        internal_routes,
        cross_exchange_generate_kwargs,
        starting_usdt_value,
        destination_fee_rate,
        max_slippage_percent,
    ):
        source_id = (
            cross_exchange_generate_kwargs[
                "source_exchange"
            ]
        )

        coin = (
            cross_exchange_generate_kwargs[
                "coin_asset"
            ]
        )

        self.calls.append(
            (
                source_id,
                self.destination_id,
                coin,
            )
        )

        cross_route = {
            "route_id": (
                f"CROSS-{source_id}-"
                f"{self.destination_id}-"
                f"{coin}"
            ),
            "route_type": (
                "direct_cross_exchange"
            ),
            "coin_asset": coin,
            "source_exchange": (
                source_id
            ),
            "destination_exchange": (
                self.destination_id
            ),
            "executable": True,
            "net_profit": 0.2,
            "net_profit_percent": 0.2,
        }

        return {
            "ranked_routes": [
                cross_route,
            ],
            "ranked_internal": [],
            "ranked_cross_exchange": [
                cross_route,
            ],
            "rejected_cross_exchange": [],
            "paper_only": True,
            "live_order_submitted": False,
        }


class FakeExchange:
    def __init__(self, exchange_id):
        self.id = exchange_id

    def load_markets(self):
        return {}


class FakePipelineFactory:
    def __init__(self):
        self.internal_calls = []
        self.cross_calls = []

    def build_internal(self, exchange):
        return FakeInternalScanner(
            exchange_id=exchange.id,
            calls=self.internal_calls,
        )

    def build_cross_exchange(
        self,
        destination_exchange,
    ):
        return FakeCrossCoordinator(
            destination_id=(
                destination_exchange.id
            ),
            calls=self.cross_calls,
        )


class FakeBootstrap:
    def create(self, exchange_id):
        return FakeExchange(
            exchange_id
        )


class FakePreparer:
    def __init__(
        self,
        source_exchange,
        destination_exchange,
    ):
        pass

    def prepare(
        self,
        source_exchange_id,
        destination_exchange_id,
        coin_asset,
        starting_usdt_value,
        source_fee_rate,
        max_slippage_percent,
    ):
        return {
            "prepare_complete": True,
            "markets": {},
            "coin_asset": coin_asset,
            "coin_amount": 1.0,
            "source_networks": {},
            "destination_networks": {},
            "source_network_identity_records": {},
            "destination_network_identity_records": {},
            "bridge_quotes": {},
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_internal_coin_scan_runs_once_per_exchange_not_per_destination():
    factory = FakePipelineFactory()

    scanner = DeduplicatedUnifiedPublicPaperScanner(
        bootstrap=FakeBootstrap(),
        pipeline_factory=factory,
        input_preparer_factory=FakePreparer,
    )

    scanner.scan(
        exchange_coin_assets={
            "kucoin": {
                "ETH",
            },
            "gate": {
                "ETH",
            },
            "htx": {
                "ETH",
            },
        },
        fee_rates={
            "kucoin": 0.001,
            "gate": 0.002,
            "htx": 0.002,
        },
        starting_usdt_value=100.0,
        max_slippage_percent=0.5,
    )

    assert sorted(
        factory.internal_calls
    ) == [
        ("gate", "ETH"),
        ("htx", "ETH"),
        ("kucoin", "ETH"),
    ]


def test_cross_exchange_still_runs_every_ordered_pair():
    factory = FakePipelineFactory()

    scanner = DeduplicatedUnifiedPublicPaperScanner(
        bootstrap=FakeBootstrap(),
        pipeline_factory=factory,
        input_preparer_factory=FakePreparer,
    )

    result = scanner.scan(
        exchange_coin_assets={
            "kucoin": {"ETH"},
            "gate": {"ETH"},
            "htx": {"ETH"},
        },
        fee_rates={
            "kucoin": 0.001,
            "gate": 0.002,
            "htx": 0.002,
        },
        starting_usdt_value=100.0,
        max_slippage_percent=0.5,
    )

    assert len(
        factory.cross_calls
    ) == 6

    assert result[
        "ordered_exchange_pair_count"
    ] == 6


def test_internal_and_cross_routes_are_ranked_together():
    factory = FakePipelineFactory()

    scanner = DeduplicatedUnifiedPublicPaperScanner(
        bootstrap=FakeBootstrap(),
        pipeline_factory=factory,
        input_preparer_factory=FakePreparer,
    )

    result = scanner.scan(
        exchange_coin_assets={
            "kucoin": {"ETH"},
            "gate": {"ETH"},
        },
        fee_rates={
            "kucoin": 0.001,
            "gate": 0.002,
        },
        starting_usdt_value=100.0,
        max_slippage_percent=0.5,
    )

    assert result["best_route"][
        "route_type"
    ] == "direct_cross_exchange"

    assert (
        result["internal_route_count"]
        == 2
    )

    assert (
        result["cross_exchange_route_count"]
        == 2
    )

    assert result[
        "route_count"
    ] == 4


def test_scanner_is_paper_only():
    scanner = DeduplicatedUnifiedPublicPaperScanner(
        bootstrap=FakeBootstrap(),
        pipeline_factory=FakePipelineFactory(),
        input_preparer_factory=FakePreparer,
    )

    result = scanner.scan(
        exchange_coin_assets={
            "kucoin": {"ETH"},
            "gate": {"ETH"},
        },
        fee_rates={
            "kucoin": 0.001,
            "gate": 0.002,
        },
        starting_usdt_value=100.0,
        max_slippage_percent=0.5,
    )

    assert result["paper_only"] is True
    assert (
        result["live_order_submitted"]
        is False
    )
