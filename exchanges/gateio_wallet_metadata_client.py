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


class GateIOWalletMetadataClient:
    def __init__(
        self,
        api_key=None,
        api_secret=None,
        base_url="https://api.gateio.ws",
        timeout_seconds=10.0,
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

        self.read_only = True

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
