"""
ArbOS™
EX-221
LBank Public Spot Client

Public spot-market transport.

Confirmed live endpoint:
GET https://api.lbkex.com/v2/depth.do

Read-only.
No authentication.
No transfers.
No live orders.
"""

import requests


class LBankPublicSpotClient:
    def __init__(
        self,
        base_url="https://api.lbkex.com",
        session=None,
        timeout_seconds=10.0,
    ):
        self.base_url = str(
            base_url
            or ""
        ).rstrip("/")

        if not self.base_url:
            raise ValueError(
                "base_url is required"
            )

        timeout_seconds = float(
            timeout_seconds
        )

        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be positive"
            )

        self._timeout_seconds = (
            timeout_seconds
        )

        self._session = (
            session
            if session is not None
            else requests.Session()
        )

    @staticmethod
    def normalize_symbol(
        symbol,
    ):
        symbol = str(
            symbol
            or ""
        ).strip().lower()

        if not symbol:
            raise ValueError(
                "symbol is required"
            )

        if "/" in symbol:
            base, quote = symbol.split(
                "/",
                1,
            )

            return (
                f"{base}_{quote}"
            )

        return symbol.replace(
            "-",
            "_",
        )

    def fetch_markets(
        self,
    ):
        try:
            response = self._session.get(
                (
                    f"{self.base_url}"
                    "/v2/currencyPairs.do"
                ),
                params=None,
                timeout=self._timeout_seconds,
            )

            response.raise_for_status()

            payload = response.json()

            if not isinstance(
                payload,
                dict,
            ):
                raise ValueError(
                    "unexpected markets payload"
                )

            if str(
                payload.get(
                    "result",
                    "",
                )
            ).strip().lower() != "true":
                raise ValueError(
                    payload.get(
                        "msg",
                        "exchange_error",
                    )
                )

            markets = payload.get(
                "data"
            )

            if not isinstance(
                markets,
                list,
            ):
                raise ValueError(
                    "unexpected markets payload"
                )

            return {
                "fetch_complete": True,
                "markets": list(
                    markets
                ),
                "market_count": len(
                    markets
                ),
                "reason": None,
                "paper_only": True,
                "live_order_submitted": False,
            }

        except Exception as exc:
            return {
                "fetch_complete": False,
                "markets": [],
                "market_count": 0,
                "reason": (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        symbol = self.normalize_symbol(
            symbol
        )

        limit = int(
            limit
        )

        if limit <= 0:
            raise ValueError(
                "limit must be positive"
            )

        try:
            response = self._session.get(
                f"{self.base_url}/v2/depth.do",
                params={
                    "symbol": symbol,
                    "size": limit,
                },
                timeout=self._timeout_seconds,
            )

            response.raise_for_status()

            payload = response.json()

            if not isinstance(
                payload,
                dict,
            ):
                raise ValueError(
                    "unexpected order book payload"
                )

            if str(
                payload.get(
                    "result",
                    "",
                )
            ).strip().lower() != "true":
                raise ValueError(
                    payload.get(
                        "msg",
                        "exchange_error",
                    )
                )

            data = payload.get(
                "data"
            )

            if not isinstance(
                data,
                dict,
            ):
                raise ValueError(
                    "missing depth data"
                )

            bids = data.get(
                "bids"
            )

            asks = data.get(
                "asks"
            )

            if (
                not isinstance(
                    bids,
                    list,
                )
                or not isinstance(
                    asks,
                    list,
                )
            ):
                raise ValueError(
                    "unexpected depth payload"
                )

            return {
                "fetch_complete": True,
                "symbol": symbol,
                "bids": bids,
                "asks": asks,
                "timestamp": data.get(
                    "timestamp",
                    payload.get(
                        "ts"
                    ),
                ),
                "reason": None,
                "paper_only": True,
                "live_order_submitted": False,
            }

        except Exception as exc:
            return {
                "fetch_complete": False,
                "symbol": symbol,
                "bids": [],
                "asks": [],
                "timestamp": None,
                "reason": (
                    f"{type(exc).__name__}: {exc}"
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }
