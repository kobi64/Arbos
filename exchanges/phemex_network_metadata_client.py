"""
ArbOS™
EX-232
Phemex Network Metadata Client

Retrieves Phemex public chain-setting metadata for a currency.

Verified public endpoint:
GET /exchange/public/cfg/chain-settings

This endpoint provides network discovery/status metadata only.
It does not provide verified withdrawal fees, minimums,
confirmations, or separate deposit/withdraw enablement.

Read-only.
No authentication.
No transfers.
No live orders.
"""

import requests


class PhemexNetworkMetadataClient:
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
    def _normalize_currency(
        currency,
    ):
        currency = str(
            currency
            or ""
        ).strip().upper()

        if not currency:
            raise ValueError(
                "currency is required"
            )

        return currency

    def fetch_networks(
        self,
        currency,
    ):
        currency = (
            self._normalize_currency(
                currency
            )
        )

        try:
            response = (
                self._session.get(
                    (
                        f"{self.base_url}"
                        "/exchange/public/cfg/"
                        "chain-settings"
                    ),
                    params={
                        "currency": currency,
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
                    "unexpected Phemex network "
                    "metadata payload"
                )

            return payload

        except Exception as exc:
            raise RuntimeError(
                "Phemex network metadata unavailable: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ) from exc
