from exchanges.public_native_source_discovery_coordinator import (
    PublicNativeSourceDiscoveryCoordinator,
)


class GateExchange:
    id = "gate"

    def publicSpotGetCurrencyPairs(self):
        return {
            "data": [
                {"id": "BTC_USDT"},
            ],
        }

    def publicSpotGetOrderBook(self):
        return {}


class UnknownExchange:
    id = "unknown"

    def publicGetSomethingMarkets(self):
        return {}


class FailingGateExchange:
    id = "gate"

    def publicSpotGetCurrencyPairs(self):
        raise TimeoutError(
            "public API timeout"
        )


def test_discovers_selects_and_probes_exchange():
    result = (
        PublicNativeSourceDiscoveryCoordinator()
        .run(
            GateExchange()
        )
    )

    assert result["exchange_id"] == "gate"
    assert result["candidate_selected"] is True
    assert result["selected_method"] == (
        "publicSpotGetCurrencyPairs"
    )
    assert result["probe_success"] is True
    assert result["public_api_called"] is True
    assert result["discovery_complete"] is True


def test_unknown_exchange_does_not_probe():
    result = (
        PublicNativeSourceDiscoveryCoordinator()
        .run(
            UnknownExchange()
        )
    )

    assert result["candidate_selected"] is False
    assert result["selected_method"] is None
    assert result["probe_success"] is False
    assert result["public_api_called"] is False


def test_probe_failure_is_recorded():
    result = (
        PublicNativeSourceDiscoveryCoordinator()
        .run(
            FailingGateExchange()
        )
    )

    assert result["candidate_selected"] is True
    assert result["probe_success"] is False
    assert result["error_type"] == "TimeoutError"
    assert result["error"] == "public API timeout"


def test_requires_exchange():
    try:
        (
            PublicNativeSourceDiscoveryCoordinator()
            .run(None)
        )
        assert False
    except ValueError as exc:
        assert str(exc) == "exchange is required"


def test_coordinator_is_public_only():
    result = (
        PublicNativeSourceDiscoveryCoordinator()
        .run(
            GateExchange()
        )
    )

    assert result["live_order_submitted"] is False
