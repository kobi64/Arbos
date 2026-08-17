"""
ArbOS™
EX-224
Gate.io Wallet Metadata Client

Credential-aware read-only metadata client shell.

Intended only for funding/network metadata reads.

No order placement.
No withdrawal submission.
No transfer submission.
"""

import requests


class GateIOWalletMetadataClient:
    def __init__(
        self,
        api_key=None,
        api_secret=None,
        base_url="https://api.gateio.ws",
        timeout_seconds=10.0,
        session=None,
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

        self.read_only = True

    def fetch_currency_chains(
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
                (
                    f"{self.base_url}"
                    "/api/v4/wallet/currency_chains"
                ),
                params={
                    "currency": currency,
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
                    "unexpected Gate.io "
                    "currency-chain payload"
                )

            currencies = []

            for item in payload:
                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                network = str(
                    item.get(
                        "chain",
                        "",
                    )
                    or ""
                ).strip().upper()

                if not network:
                    continue

                deposit_disabled = bool(
                    item.get(
                        "is_deposit_disabled",
                        False,
                    )
                )

                withdraw_disabled = bool(
                    item.get(
                        "is_withdraw_disabled",
                        False,
                    )
                )

                currencies.append({
                    "asset": currency,
                    "coin": currency,
                    "network": network,
                    "chain": network,
                    "deposit": (
                        not deposit_disabled
                    ),
                    "withdraw": (
                        not withdraw_disabled
                    ),
                    "raw": dict(item),
                })

            return {
                "fetch_complete": True,
                "currency": currency,
                "currencies": currencies,
                "reason": None,
                "read_only": True,
                "paper_only": True,
                "live_order_submitted": False,
                "live_transfer_submitted": False,
            }

        except Exception as exc:
            return {
                "fetch_complete": False,
                "currency": currency,
                "currencies": [],
                "reason": (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
                "read_only": True,
                "paper_only": True,
                "live_order_submitted": False,
                "live_transfer_submitted": False,
            }

    def fetch_currencies(
        self,
    ):
        if (
            not self._api_key
            or not self._api_secret
        ):
            return {
                "fetch_complete": False,
                "reason": "credentials_unavailable",
                "currencies": [],
                "read_only": True,
                "paper_only": True,
                "live_order_submitted": False,
                "live_transfer_submitted": False,
            }

        return {
            "fetch_complete": False,
            "reason": (
                "authenticated_metadata_transport_"
                "not_implemented"
            ),
            "currencies": [],
            "read_only": True,
            "paper_only": True,
            "live_order_submitted": False,
            "live_transfer_submitted": False,
        }
