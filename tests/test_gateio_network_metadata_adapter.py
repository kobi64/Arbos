import pytest

from exchanges.gateio_network_metadata_adapter import (
    GateIONetworkMetadataAdapter,
)


class FakeClient:
    def fetch_currencies(self):
        return {
            "fetch_complete": False,
            "reason": "credentials_unavailable",
            "currencies": [],
            "read_only": True,
            "paper_only": True,
            "live_order_submitted": False,
            "live_transfer_submitted": False,
        }


def test_credentials_unavailable_fails_closed():
    adapter = GateIONetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        "USDT"
    )

    assert result[
        "network_metadata_available"
    ] is False

    assert result[
        "network_metadata_reason"
    ] == "credentials_unavailable"

    assert result[
        "transfer_verification_available"
    ] is False

    assert result[
        "networks"
    ] == []


def test_get_networks_returns_empty_list():
    adapter = GateIONetworkMetadataAdapter(
        client=FakeClient(),
    )

    assert adapter.get_networks(
        "USDT"
    ) == []


def test_coin_is_normalized():
    adapter = GateIONetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        " usdt "
    )

    assert result["coin"] == "USDT"


def test_coin_is_required():
    adapter = GateIONetworkMetadataAdapter(
        client=FakeClient(),
    )

    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        adapter.describe_networks("")


def test_client_is_required():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        GateIONetworkMetadataAdapter(
            client=None,
        )


class FakePublicClient:
    def __init__(
        self,
        result,
    ):
        self.result = result
        self.calls = []

    def fetch_currency_chains(
        self,
        currency,
    ):
        self.calls.append(
            currency
        )

        return self.result


def test_public_currency_chains_enable_transfer_verification():
    client = FakePublicClient({
        "fetch_complete": True,
        "currency": "USDT",
        "currencies": [
            {
                "asset": "USDT",
                "coin": "USDT",
                "network": "ETH",
                "chain": "ETH",
                "deposit": True,
                "withdraw": True,
            },
            {
                "asset": "USDT",
                "coin": "USDT",
                "network": "TRX",
                "chain": "TRX",
                "deposit": True,
                "withdraw": False,
            },
        ],
        "reason": None,
        "paper_only": True,
        "live_order_submitted": False,
        "live_transfer_submitted": False,
    })

    adapter = GateIONetworkMetadataAdapter(
        client=client,
    )

    result = adapter.describe_networks(
        " usdt "
    )

    assert client.calls == [
        "USDT",
    ]

    assert result[
        "network_metadata_available"
    ] is True

    assert result[
        "network_metadata_reason"
    ] is None

    assert result[
        "transfer_verification_available"
    ] is True

    assert len(
        result["networks"]
    ) == 2

    assert result[
        "networks"
    ][0].network == "ETH"

    assert result[
        "networks"
    ][0].deposit_enabled is True

    assert result[
        "networks"
    ][0].withdraw_enabled is True


def test_public_currency_chain_failure_fails_closed():
    client = FakePublicClient({
        "fetch_complete": False,
        "currency": "USDT",
        "currencies": [],
        "reason": "RuntimeError: offline",
        "paper_only": True,
        "live_order_submitted": False,
        "live_transfer_submitted": False,
    })

    adapter = GateIONetworkMetadataAdapter(
        client=client,
    )

    result = adapter.describe_networks(
        "USDT"
    )

    assert result[
        "network_metadata_available"
    ] is False

    assert result[
        "network_metadata_reason"
    ] == "RuntimeError: offline"

    assert result[
        "transfer_verification_available"
    ] is False

    assert result[
        "networks"
    ] == []


