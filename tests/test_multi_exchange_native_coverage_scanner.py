from exchanges.multi_exchange_native_coverage_scanner import (
    MultiExchangeNativeCoverageScanner,
)


class FakeFallbackRegistry:
    def __init__(self, supported):
        self._supported = set(supported)

    def has(self, exchange_id):
        return exchange_id in self._supported


class FakeExchange:
    def __init__(self, exchange_id, markets):
        self.id = exchange_id
        self._markets = markets

    def load_markets(self):
        return self._markets


class FakeNativeSource:
    def __init__(self, result):
        self._result = result

    def fetch(self):
        return self._result


def active_spot(symbol):
    return {
        symbol: {
            "id": symbol.replace("/", "-"),
            "spot": True,
            "active": True,
        }
    }


def test_scans_multiple_exchanges():
    scanner = MultiExchangeNativeCoverageScanner(
        fallback_registry=FakeFallbackRegistry(
            {"kucoin", "digifinex"}
        )
    )

    result = scanner.scan(
        [
            {
                "exchange": FakeExchange(
                    "kucoin",
                    active_spot("BTC/USDT"),
                ),
                "native_market_source": FakeNativeSource({
                    "fetch_complete": True,
                    "symbols": [
                        "BTC/USDT",
                        "AAA/USDT",
                    ],
                    "markets": [
                        {
                            "symbol": "BTC/USDT",
                            "status": "TRADING",
                            "order_types": [
                                "LIMIT",
                                "MARKET",
                            ],
                            "raw": {
                                "symbol": "BTC-USDT",
                            },
                        },
                        {
                            "symbol": "AAA/USDT",
                            "status": "TRADING",
                            "order_types": [
                                "LIMIT",
                                "MARKET",
                            ],
                            "raw": {
                                "symbol": "AAA-USDT",
                            },
                        },
                    ],
                }),
            },
            {
                "exchange": FakeExchange(
                    "digifinex",
                    active_spot("ETH/USDT"),
                ),
                "native_market_source": FakeNativeSource({
                    "fetch_complete": True,
                    "symbols": [
                        "ETH/USDT",
                    ],
                    "markets": [
                        {
                            "symbol": "ETH/USDT",
                            "status": "TRADING",
                            "order_types": [
                                "LIMIT",
                                "MARKET",
                            ],
                            "raw": {
                                "symbol": "ETH-USDT",
                            },
                        },
                    ],
                }),
            },
        ]
    )

    assert result["exchange_count"] == 2
    assert len(result["audits"]) == 2
    assert result["scan_complete"] is True
    assert result["live_order_submitted"] is False


def test_ranks_by_verified_raw_only_count():
    scanner = MultiExchangeNativeCoverageScanner(
        fallback_registry=FakeFallbackRegistry(
            {"kucoin", "digifinex"}
        )
    )

    result = scanner.scan(
        [
            {
                "exchange": FakeExchange(
                    "digifinex",
                    active_spot("ETH/USDT"),
                ),
                "native_market_source": FakeNativeSource({
                    "fetch_complete": True,
                    "symbols": [
                        "ETH/USDT",
                    ],
                    "markets": [
                        {
                            "symbol": "ETH/USDT",
                            "status": "TRADING",
                            "order_types": [
                                "LIMIT",
                            ],
                            "raw": {
                                "symbol": "ETH-USDT",
                            },
                        },
                    ],
                }),
            },
            {
                "exchange": FakeExchange(
                    "kucoin",
                    active_spot("BTC/USDT"),
                ),
                "native_market_source": FakeNativeSource({
                    "fetch_complete": True,
                    "symbols": [
                        "BTC/USDT",
                        "AAA/USDT",
                        "BBB/USDT",
                    ],
                    "markets": [
                        {
                            "symbol": "BTC/USDT",
                            "status": "TRADING",
                            "order_types": [
                                "LIMIT",
                            ],
                            "raw": {
                                "symbol": "BTC-USDT",
                            },
                        },
                        {
                            "symbol": "AAA/USDT",
                            "status": "TRADING",
                            "order_types": [
                                "LIMIT",
                            ],
                            "raw": {
                                "symbol": "AAA-USDT",
                            },
                        },
                        {
                            "symbol": "BBB/USDT",
                            "status": "TRADING",
                            "order_types": [
                                "LIMIT",
                            ],
                            "raw": {
                                "symbol": "BBB-USDT",
                            },
                        },
                    ],
                }),
            },
        ]
    )

    ranked = result["ranked_exchanges"]

    assert ranked[0]["exchange_id"] == "kucoin"
    assert ranked[0]["verified_raw_only_count"] == 2
    assert ranked[1]["exchange_id"] == "digifinex"
    assert ranked[1]["verified_raw_only_count"] == 0


