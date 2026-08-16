"""
ArbOS™
EX-231
CoinEx Network Metadata Client

Retrieves CoinEx public deposit / withdrawal configuration
for a requested currency.

Read-only.
No authentication.
No transfers.
No live orders.
"""

import requests


class CoinExNetworkMetadataClient:
    BASE_URL = (
        "https://api.coinex.com/"
        "v2/assets/deposit-withdraw-config"
    )

    def __init__(
        self,
        session=None,
        timeout=10,
    ):
        self._session = (
            session
            if session is not None
            else requests
        )
        self._timeout = timeout

    def fetch_currency_metadata(
        self,
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

        try:
            response = self._session.get(
                self.BASE_URL,
                params={
                    "ccy": currency,
                },
                timeout=self._timeout,
            )

            response.raise_for_status()

            payload = response.json()

        except Exception as exc:
            raise RuntimeError(
                "CoinEx metadata unavailable: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise RuntimeError(
                "CoinEx metadata unavailable: "
                "invalid response"
            )

        if payload.get("code") != 0:
            raise RuntimeError(
                "CoinEx metadata unavailable: "
                f"{payload.get('message', 'unknown error')}"
            )

        data = payload.get(
            "data"
        )

        if not isinstance(
            data,
            dict,
        ):
            raise RuntimeError(
                "CoinEx metadata unavailable: "
                "missing data"
            )

        chains = data.get(
            "chains"
        )

        if not isinstance(
            chains,
            list,
        ):
            raise RuntimeError(
                "CoinEx metadata unavailable: "
                "missing chains"
            )

        return data

    def describe(self):
        return {
            "exchange_id": "coinex",
            "source": (
                "coinex_public_deposit_"
                "withdraw_config"
            ),
            "network_metadata": True,
            "transfer_metadata": True,
            "authentication_required": False,
            "paper_only": True,
            "live_order_submitted": False,
            "live_transfer_submitted": False,
        }
