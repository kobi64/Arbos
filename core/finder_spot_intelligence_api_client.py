"""
ArbOS™
EX-213
Finder Spot Intelligence API Client

Reads Finder's public landing-ticker intelligence feed.

Initial scope:
- cross-exchange intelligence
- plain USDT quote only
- external intelligence only
- paper safe

Non-standard quote types such as USDTM and X_USDT
are excluded until explicitly understood and supported.

No authentication.
No transfers.
No live orders.
"""

import requests


class FinderSpotIntelligenceAPIClient:
    DEFAULT_URL = (
        "https://finder-arbitrage.com/"
        "api/landing-ticker"
    )

    def __init__(
        self,
        session=None,
        timeout_seconds=20.0,
        url=None,
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

        self._url = (
            str(url).strip()
            if url is not None
            else self.DEFAULT_URL
        )

    def fetch(self):
        try:
            response = self._session.get(
                self._url,
                timeout=self._timeout_seconds,
                headers={
                    "Accept": "application/json",
                },
            )

            response.raise_for_status()
            payload = response.json()

        except Exception as exc:
            return self._failure(
                reason="request_failed",
                error=str(exc),
            )

        if not isinstance(
            payload,
            dict,
        ):
            return self._failure(
                reason="invalid_payload",
            )

        items = payload.get(
            "items"
        )

        if not isinstance(
            items,
            list,
        ):
            return self._failure(
                reason="invalid_payload",
            )

        accepted = []
        filtered_non_usdt_count = 0

        for item in items:
            if not isinstance(
                item,
                dict,
            ):
                continue

            quote = str(
                item.get(
                    "quote",
                    "",
                )
                or ""
            ).strip().upper()

            # EX-213 safety boundary:
            # initially accept only ordinary
            # USDT-quoted opportunities.
            if quote != "USDT":
                filtered_non_usdt_count += 1
                continue

            accepted.append(
                item
            )

        return {
            "fetch_complete": True,
            "source": "finder",
            "feed": "landing-ticker",
            "results": accepted,
            "result_count": len(
                accepted
            ),
            "raw_result_count": len(
                items
            ),
            "filtered_non_usdt_count": (
                filtered_non_usdt_count
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def _failure(
        self,
        reason,
        error=None,
    ):
        result = {
            "fetch_complete": False,
            "source": "finder",
            "feed": "landing-ticker",
            "reason": reason,
            "results": [],
            "result_count": 0,
            "filtered_non_usdt_count": 0,
            "paper_only": True,
            "live_order_submitted": False,
        }

        if error is not None:
            result["error"] = error

        return result
