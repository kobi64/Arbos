from core.ex373_sustained_multi_cycle_feed_benchmark import (
    CYCLES_PER_SYMBOL,
    EXCHANGE_IDS,
    RECOVERY_ATTEMPTS,
    RECOVERY_DELAY_SECONDS,
    REQUESTED_COINS,
)


def test_ex373_uses_100_coin_sustained_workload():
    assert REQUESTED_COINS == 100
    assert CYCLES_PER_SYMBOL == 5


def test_ex373_uses_nine_exchanges():
    assert len(EXCHANGE_IDS) == 9
    assert len(set(EXCHANGE_IDS)) == 9


def test_ex373_preserves_bounded_recovery_policy():
    assert RECOVERY_ATTEMPTS["kucoin"] == 2

    for exchange_id in EXCHANGE_IDS:
        if exchange_id != "kucoin":
            assert (
                RECOVERY_ATTEMPTS[
                    exchange_id
                ]
                == 1
            )


def test_ex373_preserves_recovery_delay():
    assert set(
        RECOVERY_DELAY_SECONDS
    ) == set(EXCHANGE_IDS)

    assert all(
        delay == 1.0
        for delay
        in RECOVERY_DELAY_SECONDS.values()
    )


def test_ex373_expected_update_math():
    # EX-372 established 543 subscriptions
    # for this bounded nine-exchange topology.
    subscription_count = 543

    expected_updates = (
        subscription_count
        * CYCLES_PER_SYMBOL
    )

    assert expected_updates == 2715


def test_ex373_preserves_ex372_subscription_pacing_profile():
    from core.ex373_sustained_multi_cycle_feed_benchmark import (
        SUBSCRIPTION_START_STAGGER_SECONDS,
    )

    assert SUBSCRIPTION_START_STAGGER_SECONDS == {
        "binance": 0.5,
        "bitget": 0.10,
        "gate": 0.10,
        "kucoin": 0.25,
        "poloniex": 0.10,
        "xt": 1.00,
    }


def test_ex373_uses_venue_specific_timeouts_for_slow_feeds():
    from core.ex373_sustained_multi_cycle_feed_benchmark import (
        CYCLE_TIMEOUT_SECONDS,
    )

    assert CYCLE_TIMEOUT_SECONDS["poloniex"] == 30.0
    assert CYCLE_TIMEOUT_SECONDS["coinex"] == 20.0

    # Preserve previously tuned profiles.
    assert CYCLE_TIMEOUT_SECONDS["kucoin"] == 20.0
    assert CYCLE_TIMEOUT_SECONDS["xt"] == 30.0
    assert CYCLE_TIMEOUT_SECONDS["binance"] == 30.0
