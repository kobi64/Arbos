"""
ArbOS™
EX-218
Poloniex Public Spot Client

Public market/reference data only.
No authentication.
No transfers.
No live orders.
"""

import requests


class PoloniexPublicSpotClient:
    BASE_URL = "https://api.poloniex.com"

    def __init__(
        self,
        session=None,
        timeout_seconds=10.0,
    ):
        timeout_seconds = float(
            timeout_seconds
        )

        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be positive"
            )

        self._session = (
            session
            if session is not None
            else requests.Session()
        )

        self._timeout_seconds = (
            timeout_seconds
        )

    def _get(
        self,
        path,
        result_key,
    ):
        try:
            response = self._session.get(
                f"{self.BASE_URL}{path}",
                timeout=self._timeout_seconds,
            )

            response.raise_for_status()

            payload = response.json()

            if not isinstance(
                payload,
                list,
            ):
                raise ValueError(
                    "unexpected response payload"
                )

            return {
                "fetch_complete": True,
                result_key: payload,
                "reason": None,
                "paper_only": True,
                "live_order_submitted": False,
            }

        except Exception as exc:
            return {
                "fetch_complete": False,
                result_key: [],
                "reason": (
                    f"{type(exc).__name__}: {exc}"
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

    def fetch_markets(
        self,
    ):
        return self._get(
            "/markets",
            "markets",
        )

    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        symbol = str(
            symbol
            or ""
        ).strip().upper()

        if not symbol:
            raise ValueError(
                "symbol is required"
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
                (
                    f"{self.BASE_URL}/markets/"
                    f"{symbol}/orderBook"
                ),
                params={
                    "limit": limit,
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
                    "unexpected response payload"
                )

            asks = payload.get(
                "asks"
            )

            bids = payload.get(
                "bids"
            )

            if (
                not isinstance(
                    asks,
                    list,
                )
                or not isinstance(
                    bids,
                    list,
                )
            ):
                raise ValueError(
                    "unexpected order book payload"
                )

            return {
                "fetch_complete": True,
                "symbol": symbol,
                "time": payload.get(
                    "time"
                ),
                "scale": payload.get(
                    "scale"
                ),
                "asks": asks,
                "bids": bids,
                "reason": None,
                "paper_only": True,
                "live_order_submitted": False,
            }

        except Exception as exc:
            return {
                "fetch_complete": False,
                "symbol": symbol,
                "asks": [],
                "bids": [],
                "reason": (
                    f"{type(exc).__name__}: {exc}"
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

    def fetch_currencies(
        self,
    ):
        return self._get(
            "/v2/currencies",
            "currencies",
        )
