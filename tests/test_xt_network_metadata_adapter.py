import pytest

from exchanges.xt_network_metadata_adapter import (
    XTNetworkMetadataAdapter,
)


class FakeClient:
    def fetch(self):
        return {
            "exchange_id": "xt",
            "fetch_complete": True,
            "reason": None,
            "currencies": [
                {
                    "currency": "usdt",
                    "supportChains": [
                        {
                            "chain": "Tron",
                            "depositEnabled": True,
                            "withdrawEnabled": True,
                            "contract": (
                                "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
                            ),
                            "depositMinAmount": 0.1,
                            "depositFeeRate": 0,
                            "depositConfirmations": 3,
                            "withdrawMinAmount": 10,
                            "withdrawPrecision": 6,
                            "withdrawFeeAmount": 1,
                            "withdrawFeeCurrency": "usdt",
                            "withdrawFeeCurrencyId": 11,
                        },
                        {
                            "chain": "Ethereum",
                            "depositEnabled": True,
                            "withdrawEnabled": False,
                            "contract": (
                                "0xdac17f958d2ee523a2206206994597c13d831ec7"
                            ),
                            "depositMinAmount": 0,
                            "depositFeeRate": 0,
                            "depositConfirmations": 12,
                            "withdrawMinAmount": 10,
                            "withdrawPrecision": 6,
                            "withdrawFeeAmount": 2,
                            "withdrawFeeCurrency": "usdt",
                            "withdrawFeeCurrencyId": 11,
                        },
                    ],
                },
            ],
            "read_only": True,
            "paper_only": True,
            "live_order_submitted": False,
            "live_transfer_submitted": False,
        }


class FailedClient:
    def fetch(self):
        return {
            "exchange_id": "xt",
            "fetch_complete": False,
            "reason": "exchange_error",
            "currencies": [],
            "read_only": True,
            "paper_only": True,
            "live_order_submitted": False,
            "live_transfer_submitted": False,
        }


def test_client_is_required():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        XTNetworkMetadataAdapter(
            client=None,
        )


def test_describes_xt_networks():
    adapter = XTNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        "USDT"
    )

    assert result[
        "network_metadata_available"
    ] is True

    assert result[
        "transfer_verification_available"
    ] is True

    assert len(
        result["networks"]
    ) == 2

    tron = result["networks"][0]

    assert tron[
        "network"
    ] == "Tron"

    assert tron[
        "deposit_enabled"
    ] is True

    assert tron[
        "withdraw_enabled"
    ] is True

    assert tron[
        "deposit_confirmations"
    ] == 3

    assert tron[
        "minimum_deposit"
    ] == 0.1

    assert tron[
        "minimum_withdrawal"
    ] == 10.0

    assert tron[
        "withdraw_fee"
    ] == 1.0

    assert tron[
        "withdraw_fee_currency"
    ] == "USDT"


def test_contract_metadata_is_preserved():
    adapter = XTNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        "USDT"
    )

    tron = result[
        "networks"
    ][0]

    assert tron[
        "contract_address"
    ] == (
        "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
    )


def test_disabled_withdrawal_is_preserved():
    adapter = XTNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        "USDT"
    )

    ethereum = result[
        "networks"
    ][1]

    assert ethereum[
        "deposit_enabled"
    ] is True

    assert ethereum[
        "withdraw_enabled"
    ] is False


def test_coin_is_normalized():
    adapter = XTNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        " usdt "
    )

    assert result["coin"] == "USDT"


def test_unknown_coin_returns_available_empty_metadata():
    adapter = XTNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        "XYZ"
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


def test_failed_fetch_fails_closed():
    adapter = XTNetworkMetadataAdapter(
        client=FailedClient(),
    )

    result = adapter.describe_networks(
        "USDT"
    )

    assert result[
        "network_metadata_available"
    ] is False

    assert result[
        "transfer_verification_available"
    ] is False

    assert result[
        "networks"
    ] == []


def test_coin_is_required():
    adapter = XTNetworkMetadataAdapter(
        client=FakeClient(),
    )

    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        adapter.describe_networks("")
