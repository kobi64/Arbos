"""
ArbOS™
EX-206
CCXT Pro Multi-Symbol Feed Manager

Manages normalized public market symbols for persistent
CCXT Pro WebSocket market-data feeds.

Public market data only.
No authentication.
No transfers.
No live orders.
"""


class CCXTProMultiSymbolFeedManager:
    def __init__(
        self,
        feed,
        exchange,
        symbols,
        limit=None,
        retry_delay_seconds=1.0,
    ):
        if feed is None:
            raise ValueError("feed is required")

        if exchange is None:
            raise ValueError("exchange is required")

        normalized = []
        seen = set()

        for symbol in symbols or []:
            value = str(symbol).strip().upper()

            if not value:
                continue

            if value in seen:
                continue

            seen.add(value)
            normalized.append(value)

        if not normalized:
            raise ValueError("symbols are required")

        self._feed = feed
        self._exchange = exchange
        self._symbols = normalized
        self._limit = limit
        self._retry_delay_seconds = float(
            retry_delay_seconds
        )

        self._completed_updates = 0
        self._failed_updates = 0
        self._running = False
        self._tasks = []

    @property
    def symbols(self):
        return list(self._symbols)


    async def run_cycles(
        self,
        cycles_per_symbol=1,
    ):
        import asyncio

        if cycles_per_symbol <= 0:
            raise ValueError(
                "cycles_per_symbol must be positive"
            )

        completed_updates = 0
        failed_updates = 0

        async def run_symbol(symbol):
            nonlocal completed_updates
            nonlocal failed_updates

            for _ in range(
                cycles_per_symbol
            ):
                try:
                    await self._feed.watch_once(
                        symbol,
                        limit=self._limit,
                    )
                    completed_updates += 1
                    self._completed_updates += 1
                except Exception:
                    failed_updates += 1
                    self._failed_updates += 1

                    if (
                        self._retry_delay_seconds
                        > 0
                    ):
                        await asyncio.sleep(
                            self._retry_delay_seconds
                        )

        await asyncio.gather(
            *[
                run_symbol(symbol)
                for symbol in self._symbols
            ]
        )

        return {
            "completed_updates": (
                completed_updates
            ),
            "failed_updates": (
                failed_updates
            ),
            "symbol_count": len(
                self._symbols
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }


    def is_running(self):
        return getattr(
            self,
            "_running",
            False,
        )

    async def _persistent_symbol_loop(
        self,
        symbol,
    ):
        import asyncio

        while self._running:
            try:
                await self._feed.watch_once(
                    symbol,
                    limit=self._limit,
                )

                self._completed_updates += 1

            except asyncio.CancelledError:
                raise

            except Exception:
                self._failed_updates += 1

                if (
                    self._retry_delay_seconds
                    > 0
                ):
                    await asyncio.sleep(
                        self._retry_delay_seconds
                    )

    async def start(self):
        import asyncio

        if self.is_running():
            return {
                "started": False,
                "reason": "already_running",
                "paper_only": True,
                "live_order_submitted": False,
            }

        self._running = True

        self._tasks = [
            asyncio.create_task(
                self._persistent_symbol_loop(
                    symbol
                )
            )
            for symbol in self._symbols
        ]

        return {
            "started": True,
            "symbol_count": len(
                self._symbols
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    async def stop(self):
        import asyncio

        self._running = False

        tasks = getattr(
            self,
            "_tasks",
            [],
        )

        for task in tasks:
            task.cancel()

        if tasks:
            await asyncio.gather(
                *tasks,
                return_exceptions=True,
            )

        self._tasks = []

        close = getattr(
            self._exchange,
            "close",
            None,
        )

        if close is not None:
            result = close()

            if hasattr(
                result,
                "__await__",
            ):
                await result

        return {
            "stopped": True,
            "paper_only": True,
            "live_order_submitted": False,
        }


    def statistics(self):
        return {
            "symbols": len(
                self._symbols
            ),
            "completed_updates": (
                self._completed_updates
            ),
            "failed_updates": (
                self._failed_updates
            ),
            "running": self.is_running(),
            "paper_only": True,
            "live_order_submitted": False,
        }
