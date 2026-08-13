import pytest

from exchanges.weex_verification_adapter import (
    WeexVerificationAdapter,
)


def test_normalizes_order_book():
    adapter = WeexVerificationAdapter()

    result = adapter.normalize_depth(
        {
            "fetch_complete": True,
            "symbol": "COTIUSDT",
            "last_update_id": 123,
            "bids": [
                ["0.1000", "100"],
                ["0.0990", "200"],
            ],
            "asks": [
                ["0.1010", "50"],
                ["0.1020", "150"],
            ],
        }
    )

    assert result["exchange"] == "weex"
    assert result["symbol"] == "COTIUSDT"

    assert result["best_bid"] == 0.1000
    assert result["best_ask"] == 0.1010

    assert result["bids"][0] == {
        "price": 0.1000,
        "quantity": 100.0,
    }

    assert result["asks"][0] == {
        "price": 0.1010,
        "quantity": 50.0,
    }


def test_failed_depth_is_not_treated_as_valid():
    adapter = WeexVerificationAdapter()

    result = adapter.normalize_depth(
        {
            "fetch_complete": False,
            "reason": "request_failed",
        }
    )

    assert result["available"] is False
    assert result["reason"] == "request_failed"


def test_normalizes_coin_network_metadata():
    adapter = WeexVerificationAdapter()

    result = adapter.normalize_coin(
        {
            "coin": "COTI",
            "depositAllEnable": True,
            "withdrawAllEnable": True,
            "networkList": [
                {
                    "network": "ERC20",
                    "isDefault": True,
                    "depositEnable": True,
                    "withdrawEnable": True,
                    "withdrawFee": "10",
                    "withdrawMin": "20",
                    "withdrawIntegerMultiple": "1",
                    "minConfirm": 12,
                },
            ],
        }
    )

    assert result["exchange"] == "weex"
    assert result["coin"] == "COTI"

    assert result[
        "deposit_enabled"
    ] is True

    assert result[
        "withdraw_enabled"
    ] is True

    network = result["networks"][0]

    assert network["network"] == "ERC20"
    assert network["deposit_enabled"] is True
    assert network["withdraw_enabled"] is True
    assert network["withdraw_fee"] == 10.0
    assert network["withdraw_min"] == 20.0
    assert network["min_confirmations"] == 12


def test_disabled_network_is_preserved():
    adapter = WeexVerificationAdapter()

    result = adapter.normalize_coin(
        {
            "coin": "TEST",
            "depositAllEnable": False,
            "withdrawAllEnable": False,
            "networkList": [
                {
                    "network": "ERC20",
                    "depositEnable": False,
                    "withdrawEnable": False,
                    "withdrawFee": "1",
                    "withdrawMin": "5",
                },
            ],
        }
    )

    network = result["networks"][0]

    assert network[
        "deposit_enabled"
    ] is False

    assert network[
        "withdraw_enabled"
    ] is False


def test_coin_is_required():
    adapter = WeexVerificationAdapter()

    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        adapter.normalize_coin(
            {
                "networkList": [],
            }
        )


def test_invalid_network_list_is_rejected():
    adapter = WeexVerificationAdapter()

    with pytest.raises(
        ValueError,
        match="networkList must be a list",
    ):
        adapter.normalize_coin(
            {
                "coin": "COTI",
                "networkList": {},
            }
        )


def test_adapter_is_paper_safe():
    adapter = WeexVerificationAdapter()

    result = adapter.normalize_coin(
        {
            "coin": "COTI",
            "depositAllEnable": True,
            "withdrawAllEnable": True,
            "networkList": [],
        }
    )

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False


def test_network_names_are_canonicalized():
    from exchanges.weex_network_normalizer import (
        WeexNetworkNormalizer,
    )

    adapter = WeexVerificationAdapter(
        network_normalizer=(
            WeexNetworkNormalizer()
        )
    )

    result = adapter.normalize_coin(
        {
            "coin": "USDT",
            "depositAllEnable": True,
            "withdrawAllEnable": True,
            "networkList": [
                {
                    "network": "Tron (TRC20)",
                    "depositEnable": True,
                    "withdrawEnable": True,
                    "withdrawFee": "1.5",
                    "withdrawMin": "10",
                    "minConfirm": 20,
                },
                {
                    "network": "Ethereum (ETH)",
                    "depositEnable": True,
                    "withdrawEnable": True,
                    "withdrawFee": "1",
                    "withdrawMin": "20",
                    "minConfirm": 12,
                },
            ],
        }
    )

    assert result[
        "networks"
    ][0][
        "network"
    ] == "TRC20"

    assert result[
        "networks"
    ][1][
        "network"
    ] == "ERC20"


def test_raw_network_name_is_preserved():
    from exchanges.weex_network_normalizer import (
        WeexNetworkNormalizer,
    )

    adapter = WeexVerificationAdapter(
        network_normalizer=(
            WeexNetworkNormalizer()
        )
    )

    result = adapter.normalize_coin(
        {
            "coin": "USDT",
            "depositAllEnable": True,
            "withdrawAllEnable": True,
            "networkList": [
                {
                    "network": (
                        "Arbitrum One (ARB)"
                    ),
                    "depositEnable": True,
                    "withdrawEnable": True,
                },
            ],
        }
    )

    network = result[
        "networks"
    ][0]

    assert network[
        "network"
    ] == "ARBITRUM"

    assert network[
        "raw_network"
    ] == (
        "Arbitrum One (ARB)"
    )


def test_network_normalizer_is_optional():
    adapter = WeexVerificationAdapter()

    result = adapter.normalize_coin(
        {
            "coin": "COTI",
            "depositAllEnable": True,
            "withdrawAllEnable": True,
            "networkList": [
                {
                    "network": "ERC20",
                    "depositEnable": True,
                    "withdrawEnable": True,
                },
            ],
        }
    )

    assert result[
        "networks"
    ][0][
        "network"
    ] == "ERC20"
