import pytest

from exchanges.weex_network_normalizer import (
    WeexNetworkNormalizer,
)


def test_tron_is_normalized():
    normalizer = WeexNetworkNormalizer()

    assert normalizer.normalize(
        "Tron (TRC20)"
    ) == "TRC20"


def test_ethereum_is_normalized():
    normalizer = WeexNetworkNormalizer()

    assert normalizer.normalize(
        "Ethereum (ETH)"
    ) == "ERC20"


def test_bsc_is_normalized():
    normalizer = WeexNetworkNormalizer()

    assert normalizer.normalize(
        "BNB Smart Chain (BSC)"
    ) == "BSC"


def test_arbitrum_is_normalized():
    normalizer = WeexNetworkNormalizer()

    assert normalizer.normalize(
        "Arbitrum One (ARB)"
    ) == "ARBITRUM"


def test_solana_is_normalized():
    normalizer = WeexNetworkNormalizer()

    assert normalizer.normalize(
        "Solana (SOL)"
    ) == "SOL"


def test_polygon_is_normalized():
    normalizer = WeexNetworkNormalizer()

    assert normalizer.normalize(
        "Polygon PoS (MATIC)"
    ) == "POLYGON"


def test_optimism_is_normalized():
    normalizer = WeexNetworkNormalizer()

    assert normalizer.normalize(
        "Optimism (OP)"
    ) == "OPTIMISM"


def test_avalanche_c_chain_is_normalized():
    normalizer = WeexNetworkNormalizer()

    assert normalizer.normalize(
        "Avalanche C-Chain (AVAX-C)"
    ) == "AVAXC"


def test_ton_is_normalized():
    normalizer = WeexNetworkNormalizer()

    assert normalizer.normalize(
        "The Open Network (TON)"
    ) == "TON"


def test_unknown_network_is_preserved_safely():
    normalizer = WeexNetworkNormalizer()

    assert normalizer.normalize(
        "Some Future Chain"
    ) == "SOME FUTURE CHAIN"


def test_network_is_required():
    normalizer = WeexNetworkNormalizer()

    with pytest.raises(
        ValueError,
        match="network is required",
    ):
        normalizer.normalize("")