def test_public_empty_currency_chains_do_not_verify_transfer():
    client = FakePublicClient({
        "fetch_complete": True,
        "currency": "USDT",
        "currencies": [],
        "reason": None,
        "paper_only": True,
        "live_order_submitted": False,
        "live_transfer_submitted": False,
    })

    adapter = GateIONetworkMetadataAdapter(
        client=client,
    )

    result = adapter.describe_networks(
        "USDT"
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


def test_public_gate_minimum_withdrawal_is_preserved():
    client = FakePublicClient({
        "fetch_complete": True,
        "currency": "BTC",
        "currencies": [
            {
                "asset": "BTC",
                "coin": "BTC",
                "network": "BTC",
                "chain": "BTC",
                "deposit": True,
                "withdraw": True,
                "raw": {
                    "withdraw_amount_min": "0.0005",
                },
            },
        ],
        "reason": None,
    })

    network = (
        GateIONetworkMetadataAdapter(
            client=client,
        )
        .get_networks("BTC")[0]
    )

    assert network.min_withdraw == 0.0005

    # Gate public chain metadata currently does not
    # expose a trustworthy withdrawal-fee field.
    assert network.withdraw_fee is None


def test_gate_invalid_minimum_withdrawal_fails_closed():
    client = FakePublicClient({
        "fetch_complete": True,
        "currency": "USDT",
        "currencies": [
            {
                "asset": "USDT",
                "network": "ETH",
                "deposit": True,
                "withdraw": True,
                "raw": {
                    "withdraw_amount_min": "invalid",
                },
            },
        ],
        "reason": None,
    })

    network = (
        GateIONetworkMetadataAdapter(
            client=client,
        )
        .get_networks("USDT")[0]
    )

    assert network.min_withdraw is None


def test_gate_negative_minimum_withdrawal_is_not_accepted():
    client = FakePublicClient({
        "fetch_complete": True,
        "currency": "USDT",
        "currencies": [
            {
                "asset": "USDT",
                "network": "ETH",
                "deposit": True,
                "withdraw": True,
                "raw": {
                    "withdraw_amount_min": "-1",
                },
            },
        ],
        "reason": None,
    })

    network = (
        GateIONetworkMetadataAdapter(
            client=client,
        )
        .get_networks("USDT")[0]
    )

    assert network.min_withdraw is None


class FakePublicAndFeeClient:
    def __init__(
        self,
        public_result,
        fee_result,
    ):
        self.public_result = public_result
        self.fee_result = fee_result
        self.public_calls = []
        self.fee_calls = 0

    def fetch_currency_chains(
        self,
        currency,
    ):
        self.public_calls.append(
            currency
        )
        return self.public_result

    def fetch_currencies(
        self,
    ):
        self.fee_calls += 1
        return self.fee_result


def test_gate_per_chain_withdrawal_fee_is_preserved():
    client = FakePublicAndFeeClient(
        public_result={
            "fetch_complete": True,
            "currency": "USDT",
            "currencies": [
                {
                    "asset": "USDT",
                    "network": "ETH",
                    "deposit": True,
                    "withdraw": True,
                    "raw": {
                        "withdraw_amount_min": "1",
                    },
                },
                {
                    "asset": "USDT",
                    "network": "TRX",
                    "deposit": True,
                    "withdraw": True,
                    "raw": {
                        "withdraw_amount_min": "10",
                    },
                },
            ],
            "reason": None,
        },
        fee_result={
            "fetch_complete": True,
            "currencies": [
                {
                    "currency": "USDT",
                    "withdraw_fix": "2.5",
                    "withdraw_fix_on_chains": {
                        "ETH": "3.5",
                        "TRX": "1",
                    },
                },
            ],
            "reason": None,
        },
    )

    networks = (
        GateIONetworkMetadataAdapter(
            client=client,
        )
        .get_networks(
            "USDT"
        )
    )

    by_network = {
        item.network: item
        for item in networks
    }

    assert (
        by_network["ETH"]
        .withdraw_fee
        == 3.5
    )

    assert (
        by_network["TRX"]
        .withdraw_fee
        == 1.0
    )

    assert (
        by_network["ETH"]
        .min_withdraw
        == 1.0
    )

    assert (
        by_network["TRX"]
        .min_withdraw
        == 10.0
    )


def test_gate_default_withdrawal_fee_is_fallback():
    client = FakePublicAndFeeClient(
        public_result={
            "fetch_complete": True,
            "currency": "BTC",
            "currencies": [
                {
                    "asset": "BTC",
                    "network": "BTC",
                    "deposit": True,
                    "withdraw": True,
                    "raw": {
                        "withdraw_amount_min": "0.0005",
                    },
                },
            ],
            "reason": None,
        },
        fee_result={
            "fetch_complete": True,
            "currencies": [
                {
                    "currency": "BTC",
                    "withdraw_fix": "0.0001",
                    "withdraw_fix_on_chains": {},
                },
            ],
            "reason": None,
        },
    )

    network = (
        GateIONetworkMetadataAdapter(
            client=client,
        )
        .get_networks(
            "BTC"
        )[0]
    )

    assert (
        network.withdraw_fee
        == 0.0001
    )

    assert (
        network.min_withdraw
        == 0.0005
    )


def test_gate_fee_lookup_failure_preserves_public_metadata():
    client = FakePublicAndFeeClient(
        public_result={
            "fetch_complete": True,
            "currency": "SOL",
            "currencies": [
                {
                    "asset": "SOL",
                    "network": "SOL",
                    "deposit": True,
                    "withdraw": True,
                    "raw": {
                        "withdraw_amount_min": "0.1",
                    },
                },
            ],
            "reason": None,
        },
        fee_result={
            "fetch_complete": False,
            "currencies": [],
            "reason": (
                "credentials_unavailable"
            ),
        },
    )

    network = (
        GateIONetworkMetadataAdapter(
            client=client,
        )
        .get_networks(
            "SOL"
        )[0]
    )

    assert (
        network.min_withdraw
        == 0.1
    )

    assert (
        network.withdraw_fee
        is None
    )


def test_gate_invalid_withdrawal_fee_fails_closed():
    client = FakePublicAndFeeClient(
        public_result={
            "fetch_complete": True,
            "currency": "USDT",
            "currencies": [
                {
                    "asset": "USDT",
                    "network": "ETH",
                    "deposit": True,
                    "withdraw": True,
                    "raw": {
                        "withdraw_amount_min": "1",
                    },
                },
            ],
            "reason": None,
        },
        fee_result={
            "fetch_complete": True,
            "currencies": [
                {
                    "currency": "USDT",
                    "withdraw_fix": "-1",
                    "withdraw_fix_on_chains": {
                        "ETH": "invalid",
                    },
                },
            ],
            "reason": None,
        },
    )

    network = (
        GateIONetworkMetadataAdapter(
            client=client,
        )
        .get_networks(
            "USDT"
        )[0]
    )

    assert (
        network.withdraw_fee
        is None
    )
