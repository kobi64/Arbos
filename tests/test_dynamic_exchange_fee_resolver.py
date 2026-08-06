import pytest

from core.dynamic_exchange_fee_resolver import (
    DynamicExchangeFeeResolver,
)


def test_resolves_taker_fee_for_known_exchange():
    resolver = DynamicExchangeFeeResolver({
        "kraken": {"maker": 0.0025, "taker": 0.0040},
    })

    result = resolver.resolve(
        exchange_id="kraken",
        fee_type="taker",
    )

    assert result["exchange_id"] == "kraken"
    assert result["fee_type"] == "taker"
    assert result["fee_rate"] == 0.0040


def test_resolves_maker_fee_for_known_exchange():
    resolver = DynamicExchangeFeeResolver({
        "kraken": {"maker": 0.0025, "taker": 0.0040},
    })

    result = resolver.resolve(
        exchange_id="kraken",
        fee_type="maker",
    )

    assert result["fee_rate"] == 0.0025


def test_defaults_to_taker_fee():
    resolver = DynamicExchangeFeeResolver({
        "kraken": {"maker": 0.0025, "taker": 0.0040},
    })

    result = resolver.resolve(exchange_id="kraken")

    assert result["fee_type"] == "taker"
    assert result["fee_rate"] == 0.0040


def test_unknown_exchange_is_rejected():
    resolver = DynamicExchangeFeeResolver({
        "kraken": {"maker": 0.0025, "taker": 0.0040},
    })

    with pytest.raises(ValueError, match="exchange fee configuration not found"):
        resolver.resolve(exchange_id="unknown")


def test_invalid_fee_type_is_rejected():
    resolver = DynamicExchangeFeeResolver({
        "kraken": {"maker": 0.0025, "taker": 0.0040},
    })

    with pytest.raises(ValueError, match="invalid fee_type"):
        resolver.resolve(
            exchange_id="kraken",
            fee_type="invalid",
        )


def test_negative_fee_configuration_is_rejected():
    with pytest.raises(ValueError, match="fee rates must be non-negative"):
        DynamicExchangeFeeResolver({
            "kraken": {"maker": -0.001, "taker": 0.0040},
        })
