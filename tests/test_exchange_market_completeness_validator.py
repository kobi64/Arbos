import pytest

from exchanges.exchange_market_completeness_validator import (
    ExchangeMarketCompletenessValidator,
)


def validator():
    return ExchangeMarketCompletenessValidator()


def test_matching_catalogues_are_complete():
    result = validator().validate(
        exchange_id="kucoin",
        ccxt_symbols=[
            "BTC/USDT",
            "ETH/USDT",
        ],
        raw_symbols=[
            "BTC/USDT",
            "ETH/USDT",
        ],
    )

    assert result["complete_match"] is True
    assert result["matched_count"] == 2
    assert result["discrepancy_count"] == 0


def test_raw_only_market_is_detected():
    result = validator().validate(
        exchange_id="digifinex",
        ccxt_symbols=[
            "BTC/USDT",
        ],
        raw_symbols=[
            "BTC/USDT",
            "COTI/USDT",
        ],
    )

    assert result["complete_match"] is False
    assert result["raw_only"] == [
        "COTI/USDT",
    ]
    assert result["raw_only_count"] == 1


def test_ccxt_only_market_is_detected():
    result = validator().validate(
        exchange_id="example",
        ccxt_symbols=[
            "BTC/USDT",
            "OLD/USDT",
        ],
        raw_symbols=[
            "BTC/USDT",
        ],
    )

    assert result["ccxt_only"] == [
        "OLD/USDT",
    ]
    assert result["ccxt_only_count"] == 1


def test_raw_symbol_formats_are_normalized():
    result = validator().validate(
        exchange_id="digifinex",
        ccxt_symbols=[
            "BTC/USDT",
            "ETH/USDT",
        ],
        raw_symbols=[
            "btc_usdt",
            "eth-usdt",
            "coti_usdt",
        ],
    )

    assert "BTC/USDT" in result["matched"]
    assert "ETH/USDT" in result["matched"]
    assert "COTI/USDT" in result["raw_only"]


def test_duplicate_symbols_do_not_inflate_counts():
    result = validator().validate(
        exchange_id="test",
        ccxt_symbols=[
            "BTC/USDT",
            "BTC/USDT",
        ],
        raw_symbols=[
            "btc_usdt",
            "BTC/USDT",
        ],
    )

    assert result["ccxt_market_count"] == 1
    assert result["raw_market_count"] == 1
    assert result["matched_count"] == 1


def test_market_records_include_classification():
    result = validator().validate(
        exchange_id="digifinex",
        ccxt_symbols=[
            "BTC/USDT",
        ],
        raw_symbols=[
            "BTC_USDT",
            "COTI_USDT",
        ],
    )

    records = {
        item["symbol"]: item
        for item in result["markets"]
    }

    assert records["BTC/USDT"]["status"] == "MATCHED"
    assert records["COTI/USDT"]["status"] == "RAW_ONLY"
    assert records["COTI/USDT"]["ccxt_present"] is False
    assert records["COTI/USDT"]["raw_present"] is True


def test_missing_exchange_id_is_rejected():
    with pytest.raises(
        ValueError,
        match="exchange_id is required",
    ):
        validator().validate(
            exchange_id="",
            ccxt_symbols=[],
            raw_symbols=[],
        )


def test_missing_ccxt_symbols_is_rejected():
    with pytest.raises(
        ValueError,
        match="ccxt_symbols is required",
    ):
        validator().validate(
            exchange_id="digifinex",
            ccxt_symbols=None,
            raw_symbols=[],
        )


def test_missing_raw_symbols_is_rejected():
    with pytest.raises(
        ValueError,
        match="raw_symbols is required",
    ):
        validator().validate(
            exchange_id="digifinex",
            ccxt_symbols=[],
            raw_symbols=None,
        )


def test_validator_never_submits_live_order():
    result = validator().validate(
        exchange_id="digifinex",
        ccxt_symbols=[],
        raw_symbols=[
            "COTI_USDT",
        ],
    )

    assert result["live_order_submitted"] is False
