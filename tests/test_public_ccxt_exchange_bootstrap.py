from core.public_ccxt_exchange_bootstrap import (
    PublicCCXTExchangeBootstrap,
)


class FakeCCXT:
    class kucoin:
        def __init__(self, config):
            self.config = config

    class gate:
        def __init__(self, config):
            self.config = config


def test_builds_public_exchange_without_credentials():
    bootstrap = PublicCCXTExchangeBootstrap(
        ccxt_module=FakeCCXT,
    )

    exchange = bootstrap.create("kucoin")

    assert exchange.config["enableRateLimit"] is True
    assert "apiKey" not in exchange.config
    assert "secret" not in exchange.config


def test_rejects_unknown_exchange_id():
    bootstrap = PublicCCXTExchangeBootstrap(
        ccxt_module=FakeCCXT,
    )

    try:
        bootstrap.create("unknown")
    except ValueError as exc:
        assert str(exc) == "unsupported exchange_id"
    else:
        raise AssertionError("expected ValueError")
