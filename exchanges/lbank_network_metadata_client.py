"""
ArbOS™
EX-221
LBank Network Metadata Client

Public read-only asset/network metadata transport.

Confirmed live endpoint:
GET https://api.lbkex.com/v2/assetConfigs.do

Read-only.
No authentication.
No withdrawals.
No transfers.
No live orders.
"""

import requests


class LBankNetworkMetadataClient:
    def __init__(
        self,
        base_url="https://api.lbkex.com",
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

    def fetch_asset_metadata(
        self,
        asset,
    ):
        asset = str(
            asset
            or ""
        ).strip().upper()

        if not asset:
            raise ValueError(
                "asset is required"
            )

        try:
            response = self._session.get(
                (
                    f"{self.base_url}"
                    "/v2/assetConfigs.do"
                ),
                params={
                    "assetCode": (
                        asset.lower()
                    ),
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
                    "unexpected asset metadata payload"
                )

            if str(
                payload.get(
                    "result",
                    "",
                )
            ).strip().lower() != "true":
                raise ValueError(
                    payload.get(
                        "msg",
                        "exchange_error",
                    )
                )

            data = payload.get(
                "data"
            )

            if not isinstance(
                data,
                list,
            ):
                raise ValueError(
                    "unexpected asset metadata payload"
                )

            return {
                "fetch_complete": True,
                "asset": asset,
                "networks": data,
                "reason": None,
                "paper_only": True,
                "live_order_submitted": False,
                "live_transfer_submitted": False,
            }

        except Exception as exc:
            return {
                "fetch_complete": False,
                "asset": asset,
                "networks": [],
                "reason": (
                    f"{type(exc).__name__}: {exc}"
                ),
                "paper_only": True,
                "live_order_submitted": False,
                "live_transfer_submitted": False,
            }
