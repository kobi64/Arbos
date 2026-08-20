import pytest

from core.exchange_subscription_capacity_profiles import (
    ExchangeSubscriptionCapacityProfiles,
)
from core.hundred_coin_public_paper_scan_application import (
    HundredCoinPublicPaperScanApplication,
)


class FakeExchange:
    def __init__(
        self,
        config,
        assets,
        ticker_failure=False,
    ):
        self.config = config
        self._assets = assets
        self._ticker_failure = (
            ticker_failure
        )

    def load_markets(self):
        return {
            f"{asset}/USDT": {
                "spot": True,
                "active": True,
                "base": asset,
                "quote": "USDT",
                "info": {
                    "baseCoin": asset,
                },
            }
            for asset in self._assets
        }

    def fetch_tickers(self):
        if self._ticker_failure:
            raise RuntimeError(
                "ticker failure"
            )

        return {
            f"{asset}/USDT": {
                "quoteVolume": (
                    1000000.0 - index
                )
            }
            for index, asset in enumerate(
                self._assets
            )
        }


class FakeCCXT:
    pass


def make_exchange_class(
    assets,
    ticker_failure=False,
):
    class Exchange(FakeExchange):
        def __init__(self, config):
            super().__init__(
                config=config,
                assets=assets,
                ticker_failure=(
                    ticker_failure
                ),
            )

    return Exchange


def capacity_registry(
    exchanges,
    capacity=20,
):
    registry = (
        ExchangeSubscriptionCapacityProfiles()
    )

    for exchange_id in exchanges:
        registry.register({
            "exchange_id": exchange_id,
            "max_symbols_per_batch": (
                capacity
            ),
            "max_batches": 1,
        })

    return registry


class FakeHarness:
    def __init__(self):
        self.calls = []

    def run(self, **kwargs):
        self.calls.append(kwargs)

        approved = sorted(
            set.intersection(
                *[
                    set(items)
                    for items in kwargs[
                        "exchange_coin_assets"
                    ].values()
                ]
            )
        )[
            :kwargs[
                "requested_coin_count"
            ]
        ]

        return {
            "harness_ready": True,
            "scan_executed": True,
            "readiness": "PASS",
            "reason": None,
            "approved_coin_count": len(
                approved
            ),
            "approved_coin_assets": (
                approved
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }


def build_application(
    *,
    gate_failure=False,
):
    ccxt_module = FakeCCXT()

    ccxt_module.kucoin = (
        make_exchange_class(
            [
                "BTC",
                "ETH",
                "SOL",
                "XRP",
            ]
        )
    )

    ccxt_module.gate = (
        make_exchange_class(
            [
                "BTC",
                "ETH",
                "SOL",
                "DOGE",
            ],
            ticker_failure=(
                gate_failure
            ),
        )
    )

    application = (
        HundredCoinPublicPaperScanApplication(
            ccxt_module=ccxt_module,
            capacity_profiles=(
                capacity_registry(
                    [
                        "kucoin",
                        "gate",
                    ]
                )
            ),
        )
    )

    fake_harness = FakeHarness()
    application._harness = (
        fake_harness
    )

    return application, fake_harness


def test_discovers_then_passes_exchange_universes_to_harness():
    application, harness = (
        build_application()
    )

    result = application.run(
        exchange_ids=[
            "kucoin",
            "gate",
        ],
        fee_rates={
            "kucoin": 0.001,
            "gate": 0.001,
        },
        starting_usdt_value=100.0,
        max_slippage_percent=0.5,
        requested_coin_count=3,
        discovery_limit=4,
    )

    assert len(harness.calls) == 1

    call = harness.calls[0]

    assert call[
        "exchange_coin_assets"
    ] == {
        "kucoin": {
            "BTC",
            "ETH",
            "SOL",
            "XRP",
        },
        "gate": {
            "BTC",
            "ETH",
            "SOL",
            "DOGE",
        },
    }

    assert result[
        "production_wiring"
    ] is True

    assert result[
        "paper_only"
    ] is True

    assert (
        result[
            "live_order_submitted"
        ]
        is False
    )


def test_public_bootstrap_enables_rate_limit():
    application, _ = (
        build_application()
    )

    exchange = (
        application._bootstrap.create(
            "kucoin"
        )
    )

    assert (
        exchange.config[
            "enableRateLimit"
        ]
        is True
    )


def test_duplicate_exchange_ids_are_removed():
    application, harness = (
        build_application()
    )

    result = application.run(
        exchange_ids=[
            "kucoin",
            "kucoin",
            "gate",
        ],
        fee_rates={
            "kucoin": 0.001,
            "gate": 0.001,
        },
        starting_usdt_value=100.0,
        max_slippage_percent=0.5,
        requested_coin_count=2,
        discovery_limit=4,
    )

    assert result["exchange_ids"] == [
        "kucoin",
        "gate",
    ]

    assert len(
        harness.calls
    ) == 1


def test_ticker_failure_is_recorded_and_excluded():
    application, harness = (
        build_application(
            gate_failure=True
        )
    )

    result = application.run(
        exchange_ids=[
            "kucoin",
            "gate",
        ],
        fee_rates={
            "kucoin": 0.001,
            "gate": 0.001,
        },
        starting_usdt_value=100.0,
        max_slippage_percent=0.5,
        requested_coin_count=2,
        discovery_limit=4,
    )

    assert result[
        "discovery"
    ]["gate"][
        "discovery_ready"
    ] is False

    assert result[
        "discovery"
    ]["gate"][
        "reason"
    ] == (
        "ticker_discovery_failed"
    )

    assert (
        "gate"
        not in harness.calls[0][
            "exchange_coin_assets"
        ]
    )


def test_at_least_two_exchanges_required():
    application, _ = (
        build_application()
    )

    with pytest.raises(
        ValueError,
        match=(
            "at least two exchanges "
            "are required"
        ),
    ):
        application.run(
            exchange_ids=[
                "kucoin",
            ],
            fee_rates={
                "kucoin": 0.001,
            },
            starting_usdt_value=100.0,
            max_slippage_percent=0.5,
        )


def test_discovery_limit_must_be_positive():
    application, _ = (
        build_application()
    )

    with pytest.raises(
        ValueError,
        match=(
            "discovery_limit must "
            "be positive"
        ),
    ):
        application.run(
            exchange_ids=[
                "kucoin",
                "gate",
            ],
            fee_rates={
                "kucoin": 0.001,
                "gate": 0.001,
            },
            starting_usdt_value=100.0,
            max_slippage_percent=0.5,
            discovery_limit=0,
        )


def test_ccxt_module_is_required():
    with pytest.raises(
        ValueError,
        match="ccxt_module is required",
    ):
        (
            HundredCoinPublicPaperScanApplication(
                ccxt_module=None
            )
        )
