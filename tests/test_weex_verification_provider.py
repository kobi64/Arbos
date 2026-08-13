import pytest

from exchanges.weex_verification_provider import (
    WeexVerificationProvider,
)


class FakeClient:
    def fetch_depth(
        self,
        symbol,
        limit=200,
    ):
        return {
            "fetch_complete": True,
            "symbol": symbol,
            "last_update_id": 123,
            "bids": [
                ["0.1000", "100"],
            ],
            "asks": [
                ["0.1010", "50"],
            ],
        }

    def fetch_coins(self):
        return {
            "fetch_complete": True,
            "coins": [
                {
                    "coin": "COTI",
                    "depositAllEnable": True,
                    "withdrawAllEnable": True,
                    "networkList": [
                        {
                            "network": "ERC20",
                            "depositEnable": True,
                            "withdrawEnable": True,
                            "withdrawFee": "10",
                            "withdrawMin": "20",
                            "minConfirm": 12,
                        },
                        {
                            "network": "BEP20",
                            "depositEnable": False,
                            "withdrawEnable": True,
                            "withdrawFee": "1",
                            "withdrawMin": "5",
                            "minConfirm": 15,
                        },
                    ],
                },
            ],
        }


class FakeAdapter:
    def normalize_depth(
        self,
        depth,
    ):
        return {
            "exchange": "weex",
            "available": True,
            "symbol": depth["symbol"],
            "best_bid": 0.1000,
            "best_ask": 0.1010,
            "paper_only": True,
            "live_order_submitted": False,
        }

    def normalize_coin(
        self,
        coin_data,
    ):
        return {
            "exchange": "weex",
            "coin": coin_data["coin"],
            "deposit_enabled": True,
            "withdraw_enabled": True,
            "networks": [
                {
                    "network": "ERC20",
                    "deposit_enabled": True,
                    "withdraw_enabled": True,
                    "withdraw_fee": 10.0,
                    "withdraw_min": 20.0,
                    "min_confirmations": 12,
                },
                {
                    "network": "BEP20",
                    "deposit_enabled": False,
                    "withdraw_enabled": True,
                    "withdraw_fee": 1.0,
                    "withdraw_min": 5.0,
                    "min_confirmations": 15,
                },
            ],
            "paper_only": True,
            "live_order_submitted": False,
        }


def build_provider():
    return WeexVerificationProvider(
        client=FakeClient(),
        adapter=FakeAdapter(),
    )


def test_get_order_book_returns_normalized_depth():
    provider = build_provider()

    result = provider.get_order_book(
        "COTIUSDT"
    )

    assert result["exchange"] == "weex"
    assert result["symbol"] == "COTIUSDT"
    assert result["available"] is True
    assert result["best_bid"] == 0.1000
    assert result["best_ask"] == 0.1010


def test_get_coin_returns_normalized_metadata():
    provider = build_provider()

    result = provider.get_coin(
        "COTI"
    )

    assert result["coin"] == "COTI"
    assert len(result["networks"]) == 2


def test_get_network_finds_requested_network():
    provider = build_provider()

    result = provider.get_network(
        coin="COTI",
        network="ERC20",
    )

    assert result["available"] is True
    assert result["network"] == "ERC20"
    assert result["deposit_enabled"] is True
    assert result["withdraw_enabled"] is True
    assert result["withdraw_fee"] == 10.0


def test_disabled_deposit_status_is_preserved():
    provider = build_provider()

    result = provider.get_network(
        coin="COTI",
        network="BEP20",
    )

    assert result["available"] is True
    assert result["deposit_enabled"] is False
    assert result["withdraw_enabled"] is True


def test_unknown_coin_is_unavailable():
    provider = build_provider()

    result = provider.get_coin(
        "UNKNOWN"
    )

    assert result["available"] is False
    assert result["reason"] == "coin_not_found"


def test_unknown_network_is_unavailable():
    provider = build_provider()

    result = provider.get_network(
        coin="COTI",
        network="SOL",
    )

    assert result["available"] is False
    assert result["reason"] == "network_not_found"


def test_coin_is_required():
    provider = build_provider()

    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        provider.get_coin("")


def test_network_is_required():
    provider = build_provider()

    with pytest.raises(
        ValueError,
        match="network is required",
    ):
        provider.get_network(
            coin="COTI",
            network="",
        )


def test_provider_is_paper_safe():
    provider = build_provider()

    result = provider.get_network(
        coin="COTI",
        network="ERC20",
    )

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False


def test_provider_can_return_canonical_network_names():
    from exchanges.weex_network_normalizer import (
        WeexNetworkNormalizer,
    )
    from exchanges.weex_verification_adapter import (
        WeexVerificationAdapter,
    )

    class LiveStyleClient:
        def fetch_coins(self):
            return {
                "fetch_complete": True,
                "coins": [
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
                        ],
                    },
                ],
            }

    provider = WeexVerificationProvider(
        client=LiveStyleClient(),
        adapter=WeexVerificationAdapter(
            network_normalizer=(
                WeexNetworkNormalizer()
            )
        ),
    )

    result = provider.get_network(
        coin="USDT",
        network="TRC20",
    )

    assert result["available"] is True
    assert result["network"] == "TRC20"
    assert result["raw_network"] == "Tron (TRC20)"


def test_coin_with_empty_network_list_reports_missing_network_metadata():
    class EmptyNetworkClient:
        def fetch_coins(self):
            return {
                "fetch_complete": True,
                "coins": [
                    {
                        "coin": "FIR",
                        "depositAllEnable": True,
                        "withdrawAllEnable": True,
                        "networkList": [],
                    },
                ],
            }

    from exchanges.weex_verification_adapter import (
        WeexVerificationAdapter,
    )

    provider = WeexVerificationProvider(
        client=EmptyNetworkClient(),
        adapter=WeexVerificationAdapter(),
    )

    result = provider.get_coin(
        "FIR"
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


def test_coin_with_networks_reports_transfer_verification_available():
    class NetworkClient:
        def fetch_coins(self):
            return {
                "fetch_complete": True,
                "coins": [
                    {
                        "coin": "USDT",
                        "depositAllEnable": True,
                        "withdrawAllEnable": True,
                        "networkList": [
                            {
                                "network": "TRC20",
                                "depositEnable": True,
                                "withdrawEnable": True,
                                "withdrawFee": "1",
                                "withdrawMin": "10",
                            },
                        ],
                    },
                ],
            }

    from exchanges.weex_verification_adapter import (
        WeexVerificationAdapter,
    )

    provider = WeexVerificationProvider(
        client=NetworkClient(),
        adapter=WeexVerificationAdapter(),
    )

    result = provider.get_coin(
        "USDT"
    )

    assert result[
        "network_metadata_available"
    ] is True

    assert result[
        "network_metadata_reason"
    ] is None

    assert result[
        "transfer_verification_available"
    ] is True
