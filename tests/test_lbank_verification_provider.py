import pytest

from exchanges.lbank_verification_provider import (
    LBankVerificationProvider,
)


class FakeClient:
    def fetch_asset_metadata(
        self,
        asset,
    ):
        if asset == "UNKNOWN":
            return {
                "fetch_complete": True,
                "asset": asset,
                "networks": [],
                "reason": None,
                "paper_only": True,
                "live_order_submitted": False,
                "live_transfer_submitted": False,
            }

        return {
            "fetch_complete": True,
            "asset": asset,
            "networks": [
                {
                    "assetCode": "usdt",
                    "chainName": "erc20",
                    "canDeposit": True,
                    "canDraw": True,
                    "canStationDraw": True,
                    "contractInfo": (
                        "0xdac17f958d2ee523a2206206994597c13d831ec7"
                    ),
                    "hasMemo": False,
                    "assetFee": {
                        "feeAmt": "1",
                        "minAmt": "10",
                        "minDepositAmt": "0.0001",
                    },
                },
            ],
            "reason": None,
            "paper_only": True,
            "live_order_submitted": False,
            "live_transfer_submitted": False,
        }


class FakeNormalizer:
    def normalize_record(
        self,
        record,
    ):
        if not record:
            return None

        return {
            "asset": "USDT",
            "network": "ETH",
            "raw_network": "erc20",
            "deposit_enabled": True,
            "withdraw_enabled": True,
            "station_withdraw_enabled": True,
            "contract_address": (
                "0xdac17f958d2ee523a2206206994597c13d831ec7"
            ),
            "memo_required": False,
            "withdraw_fee": 1.0,
            "min_withdraw": 10.0,
            "min_deposit": 0.0001,
        }


def build_provider():
    return LBankVerificationProvider(
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
    ) == 1

    assert result[
        "networks"
    ][0][
        "network"
    ] == "ETH"


def test_contract_identity_is_preserved():
    provider = build_provider()

    result = provider.get_coin(
        "USDT"
    )

    assert result[
        "networks"
    ][0][
        "contract_address"
    ] == (
        "0xdac17f958d2ee523a2206206994597c13d831ec7"
    )


def test_empty_network_list_is_explicit():
    provider = build_provider()

    result = provider.get_coin(
        "UNKNOWN"
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


def test_coin_is_required():
    provider = build_provider()

    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        provider.get_coin("")


def test_failed_metadata_fetch_is_fail_closed():
    class FailedClient:
        def fetch_asset_metadata(
            self,
            asset,
        ):
            return {
                "fetch_complete": False,
                "asset": asset,
                "networks": [],
                "reason": "request_failed",
                "paper_only": True,
                "live_order_submitted": False,
                "live_transfer_submitted": False,
            }

    provider = LBankVerificationProvider(
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
