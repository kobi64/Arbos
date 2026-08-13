import pytest

from core.external_arbitrage_signal_normalizer import (
    ExternalArbitrageSignalNormalizer,
)


def raw_signal():
    return {
        "signal_id": "CMG-001",
        "coin": "COTI",
        "buy_exchange": "gate",
        "sell_exchange": "kucoin",
        "buy_price": 0.085,
        "sell_price": 0.091,
        "spread_percent": 7.05,
        "status": "exploitable",
        "observed_at": 1000.0,
    }


def test_normalizes_external_signal():
    normalizer = ExternalArbitrageSignalNormalizer()

    result = normalizer.normalize(
        source="coinmarketgap",
        signal=raw_signal(),
    )

    assert result[
        "source"
    ] == "coinmarketgap"

    assert result[
        "source_signal_id"
    ] == "CMG-001"

    assert result[
        "coin"
    ] == "COTI"

    assert result[
        "buy_exchange"
    ] == "gate"

    assert result[
        "sell_exchange"
    ] == "kucoin"

    assert result[
        "buy_price"
    ] == 0.085

    assert result[
        "sell_price"
    ] == 0.091

    assert result[
        "reported_spread_percent"
    ] == 7.05

    assert result[
        "reported_status"
    ] == "exploitable"

    assert result[
        "observed_at"
    ] == 1000.0


def test_normalizes_case_and_whitespace():
    normalizer = ExternalArbitrageSignalNormalizer()

    signal = raw_signal()

    signal["coin"] = " coti "
    signal["buy_exchange"] = " GATE "
    signal["sell_exchange"] = " KuCoin "

    result = normalizer.normalize(
        source=" CoinMarketGap ",
        signal=signal,
    )

    assert result["source"] == "coinmarketgap"
    assert result["coin"] == "COTI"
    assert result["buy_exchange"] == "gate"
    assert result["sell_exchange"] == "kucoin"


def test_generates_stable_signal_key():
    normalizer = ExternalArbitrageSignalNormalizer()

    result = normalizer.normalize(
        source="coinmarketgap",
        signal=raw_signal(),
    )

    assert result[
        "signal_key"
    ] == (
        "coinmarketgap:"
        "CMG-001"
    )


def test_preserves_raw_signal_copy():
    normalizer = ExternalArbitrageSignalNormalizer()

    signal = raw_signal()

    result = normalizer.normalize(
        source="coinmarketgap",
        signal=signal,
    )

    signal["coin"] = "CHANGED"

    assert result[
        "raw"
    ][
        "coin"
    ] == "COTI"


def test_missing_source_is_rejected():
    normalizer = ExternalArbitrageSignalNormalizer()

    with pytest.raises(
        ValueError,
        match="source is required",
    ):
        normalizer.normalize(
            source="",
            signal=raw_signal(),
        )


def test_missing_signal_id_is_rejected():
    normalizer = ExternalArbitrageSignalNormalizer()

    signal = raw_signal()
    signal.pop("signal_id")

    with pytest.raises(
        ValueError,
        match="signal_id is required",
    ):
        normalizer.normalize(
            source="coinmarketgap",
            signal=signal,
        )


def test_missing_coin_is_rejected():
    normalizer = ExternalArbitrageSignalNormalizer()

    signal = raw_signal()
    signal.pop("coin")

    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        normalizer.normalize(
            source="coinmarketgap",
            signal=signal,
        )


def test_missing_exchange_is_rejected():
    normalizer = ExternalArbitrageSignalNormalizer()

    signal = raw_signal()
    signal["buy_exchange"] = ""

    with pytest.raises(
        ValueError,
        match="buy_exchange is required",
    ):
        normalizer.normalize(
            source="coinmarketgap",
            signal=signal,
        )


def test_normalized_signal_is_not_trusted_as_executable():
    normalizer = ExternalArbitrageSignalNormalizer()

    result = normalizer.normalize(
        source="coinmarketgap",
        signal=raw_signal(),
    )

    assert result[
        "externally_reported"
    ] is True

    assert result[
        "arbos_verified"
    ] is False

    assert result[
        "executable"
    ] is False

    assert result[
        "verification_required"
    ] is True


def test_normalizer_is_paper_safe():
    normalizer = ExternalArbitrageSignalNormalizer()

    result = normalizer.normalize(
        source="coinmarketgap",
        signal=raw_signal(),
    )

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False
