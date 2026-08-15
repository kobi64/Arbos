import pytest

from exchanges.lbank_network_identity_metadata_adapter import (
    LBankNetworkIdentityMetadataAdapter,
)


class FakeProvider:
    def get_coin(
        self,
        coin,
    ):
        if coin == "UNKNOWN":
            return {
                "exchange": "lbank",
                "coin": coin,
                "available": True,
                "networks": [],
            }

        return {
            "exchange": "lbank",
            "coin": coin,
            "available": True,
            "networks": [
                {
                    "asset": "USDT",
                    "network": "ETH",
                    "raw_network": "erc20",
                    "deposit_enabled": True,
                    "withdraw_enabled": True,
                    "withdraw_fee": 1.0,
                    "min_withdraw": 10.0,
                    "min_deposit": 0.0001,
                    "contract_address": (
                        "0xdac17f958d2ee523a2206206994597c13d831ec7"
                    ),
                    "memo_required": False,
                },
                {
                    "asset": "LUNC",
                    "network": "LUNC",
                    "raw_network": "terra classic",
                    "deposit_enabled": True,
                    "withdraw_enabled": True,
                    "withdraw_fee": 15000.0,
                    "min_withdraw": 30000.0,
                    "min_deposit": 0.0001,
                    "contract_address": None,
                    "memo_required": True,
                },
            ],
        }


def test_returns_identity_records():
    adapter = (
        LBankNetworkIdentityMetadataAdapter(
            provider=FakeProvider(),
        )
    )

    records = adapter.get_records(
        "USDT"
    )

    assert len(records) == 2

    eth = next(
        record
        for record in records
        if record["network"] == "ETH"
    )

    assert eth["coin"] == "USDT"
    assert eth["network_name"] == "ETH"

    assert eth["contract_address"] == (
        "0xdac17f958d2ee523a2206206994597c13d831ec7"
    )

    assert eth["deposit"] is True
    assert eth["withdraw"] is True


def test_does_not_invent_chain_id():
    adapter = (
        LBankNetworkIdentityMetadataAdapter(
            provider=FakeProvider(),
        )
    )

    records = adapter.get_records(
        "USDT"
    )

    assert all(
        record["chain_id"] is None
        for record in records
    )


def test_preserves_missing_contract_identity():
    adapter = (
        LBankNetworkIdentityMetadataAdapter(
            provider=FakeProvider(),
        )
    )

    records = adapter.get_records(
        "USDT"
    )

    lunc = next(
        record
        for record in records
        if record["network"] == "LUNC"
    )

    assert lunc[
        "contract_address"
    ] is None

    assert lunc[
        "raw_info"
    ][
        "memo_required"
    ] is True


def test_unknown_coin_returns_empty_list():
    adapter = (
        LBankNetworkIdentityMetadataAdapter(
            provider=FakeProvider(),
        )
    )

    assert adapter.get_records(
        "UNKNOWN"
    ) == []


def test_coin_is_required():
    adapter = (
        LBankNetworkIdentityMetadataAdapter(
            provider=FakeProvider(),
        )
    )

    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        adapter.get_records("")


def test_provider_is_required():
    with pytest.raises(
        ValueError,
        match="provider is required",
    ):
        LBankNetworkIdentityMetadataAdapter(
            provider=None,
        )
