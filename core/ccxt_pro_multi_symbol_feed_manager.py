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
        health_supervisor=None,
        backoff_policy=None,
        cycle_timeout_seconds=10.0,
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

        self._health_supervisor = (
            health_supervisor
        )

        self._backoff_policy = (
            backoff_policy
        )

        self._cycle_timeout_seconds = float(
            cycle_timeout_seconds
        )

        if self._cycle_timeout_seconds <= 0:
            raise ValueError(
                "cycle_timeout_seconds must be positive"
            )

        self._completed_updates = 0
        self._failed_updates = 0
        self._running = False
        self._tasks = {}

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
                    await asyncio.wait_for(
                        self._feed.watch_once(
                            symbol,
                            limit=self._limit,
                        ),
                        timeout=(
                            self._cycle_timeout_seconds
                        ),
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

        loop = asyncio.get_running_loop()

        exchange_id = str(
            getattr(
                self._exchange,
                "id",
                "",
            )
            or ""
        ).strip().lower()

        failure_attempt = 0

        while self._running:
            started = loop.time()

            try:
                await self._feed.watch_once(
                    symbol,
                    limit=self._limit,
                )

                latency_ms = (
                    loop.time()
                    - started
                ) * 1000.0

                self._completed_updates += 1
                failure_attempt = 0

                if (
                    self._health_supervisor
                    is not None
                ):
                    self._health_supervisor.record_success(
                        exchange_id=exchange_id,
                        symbol=symbol,
                        latency_ms=latency_ms,
                    )

            except asyncio.CancelledError:
                raise

            except Exception as exc:
                latency_ms = (
                    loop.time()
                    - started
                ) * 1000.0

                self._failed_updates += 1
                failure_attempt += 1

                if (
                    self._health_supervisor
                    is not None
                ):
                    self._health_supervisor.record_failure(
                        exchange_id=exchange_id,
                        symbol=symbol,
                        latency_ms=latency_ms,
                        reason=(
                            f"{type(exc).__name__}: {exc}"
                        ),
                    )

                retry = True
                delay_seconds = (
                    self._retry_delay_seconds
                )

                if (
                    self._backoff_policy
                    is not None
                ):
                    policy = (
                        self._backoff_policy.evaluate(
                            attempt=failure_attempt,
                            error_type="NETWORK_ERROR",
                            execution_uncertain=False,
                        )
                    )

                    retry = (
                        policy.get(
                            "retry"
                        )
                        is True
                    )

                    delay_seconds = float(
                        policy.get(
                            "delay_seconds",
                            0.0,
                        )
                        or 0.0
                    )

                if not retry:
                    break

                if delay_seconds > 0:
                    await asyncio.sleep(
                        delay_seconds
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

        self._tasks = {
            symbol: asyncio.create_task(
                self._persistent_symbol_loop(
                    symbol
                )
            )
            for symbol in self._symbols
        }

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
            {},
        )

        for task in tasks.values():
            task.cancel()

        if tasks:
            await asyncio.gather(
                *tasks.values(),
                return_exceptions=True,
            )

        self._tasks = {}

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


    def health_snapshot(self):
        if self._health_supervisor is None:
            raise ValueError(
                "health_supervisor is required"
            )

        exchange_id = str(
            getattr(
                self._exchange,
                "id",
                "",
            )
            or ""
        ).strip().lower()

        symbol_health = {}
        healthy_symbols = []
        unhealthy_symbols = []

        for symbol in self._symbols:
            result = (
                self._health_supervisor
                .check_symbol(
                    exchange_id=exchange_id,
                    symbol=symbol,
                )
            )

            record = dict(result)

            symbol_health[
                symbol
            ] = record

            if (
                record.get(
                    "healthy"
                )
                is True
            ):
                healthy_symbols.append(
                    symbol
                )
            else:
                unhealthy_symbols.append(
                    symbol
                )

        return {
            "exchange_id": exchange_id,
            "symbol_count": len(
                self._symbols
            ),
            "healthy_symbol_count": len(
                healthy_symbols
            ),
            "unhealthy_symbol_count": len(
                unhealthy_symbols
            ),
            "healthy_symbols": (
                healthy_symbols
            ),
            "unhealthy_symbols": (
                unhealthy_symbols
            ),
            "symbols": symbol_health,
            "paper_only": True,
            "live_order_submitted": False,
        }


    async def apply_symbol_rotation(
        self,
        active_symbols,
    ):
        import asyncio

        normalized = []
        seen = set()

        for symbol in active_symbols or []:
            value = str(
                symbol
                or ""
            ).strip().upper()

            if not value:
                continue

            if value in seen:
                continue

            seen.add(value)
            normalized.append(value)

        if not normalized:
            raise ValueError(
                "active_symbols are required"
            )

        current = list(
            self._symbols
        )

        current_set = set(
            current
        )

        target_set = set(
            normalized
        )

        removed_symbols = [
            symbol
            for symbol in current
            if symbol not in target_set
        ]

        added_symbols = [
            symbol
            for symbol in normalized
            if symbol not in current_set
        ]

        if self.is_running():
            removed_tasks = []

            for symbol in removed_symbols:
                task = self._tasks.pop(
                    symbol,
                    None,
                )

                if task is None:
                    continue

                task.cancel()
                removed_tasks.append(
                    task
                )

            if removed_tasks:
                await asyncio.gather(
                    *removed_tasks,
                    return_exceptions=True,
                )

            for symbol in added_symbols:
                self._tasks[
                    symbol
                ] = asyncio.create_task(
                    self._persistent_symbol_loop(
                        symbol
                    )
                )

        self._symbols = normalized

        return {
            "updated": True,
            "removed_symbols": (
                removed_symbols
            ),
            "added_symbols": (
                added_symbols
            ),
            "active_symbols": list(
                self._symbols
            ),
            "active_symbol_count": len(
                self._symbols
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
