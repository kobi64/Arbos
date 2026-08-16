"""
ArbOS™
EX-232
Phemex Public Spot Client

Public read-only Phemex spot order-book transport.

Verified spot endpoint:
GET /md/orderbook

Important:
- canonical ArbOS™ symbols such as BTC/USDT are converted
  to Phemex native spot symbols such as sBTCUSDT
- plain BTCUSDT is also interpreted as spot input and
  converted to sBTCUSDT
- the V2 order-book endpoint is not used here because that
  serves Phemex perpetual instruments

No authentication.
No transfers.
No live orders.
"""

import requests


class PhemexPublicSpotClient:
    def __init__(
        self,
        base_url="https://api.phemex.com",
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
        ).strip()

        if not symbol:
            raise ValueError(
                "symbol is required"
            )

        compact = (
            symbol
            .replace(
                "/",
                "",
            )
            .upper()
        )

        if compact.startswith(
            "S"
        ):
            compact = (
                compact[1:]
            )

        if not compact:
            raise ValueError(
                "symbol is required"
            )

        return (
            "s"
            + compact
        )

    def fetch_products(
        self,
    ):
        try:
            response = (
                self._session.get(
                    (
                        f"{self.base_url}"
                        "/public/products"
                    ),
                    params=None,
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
                    "unexpected Phemex "
                    "products payload"
                )

            return payload

        except Exception as exc:
            raise RuntimeError(
                "Phemex public products unavailable: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ) from exc

    def fetch_order_book(
        self,
        symbol,
        limit=30,
    ):
        native_symbol = (
            self._normalize_symbol(
                symbol
            )
        )

        if (
            not isinstance(
                limit,
                int,
            )
            or isinstance(
                limit,
                bool,
            )
            or limit <= 0
        ):
            raise ValueError(
                "limit must be positive"
            )

        try:
            response = (
                self._session.get(
                    (
                        f"{self.base_url}"
                        "/md/orderbook"
                    ),
                    params={
                        "symbol": (
                            native_symbol
                        ),
                    },
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
                    "unexpected Phemex "
                    "order book payload"
                )

            return payload

        except Exception as exc:
            raise RuntimeError(
                "Phemex public spot order book "
                "unavailable: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ) from exc
