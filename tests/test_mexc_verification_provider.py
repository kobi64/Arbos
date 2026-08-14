import pytest

from exchanges.mexc_verification_provider import (
    MexcVerificationProvider,
)


class FakeClient:
    def fetch_currencies(self):
        return {
            "fetch_complete": True,
            "currencies": [
                {
                    "coin": "USDT",
                    "networkList": [
                        {
                            "coin": "USDT",
                            "network": "TRX",
                            "depositEnable": True,
                            "withdrawEnable": True,
                            "withdrawFee": "1",
                            "withdrawMin": "10",
                            "minConfirm": "20",
                            "contract": "TR7TEST",
                        },
                        {
                            "coin": "USDT",
                            "network": "ETH",
                            "depositEnable": True,
                            "withdrawEnable": False,
                            "withdrawFee": "5",
                            "withdrawMin": "20",
                            "minConfirm": "12",
                            "contract": "0xabc",
                        },
                    ],
                },
                {
                    "coin": "EMPTY",
                    "networkList": [],
                },
            ],
            "paper_only": True,
            "live_order_submitted": False,
            "live_transfer_submitted": False,
        }


class FakeNormalizer:
    def normalize(self, row):
        mapping = {
            "TRX": "TRC20",
            "ETH": "ERC20",
        }

        raw = row.get("network")

        return {
            "network": mapping.get(
                raw,
                raw,
            ),
            "raw_network": raw,
            "deposit_enabled": bool(
                row.get("depositEnable")
            ),
            "withdraw_enabled": bool(
                row.get("withdrawEnable")
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
                "contract"
            ),
        }


def build_provider():
    return MexcVerificationProvider(
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

    assert result[
        "networks"
    ][0][
        "network"
    ] == "TRC20"


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


def test_failed_metadata_fetch_is_fail_closed():
    class FailedClient:
        def fetch_currencies(self):
            return {
                "fetch_complete": False,
                "currencies": [],
                "reason": "credentials_unavailable",
                "paper_only": True,
                "live_order_submitted": False,
                "live_transfer_submitted": False,
            }

    provider = MexcVerificationProvider(
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
    ] == "credentials_unavailable"

    assert result[
        "network_metadata_available"
    ] is False

    assert result[
        "transfer_verification_available"
    ] is False

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False

    assert result[
        "live_transfer_submitted"
    ] is False
