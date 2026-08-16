from exchanges.poloniex_network_normalizer import (
    PoloniexNetworkNormalizer,
)


def test_normalizes_tron_network():
    normalizer = PoloniexNetworkNormalizer()

    result = normalizer.normalize({
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
    })

    assert result[
        "network"
    ] == "TRC20"

    assert result[
        "deposit_enabled"
    ] is True

    assert result[
        "withdraw_enabled"
    ] is True

    assert result[
        "withdraw_fee"
    ] == 1.0

    assert result[
        "min_withdraw"
    ] == 10.0

    assert result[
        "confirmations"
    ] == 20

    assert result[
        "contract_address"
    ] == (
        "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
    )


def test_normalizes_common_blockchain_aliases():
    normalizer = PoloniexNetworkNormalizer()

    cases = {
        "TRX": "TRC20",
        "ETH": "ERC20",
        "BSC": "BSC",
        "SOL": "SOL",
        "ARBITRUM": "ARBITRUM",
        "MATIC": "POLYGON",
        "AVAXC": "AVAXC",
    }

    for raw, expected in cases.items():
        result = normalizer.normalize({
            "coin": "TEST",
            "name": raw,
            "blockchain": raw,
            "withdrawalEnable": True,
            "depositEnable": True,
            "withdrawMin": "1",
            "withdrawFee": "0.1",
            "minConfirm": 10,
        })

        assert result[
            "network"
        ] == expected


def test_missing_optional_values_are_safe():
    normalizer = PoloniexNetworkNormalizer()

    result = normalizer.normalize({
        "coin": "TEST",
        "name": "Test",
        "blockchain": "TESTNET",
        "withdrawalEnable": False,
        "depositEnable": True,
    })

    assert result[
        "network"
    ] == "TESTNET"

    assert result[
        "withdraw_fee"
    ] is None

    assert result[
        "min_withdraw"
    ] is None

    assert result[
        "confirmations"
    ] is None

    assert result[
        "contract_address"
    ] is None


def test_preserves_raw_network_identity():
    normalizer = PoloniexNetworkNormalizer()

    result = normalizer.normalize({
        "coin": "TOKENBSC",
        "name": "BNB Smart Chain",
        "blockchain": "BSC",
        "withdrawalEnable": True,
        "depositEnable": True,
        "withdrawMin": "5",
        "withdrawFee": "0.5",
        "minConfirm": 15,
        "contractAddress": "0x1234",
    })

    assert result[
        "raw_network"
    ] == "BSC"

    assert result[
        "network_name"
    ] == "BNB Smart Chain"

    assert result[
        "contract_address"
    ] == "0x1234"


def test_negative_withdraw_min_is_normalized_to_zero():
    normalizer = PoloniexNetworkNormalizer()

    result = normalizer.normalize({
        "coin": "USDTETH",
        "name": "Ethereum",
        "blockchain": "ETH",
        "withdrawalEnable": True,
        "depositEnable": True,
        "withdrawMin": "-1",
        "withdrawFee": "0.5",
        "minConfirm": 12,
    })

    assert result[
        "min_withdraw"
    ] == 0.0
