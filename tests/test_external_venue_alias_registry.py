import pytest

from core.external_venue_alias_registry import (
    ExternalVenueAliasRegistry,
)


def test_gate_alias_maps_to_gateio():
    registry = ExternalVenueAliasRegistry()

    assert registry.canonicalize(
        "gate"
    ) == "gateio"

    assert registry.canonicalize(
        "Gate.io"
    ) == "gateio"


def test_huobi_alias_maps_to_htx():
    registry = ExternalVenueAliasRegistry()

    assert registry.canonicalize(
        "huobi"
    ) == "htx"

    assert registry.canonicalize(
        "HuobiGlobal"
    ) == "htx"


def test_existing_canonical_name_is_preserved():
    registry = ExternalVenueAliasRegistry()

    assert registry.canonicalize(
        "KuCoin"
    ) == "kucoin"

    assert registry.canonicalize(
        "bitget"
    ) == "bitget"


def test_unknown_exchange_is_normalized_not_invented():
    registry = ExternalVenueAliasRegistry()

    assert registry.canonicalize(
        " SomeNewExchange "
    ) == "somenewexchange"


def test_missing_exchange_is_rejected():
    registry = ExternalVenueAliasRegistry()

    with pytest.raises(
        ValueError,
        match="exchange is required",
    ):
        registry.canonicalize("")
