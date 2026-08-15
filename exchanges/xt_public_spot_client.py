"""
ArbOS™
EX-230
XT Public Spot Client

Public read-only XT spot market transport.

Endpoint:
GET /v4/public/depth

No authentication.
No transfers.
No live orders.
"""

import requests


class XTPublicSpotClient:
    def __init__(
        self,
        base_url="https://sapi.xt.com",
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

        return (
            symbol
            .replace("/", "_")
            .strip()
            .lower()
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

        if (
            not isinstance(limit, int)
            or isinstance(limit, bool)
            or limit <= 0
        ):
            raise ValueError(
                "limit must be positive"
            )

        try:
            response = self._session.get(
                (
                    f"{self.base_url}"
                    "/v4/public/depth"
                ),
                params={
                    "symbol": native_symbol,
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
                    "unexpected XT order book payload"
                )

            return payload

        except Exception as exc:
            raise RuntimeError(
                "XT public order book unavailable: "
                f"{type(exc).__name__}: {exc}"
            ) from exc
