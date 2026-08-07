from exchanges.ccxt_network_metadata_adapter import (
    CCXTNetworkMetadataAdapter,
)


class FakeExchange:
    def load_currencies(self):
        return {
            "USDT": {
                "code": "USDT",
                "deposit": True,
                "withdraw": True,
                "networks": {
                    "TRC20": {
                        "deposit": True,
                        "withdraw": True,
                        "fee": 1.0,
                        "limits": {
                            "withdraw": {
                                "min": 10.0,
                            },
                        },
                    },
                    "ERC20": {
                        "deposit": True,
                        "withdraw": False,
                        "fee": 8.0,
                        "limits": {
                            "withdraw": {
                                "min": 20.0,
                            },
                        },
                    },
                },
            },
        }


def test_converts_ccxt_networks_to_network_info():
    adapter = CCXTNetworkMetadataAdapter(
        FakeExchange()
    )

    networks = adapter.get_networks("USDT")

    assert len(networks) == 2

    trc20 = next(
        network
        for network in networks
        if network.network == "TRC20"
    )

    assert trc20.coin == "USDT"
    assert trc20.deposit_enabled is True
    assert trc20.withdraw_enabled is True
    assert trc20.withdraw_fee == 1.0
    assert trc20.min_withdraw == 10.0


def test_preserves_disabled_withdrawal_status():
    adapter = CCXTNetworkMetadataAdapter(
        FakeExchange()
    )

    networks = adapter.get_networks("USDT")

    erc20 = next(
        network
        for network in networks
        if network.network == "ERC20"
    )

    assert erc20.deposit_enabled is True
    assert erc20.withdraw_enabled is False
    assert erc20.withdraw_fee == 8.0
    assert erc20.min_withdraw == 20.0
