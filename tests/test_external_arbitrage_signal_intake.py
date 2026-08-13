import pytest

from core.external_arbitrage_signal_intake import (
    ExternalArbitrageSignalIntake,
)


def signal(
    signal_key="coinmarketgap:CMG-001",
):
    return {
        "signal_key": signal_key,
        "source": "coinmarketgap",
        "source_signal_id": "CMG-001",
        "coin": "COTI",
        "buy_exchange": "gate",
        "sell_exchange": "kucoin",
        "reported_status": "exploitable",
        "verification_required": True,
        "arbos_verified": False,
        "executable": False,
    }


def test_accepts_new_external_signal():
    intake = ExternalArbitrageSignalIntake()

    result = intake.submit(
        signal()
    )

    assert result["accepted"] is True

    assert result[
        "signal_key"
    ] == "coinmarketgap:CMG-001"

    assert result[
        "verification_required"
    ] is True


def test_rejects_duplicate_signal_key():
    intake = ExternalArbitrageSignalIntake()

    intake.submit(
        signal()
    )

    result = intake.submit(
        signal()
    )

    assert result["accepted"] is False

    assert result[
        "reason"
    ] == "duplicate_external_signal"


def test_different_sources_can_submit_same_coin_route():
    intake = ExternalArbitrageSignalIntake()

    first = signal(
        "coinmarketgap:CMG-001"
    )

    second = signal(
        "arbihunt:AH-001"
    )

    second["source"] = "arbihunt"
    second[
        "source_signal_id"
    ] = "AH-001"

    assert intake.submit(
        first
    )["accepted"] is True

    assert intake.submit(
        second
    )["accepted"] is True


def test_missing_signal_key_is_rejected():
    intake = ExternalArbitrageSignalIntake()

    bad = signal()
    bad.pop(
        "signal_key"
    )

    with pytest.raises(
        ValueError,
        match="signal_key is required",
    ):
        intake.submit(
            bad
        )


def test_statistics_track_received_accepted_and_duplicates():
    intake = ExternalArbitrageSignalIntake()

    intake.submit(
        signal()
    )

    intake.submit(
        signal()
    )

    intake.submit(
        signal(
            "coinmarketgap:CMG-002"
        )
    )

    stats = intake.statistics()

    assert stats["received"] == 3
    assert stats["accepted"] == 2
    assert stats["duplicates"] == 1


def test_intake_never_marks_external_signal_executable():
    intake = ExternalArbitrageSignalIntake()

    external = signal()
    external["executable"] = True
    external["arbos_verified"] = True

    result = intake.submit(
        external
    )

    assert result[
        "arbos_verified"
    ] is False

    assert result[
        "executable"
    ] is False

    assert result[
        "verification_required"
    ] is True


def test_intake_is_paper_safe():
    intake = ExternalArbitrageSignalIntake()

    result = intake.submit(
        signal()
    )

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False
