from exchanges.ourbit_network_metadata_adapter import (
    OurbitNetworkMetadataAdapter,
)


class FakeUnavailableClient:
    def fetch_currencies(self):
        return {
            "fetch_complete": False,
            "reason": "credentials_unavailable",
            "currencies": [],
            "read_only": True,
            "paper_only": True,
            "live_order_submitted": False,
            "live_transfer_submitted": False,
        }


def test_credentials_unavailable_fails_closed():
    adapter = OurbitNetworkMetadataAdapter(
        client=FakeUnavailableClient(),
    )

    result = adapter.fetch(
        "USDT"
    )

    assert result[
        "available"
    ] is False

    assert result[
        "network_metadata_available"
    ] is False

    assert result[
        "network_metadata_reason"
    ] == "credentials_unavailable"

    assert result[
        "transfer_verification_available"
    ] is False

    assert result[
        "networks"
    ] == []


def test_result_is_paper_safe():
    adapter = OurbitNetworkMetadataAdapter(
        client=FakeUnavailableClient(),
    )

    result = adapter.fetch(
        "USDT"
    )

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False

    assert result[
        "live_transfer_submitted"
    ] is False


def test_coin_is_normalized():
    adapter = OurbitNetworkMetadataAdapter(
        client=FakeUnavailableClient(),
    )

    result = adapter.fetch(
        " usdt "
    )

    assert result[
        "coin"
    ] == "USDT"


def test_coin_is_required():
    adapter = OurbitNetworkMetadataAdapter(
        client=FakeUnavailableClient(),
    )

    try:
        adapter.fetch("")
    except ValueError as exc:
        assert str(exc) == (
            "coin is required"
        )
    else:
        raise AssertionError(
            "ValueError not raised"
        )


def test_client_is_required():
    try:
        OurbitNetworkMetadataAdapter(
            client=None,
        )
    except ValueError as exc:
        assert str(exc) == (
            "client is required"
        )
    else:
        raise AssertionError(
            "ValueError not raised"
        )


def test_get_networks_returns_empty_when_metadata_unavailable():
    adapter = OurbitNetworkMetadataAdapter(
        client=FakeUnavailableClient(),
    )

    assert adapter.get_networks(
        "USDT"
    ) == []


def test_describe_networks_preserves_fail_closed_reason():
    adapter = OurbitNetworkMetadataAdapter(
        client=FakeUnavailableClient(),
    )

    result = adapter.describe_networks(
        "USDT"
    )

    assert result[
        "coin"
    ] == "USDT"

    assert result[
        "available"
    ] is False

    assert result[
        "network_metadata_available"
    ] is False

    assert result[
        "network_metadata_reason"
    ] == "credentials_unavailable"

    assert result[
        "transfer_verification_available"
    ] is False

    assert result[
        "networks"
    ] == []

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False

    assert result[
        "live_transfer_submitted"
    ] is False