def test_records_failed_native_fetch_without_aborting_scan():
    scanner = MultiExchangeNativeCoverageScanner(
        fallback_registry=FakeFallbackRegistry(
            {"kucoin"}
        )
    )

    result = scanner.scan(
        [
            {
                "exchange": FakeExchange(
                    "kucoin",
                    active_spot("BTC/USDT"),
                ),
                "native_market_source": FakeNativeSource({
                    "fetch_complete": False,
                    "symbols": [],
                    "markets": [],
                }),
            },
        ]
    )

    audit = result["audits"][0]

    assert audit["native_fetch_complete"] is False
    assert audit["audit_complete"] is False
    assert audit["fallback_coverage"] == "UNKNOWN"


def test_requires_entries():
    scanner = MultiExchangeNativeCoverageScanner(
        fallback_registry=FakeFallbackRegistry(
            set()
        )
    )

    try:
        scanner.scan(None)
        assert False
    except ValueError as exc:
        assert str(exc) == "entries are required"


def test_samples_verified_native_depth_when_provider_supplied():
    class FakeProvider:
        def snapshot(self, symbol):
            if symbol == "BBB/USDT":
                raise ValueError(
                    "depth unavailable"
                )

            return {
                "bids": [[1.0, 10.0]],
                "asks": [[1.1, 10.0]],
            }

    scanner = MultiExchangeNativeCoverageScanner(
        fallback_registry=FakeFallbackRegistry(
            {"kucoin"}
        )
    )

    result = scanner.scan([
        {
            "exchange": FakeExchange(
                "kucoin",
                active_spot("BTC/USDT"),
            ),
            "native_market_source": FakeNativeSource({
                "fetch_complete": True,
                "symbols": [
                    "BTC/USDT",
                    "AAA/USDT",
                    "BBB/USDT",
                ],
                "markets": [
                    {
                        "symbol": "BTC/USDT",
                        "status": "TRADING",
                        "order_types": ["LIMIT"],
                        "raw": {
                            "symbol": "BTC-USDT",
                        },
                    },
                    {
                        "symbol": "AAA/USDT",
                        "status": "TRADING",
                        "order_types": ["LIMIT"],
                        "raw": {
                            "symbol": "AAA-USDT",
                        },
                    },
                    {
                        "symbol": "BBB/USDT",
                        "status": "TRADING",
                        "order_types": ["LIMIT"],
                        "raw": {
                            "symbol": "BBB-USDT",
                        },
                    },
                ],
            }),
            "order_book_provider": FakeProvider(),
            "depth_sample_size": 10,
        },
    ])

    audit = result["audits"][0]

    assert audit["depth_sampled_count"] == 2
    assert audit["usable_depth_count"] == 1
    assert audit["failed_depth_count"] == 1
    assert audit["usable_depth_ratio"] == 0.5


def test_exchange_failure_does_not_abort_other_exchanges():
    class FailingExchange:
        id = "kucoin"

        def load_markets(self):
            raise TimeoutError(
                "public API timeout"
            )

    scanner = MultiExchangeNativeCoverageScanner(
        fallback_registry=FakeFallbackRegistry(
            {"kucoin", "digifinex"}
        )
    )

    result = scanner.scan([
        {
            "exchange": FailingExchange(),
            "native_market_source": FakeNativeSource({
                "fetch_complete": True,
                "symbols": [],
                "markets": [],
            }),
        },
        {
            "exchange": FakeExchange(
                "digifinex",
                active_spot("ETH/USDT"),
            ),
            "native_market_source": FakeNativeSource({
                "fetch_complete": True,
                "symbols": [
                    "ETH/USDT",
                ],
                "markets": [
                    {
                        "symbol": "ETH/USDT",
                        "status": "TRADING",
                        "order_types": [
                            "LIMIT",
                            "MARKET",
                        ],
                        "raw": {
                            "symbol": "ETH-USDT",
                        },
                    },
                ],
            }),
        },
    ])

    assert result["exchange_count"] == 2

    assert result["successful_exchange_count"] == 1
    assert result["failed_exchange_count"] == 1

    failed = result["failed_exchanges"]

    assert len(failed) == 1
    assert failed[0]["exchange_id"] == "kucoin"
    assert failed[0]["scan_failed"] is True
    assert failed[0]["error_type"] == "TimeoutError"

    successful = [
        audit
        for audit in result["audits"]
        if audit.get("scan_failed") is not True
    ]

    assert len(successful) == 1
    assert successful[0]["exchange_id"] == "digifinex"

    assert result["scan_complete"] is True
    assert result["live_order_submitted"] is False
