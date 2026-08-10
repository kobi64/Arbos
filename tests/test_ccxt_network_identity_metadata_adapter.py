import pytest

from exchanges.ccxt_network_identity_metadata_adapter import (
    CCXTNetworkIdentityMetadataAdapter,
)


class FakeExchange:
    def load_currencies(self):
        return {
            "COTI": {
                "code": "COTI",
                "deposit": True,
                "withdraw": True,
                "networks": {
                    "COTI": {
                        "deposit": True,
                        "withdraw": True,
                        "fee": 150.0,
                        "info": {
                            "chainName": "COTI",
                            "chainId": "cotievm",
                            "contractAddress": "",
                        },
                    },
                    "ERC20": {
                        "deposit": True,
                        "withdraw": False,
                        "fee": 150.0,
                        "info": {
                            "chainName": "ERC20",
                            "chainId": "eth",
                            "contractAddress": (
                                "0xddb3422497e61e13543bea06989c0789117555c5"
                            ),
                        },
                    },
                },
            },
        }


class FetchCurrenciesExchange:
    def fetch_currencies(self):
        return {
            "USDT": {
                "code": "USDT",
                "deposit": True,
                "withdraw": True,
                "networks": {
                    "TRC20": {
                        "deposit": True,
                        "withdraw": True,
                        "fee": 1.0,
                        "info": {
                            "chainId": "tron",
                        },
                    },
                },
            },
        }


class LoadMarketsFallbackExchange:
    def __init__(self):
        self.currencies = {}

    def load_markets(self):
        self.currencies = {
            "BTC": {
                "code": "BTC",
                "deposit": True,
                "withdraw": True,
                "networks": {
                    "BTC": {
                        "deposit": True,
                        "withdraw": True,
                        "fee": 0.0001,
                        "info": {
                            "chainId": "bitcoin",
                        },
                    },
                },
            },
        }
        return {}


def test_extracts_chain_identity():
    adapter = CCXTNetworkIdentityMetadataAdapter(
        FakeExchange()
    )

    records = adapter.get_records("COTI")

    coti = next(
        record
        for record in records
        if record["network"] == "COTI"
    )

    assert coti["chain_id"] == "cotievm"
    assert coti["withdraw"] is True
    assert coti["deposit"] is True
    assert coti["withdraw_fee"] == 150.0


def test_extracts_contract_address():
    records = (
        CCXTNetworkIdentityMetadataAdapter(
            FakeExchange()
        ).get_records("COTI")
    )

    erc20 = next(
        record
        for record in records
        if record["network"] == "ERC20"
    )

    assert erc20["chain_id"] == "eth"
    assert erc20["contract_address"] == (
        "0xddb3422497e61e13543bea06989c0789117555c5"
    )


def test_supports_fetch_currencies():
    adapter = CCXTNetworkIdentityMetadataAdapter(
        FetchCurrenciesExchange()
    )

    records = adapter.get_records("USDT")

    assert len(records) == 1
    assert records[0]["network"] == "TRC20"
    assert records[0]["chain_id"] == "tron"


def test_supports_load_markets_fallback():
    adapter = CCXTNetworkIdentityMetadataAdapter(
        LoadMarketsFallbackExchange()
    )

    records = adapter.get_records("BTC")

    assert len(records) == 1
    assert records[0]["chain_id"] == "bitcoin"


def test_unknown_coin_returns_empty_list():
    adapter = CCXTNetworkIdentityMetadataAdapter(
        FakeExchange()
    )

    assert adapter.get_records("UNKNOWN") == []


def test_missing_coin_is_rejected():
    adapter = CCXTNetworkIdentityMetadataAdapter(
        FakeExchange()
    )

    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        adapter.get_records("")


def test_missing_exchange_is_rejected():
    with pytest.raises(
        ValueError,
        match="exchange is required",
    ):
        CCXTNetworkIdentityMetadataAdapter(
            None
        )
