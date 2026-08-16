import pytest

from core.broad_public_paper_scan_application import (
    BroadPublicPaperScanApplication,
)


class FakeExchange:
    def __init__(self, config):
        self.config = config
        self.id = "fake"

    def load_markets(self):
        return {}


class FakeCCXT:
    fake = FakeExchange


class FakeUniverseSelector:
    pass


class FakePipelineFactory:
    pass


class FakeInputPreparer:
    pass


def test_requires_ccxt_module():
    with pytest.raises(
        ValueError,
        match="ccxt_module is required",
    ):
        BroadPublicPaperScanApplication(
            ccxt_module=None
        )


def test_builds_production_composition_root():
    app = BroadPublicPaperScanApplication(
        ccxt_module=FakeCCXT,
    )

    assert app._bootstrap is not None
    assert app._universe_selector is not None
    assert app._pipeline_factory is not None
    assert app._input_preparer_factory is not None
    assert app._scanner is not None
    assert app._coordinator is not None


def test_accepts_dependency_overrides():
    selector = FakeUniverseSelector()
    pipeline = FakePipelineFactory()

    app = BroadPublicPaperScanApplication(
        ccxt_module=FakeCCXT,
        universe_selector=selector,
        pipeline_factory=pipeline,
        input_preparer_factory=(
            FakeInputPreparer
        ),
    )

    assert (
        app._universe_selector
        is selector
    )

    assert (
        app._pipeline_factory
        is pipeline
    )

    assert (
        app._input_preparer_factory
        is FakeInputPreparer
    )


def test_bootstrap_creates_rate_limited_exchange():
    app = BroadPublicPaperScanApplication(
        ccxt_module=FakeCCXT,
    )

    exchange = app._bootstrap.create(
        "fake"
    )

    assert exchange.config == {
        "enableRateLimit": True,
    }


def test_application_remains_paper_only():
    app = BroadPublicPaperScanApplication(
        ccxt_module=FakeCCXT,
    )

    assert app._scanner is not None
    assert app._coordinator is not None
