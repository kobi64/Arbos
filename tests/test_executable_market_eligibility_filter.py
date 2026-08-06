from core.executable_market_eligibility_filter import (
    ExecutableMarketEligibilityFilter,
)


def sample_markets():
    return {
        "BTC/USDT": {
            "spot": True,
            "active": True,
        },
        "ADA/BTC": {
            "spot": True,
            "active": True,
        },
        "AAVE/BTC": {
            "spot": True,
            "active": False,
        },
        "ETH/USDT:USDT": {
            "spot": False,
            "active": True,
        },
    }


def test_keeps_only_active_spot_markets():
    eligibility = ExecutableMarketEligibilityFilter()

    result = eligibility.filter(sample_markets())

    assert set(result) == {
        "BTC/USDT",
        "ADA/BTC",
    }


def test_preserves_original_market_metadata():
    markets = sample_markets()

    eligibility = ExecutableMarketEligibilityFilter()

    result = eligibility.filter(markets)

    assert result["BTC/USDT"] is markets["BTC/USDT"]


def test_missing_active_state_is_not_eligible():
    markets = {
        "BTC/USDT": {
            "spot": True,
        },
    }

    eligibility = ExecutableMarketEligibilityFilter()

    result = eligibility.filter(markets)

    assert result == {}


def test_inactive_market_is_not_eligible():
    markets = {
        "AAVE/BTC": {
            "spot": True,
            "active": False,
        },
    }

    eligibility = ExecutableMarketEligibilityFilter()

    result = eligibility.filter(markets)

    assert result == {}
