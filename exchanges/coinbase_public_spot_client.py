"""
ArbOS™
EX-235
Coinbase Public Spot Client

Read-only client for verified Coinbase Exchange public endpoints.

Supports:
- products
- Level 2 order books
- product ticker
- currencies / supported networks

No authentication.
No transfers.
No live orders.
"""

import requests


class CoinbasePublicSpotClient:
    def __init__(
        self,
        base_url="https://api.exchange.coinbase.com",
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
    def _normalize_product_id(
        product_id,
    ):
        product_id = str(
            product_id
            or ""
        ).strip().upper()

        if not product_id:
            raise ValueError(
                "product_id is required"
            )

        return (
            product_id
            .replace("/", "-")
            .replace("_", "-")
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
                    headers={
                        "User-Agent": "ArbOS/EX-235",
                        "Accept": "application/json",
                    },
                )
            )

            response.raise_for_status()

            return response.json()

        except Exception as exc:
            raise RuntimeError(
                "Coinbase public request unavailable: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ) from exc

    def fetch_products(
        self,
    ):
        payload = self._get(
            "/products"
        )

        if not isinstance(
            payload,
            list,
        ):
            raise RuntimeError(
                "Coinbase public request unavailable: "
                "unexpected products payload"
            )

        return payload

    def fetch_order_book(
        self,
        product_id,
        level=2,
    ):
        product_id = (
            self._normalize_product_id(
                product_id
            )
        )

        try:
            level = int(
                level
            )
        except Exception as exc:
            raise ValueError(
                "level must be positive"
            ) from exc

        if level <= 0:
            raise ValueError(
                "level must be positive"
            )

        payload = self._get(
            (
                f"/products/"
                f"{product_id}"
                f"/book"
            ),
            params={
                "level": level,
            },
        )

        if not isinstance(
            payload,
            dict,
        ):
            raise RuntimeError(
                "Coinbase public request unavailable: "
                "unexpected order book payload"
            )

        return payload

    def fetch_ticker(
        self,
        product_id,
    ):
        product_id = (
            self._normalize_product_id(
                product_id
            )
        )

        payload = self._get(
            (
                f"/products/"
                f"{product_id}"
                f"/ticker"
            )
        )

        if not isinstance(
            payload,
            dict,
        ):
            raise RuntimeError(
                "Coinbase public request unavailable: "
                "unexpected ticker payload"
            )

        return payload

    def fetch_currencies(
        self,
    ):
        payload = self._get(
            "/currencies"
        )

        if not isinstance(
            payload,
            list,
        ):
            raise RuntimeError(
                "Coinbase public request unavailable: "
                "unexpected currencies payload"
            )

        return payload
