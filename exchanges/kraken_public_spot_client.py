"""
ArbOS™
EX-223
Kraken Public Spot Client

Public spot-market transport.

Confirmed live endpoint:
GET https://api.kraken.com/0/public/Depth

Read-only.
No authentication.
No transfers.
No live orders.
"""

import requests


class KrakenPublicSpotClient:
    def __init__(
        self,
        base_url="https://api.kraken.com",
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

        if "/" in symbol:
            base, quote = symbol.split(
                "/",
                1,
            )

            return f"{base}{quote}"

        return (
            symbol
            .replace("-", "")
            .replace("_", "")
        )

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
                (
                    f"{self.base_url}"
                    "/0/public/Depth"
                ),
                params={
                    "pair": symbol,
                    "count": limit,
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

            errors = payload.get(
                "error"
            )

            if errors:
                raise ValueError(
                    "; ".join(
                        str(item)
                        for item in errors
                    )
                )

            result = payload.get(
                "result"
            )

            if (
                not isinstance(
                    result,
                    dict,
                )
                or not result
            ):
                raise ValueError(
                    "missing order book result"
                )

            book = next(
                iter(
                    result.values()
                )
            )

            if not isinstance(
                book,
                dict,
            ):
                raise ValueError(
                    "unexpected order book result"
                )

            bids = book.get(
                "bids"
            )

            asks = book.get(
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
