"""
ArbOS™
EX-229
Bitget Network Metadata Client

Public read-only coin/network metadata transport.

Endpoint:
GET /api/v2/spot/public/coins

No authentication.
No withdrawals.
No transfers.
No live orders.
"""

import requests


class BitgetNetworkMetadataClient:
    def __init__(
        self,
        base_url="https://api.bitget.com",
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

    def fetch_currencies(
        self,
    ):
        try:
            response = self._session.get(
                (
                    f"{self.base_url}"
                    "/api/v2/spot/public/coins"
                ),
                timeout=self._timeout_seconds,
            )

            response.raise_for_status()

            payload = response.json()

            if not isinstance(
                payload,
                dict,
            ):
                raise ValueError(
                    "unexpected coin metadata payload"
                )

            if str(
                payload.get(
                    "code",
                    "",
                )
            ) != "00000":
                raise ValueError(
                    payload.get(
                        "msg",
                        "exchange_error",
                    )
                )

            currencies = payload.get(
                "data"
            )

            if not isinstance(
                currencies,
                list,
            ):
                raise ValueError(
                    "unexpected currency metadata"
                )

            return {
                "fetch_complete": True,
                "reason": None,
                "currencies": currencies,
                "read_only": True,
                "paper_only": True,
                "live_order_submitted": False,
                "live_transfer_submitted": False,
            }

        except Exception as exc:
            return {
                "fetch_complete": False,
                "reason": (
                    f"{type(exc).__name__}: {exc}"
                ),
                "currencies": [],
                "read_only": True,
                "paper_only": True,
                "live_order_submitted": False,
                "live_transfer_submitted": False,
            }
