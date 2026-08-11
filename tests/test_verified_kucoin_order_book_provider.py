from exchanges.verified_kucoin_order_book_provider import (
    VerifiedKuCoinOrderBookProvider,
)


class FakeExchange:
    id = "kucoin"

    def load_markets(self):
        return {}

    def fetch_order_book(
        self,
        symbol,
        limit=None,
    ):
        raise ValueError(
            "normalized market unavailable"
        )

    def publicGetSymbols(self):
        return {
            "code": "200000",
            "data": [
                {
                    "symbol": "COTI-USDT",
                    "baseCurrency": "COTI",
                    "quoteCurrency": "USDT",
                    "enableTrading": True,
                },
            ],
        }

    def publicGetMarketOrderbookLevel220(
        self,
        params,
    ):
        return {
            "code": "200000",
            "data": {
                "time": 123,
                "sequence": "1",
                "bids": [
                    ["0.00951", "1000"],
                ],
                "asks": [
                    ["0.00953", "1000"],
                ],
            },
        }


def test_uses_verified_native_kucoin_depth():
    provider = VerifiedKuCoinOrderBookProvider(
        FakeExchange()
    )

    result = provider.snapshot(
        "COTI/USDT"
    )

    assert result["market_verified"] is True

    assert result["market_source"] == (
        "VERIFIED_RAW_ONLY_KUCOIN_NATIVE"
    )

    assert result["bids"][0][0] == 0.00951
    assert result["asks"][0][0] == 0.00953
