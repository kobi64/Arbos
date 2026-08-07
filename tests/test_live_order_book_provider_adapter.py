from core.live_order_book_provider_adapter import (
    LiveOrderBookProviderAdapter,
)


class FakeSnapshotEngine:
    def snapshot(self, symbol):
        return {
            "symbol": symbol,
            "bids": [[100.0, 2.0]],
            "asks": [[101.0, 2.0]],
        }


def test_exposes_snapshot_as_get_order_book():
    adapter = LiveOrderBookProviderAdapter(
        FakeSnapshotEngine()
    )

    result = adapter.get_order_book("BTC/USDT")

    assert result["symbol"] == "BTC/USDT"
    assert result["bids"][0] == [100.0, 2.0]
    assert result["asks"][0] == [101.0, 2.0]
