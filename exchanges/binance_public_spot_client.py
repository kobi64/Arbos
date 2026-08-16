"""
ArbOS™
EX-234
Binance Public Spot Client

Read-only client for verified Binance public SPOT endpoints.

Supports:
- exchange information
- order book depth
- book ticker verification

No authentication.
No transfers.
No live orders.
"""

import requests


class BinancePublicSpotClient:
    def __init__(
        self,
        base_url="https://api.binance.com",
        session=None,
        timeout=10.0,
    ):
        self.base_url = str(
            base_url
            or ""
        ).rstrip("/")

        if not self.base_url:
            raise ValueError(
                "base_url is required"
            )

        timeout = float(
            timeout
        )

        if timeout <= 0:
            raise ValueError(
                "timeout must be positive"
            )

        self._timeout = timeout

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

        return (
            symbol
            .replace("/", "")
            .replace("-", "")
        )

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
                    timeout=self._timeout,
                )
            )

            response.raise_for_status()

            payload = response.json()

            if not isinstance(
                payload,
                dict,
            ):
                raise ValueError(
                    "unexpected Binance payload"
                )

            return payload

        except Exception as exc:
            raise RuntimeError(
                "Binance public request unavailable: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ) from exc

    def fetch_exchange_info(
        self,
    ):
        return self._get(
            "/api/v3/exchangeInfo"
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

        return self._get(
            "/api/v3/depth",
            params={
                "symbol": native_symbol,
                "limit": limit,
            },
        )

    def fetch_book_ticker(
        self,
        symbol,
    ):
        native_symbol = (
            self._normalize_symbol(
                symbol
            )
        )

        return self._get(
            "/api/v3/ticker/bookTicker",
            params={
                "symbol": native_symbol,
            },
        )
