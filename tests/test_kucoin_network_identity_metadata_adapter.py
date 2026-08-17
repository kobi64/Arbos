from exchanges.kucoin_network_identity_metadata_adapter import (
    KuCoinNetworkIdentityMetadataAdapter,
)


class FakeClient:
    def __init__(
        self,
        result,
    ):
        self.result = result
        self.calls = []

    def fetch_currency_chains(
        self,
        coin,
    ):
        self.calls.append(
            coin
        )
        return self.result


def test_contract_address_is_preserved_without_promoting_chain_label():
    client = FakeClient({
        "fetch_complete": True,
        "currencies": [
            {
                "asset": "USDT",
                "network": "BSC",
                "deposit": True,
                "withdraw": True,
                "raw": {
                    "chainId": "bsc",
                    "contractAddress": (
                        "0x55d398326f99059fF775485246999027B3197955"
                    ),
                },
            },
        ],
    })

    adapter = KuCoinNetworkIdentityMetadataAdapter(
        client
    )

    records = adapter.get_records(
        " usdt "
    )

    assert client.calls == ["USDT"]
    assert len(records) == 1
    assert records[0]["coin"] == "USDT"
    assert records[0]["network"] == "BSC"
    assert records[0]["chain_id"] is None
    assert records[0]["contract_address"] == (
        "0x55d398326f99059fF775485246999027B3197955"
    )
    assert records[0]["deposit"] is True
    assert records[0]["withdraw"] is True


def test_kucoin_chain_id_label_is_not_identity_proof():
    client = FakeClient({
        "fetch_complete": True,
        "currencies": [
            {
                "asset": "BTC",
                "network": "BTC",
                "deposit": True,
                "withdraw": True,
                "raw": {
                    "chainId": "btc",
                    "contractAddress": "",
                },
            },
        ],
    })

    records = (
        KuCoinNetworkIdentityMetadataAdapter(
            client
        ).get_records("BTC")
    )

    assert len(records) == 1
    assert records[0]["chain_id"] is None
    assert records[0]["contract_address"] is None


def test_failed_fetch_fails_closed():
    client = FakeClient({
        "fetch_complete": False,
        "reason": "offline",
        "currencies": [],
    })

    assert (
        KuCoinNetworkIdentityMetadataAdapter(
            client
        ).get_records("USDT")
        == []
    )


def test_invalid_coin_is_rejected():
    client = FakeClient({
        "fetch_complete": True,
        "currencies": [],
    })

    try:
        KuCoinNetworkIdentityMetadataAdapter(
            client
        ).get_records("")
        assert False
    except ValueError as exc:
        assert str(exc) == "coin is required"
