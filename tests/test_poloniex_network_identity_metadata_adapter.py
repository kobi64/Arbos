import pytest

from exchanges.poloniex_network_identity_metadata_adapter import (
    PoloniexNetworkIdentityMetadataAdapter,
)


class FakeProvider:
    def get_coin(
        self,
        coin,
    ):
        if coin == "UNKNOWN":
            return {
                "exchange": "poloniex",
                "coin": coin,
                "available": False,
                "reason": "coin_not_found",
                "networks": [],
            }

        return {
            "exchange": "poloniex",
            "coin": coin,
            "available": True,
            "networks": [
                {
                    "network": "TRC20",
                    "raw_network": "TRX",
                    "network_name": "Tron",
                    "deposit_enabled": True,
                    "withdraw_enabled": True,
                    "withdraw_fee": 1.0,
                    "min_withdraw": 10.0,
                    "confirmations": 20,
                    "contract_address": (
                        "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
                    ),
                },
                {
                    "network": "ERC20",
                    "raw_network": "ETH",
                    "network_name": "Ethereum",
                    "deposit_enabled": True,
                    "withdraw_enabled": False,
                    "withdraw_fee": 5.0,
                    "min_withdraw": 20.0,
                    "confirmations": 12,
                    "contract_address": (
                        "0xdac17f958d2ee523a2206206994597c13d831ec7"
                    ),
                },
            ],
        }


def test_returns_identity_records():
    adapter = (
        PoloniexNetworkIdentityMetadataAdapter(
            provider=FakeProvider(),
        )
    )

    records = adapter.get_records(
        "USDT"
    )

    assert len(records) == 2

    trc20 = next(
        record
        for record in records
        if record["network"] == "TRC20"
    )

    assert trc20["coin"] == "USDT"

    assert trc20[
        "network_name"
    ] == "TRC20"

    assert trc20[
        "contract_address"
    ] == (
        "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
    )

    assert trc20[
        "deposit"
    ] is True

    assert trc20[
        "withdraw"
    ] is True


def test_does_not_invent_chain_id():
    adapter = (
        PoloniexNetworkIdentityMetadataAdapter(
            provider=FakeProvider(),
        )
    )

    records = adapter.get_records(
        "USDT"
    )

    trc20 = next(
        record
        for record in records
        if record["network"] == "TRC20"
    )

    assert trc20[
        "chain_id"
    ] is None


def test_disabled_withdrawal_is_preserved():
    adapter = (
        PoloniexNetworkIdentityMetadataAdapter(
            provider=FakeProvider(),
        )
    )

    records = adapter.get_records(
        "USDT"
    )

    erc20 = next(
        record
        for record in records
        if record["network"] == "ERC20"
    )

    assert erc20[
        "withdraw"
    ] is False

    assert erc20[
        "deposit"
    ] is True


def test_unknown_coin_returns_empty_list():
    adapter = (
        PoloniexNetworkIdentityMetadataAdapter(
            provider=FakeProvider(),
        )
    )

    assert adapter.get_records(
        "UNKNOWN"
    ) == []


def test_coin_is_required():
    adapter = (
        PoloniexNetworkIdentityMetadataAdapter(
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
        PoloniexNetworkIdentityMetadataAdapter(
            provider=None,
        )
