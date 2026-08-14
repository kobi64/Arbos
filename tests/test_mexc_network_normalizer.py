from exchanges.mexc_network_normalizer import (
    MexcNetworkNormalizer,
)


def test_normalizes_tron_network():
    normalizer = MexcNetworkNormalizer()

    result = normalizer.normalize({
        "coin": "USDT",
        "network": "TRX",
        "depositEnable": True,
        "withdrawEnable": True,
        "withdrawFee": "1.0",
        "withdrawMin": "10",
        "minConfirm": "20",
        "contract": (
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


def test_normalizes_common_network_aliases():
    normalizer = MexcNetworkNormalizer()

    cases = {
        "TRX": "TRC20",
        "ETH": "ERC20",
        "BEP20(BSC)": "BSC",
        "BSC": "BSC",
        "SOL": "SOL",
        "ARBITRUM": "ARBITRUM",
        "MATIC": "POLYGON",
        "AVAX_CCHAIN": "AVAXC",
    }

    for raw, expected in cases.items():
        result = normalizer.normalize({
            "coin": "TEST",
            "network": raw,
            "depositEnable": True,
            "withdrawEnable": True,
            "withdrawFee": "0.1",
            "withdrawMin": "1",
            "minConfirm": "10",
        })

        assert result[
            "network"
        ] == expected


def test_missing_optional_values_are_safe():
    normalizer = MexcNetworkNormalizer()

    result = normalizer.normalize({
        "coin": "TEST",
        "network": "TESTNET",
        "depositEnable": False,
        "withdrawEnable": False,
    })

    assert result[
        "network"
    ] == "TESTNET"

    assert result[
        "withdraw_fee"
    ] is None

    assert result[
        "min_withdraw"
    ] == 0.0

    assert result[
        "confirmations"
    ] is None

    assert result[
        "contract_address"
    ] is None


def test_negative_withdraw_min_is_normalized_to_zero():
    normalizer = MexcNetworkNormalizer()

    result = normalizer.normalize({
        "coin": "TEST",
        "network": "ETH",
        "depositEnable": True,
        "withdrawEnable": True,
        "withdrawFee": "1",
        "withdrawMin": "-1",
    })

    assert result[
        "min_withdraw"
    ] == 0.0


def test_preserves_raw_network_identity():
    normalizer = MexcNetworkNormalizer()

    result = normalizer.normalize({
        "coin": "TOKEN",
        "network": "BEP20(BSC)",
        "depositEnable": True,
        "withdrawEnable": True,
        "withdrawFee": "0.5",
        "withdrawMin": "5",
        "minConfirm": "15",
        "contract": "0x1234",
    })

    assert result[
        "raw_network"
    ] == "BEP20(BSC)"

    assert result[
        "contract_address"
    ] == "0x1234"
