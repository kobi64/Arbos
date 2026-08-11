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


class FakePreparer:
    def __init__(
        self,
        source_exchange,
        destination_exchange,
    ):
        self.source_exchange = source_exchange
        self.destination_exchange = destination_exchange

    def prepare(
        self,
        source_exchange_id,
        destination_exchange_id,
        coin_asset,
        starting_usdt_value,
        source_fee_rate,
        **kwargs,
    ):
        return {
            "markets": {"dummy": {}},
            "coin_asset": coin_asset,
            "coin_amount": 99.9,
            "source_networks": {
                coin_asset: [],
            },
            "destination_networks": {
                coin_asset: [],
            },
            "bridge_quotes": {},
        }


def test_can_prepare_live_inputs_automatically():
    factory = FakePipelineFactory()

    runner = PublicLiveMultiPathVerificationRunner(
        bootstrap=FakeBootstrap(),
        pipeline_factory=factory,
        input_preparer_factory=FakePreparer,
    )

    result = runner.run(
        source_exchange_id="kucoin",
        destination_exchange_id="gate",
        prepare_kwargs={
            "coin_asset": "COINX",
            "starting_usdt_value": 100.0,
            "source_fee_rate": 0.001,
            "destination_fee_rate": 0.001,
            "max_slippage_percent": 0.5,
        },
    )

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False


def test_forwards_minimum_profit_percent_from_prepare_kwargs():
    class CapturingScanner:
        def __init__(self):
            self.scan_kwargs = None

        def scan(self, **kwargs):
            self.scan_kwargs = kwargs
            return {
                "best_route": None,
                "ranked_routes": [],
                "paper_only": True,
                "live_order_submitted": False,
            }

    class CapturingFactory:
        def __init__(self):
            self.scanner = CapturingScanner()

        def build(
            self,
            source_exchange,
            destination_exchange,
        ):
            return self.scanner

    class FakeBootstrap:
        def create(self, exchange_id):
            return object()

    class FakePreparer:
        def __init__(
            self,
            source_exchange,
            destination_exchange,
        ):
            pass

        def prepare(self, **kwargs):
            return {
                "markets": {},
                "coin_asset": "ETH",
                "coin_amount": 0.05,
                "source_networks": {},
                "destination_networks": {},
                "bridge_quotes": {},
            }

    factory = CapturingFactory()

    runner = PublicLiveMultiPathVerificationRunner(
        bootstrap=FakeBootstrap(),
        pipeline_factory=factory,
        input_preparer_factory=FakePreparer,
    )

    runner.run(
        source_exchange_id="kucoin",
        destination_exchange_id="gate",
        prepare_kwargs={
            "coin_asset": "ETH",
            "starting_usdt_value": 100.0,
            "source_fee_rate": 0.001,
            "destination_fee_rate": 0.001,
            "max_slippage_percent": 0.5,
            "minimum_profit_percent": 0.5,
        },
    )

    assert (
        factory.scanner.scan_kwargs[
            "minimum_profit_percent"
        ]
        == 0.5
    )


def test_forwards_slippage_limit_to_input_preparer():
    class CapturingPreparer:
        calls = []

        def __init__(
            self,
            source_exchange,
            destination_exchange,
        ):
            pass

        def prepare(self, **kwargs):
            self.__class__.calls.append(
                dict(kwargs)
            )

            return {
                "prepare_complete": True,
                "markets": {},
                "coin_asset": "ALT",
                "coin_amount": 10.0,
                "source_networks": {},
                "destination_networks": {},
                "source_network_identity_records": {},
                "destination_network_identity_records": {},
                "bridge_quotes": {},
            }

    runner = PublicLiveMultiPathVerificationRunner(
        bootstrap=FakeBootstrap(),
        pipeline_factory=FakePipelineFactory(),
        input_preparer_factory=CapturingPreparer,
    )

    runner.run(
        source_exchange_id="kucoin",
        destination_exchange_id="gate",
        prepare_kwargs={
            "coin_asset": "ALT",
            "starting_usdt_value": 100.0,
            "source_fee_rate": 0.001,
            "destination_fee_rate": 0.002,
            "max_slippage_percent": 0.75,
        },
    )

    assert (
        CapturingPreparer.calls[-1][
            "max_slippage_percent"
        ]
        == 0.75
    )


