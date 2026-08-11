from exchanges.native_depth_usability_sampler import (
    NativeDepthUsabilitySampler,
)


class FakeProvider:
    def __init__(self, failing=None):
        self._failing = set(failing or [])

    def snapshot(self, symbol):
        if symbol in self._failing:
            raise ValueError("depth unavailable")

        return {
            "symbol": symbol,
            "bids": [[1.0, 10.0]],
            "asks": [[1.1, 10.0]],
            "market_source": "VERIFIED_RAW_ONLY_TEST_NATIVE",
        }


def test_samples_verified_raw_only_depth():
    sampler = NativeDepthUsabilitySampler()

    result = sampler.sample(
        symbols=[
            "AAA/USDT",
            "BBB/USDT",
        ],
        provider=FakeProvider(),
        sample_size=10,
    )

    assert result["sampled_count"] == 2
    assert result["usable_depth_count"] == 2
    assert result["failed_depth_count"] == 0
    assert result["usable_depth_ratio"] == 1.0


def test_records_failed_depth():
    sampler = NativeDepthUsabilitySampler()

    result = sampler.sample(
        symbols=[
            "AAA/USDT",
            "BBB/USDT",
        ],
        provider=FakeProvider(
            failing={"BBB/USDT"}
        ),
        sample_size=10,
    )

    assert result["sampled_count"] == 2
    assert result["usable_depth_count"] == 1
    assert result["failed_depth_count"] == 1
    assert result["usable_depth_ratio"] == 0.5

    assert result["failed_symbols"] == [
        "BBB/USDT",
    ]


def test_respects_sample_size():
    sampler = NativeDepthUsabilitySampler()

    result = sampler.sample(
        symbols=[
            "AAA/USDT",
            "BBB/USDT",
            "CCC/USDT",
        ],
        provider=FakeProvider(),
        sample_size=2,
    )

    assert result["sampled_count"] == 2


def test_empty_symbols_returns_empty_result():
    sampler = NativeDepthUsabilitySampler()

    result = sampler.sample(
        symbols=[],
        provider=FakeProvider(),
        sample_size=10,
    )

    assert result["sampled_count"] == 0
    assert result["usable_depth_ratio"] == 0.0


def test_sampler_is_research_only():
    sampler = NativeDepthUsabilitySampler()

    result = sampler.sample(
        symbols=["AAA/USDT"],
        provider=FakeProvider(),
        sample_size=1,
    )

    assert result["sampling_complete"] is True
    assert result["live_order_submitted"] is False
