import copy

import pytest

from core.repeat_scale_market_provenance_binding import (
    RepeatScaleMarketProvenanceBinding,
)


def provenance():
    return {
        "route_id": "ROUTE-351",
        "independent_revalidation_capture": True,
        "snapshot_age_verified": False,
        "snapshot_count": 2,
        "symbols": [
            "BTC/USDT",
            "BTC/USDT",
        ],
        "exchange_ids": [
            "kucoin",
            "gateio",
        ],
        "earliest_timestamp": 1000.0,
        "latest_timestamp": 1000.1,
        "snapshot_spread_ms": 100.0,
        "entry_symbol": "BTC/USDT",
        "entry_side": "buy",
        "available_liquidity": 50000.0,
        "best_price": 100.0,
        "average_price": 100.2,
        "slippage_percent": 0.2,
    }


def test_create_is_deterministic():
    first = (
        RepeatScaleMarketProvenanceBinding
        .create(provenance())
    )
    second = (
        RepeatScaleMarketProvenanceBinding
        .create(provenance())
    )

    assert (
        first["market_provenance_id"]
        == second["market_provenance_id"]
    )
    assert first[
        "market_provenance_id"
    ].startswith("MP-")


def test_verify_accepts_exact_provenance():
    item = provenance()

    binding = (
        RepeatScaleMarketProvenanceBinding
        .create(item)
    )

    assert (
        RepeatScaleMarketProvenanceBinding
        .verify(
            item,
            binding[
                "market_provenance_id"
            ],
        )
        is True
    )


@pytest.mark.parametrize(
    "field,new_value",
    [
        ("route_id", "OTHER"),
        ("snapshot_count", 3),
        ("earliest_timestamp", 999.0),
        ("latest_timestamp", 1001.0),
        ("snapshot_spread_ms", 200.0),
        ("entry_symbol", "ETH/USDT"),
        ("entry_side", "sell"),
        ("available_liquidity", 1.0),
        ("best_price", 101.0),
        ("average_price", 101.2),
        ("slippage_percent", 1.2),
    ],
)
def test_verify_rejects_mutated_provenance(
    field,
    new_value,
):
    original = provenance()

    provenance_id = (
        RepeatScaleMarketProvenanceBinding
        .create(original)[
            "market_provenance_id"
        ]
    )

    changed = copy.deepcopy(
        original
    )
    changed[field] = new_value

    assert (
        RepeatScaleMarketProvenanceBinding
        .verify(
            changed,
            provenance_id,
        )
        is False
    )


def test_verify_rejects_mutated_symbols():
    original = provenance()

    provenance_id = (
        RepeatScaleMarketProvenanceBinding
        .create(original)[
            "market_provenance_id"
        ]
    )

    changed = copy.deepcopy(
        original
    )
    changed["symbols"][0] = (
        "ETH/USDT"
    )

    assert (
        RepeatScaleMarketProvenanceBinding
        .verify(
            changed,
            provenance_id,
        )
        is False
    )


def test_verify_rejects_mutated_exchange():
    original = provenance()

    provenance_id = (
        RepeatScaleMarketProvenanceBinding
        .create(original)[
            "market_provenance_id"
        ]
    )

    changed = copy.deepcopy(
        original
    )
    changed["exchange_ids"][0] = (
        "other"
    )

    assert (
        RepeatScaleMarketProvenanceBinding
        .verify(
            changed,
            provenance_id,
        )
        is False
    )


def test_non_authoritative_flags_do_not_change_identity():
    original = provenance()

    first = (
        RepeatScaleMarketProvenanceBinding
        .create(original)[
            "market_provenance_id"
        ]
    )

    changed = copy.deepcopy(
        original
    )
    changed[
        "snapshot_age_verified"
    ] = True

    second = (
        RepeatScaleMarketProvenanceBinding
        .create(changed)[
            "market_provenance_id"
        ]
    )

    assert first == second


def test_missing_required_field_rejected():
    item = provenance()
    del item["route_id"]

    with pytest.raises(
        ValueError,
        match="route_id is required",
    ):
        (
            RepeatScaleMarketProvenanceBinding
            .create(item)
        )


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        True,
        float("nan"),
        float("inf"),
    ],
)
def test_invalid_best_price_rejected(
    value,
):
    item = provenance()
    item["best_price"] = value

    with pytest.raises(ValueError):
        (
            RepeatScaleMarketProvenanceBinding
            .create(item)
        )


def test_binding_contains_normalized_copy():
    item = provenance()

    result = (
        RepeatScaleMarketProvenanceBinding
        .create(item)
    )

    binding = result[
        "market_provenance_binding"
    ]

    assert binding["route_id"] == (
        "ROUTE-351"
    )
    assert binding["entry_side"] == (
        "buy"
    )
    assert binding["exchange_ids"] == [
        "kucoin",
        "gateio",
    ]
