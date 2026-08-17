"""
ArbOS™
EX-225
KuCoin Wallet Metadata Client

Credential-aware read-only metadata client shell.

Intended only for funding/network metadata reads.

No order placement.
No withdrawal submission.
No transfer submission.
"""

import requests


class KuCoinWalletMetadataClient:
    def __init__(
        self,
        api_key=None,
        api_secret=None,
        api_passphrase=None,
        base_url="https://api.kucoin.com",
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

        self._api_passphrase = (
            str(api_passphrase).strip()
            if api_passphrase is not None
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
                    f"/api/v3/currencies/{currency}"
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
                    "unexpected KuCoin currency payload"
                )

            code = str(
                payload.get(
                    "code",
                    "",
                )
                or ""
            ).strip()

            if code != "200000":
                raise ValueError(
                    "KuCoin API error "
                    f"{code}: "
                    f"{payload.get('msg', 'unknown error')}"
                )

            data = payload.get(
                "data"
            )

            if not isinstance(
                data,
                dict,
            ):
                raise ValueError(
                    "unexpected KuCoin currency data"
                )

            chains = data.get(
                "chains"
            )

            if not isinstance(
                chains,
                list,
            ):
                raise ValueError(
                    "unexpected KuCoin chain metadata"
                )

            currencies = []

            for item in chains:
                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                raw_network = str(
                    item.get(
                        "chainId",
                        item.get(
                            "chainName",
                            "",
                        ),
                    )
                    or ""
                ).strip()

                if not raw_network:
                    continue

                network = (
                    raw_network.upper()
                )

                network_aliases = {
                    "ETH": "ETH",
                    "ERC20": "ETH",
                    "TRX": "TRX",
                    "TRC20": "TRX",
                    "BSC": "BSC",
                    "BEP20": "BSC",
                }

                network = (
                    network_aliases.get(
                        network,
                        network,
                    )
                )

                currencies.append({
                    "asset": currency,
                    "coin": currency,
                    "network": network,
                    "chain": network,
                    "deposit": bool(
                        item.get(
                            "isDepositEnabled",
                            False,
                        )
                    ),
                    "withdraw": bool(
                        item.get(
                            "isWithdrawEnabled",
                            False,
                        )
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
            or not self._api_passphrase
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
