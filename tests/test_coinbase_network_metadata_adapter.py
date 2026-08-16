import pytest

from exchanges.coinbase_network_metadata_adapter import (
    CoinbaseNetworkMetadataAdapter,
)


class FakeClient:
    def __init__(
        self,
        payload=None,
        error=None,
    ):
        self.payload = payload
        self.error = error
        self.calls = 0

    def fetch_currencies(self):
        self.calls += 1

        if self.error is not None:
            raise self.error

        return self.payload


def test_lists_supported_networks():
    client = FakeClient([
        {
            "id": "USDC",
            "status": "online",
            "default_network": "ethereum",
            "supported_networks": [
                {
                    "id": "ethereum",
                    "name": "Ethereum",
                    "status": "online",
                    "contract_address": (
                        "0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
                    ),
                    "min_withdrawal_amount": 1.0,
                    "max_withdrawal_amount": 1000000.0,
                    "network_confirmations": 14,
                    "processing_time_seconds": None,
                    "destination_tag_regex": None,
                    "is_evm_network": True,
                },
                {
                    "id": "solana",
                    "name": "Solana",
                    "status": "online",
                    "contract_address": (
                        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
                    ),
                    "min_withdrawal_amount": 1.0,
                    "max_withdrawal_amount": 1000000.0,
                    "network_confirmations": 20,
                    "processing_time_seconds": None,
                    "destination_tag_regex": None,
                    "is_evm_network": False,
                },
            ],
        }
    ])

    adapter = CoinbaseNetworkMetadataAdapter(
        client=client,
    )

    result = adapter.list_networks()

    assert result == [
        {
            "currency": "USDC",
            "network": "ethereum",
            "network_name": "Ethereum",
            "active": True,
            "default": True,
            "contract_address": (
                "0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
            ),
            "min_withdrawal": 1.0,
            "max_withdrawal": 1000000.0,
            "confirmations": 14,
            "processing_time_seconds": None,
            "destination_tag_regex": None,
            "is_evm": True,
        },
        {
            "currency": "USDC",
            "network": "solana",
            "network_name": "Solana",
            "active": True,
            "default": False,
            "contract_address": (
                "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            ),
            "min_withdrawal": 1.0,
            "max_withdrawal": 1000000.0,
            "confirmations": 20,
            "processing_time_seconds": None,
            "destination_tag_regex": None,
            "is_evm": False,
        },
    ]

    assert client.calls == 1


def test_filters_offline_currency():
    adapter = CoinbaseNetworkMetadataAdapter(
        client=FakeClient([
            {
                "id": "ABC",
                "status": "offline",
                "supported_networks": [
                    {
                        "id": "ethereum",
                        "name": "Ethereum",
                        "status": "online",
                    }
                ],
            }
        ])
    )

    assert adapter.list_networks() == []


def test_filters_offline_network():
    adapter = CoinbaseNetworkMetadataAdapter(
        client=FakeClient([
            {
                "id": "ABC",
                "status": "online",
                "supported_networks": [
                    {
                        "id": "ethereum",
                        "name": "Ethereum",
                        "status": "offline",
                    }
                ],
            }
        ])
    )

    assert adapter.list_networks() == []


def test_currency_filter_is_supported():
    adapter = CoinbaseNetworkMetadataAdapter(
        client=FakeClient([
            {
                "id": "BTC",
                "status": "online",
                "supported_networks": [],
            },
            {
                "id": "ETH",
                "status": "online",
                "default_network": "ethereum",
                "supported_networks": [
                    {
                        "id": "ethereum",
                        "name": "Ethereum",
                        "status": "online",
                    }
                ],
            },
        ])
    )

    result = adapter.list_networks(
        currency="eth"
    )

    assert len(result) == 1
    assert result[0]["currency"] == "ETH"


def test_invalid_payload_fails_closed():
    adapter = CoinbaseNetworkMetadataAdapter(
        client=FakeClient(
            payload=None,
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Coinbase currencies unavailable",
    ):
        adapter.list_networks()


def test_client_failure_is_wrapped():
    adapter = CoinbaseNetworkMetadataAdapter(
        client=FakeClient(
            error=RuntimeError(
                "network down"
            )
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Coinbase currencies unavailable",
    ):
        adapter.list_networks()


def test_requires_client():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        CoinbaseNetworkMetadataAdapter(
            client=None,
        )
