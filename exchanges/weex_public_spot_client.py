"""
ArbOS™
EX-217
WEEX Public Spot Client

Read-only public WEEX spot market and network metadata.

Responsibilities:
- fetch tradable spot symbols
- fetch public order-book depth
- fetch coin/network deposit-withdraw metadata

Paper-safe only.
No authentication.
No transfers.
No live orders.
"""

import requests


class WeexPublicSpotClient:
    BASE_URL = "https://api-spot.weex.com"

    def __init__(
        self,
        session=None,
        timeout_seconds=20.0,
    ):
        timeout_seconds = float(
            timeout_seconds
        )

        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be positive"
            )

        self._session = (
            session
            if session is not None
            else requests
        )

        self._timeout_seconds = (
            timeout_seconds
        )

    def fetch_symbols(self):
        url = (
            self.BASE_URL
            + "/api/v3/apiTradingSymbols"
        )

        try:
            response = self._session.get(
                url,
                timeout=self._timeout_seconds,
            )

            response.raise_for_status()
            payload = response.json()

        except Exception as exc:
            return self._failed_result(
                reason="request_failed",
                error=str(exc),
            )

        if not isinstance(
            payload,
            list,
        ):
            return self._failed_result(
                reason="invalid_payload",
            )

        return {
            "fetch_complete": True,
            "symbols": list(
                payload
            ),
            "symbol_count": len(
                payload
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def fetch_depth(
        self,
        symbol,
        limit=200,
    ):
        symbol = str(
            symbol
            or ""
        ).strip().upper()

        if not symbol:
            raise ValueError(
                "symbol is required"
            )

        limit = int(
            limit
        )

        if limit not in {
            15,
            200,
        }:
            raise ValueError(
                "limit must be 15 or 200"
            )

        url = (
            self.BASE_URL
            + "/api/v3/market/depth"
        )

        try:
            response = self._session.get(
                url,
                params={
                    "symbol": symbol,
                    "limit": limit,
                },
                timeout=self._timeout_seconds,
            )

            response.raise_for_status()
            payload = response.json()

        except Exception as exc:
            return self._failed_result(
                reason="request_failed",
                error=str(exc),
            )

        if not isinstance(
            payload,
            dict,
        ):
            return self._failed_result(
                reason="invalid_payload",
            )

        bids = payload.get(
            "bids"
        )

        asks = payload.get(
            "asks"
        )

        if (
            not isinstance(
                bids,
                list,
            )
            or not isinstance(
                asks,
                list,
            )
        ):
            return self._failed_result(
                reason="invalid_payload",
            )

        return {
            "fetch_complete": True,
            "symbol": symbol,
            "last_update_id": payload.get(
                "lastUpdateId"
            ),
            "bids": bids,
            "asks": asks,
            "paper_only": True,
            "live_order_submitted": False,
        }

    def fetch_coins(self):
        url = (
            self.BASE_URL
            + "/api/v3/coins"
        )

        try:
            response = self._session.get(
                url,
                timeout=self._timeout_seconds,
            )

            response.raise_for_status()
            payload = response.json()

        except Exception as exc:
            return self._failed_result(
                reason="request_failed",
                error=str(exc),
            )

        if not isinstance(
            payload,
            list,
        ):
            return self._failed_result(
                reason="invalid_payload",
            )

        return {
            "fetch_complete": True,
            "coins": list(
                payload
            ),
            "coin_count": len(
                payload
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    @staticmethod
    def _failed_result(
        reason,
        error=None,
    ):
        result = {
            "fetch_complete": False,
            "reason": reason,
            "paper_only": True,
            "live_order_submitted": False,
        }

        if error is not None:
            result["error"] = error

        return result
