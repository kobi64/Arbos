"""
ArbOS™
EX-211
CoinMarketGap API Client

Fetches CoinMarketGap arbitrage rows from the public
scanner endpoint and returns validated result sets.

The client does not determine executability.
External opportunities remain leads only.

No authentication.
No transfers.
No live orders.
"""

import requests


class CoinMarketGapAPIClient:
    DEFAULT_URL = (
        "https://www.coinmarket-gap.com/api/arb/"
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

        self._url = str(
            url
            or self.DEFAULT_URL
        ).strip()

    def fetch(
        self,
        exploitable_only=False,
    ):
        try:
            response = (
                self._session.get(
                    self._url,
                    timeout=(
                        self._timeout_seconds
                    ),
                )
            )

            response.raise_for_status()

            payload = response.json()

        except Exception:
            return self._failed_result()

        if not isinstance(
            payload,
            dict,
        ):
            return self._failed_result()

        results = payload.get(
            "results"
        )

        if not isinstance(
            results,
            list,
        ):
            return self._failed_result()

        normalized = [
            row
            for row in results
            if isinstance(
                row,
                dict,
            )
        ]

        if exploitable_only:
            normalized = [
                row
                for row in normalized
                if row.get(
                    "exploitable"
                )
                is True
            ]

        return {
            "fetch_complete": True,
            "source": "coinmarketgap",
            "results": normalized,
            "result_count": len(
                normalized
            ),
            "exploitable_only": bool(
                exploitable_only
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    @staticmethod
    def _failed_result():
        return {
            "fetch_complete": False,
            "source": "coinmarketgap",
            "results": [],
            "result_count": 0,
            "exploitable_only": False,
            "paper_only": True,
            "live_order_submitted": False,
        }
