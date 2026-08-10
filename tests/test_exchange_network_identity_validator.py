import pytest

from exchanges.exchange_network_identity_validator import (
    ExchangeNetworkIdentityValidator,
)


def validator():
    return ExchangeNetworkIdentityValidator()


def test_matching_chain_ids_are_verified():
    result = validator().validate(
        coin="USDT",
        source_exchange="kucoin",
        destination_exchange="gate",
        source_network={
            "network": "TRC20",
            "chain_id": "tron",
            "withdraw": True,
        },
        destination_network={
            "network": "TRC20",
            "chain_id": "tron",
            "deposit": True,
        },
    )

    assert result["network_match"] == "VERIFIED"
    assert result["execution_allowed"] is True
    assert result["reason"] == "matching_chain_id"


def test_matching_contracts_are_verified_case_insensitively():
    result = validator().validate(
        coin="COTI",
        source_exchange="kucoin",
        destination_exchange="gate",
        source_network={
            "network": "ERC20",
            "contract_address": "0xABC123",
            "withdraw": True,
        },
        destination_network={
            "network": "ERC20",
            "contract_address": "0xabc123",
            "deposit": True,
        },
    )

    assert result["network_match"] == "VERIFIED"
    assert result["reason"] == (
        "matching_contract_address"
    )


def test_different_contracts_are_incompatible():
    result = validator().validate(
        coin="TOKEN",
        source_exchange="a",
        destination_exchange="b",
        source_network={
            "network": "ERC20",
            "contract_address": "0x111",
        },
        destination_network={
            "network": "ERC20",
            "contract_address": "0x222",
        },
    )

    assert result["network_match"] == "INCOMPATIBLE"
    assert result["execution_allowed"] is False
    assert result["reason"] == (
        "contract_address_mismatch"
    )


def test_different_chain_ids_are_incompatible():
    result = validator().validate(
        coin="COTI",
        source_exchange="a",
        destination_exchange="b",
        source_network={
            "network": "COTI",
            "chain_id": "cotievm",
        },
        destination_network={
            "network": "COTI",
            "chain_id": "other",
        },
    )

    assert result["network_match"] == "INCOMPATIBLE"
    assert result["reason"] == "chain_id_mismatch"


def test_matching_names_without_identity_are_unverified():
    result = validator().validate(
        coin="COTI",
        source_exchange="kucoin",
        destination_exchange="digifinex",
        source_network={
            "network": "COTI",
            "chain_id": "cotievm",
            "withdraw": True,
        },
        destination_network={
            "network": "COTI",
            "chain_id": "",
            "deposit": True,
        },
    )

    assert result["network_match"] == "UNVERIFIED"
    assert result["execution_allowed"] is False
    assert result["reason"] == (
        "insufficient_network_identity"
    )


def test_different_network_names_are_incompatible():
    result = validator().validate(
        coin="USDT",
        source_exchange="a",
        destination_exchange="b",
        source_network={
            "network": "TRC20",
        },
        destination_network={
            "network": "ERC20",
        },
    )

    assert result["network_match"] == "INCOMPATIBLE"
    assert result["execution_allowed"] is False


def test_source_withdraw_disabled_blocks():
    result = validator().validate(
        coin="COTI",
        source_exchange="kucoin",
        destination_exchange="digifinex",
        source_network={
            "network": "COTI",
            "chain_id": "cotievm",
            "withdraw": False,
        },
        destination_network={
            "network": "COTI",
            "chain_id": "cotievm",
            "deposit": True,
        },
    )

    assert result["execution_allowed"] is False
    assert result["reason"] == (
        "source_withdrawal_disabled"
    )


def test_destination_deposit_disabled_blocks():
    result = validator().validate(
        coin="COTI",
        source_exchange="kucoin",
        destination_exchange="digifinex",
        source_network={
            "network": "COTI",
            "chain_id": "cotievm",
            "withdraw": True,
        },
        destination_network={
            "network": "COTI",
            "chain_id": "cotievm",
            "deposit": False,
        },
    )

    assert result["execution_allowed"] is False
    assert result["reason"] == (
        "destination_deposit_disabled"
    )


def test_coti_live_metadata_shape_remains_unverified():
    result = validator().validate(
        coin="COTI",
        source_exchange="kucoin",
        destination_exchange="digifinex",
        source_network={
            "chain_name": "COTI",
            "chain_id": "cotievm",
            "contract_address": "",
            "withdraw": True,
            "deposit": True,
        },
        destination_network={
            "network": "COTI",
            "chain": "",
            "contract_address": "",
            "withdraw": True,
            "deposit": True,
        },
    )

    assert result["network_match"] == "UNVERIFIED"
    assert result["verified"] is False
    assert result["execution_allowed"] is False


def test_validator_never_submits_transfer_or_order():
    result = validator().validate(
        coin="USDT",
        source_exchange="a",
        destination_exchange="b",
        source_network={
            "network": "TRC20",
            "chain_id": "tron",
        },
        destination_network={
            "network": "TRC20",
            "chain_id": "tron",
        },
    )

    assert result["live_transfer_submitted"] is False
    assert result["live_order_submitted"] is False


def test_missing_coin_rejected():
    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        validator().validate(
            coin="",
            source_exchange="a",
            destination_exchange="b",
            source_network={},
            destination_network={},
        )


def test_missing_source_network_rejected():
    with pytest.raises(
        ValueError,
        match="source_network is required",
    ):
        validator().validate(
            coin="COTI",
            source_exchange="a",
            destination_exchange="b",
            source_network=None,
            destination_network={},
        )


def test_missing_destination_network_rejected():
    with pytest.raises(
        ValueError,
        match="destination_network is required",
    ):
        validator().validate(
            coin="COTI",
            source_exchange="a",
            destination_exchange="b",
            source_network={},
            destination_network=None,
        )
