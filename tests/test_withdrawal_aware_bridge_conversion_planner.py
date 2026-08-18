import pytest

from exchanges.network_registry import NetworkInfo
from core.withdrawal_aware_bridge_conversion_planner import (
    WithdrawalAwareBridgeConversionPlanner,
)


def withdrawable_coin_network():
    return NetworkInfo(
        coin="COINX",
        network="ERC20",
        withdraw_enabled=True,
        min_withdraw=1.0,
        withdraw_fee=0.1,
    )


def blocked_coin_network():
    return NetworkInfo(
        coin="COINX",
        network="ERC20",
        withdraw_enabled=False,
    )


def withdrawable_btc_network():
    return NetworkInfo(
        coin="BTC",
        network="BTC",
        withdraw_enabled=True,
        min_withdraw=0.0001,
        withdraw_fee=0.00001,
    )


def test_uses_direct_withdrawal_when_coin_is_transferable():
    planner = WithdrawalAwareBridgeConversionPlanner()

    result = planner.plan(
        coin="COINX",
        amount=100.0,
        coin_network=withdrawable_coin_network(),
        btc_network=withdrawable_btc_network(),
        spot_conversion_available=True,
        convert_quote_available=True,
    )

    assert result["route_type"] == "DIRECT_WITHDRAWAL"
    assert result["bridge_asset"] is None
    assert result["conversion_required"] is False


def test_uses_btc_spot_conversion_when_coin_withdrawal_unavailable():
    planner = WithdrawalAwareBridgeConversionPlanner()

    result = planner.plan(
        coin="COINX",
        amount=100.0,
        coin_network=blocked_coin_network(),
        btc_network=withdrawable_btc_network(),
        spot_conversion_available=True,
        convert_quote_available=True,
    )

    assert result["route_type"] == "SPOT_BRIDGE_CONVERSION"
    assert result["bridge_asset"] == "BTC"
    assert result["conversion_required"] is True
    assert result["conversion_method"] == "spot"


def test_uses_convert_swap_when_spot_conversion_unavailable():
    planner = WithdrawalAwareBridgeConversionPlanner()

    result = planner.plan(
        coin="COINX",
        amount=100.0,
        coin_network=blocked_coin_network(),
        btc_network=withdrawable_btc_network(),
        spot_conversion_available=False,
        convert_quote_available=True,
    )

    assert result["route_type"] == "CONVERT_SWAP_BRIDGE"
    assert result["bridge_asset"] == "BTC"
    assert result["conversion_method"] == "convert_swap"


def test_spot_bridge_requires_withdrawable_btc_network():
    planner = WithdrawalAwareBridgeConversionPlanner()

    blocked_btc = NetworkInfo(
        coin="BTC",
        network="BTC",
        withdraw_enabled=False,
    )

    result = planner.plan(
        coin="COINX",
        amount=100.0,
        coin_network=blocked_coin_network(),
        btc_network=blocked_btc,
        spot_conversion_available=True,
        convert_quote_available=False,
    )

    assert result["route_type"] == "REJECTED"
    assert result["reason"] == "no_transfer_or_conversion_path"


def test_convert_bridge_requires_withdrawable_btc_network():
    planner = WithdrawalAwareBridgeConversionPlanner()

    blocked_btc = NetworkInfo(
        coin="BTC",
        network="BTC",
        withdraw_enabled=False,
    )

    result = planner.plan(
        coin="COINX",
        amount=100.0,
        coin_network=blocked_coin_network(),
        btc_network=blocked_btc,
        spot_conversion_available=False,
        convert_quote_available=True,
    )

    assert result["route_type"] == "REJECTED"
    assert result["reason"] == "no_transfer_or_conversion_path"


@pytest.mark.parametrize(
    "flag_name",
    [
        "spot_conversion_available",
        "convert_quote_available",
    ],
)
@pytest.mark.parametrize(
    "flag_value",
    [
        None,
        0,
        1,
        "true",
        "false",
    ],
)
def test_conversion_availability_flags_require_real_booleans(
    flag_name,
    flag_value,
):
    planner = WithdrawalAwareBridgeConversionPlanner()

    kwargs = {
        "coin": "COINX",
        "amount": 100.0,
        "coin_network": blocked_coin_network(),
        "btc_network": withdrawable_btc_network(),
        "spot_conversion_available": False,
        "convert_quote_available": False,
    }
    kwargs[flag_name] = flag_value

    with pytest.raises(
        ValueError,
        match="conversion availability flags must be booleans",
    ):
        planner.plan(**kwargs)


def test_valid_btc_network_still_allows_spot_bridge():
    planner = WithdrawalAwareBridgeConversionPlanner()

    result = planner.plan(
        coin="COINX",
        amount=100.0,
        coin_network=blocked_coin_network(),
        btc_network=withdrawable_btc_network(),
        spot_conversion_available=True,
        convert_quote_available=False,
    )

    assert result["route_type"] == "SPOT_BRIDGE_CONVERSION"
    assert result["bridge_asset"] == "BTC"
    assert result["conversion_method"] == "spot"


def test_valid_btc_network_still_allows_convert_bridge():
    planner = WithdrawalAwareBridgeConversionPlanner()

    result = planner.plan(
        coin="COINX",
        amount=100.0,
        coin_network=blocked_coin_network(),
        btc_network=withdrawable_btc_network(),
        spot_conversion_available=False,
        convert_quote_available=True,
    )

    assert result["route_type"] == "CONVERT_SWAP_BRIDGE"
    assert result["bridge_asset"] == "BTC"
    assert result["conversion_method"] == "convert_swap"
