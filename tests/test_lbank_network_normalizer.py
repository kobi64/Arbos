from exchanges.lbank_network_normalizer import (
    LBankNetworkNormalizer,
)


def build_normalizer():
    return LBankNetworkNormalizer()


def test_normalizes_common_network_names():
    normalizer = build_normalizer()

    cases = {
        "erc20": "ETH",
        "bep20(bsc)": "BSC",
        "trc20": "TRX",
        "polygon": "POLYGON",
        "arbitrum one": "ARBITRUM",
        "solana": "SOL",
        "c-chain": "AVAXC",
        "terra classic": "LUNC",
    }

    for raw, expected in cases.items():
        assert (
            normalizer.normalize_network_name(
                raw
            )
            == expected
        )


def test_unknown_network_fails_closed():
    normalizer = build_normalizer()

    assert (
        normalizer.normalize_network_name(
            "some-new-chain"
        )
        is None
    )


def test_normalizes_network_record():
    normalizer = build_normalizer()

    result = normalizer.normalize_record(
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
                "feeCode": "usdt",
                "feeRate": "0",
                "minAmt": "10",
                "minDepositAmt": "0.0001",
                "depositFee": "0",
            },
        }
    )

    assert result["asset"] == "USDT"
    assert result["network"] == "ETH"
    assert result["deposit_enabled"] is True
    assert result["withdraw_enabled"] is True

    assert result["contract_address"] == (
        "0xdac17f958d2ee523a2206206994597c13d831ec7"
    )

    assert result["memo_required"] is False
    assert result["withdraw_fee"] == 1.0
    assert result["min_withdraw"] == 10.0
    assert result["min_deposit"] == 0.0001


def test_native_asset_without_contract_is_preserved():
    normalizer = build_normalizer()

    result = normalizer.normalize_record(
        {
            "assetCode": "lunc",
            "chainName": "terra classic",
            "canDeposit": True,
            "canDraw": True,
            "contractInfo": None,
            "hasMemo": True,
            "assetFee": {
                "feeAmt": "15000",
                "minAmt": "30000",
                "minDepositAmt": "0.0001",
            },
        }
    )

    assert result["asset"] == "LUNC"
    assert result["network"] == "LUNC"
    assert result["contract_address"] is None
    assert result["memo_required"] is True


def test_disabled_transfer_state_is_preserved():
    normalizer = build_normalizer()

    result = normalizer.normalize_record(
        {
            "assetCode": "usdt",
            "chainName": "omni",
            "canDeposit": False,
            "canDraw": False,
            "contractInfo": None,
            "hasMemo": False,
            "assetFee": {
                "minAmt": "0",
                "minDepositAmt": "0",
            },
        }
    )

    assert result["deposit_enabled"] is False
    assert result["withdraw_enabled"] is False


def test_invalid_record_fails_closed():
    normalizer = build_normalizer()

    assert (
        normalizer.normalize_record(
            {}
        )
        is None
    )


def test_ton_and_toncoin_remain_distinct():
    normalizer = LBankNetworkNormalizer()

    assert (
        normalizer.normalize_network_name(
            "ton"
        )
        == "TON"
    )

    assert (
        normalizer.normalize_network_name(
            "toncoin"
        )
        == "TONCOIN"
    )
