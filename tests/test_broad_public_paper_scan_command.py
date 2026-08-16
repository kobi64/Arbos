import argparse

import pytest

import core.broad_public_paper_scan_command as command


class FakeApplication:
    last_ccxt_module = None
    last_run_kwargs = None

    def __init__(self, ccxt_module):
        type(self).last_ccxt_module = (
            ccxt_module
        )

    def run(self, **kwargs):
        type(self).last_run_kwargs = kwargs

        return {
            "route_count": 3,
            "best_route": {
                "route_id": "TEST-ROUTE",
            },
            "production_wiring": True,
            "paper_only": True,
            "live_order_submitted": False,
        }


def args(**overrides):
    values = {
        "exchanges": [
            "gate",
            "kucoin",
        ],
        "coin_limit": 100,
        "starting_usdt": 100.0,
        "max_slippage": 0.5,
        "fee_rate": 0.001,
    }

    values.update(overrides)

    return argparse.Namespace(**values)


def test_runs_broad_application_with_command_arguments(
    monkeypatch,
):
    monkeypatch.setattr(
        command,
        "BroadPublicPaperScanApplication",
        FakeApplication,
    )

    fake_ccxt = object()

    result = command.run_from_args(
        args(),
        ccxt_module=fake_ccxt,
    )

    assert (
        FakeApplication.last_ccxt_module
        is fake_ccxt
    )

    assert (
        FakeApplication.last_run_kwargs
        == {
            "exchange_ids": [
                "gate",
                "kucoin",
            ],
            "fee_rates": {
                "gate": 0.001,
                "kucoin": 0.001,
            },
            "starting_usdt_value": 100.0,
            "max_slippage_percent": 0.5,
            "coin_limit": 100,
        }
    )

    assert result["route_count"] == 3


def test_normalizes_exchange_ids(
    monkeypatch,
):
    monkeypatch.setattr(
        command,
        "BroadPublicPaperScanApplication",
        FakeApplication,
    )

    command.run_from_args(
        args(
            exchanges=[
                " GATE ",
                "KuCoin",
            ]
        ),
        ccxt_module=object(),
    )

    assert (
        FakeApplication.last_run_kwargs[
            "exchange_ids"
        ]
        == [
            "gate",
            "kucoin",
        ]
    )


def test_requires_at_least_two_exchanges():
    with pytest.raises(
        ValueError,
        match="at least two exchanges are required",
    ):
        command.run_from_args(
            args(
                exchanges=["gate"]
            ),
            ccxt_module=object(),
        )


@pytest.mark.parametrize(
    "field,value,message",
    [
        (
            "coin_limit",
            0,
            "coin_limit must be positive",
        ),
        (
            "starting_usdt",
            0,
            "starting_usdt must be positive",
        ),
        (
            "max_slippage",
            -0.1,
            "max_slippage must not be negative",
        ),
        (
            "fee_rate",
            -0.001,
            "fee_rate must not be negative",
        ),
    ],
)
def test_rejects_invalid_numeric_arguments(
    field,
    value,
    message,
):
    kwargs = {
        field: value,
    }

    with pytest.raises(
        ValueError,
        match=message,
    ):
        command.run_from_args(
            args(**kwargs),
            ccxt_module=object(),
        )


def test_command_contract_is_always_paper_only(
    monkeypatch,
):
    class UnsafeLookingFakeApplication:
        def __init__(self, ccxt_module):
            pass

        def run(self, **kwargs):
            return {
                "paper_only": False,
                "live_order_submitted": True,
            }

    monkeypatch.setattr(
        command,
        "BroadPublicPaperScanApplication",
        UnsafeLookingFakeApplication,
    )

    result = command.run_from_args(
        args(),
        ccxt_module=object(),
    )

    assert result["paper_only"] is True
    assert (
        result["live_order_submitted"]
        is False
    )


def test_parser_defaults_to_100_coin_scan():
    parser = command.build_parser()

    parsed = parser.parse_args([])

    assert parsed.coin_limit == 100
    assert parsed.starting_usdt == 100.0
    assert parsed.max_slippage == 0.5
    assert parsed.fee_rate == 0.001
    assert len(parsed.exchanges) >= 2


def test_parser_defaults_to_summary_output():
    parser = command.build_parser()

    parsed = parser.parse_args([])

    assert parsed.output == "summary"
    assert parsed.top == 10


def test_parser_accepts_raw_json_output():
    parser = command.build_parser()

    parsed = parser.parse_args([
        "--output",
        "json",
    ])

    assert parsed.output == "json"


def test_main_prints_summary_by_default(
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(
        command,
        "run_from_args",
        lambda args: {
            "ranked_routes": [],
            "route_count": 0,
            "paper_only": True,
            "live_order_submitted": False,
        },
    )

    exit_code = command.main([])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert '"route_count": 0' in captured.out
    assert '"profitable_route_count": 0' in captured.out
    assert '"paper_only": true' in captured.out


def test_main_can_print_raw_json(
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(
        command,
        "run_from_args",
        lambda args: {
            "raw_marker": "RAW",
            "paper_only": True,
            "live_order_submitted": False,
        },
    )

    exit_code = command.main([
        "--output",
        "json",
    ])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert '"raw_marker": "RAW"' in captured.out
    assert (
        '"profitable_route_count"'
        not in captured.out
    )
