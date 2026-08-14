"""
ArbOS™
EX-219
MEXC Wallet Metadata Client

Credential-aware read-only metadata client.

Uses MEXC Spot V3 signed metadata endpoint:
GET /api/v3/capital/config/getall

Read-only metadata only.
No order placement.
No withdrawal submission.
No transfer submission.
"""

import hashlib
import hmac
import time
import requests


class MexcWalletMetadataClient:
    def __init__(
        self,
        api_key=None,
        api_secret=None,
        base_url="https://api.mexc.com",
        timeout_seconds=10.0,
        session=None,
        time_provider=None,
    ):
        timeout_seconds = float(
            timeout_seconds
        )

        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be positive"
            )

        self.base_url = str(
            base_url
            or ""
        ).rstrip("/")

        if not self.base_url:
            raise ValueError(
                "base_url is required"
            )

        self._api_key = (
            str(api_key).strip()
            if api_key is not None
            else None
        )

        self._api_secret = (
            str(api_secret).strip()
            if api_secret is not None
            else None
        )

        self._timeout_seconds = (
            timeout_seconds
        )

        self._session = (
            session
            if session is not None
            else requests.Session()
        )

        self._time_provider = (
            time_provider
            if time_provider is not None
            else time.time
        )

        self.read_only = True

    def _sign(
        self,
        query_string,
    ):
        if not self._api_secret:
            raise ValueError(
                "api_secret is required"
            )

        return hmac.new(
            self._api_secret.encode(
                "utf-8"
            ),
            query_string.encode(
                "utf-8"
            ),
            hashlib.sha256,
        ).hexdigest()

    def fetch_currencies(
        self,
    ):
        if (
            not self._api_key
            or not self._api_secret
        ):
            return {
                "fetch_complete": False,
                "reason": (
                    "credentials_unavailable"
                ),
                "currencies": [],
                "read_only": True,
                "paper_only": True,
                "live_order_submitted": False,
                "live_transfer_submitted": False,
            }

        try:
            timestamp = int(
                float(
                    self._time_provider()
                )
                * 1000
            )

            query_string = (
                f"timestamp={timestamp}"
            )

            signature = self._sign(
                query_string
            )

            response = self._session.get(
                (
                    f"{self.base_url}"
                    "/api/v3/capital/config/getall"
                ),
                params={
                    "timestamp": timestamp,
                    "signature": signature,
                },
                headers={
                    "X-MEXC-APIKEY": (
                        self._api_key
                    ),
                },
                timeout=self._timeout_seconds,
            )

            response.raise_for_status()

            payload = response.json()

            if not isinstance(
                payload,
                list,
            ):
                raise ValueError(
                    "unexpected currency metadata payload"
                )

            return {
                "fetch_complete": True,
                "reason": None,
                "currencies": payload,
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
