import pytest

from exchanges.kucoin_network_metadata_adapter import (
    KuCoinNetworkMetadataAdapter,
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
    adapter = KuCoinNetworkMetadataAdapter(
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
    adapter = KuCoinNetworkMetadataAdapter(
        client=FakeClient(),
    )

    assert adapter.get_networks(
        "USDT"
    ) == []


def test_coin_is_normalized():
    adapter = KuCoinNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        " usdt "
    )

    assert result["coin"] == "USDT"


def test_coin_is_required():
    adapter = KuCoinNetworkMetadataAdapter(
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
        KuCoinNetworkMetadataAdapter(
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

    adapter = KuCoinNetworkMetadataAdapter(
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

    adapter = KuCoinNetworkMetadataAdapter(
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

    adapter = KuCoinNetworkMetadataAdapter(
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


def test_public_currency_chains_use_network_info_contract():
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
                "withdraw": False,
            },
        ],
        "reason": None,
        "paper_only": True,
        "live_order_submitted": False,
        "live_transfer_submitted": False,
    })

    adapter = KuCoinNetworkMetadataAdapter(
        client=client,
    )

    networks = adapter.get_networks(
        "USDT"
    )

    assert len(networks) == 1
    assert networks[0].coin == "USDT"
    assert networks[0].network == "ETH"
    assert networks[0].deposit_enabled is True
    assert networks[0].withdraw_enabled is False


def test_public_kucoin_withdrawal_constraints_are_preserved():
    client = FakePublicClient({
        "fetch_complete": True,
        "currency": "BTC",
        "currencies": [
            {
                "asset": "BTC",
                "coin": "BTC",
                "network": "BSC",
                "chain": "BSC",
                "deposit": True,
                "withdraw": True,
                "raw": {
                    "withdrawMinSize": "0.000008",
                    "withdrawMinFee": "0.000004",
                    "withdrawFeeRate": "0",
                },
            },
        ],
        "reason": None,
    })

    network = (
        KuCoinNetworkMetadataAdapter(
            client=client,
        )
        .get_networks("BTC")[0]
    )

    assert network.min_withdraw == 0.000008
    assert network.withdraw_fee == 0.000004


def test_kucoin_legacy_withdrawal_field_names_are_supported():
    client = FakePublicClient({
        "fetch_complete": True,
        "currency": "ETH",
        "currencies": [
            {
                "asset": "ETH",
                "network": "ETH",
                "deposit": True,
                "withdraw": True,
                "raw": {
                    "withdrawalMinSize": "0.003",
                    "withdrawalMinFee": "0.0015",
                },
            },
        ],
        "reason": None,
    })

    network = (
        KuCoinNetworkMetadataAdapter(
            client=client,
        )
        .get_networks("ETH")[0]
    )

    assert network.min_withdraw == 0.003
    assert network.withdraw_fee == 0.0015


def test_kucoin_invalid_withdrawal_constraints_fail_closed():
    client = FakePublicClient({
        "fetch_complete": True,
        "currency": "USDT",
        "currencies": [
            {
                "asset": "USDT",
                "network": "KCC",
                "deposit": True,
                "withdraw": True,
                "raw": {
                    "withdrawMinSize": "invalid",
                    "withdrawMinFee": "-1",
                },
            },
        ],
        "reason": None,
    })

    network = (
        KuCoinNetworkMetadataAdapter(
            client=client,
        )
        .get_networks("USDT")[0]
    )

    assert network.min_withdraw is None
    assert network.withdraw_fee is None


def test_kucoin_zero_withdrawal_fee_is_valid():
    client = FakePublicClient({
        "fetch_complete": True,
        "currency": "USDT",
        "currencies": [
            {
                "asset": "USDT",
                "network": "KCC",
                "deposit": True,
                "withdraw": True,
                "raw": {
                    "withdrawMinSize": "1",
                    "withdrawMinFee": "0",
                },
            },
        ],
        "reason": None,
    })

    network = (
        KuCoinNetworkMetadataAdapter(
            client=client,
        )
        .get_networks("USDT")[0]
    )

    assert network.min_withdraw == 1.0
    assert network.withdraw_fee == 0.0
