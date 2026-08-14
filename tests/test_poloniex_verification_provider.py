import pytest

from exchanges.poloniex_verification_provider import (
    PoloniexVerificationProvider,
)


class FakeClient:
    def fetch_currencies(self):
        return {
            "fetch_complete": True,
            "currencies": [
                {
                    "id": 1,
                    "coin": "USDT",
                    "delisted": False,
                    "tradeEnable": True,
                    "name": "Tether",
                    "networkList": [
                        {
                            "coin": "USDTTRON",
                            "name": "Tron",
                            "blockchain": "TRX",
                            "withdrawalEnable": True,
                            "depositEnable": True,
                            "withdrawMin": "10",
                            "withdrawFee": "1",
                            "minConfirm": 20,
                            "contractAddress": (
                                "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
                            ),
                        },
                        {
                            "coin": "USDTERC20",
                            "name": "Ethereum",
                            "blockchain": "ETH",
                            "withdrawalEnable": False,
                            "depositEnable": True,
                            "withdrawMin": "20",
                            "withdrawFee": "5",
                            "minConfirm": 12,
                            "contractAddress": (
                                "0xdac17f958d2ee523a2206206994597c13d831ec7"
                            ),
                        },
                    ],
                },
                {
                    "id": 2,
                    "coin": "EMPTY",
                    "delisted": False,
                    "tradeEnable": True,
                    "name": "Empty",
                    "networkList": [],
                },
            ],
            "paper_only": True,
            "live_order_submitted": False,
        }


class FakeNormalizer:
    def normalize(self, row):
        blockchain = row.get("blockchain")

        mapping = {
            "TRX": "TRC20",
            "ETH": "ERC20",
        }

        return {
            "network": mapping.get(
                blockchain,
                blockchain,
            ),
            "raw_network": blockchain,
            "network_name": row.get("name"),
            "deposit_enabled": bool(
                row.get("depositEnable")
            ),
            "withdraw_enabled": bool(
                row.get("withdrawalEnable")
            ),
            "withdraw_fee": float(
                row.get("withdrawFee")
            ),
            "min_withdraw": float(
                row.get("withdrawMin")
            ),
            "confirmations": int(
                row.get("minConfirm")
            ),
            "contract_address": row.get(
                "contractAddress"
            ),
        }


def build_provider():
    return PoloniexVerificationProvider(
        client=FakeClient(),
        normalizer=FakeNormalizer(),
    )


def test_get_coin_returns_normalized_networks():
    provider = build_provider()

    result = provider.get_coin(
        "USDT"
    )

    assert result[
        "available"
    ] is True

    assert result[
        "coin"
    ] == "USDT"

    assert result[
        "network_metadata_available"
    ] is True

    assert result[
        "transfer_verification_available"
    ] is True

    assert len(
        result["networks"]
    ) == 2

    trc20 = result[
        "networks"
    ][0]

    assert trc20[
        "network"
    ] == "TRC20"

    assert trc20[
        "contract_address"
    ] is not None


def test_disabled_withdrawal_is_preserved():
    provider = build_provider()

    result = provider.get_coin(
        "USDT"
    )

    erc20 = next(
        item
        for item in result[
            "networks"
        ]
        if item["network"]
        == "ERC20"
    )

    assert erc20[
        "deposit_enabled"
    ] is True

    assert erc20[
        "withdraw_enabled"
    ] is False


def test_empty_network_list_is_explicit():
    provider = build_provider()

    result = provider.get_coin(
        "EMPTY"
    )

    assert result[
        "available"
    ] is True

    assert result[
        "network_metadata_available"
    ] is False

    assert result[
        "network_metadata_reason"
    ] == "empty_network_list"

    assert result[
        "transfer_verification_available"
    ] is False

    assert result[
        "networks"
    ] == []


def test_unknown_coin_is_unavailable():
    provider = build_provider()

    result = provider.get_coin(
        "UNKNOWN"
    )

    assert result[
        "available"
    ] is False

    assert result[
        "reason"
    ] == "coin_not_found"


def test_coin_is_required():
    provider = build_provider()

    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        provider.get_coin("")


def test_failed_currency_fetch_is_fail_closed():
    class FailedClient:
        def fetch_currencies(self):
            return {
                "fetch_complete": False,
                "currencies": [],
                "reason": "request_failed",
            }

    provider = PoloniexVerificationProvider(
        client=FailedClient(),
        normalizer=FakeNormalizer(),
    )

    result = provider.get_coin(
        "USDT"
    )

    assert result[
        "available"
    ] is False

    assert result[
        "reason"
    ] == "request_failed"

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False
