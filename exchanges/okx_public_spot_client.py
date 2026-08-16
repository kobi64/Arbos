"""
ArbOS™
EX-233
OKX Public Spot Client

Read-only client for verified OKX public SPOT endpoints.

Supports:
- public SPOT instruments
- public order books

No authentication.
No transfers.
No live orders.
"""

import requests


class OKXPublicSpotClient:
    def __init__(
        self,
        base_url="https://www.okx.com",
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

        self.read_only = True

    @staticmethod
    def _normalize_symbol(
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

            base = base.strip()
            quote = quote.strip()

            if not base or not quote:
                raise ValueError(
                    "symbol is required"
                )

            return f"{base}-{quote}"

        return symbol

    @staticmethod
    def _validate_limit(
        limit,
    ):
        try:
            limit = int(
                limit
            )
        except Exception as exc:
            raise ValueError(
                "limit must be positive"
            ) from exc

        if limit <= 0:
            raise ValueError(
                "limit must be positive"
            )

        return limit

    def _get(
        self,
        path,
        params=None,
    ):
        try:
            response = (
                self._session.get(
                    (
                        f"{self.base_url}"
                        f"{path}"
                    ),
                    params=params,
                    timeout=(
                        self._timeout_seconds
                    ),
                )
            )

            response.raise_for_status()

            payload = (
                response.json()
            )

            if not isinstance(
                payload,
                dict,
            ):
                raise ValueError(
                    "unexpected OKX payload"
                )

            return payload

        except Exception as exc:
            raise RuntimeError(
                "OKX public request unavailable: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ) from exc

    def fetch_instruments(
        self,
    ):
        return self._get(
            "/api/v5/public/instruments",
            params={
                "instType": "SPOT",
            },
        )

    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        native_symbol = (
            self._normalize_symbol(
                symbol
            )
        )

        limit = self._validate_limit(
            limit
        )

        return self._get(
            "/api/v5/market/books",
            params={
                "instId": native_symbol,
                "sz": str(
                    limit
                ),
            },
        )
