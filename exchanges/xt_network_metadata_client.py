"""
ArbOS™
EX-230
XT Network Metadata Client

Public read-only network / transfer metadata transport.

Endpoint:
GET /v4/public/wallet/support/currency

No authentication.
No withdrawals.
No transfers.
No live orders.
"""

import requests


class XTNetworkMetadataClient:
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

    def fetch(
        self,
    ):
        try:
            response = self._session.get(
                (
                    f"{self.base_url}"
                    "/v4/public/wallet/support/currency"
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
                    "unexpected XT metadata payload"
                )

            if payload.get(
                "rc"
            ) != 0:
                raise ValueError(
                    payload.get(
                        "mc",
                        "exchange_error",
                    )
                )

            currencies = payload.get(
                "result"
            )

            if not isinstance(
                currencies,
                list,
            ):
                raise ValueError(
                    "invalid XT currency metadata"
                )

            return {
                "exchange_id": "xt",
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
                "exchange_id": "xt",
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
