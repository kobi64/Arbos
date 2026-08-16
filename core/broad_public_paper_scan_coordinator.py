"""
ArbOS™
EX-253
Broad Public Paper Scan Coordinator

Discovers a bounded liquid coin universe across configured
public exchanges and passes the resulting exchange/coin map
to the deduplicated unified public paper scanner.

The coordinator deliberately separates universe discovery
from execution-quality route validation.

Paper/public-data infrastructure only.
No authentication.
No transfers.
No live orders.
"""


class BroadPublicPaperScanCoordinator:
    def __init__(
        self,
        bootstrap,
        scanner,
        universe_selector=None,
    ):
        if bootstrap is None:
            raise ValueError(
                "bootstrap is required"
            )

        if universe_selector is None:
            from core.live_coin_universe_selector import (
                LiveCoinUniverseSelector,
            )

            universe_selector = (
                LiveCoinUniverseSelector()
            )

        if scanner is None:
            raise ValueError(
                "scanner is required"
            )

        self._bootstrap = bootstrap
        self._universe_selector = (
            universe_selector
        )
        self._scanner = scanner

    def run(
        self,
        exchange_ids,
        fee_rates,
        coin_limit,
        starting_usdt_value,
        max_slippage_percent,
    ):
        if not exchange_ids:
            raise ValueError(
                "exchange_ids are required"
            )

        if (
            not isinstance(
                coin_limit,
                int,
            )
            or isinstance(
                coin_limit,
                bool,
            )
            or coin_limit <= 0
        ):
            raise ValueError(
                "coin_limit must be positive"
            )

        if starting_usdt_value <= 0:
            raise ValueError(
                "starting_usdt_value must be positive"
            )

        if fee_rates is None:
            raise ValueError(
                "fee_rates are required"
            )

        normalized_exchange_ids = [
            str(exchange_id)
            .strip()
            .lower()
            for exchange_id in exchange_ids
            if str(exchange_id).strip()
        ]

        for exchange_id in normalized_exchange_ids:
            if exchange_id not in fee_rates:
                raise ValueError(
                    "fee rate is required "
                    f"for exchange: {exchange_id}"
                )

        return self.scan(
            exchange_ids=normalized_exchange_ids,
            fee_rates=fee_rates,
            starting_usdt_value=(
                starting_usdt_value
            ),
            max_slippage_percent=(
                max_slippage_percent
            ),
            coin_limit=coin_limit,
        )

    def scan(
        self,
        exchange_ids,
        fee_rates,
        starting_usdt_value,
        max_slippage_percent,
        coin_limit=100,
    ):
        if not exchange_ids:
            raise ValueError(
                "exchange_ids are required"
            )

        if (
            not isinstance(coin_limit, int)
            or isinstance(coin_limit, bool)
            or coin_limit <= 0
        ):
            raise ValueError(
                "coin_limit must be positive"
            )

        normalized_exchange_ids = sorted({
            str(exchange_id)
            .strip()
            .lower()
            for exchange_id in exchange_ids
            if str(exchange_id).strip()
        })

        if len(normalized_exchange_ids) < 2:
            raise ValueError(
                "at least two exchanges are required"
            )

        exchange_coin_assets = {}
        universe_results = {}
        discovery_failures = []

        for exchange_id in normalized_exchange_ids:
            try:
                exchange = (
                    self._bootstrap.create(
                        exchange_id
                    )
                )

                markets = (
                    exchange.load_markets()
                )

                tickers = (
                    exchange.fetch_tickers()
                )

                universe_result = (
                    self._universe_selector.select(
                        exchange_id=exchange_id,
                        markets=markets,
                        tickers=tickers,
                        limit=coin_limit,
                    )
                )

                coins = {
                    str(coin)
                    .strip()
                    .upper()
                    for coin in (
                        universe_result.get(
                            "coin_assets",
                            [],
                        )
                        or []
                    )
                    if str(coin).strip()
                }

                exchange_coin_assets[
                    exchange_id
                ] = coins

                universe_results[
                    exchange_id
                ] = dict(
                    universe_result
                )

            except Exception as exc:
                exchange_coin_assets[
                    exchange_id
                ] = set()

                discovery_failures.append({
                    "exchange_id": (
                        exchange_id
                    ),
                    "reason": (
                        "universe_discovery_failed"
                    ),
                    "error": (
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    ),
                })

        scanner_result = (
            self._scanner.scan(
                exchange_coin_assets=(
                    exchange_coin_assets
                ),
                fee_rates=fee_rates,
                starting_usdt_value=(
                    starting_usdt_value
                ),
                max_slippage_percent=(
                    max_slippage_percent
                ),
            )
        )

        unique_coin_assets = sorted({
            coin
            for coins in (
                exchange_coin_assets.values()
            )
            for coin in coins
        })

        return {
            **scanner_result,
            "exchange_coin_assets": (
                exchange_coin_assets
            ),
            "universe_results": (
                universe_results
            ),
            "discovery_failures": (
                discovery_failures
            ),
            "discovery_failure_count": len(
                discovery_failures
            ),
            "configured_exchange_count": len(
                normalized_exchange_ids
            ),
            "discovered_exchange_count": len(
                universe_results
            ),
            "failed_exchange_count": len(
                discovery_failures
            ),
            "failures": list(
                discovery_failures
            ),
            "exchange_count": len(
                normalized_exchange_ids
            ),
            "unique_coin_count": len(
                unique_coin_assets
            ),
            "unique_coin_assets": (
                unique_coin_assets
            ),
            "coin_limit": coin_limit,
            "paper_only": True,
            "live_order_submitted": False,
        }