def test_forwards_network_identity_records_to_cross_exchange_generator():
    class IdentityPreparer:
        def __init__(
            self,
            source_exchange,
            destination_exchange,
        ):
            pass

        def prepare(self, **kwargs):
            return {
                "prepare_complete": True,
                "markets": {},
                "coin_asset": "ALT",
                "coin_amount": 10.0,
                "source_networks": {
                    "ALT": [],
                },
                "destination_networks": {
                    "ALT": [],
                },
                "source_network_identity_records": {
                    "ALT": [
                        {
                            "network": "ERC20",
                            "chain_id": "1",
                        },
                    ],
                },
                "destination_network_identity_records": {
                    "ALT": [
                        {
                            "network": "ERC20",
                            "chain_id": "1",
                        },
                    ],
                },
                "bridge_quotes": {},
            }

    class CapturingScanner:
        def __init__(self):
            self.kwargs = None

        def scan(self, **kwargs):
            self.kwargs = kwargs

            return {
                "best_route": None,
                "ranked_routes": [],
                "paper_only": True,
                "live_order_submitted": False,
            }

    class CapturingFactory:
        def __init__(self):
            self.scanner = CapturingScanner()

        def build(
            self,
            source_exchange,
            destination_exchange,
        ):
            return self.scanner

    factory = CapturingFactory()

    runner = PublicLiveMultiPathVerificationRunner(
        bootstrap=FakeBootstrap(),
        pipeline_factory=factory,
        input_preparer_factory=IdentityPreparer,
    )

    runner.run(
        source_exchange_id="kucoin",
        destination_exchange_id="gate",
        prepare_kwargs={
            "coin_asset": "ALT",
            "starting_usdt_value": 100.0,
            "source_fee_rate": 0.001,
            "destination_fee_rate": 0.002,
            "max_slippage_percent": 0.5,
        },
    )

    generate_kwargs = (
        factory.scanner.kwargs[
            "cross_exchange_generate_kwargs"
        ]
    )

    assert (
        generate_kwargs[
            "source_network_identity_records"
        ]["ALT"][0]["chain_id"]
        == "1"
    )

    assert (
        generate_kwargs[
            "destination_network_identity_records"
        ]["ALT"][0]["chain_id"]
        == "1"
    )


def test_failed_source_preparation_blocks_scan_cleanly():
    class RejectedPreparer:
        def __init__(
            self,
            source_exchange,
            destination_exchange,
        ):
            pass

        def prepare(self, **kwargs):
            return {
                "prepare_complete": False,
                "reason": (
                    "source_buy_slippage_exceeded"
                ),
                "coin_asset": "ALT",
                "coin_amount": 0.0,
                "paper_only": True,
                "live_order_submitted": False,
            }

    class NeverScanner:
        def __init__(self):
            self.called = False

        def scan(self, **kwargs):
            self.called = True
            raise AssertionError(
                "scanner must not run"
            )

    class NeverFactory:
        def __init__(self):
            self.scanner = NeverScanner()

        def build(
            self,
            source_exchange,
            destination_exchange,
        ):
            return self.scanner

    factory = NeverFactory()

    runner = PublicLiveMultiPathVerificationRunner(
        bootstrap=FakeBootstrap(),
        pipeline_factory=factory,
        input_preparer_factory=RejectedPreparer,
    )

    result = runner.run(
        source_exchange_id="kucoin",
        destination_exchange_id="gate",
        prepare_kwargs={
            "coin_asset": "ALT",
            "starting_usdt_value": 100.0,
            "source_fee_rate": 0.001,
            "destination_fee_rate": 0.002,
            "max_slippage_percent": 0.5,
        },
    )

    assert factory.scanner.called is False
    assert result["scan_complete"] is False
    assert (
        result["reason"]
        == "source_buy_slippage_exceeded"
    )
    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False
