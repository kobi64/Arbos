import pytest

from exchanges.gateio_network_metadata_adapter import (
    GateIONetworkMetadataAdapter,
)


class FakeClient:
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
    adapter = GateIONetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        "USDT"
    )

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


def test_get_networks_returns_empty_list():
    adapter = GateIONetworkMetadataAdapter(
        client=FakeClient(),
    )

    assert adapter.get_networks(
        "USDT"
    ) == []


def test_coin_is_normalized():
    adapter = GateIONetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        " usdt "
    )

    assert result["coin"] == "USDT"


def test_coin_is_required():
    adapter = GateIONetworkMetadataAdapter(
        client=FakeClient(),
    )

    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        adapter.describe_networks("")


def test_client_is_required():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        GateIONetworkMetadataAdapter(
            client=None,
        )


class FakePublicClient:
    def __init__(
        self,
        result,
    ):
        self.result = result
        self.calls = []

    def fetch_currency_chains(
        self,
        currency,
    ):
        self.calls.append(
            currency
        )

        return self.result


def test_public_currency_chains_enable_transfer_verification():
    client = FakePublicClient({
        "fetch_complete": True,
        "currency": "USDT",
        "currencies": [
            {
                "asset": "USDT",
                "coin": "USDT",
                "network": "ETH",
                "chain": "ETH",
                "deposit": True,
                "withdraw": True,
            },
            {
                "asset": "USDT",
                "coin": "USDT",
                "network": "TRX",
                "chain": "TRX",
                "deposit": True,
                "withdraw": False,
            },
        ],
        "reason": None,
        "paper_only": True,
        "live_order_submitted": False,
        "live_transfer_submitted": False,
    })

    adapter = GateIONetworkMetadataAdapter(
        client=client,
    )

    result = adapter.describe_networks(
        " usdt "
    )

    assert client.calls == [
        "USDT",
    ]

    assert result[
        "network_metadata_available"
    ] is True

    assert result[
        "network_metadata_reason"
    ] is None

    assert result[
        "transfer_verification_available"
    ] is True

    assert len(
        result["networks"]
    ) == 2

    assert result[
        "networks"
    ][0].network == "ETH"

    assert result[
        "networks"
    ][0].deposit_enabled is True

    assert result[
        "networks"
    ][0].withdraw_enabled is True


def test_public_currency_chain_failure_fails_closed():
    client = FakePublicClient({
        "fetch_complete": False,
        "currency": "USDT",
        "currencies": [],
        "reason": "RuntimeError: offline",
        "paper_only": True,
        "live_order_submitted": False,
        "live_transfer_submitted": False,
    })

    adapter = GateIONetworkMetadataAdapter(
        client=client,
    )

    result = adapter.describe_networks(
        "USDT"
    )

    assert result[
        "network_metadata_available"
    ] is False

    assert result[
        "network_metadata_reason"
    ] == "RuntimeError: offline"

    assert result[
        "transfer_verification_available"
    ] is False

    assert result[
        "networks"
    ] == []


def test_public_empty_currency_chains_do_not_verify_transfer():
    client = FakePublicClient({
        "fetch_complete": True,
        "currency": "USDT",
        "currencies": [],
        "reason": None,
        "paper_only": True,
        "live_order_submitted": False,
        "live_transfer_submitted": False,
    })

    adapter = GateIONetworkMetadataAdapter(
        client=client,
    )

    result = adapter.describe_networks(
        "USDT"
    )

    assert result[
        "network_metadata_available"
    ] is True

    assert result[
        "transfer_verification_available"
    ] is False

    assert result[
        "networks"
    ] == []


def test_public_gate_minimum_withdrawal_is_preserved():
    client = FakePublicClient({
        "fetch_complete": True,
        "currency": "BTC",
        "currencies": [
            {
                "asset": "BTC",
                "coin": "BTC",
                "network": "BTC",
                "chain": "BTC",
                "deposit": True,
                "withdraw": True,
                "raw": {
                    "withdraw_amount_min": "0.0005",
                },
            },
        ],
        "reason": None,
    })

    network = (
        GateIONetworkMetadataAdapter(
            client=client,
        )
        .get_networks("BTC")[0]
    )

    assert network.min_withdraw == 0.0005

    # Gate public chain metadata currently does not
    # expose a trustworthy withdrawal-fee field.
    assert network.withdraw_fee is None


def test_gate_invalid_minimum_withdrawal_fails_closed():
    client = FakePublicClient({
        "fetch_complete": True,
        "currency": "USDT",
        "currencies": [
            {
                "asset": "USDT",
                "network": "ETH",
                "deposit": True,
                "withdraw": True,
                "raw": {
                    "withdraw_amount_min": "invalid",
                },
            },
        ],
        "reason": None,
    })

    network = (
        GateIONetworkMetadataAdapter(
            client=client,
        )
        .get_networks("USDT")[0]
    )

    assert network.min_withdraw is None


def test_gate_negative_minimum_withdrawal_is_not_accepted():
    client = FakePublicClient({
        "fetch_complete": True,
        "currency": "USDT",
        "currencies": [
            {
                "asset": "USDT",
                "network": "ETH",
                "deposit": True,
                "withdraw": True,
                "raw": {
                    "withdraw_amount_min": "-1",
                },
            },
        ],
        "reason": None,
    })

    network = (
        GateIONetworkMetadataAdapter(
            client=client,
        )
        .get_networks("USDT")[0]
    )

    assert network.min_withdraw is None
