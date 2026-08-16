"""
ArbOS™
EX-219
MEXC Public Spot Client

Public spot-market transport.

Read-only.
No authentication.
No transfers.
No live orders.
"""

import requests


class MexcPublicSpotClient:
    def __init__(
        self,
        base_url="https://api.mexc.com",
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
        ).strip().upper()

        if not symbol:
            raise ValueError(
                "symbol is required"
            )

        return (
            symbol
            .replace("/", "")
            .replace("_", "")
            .replace("-", "")
        )

    def fetch_exchange_info(
        self,
    ):
        try:
            response = self._session.get(
                (
                    f"{self.base_url}"
                    "/api/v3/exchangeInfo"
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
                    "unexpected exchange info payload"
                )

            symbols = payload.get(
                "symbols"
            )

            if not isinstance(
                symbols,
                list,
            ):
                raise ValueError(
                    "unexpected exchange info symbols"
                )

            return {
                "fetch_complete": True,
                "symbols": symbols,
                "reason": None,
                "paper_only": True,
                "live_order_submitted": False,
            }

        except Exception as exc:
            return {
                "fetch_complete": False,
                "symbols": [],
                "reason": (
                    f"{type(exc).__name__}: {exc}"
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
                f"{self.base_url}/api/v3/depth",
                params={
                    "symbol": symbol,
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
                    "unexpected order book payload"
                )

            bids = payload.get(
                "bids"
            )

            asks = payload.get(
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
                    "unexpected order book payload"
                )

            return {
                "fetch_complete": True,
                "symbol": symbol,
                "last_update_id": (
                    payload.get(
                        "lastUpdateId"
                    )
                ),
                "bids": bids,
                "asks": asks,
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
                "reason": (
                    f"{type(exc).__name__}: {exc}"
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }
