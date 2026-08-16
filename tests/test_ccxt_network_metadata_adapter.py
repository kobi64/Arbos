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


class FakeRealCCXTStyleExchange:
    def __init__(self):
        self.currencies = {}

    def load_markets(self):
        self.currencies = {
            "BTC": {
                "code": "BTC",
                "deposit": True,
                "withdraw": True,
                "networks": {
                    "BTC": {
                        "deposit": True,
                        "withdraw": True,
                        "fee": 0.0001,
                    },
                },
            },
        }
        return {}


def test_supports_ccxt_exchange_without_load_currencies():
    adapter = CCXTNetworkMetadataAdapter(
        FakeRealCCXTStyleExchange()
    )

    networks = adapter.get_networks("BTC")

    assert len(networks) == 1
    assert networks[0].network == "BTC"
    assert networks[0].withdraw_fee == 0.0001


class FakeUnknownFeeExchange:
    def __init__(self):
        self.currencies = {}

    def load_markets(self):
        self.currencies = {
            "ETH": {
                "code": "ETH",
                "deposit": True,
                "withdraw": True,
                "networks": {
                    "ETH": {
                        "deposit": True,
                        "withdraw": True,
                        "fee": None,
                    },
                },
            },
        }
        return {}


def test_preserves_unknown_withdraw_fee_as_none():
    adapter = CCXTNetworkMetadataAdapter(
        FakeUnknownFeeExchange()
    )

    networks = adapter.get_networks("ETH")

    assert len(networks) == 1
    assert networks[0].withdraw_fee is None



def test_unknown_currency_and_network_transfer_states_fail_closed():
    class FakeUnknownTransferStateExchange:
        def load_currencies(self):
            return {
                "USDT": {
                    "deposit": None,
                    "withdraw": None,
                    "networks": {
                        "TRC20": {
                            "deposit": None,
                            "withdraw": None,
                            "fee": 1.0,
                            "limits": {
                                "withdraw": {
                                    "min": 10.0,
                                },
                            },
                        },
                    },
                },
            }

    adapter = CCXTNetworkMetadataAdapter(
        FakeUnknownTransferStateExchange()
    )

    networks = adapter.get_networks(
        "USDT"
    )

    assert len(networks) == 1

    network = networks[0]

    assert network.deposit_enabled is False
    assert network.withdraw_enabled is False


def test_missing_transfer_states_fail_closed():
    class FakeMissingTransferStateExchange:
        def load_currencies(self):
            return {
                "USDT": {
                    "networks": {
                        "ERC20": {
                            "fee": 5.0,
                            "limits": {
                                "withdraw": {
                                    "min": 20.0,
                                },
                            },
                        },
                    },
                },
            }

    adapter = CCXTNetworkMetadataAdapter(
        FakeMissingTransferStateExchange()
    )

    networks = adapter.get_networks(
        "USDT"
    )

    assert len(networks) == 1

    network = networks[0]

    assert network.deposit_enabled is False
    assert network.withdraw_enabled is False
