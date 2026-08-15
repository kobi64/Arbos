"""
ArbOS™
EX-227
Hotcoin Native Market Source

Retrieves and normalizes Hotcoin's public spot-market catalogue.

Verified public endpoint:
GET /v1/common/symbols

Public market metadata only.
No authentication.
No transfers.
No live orders.
"""

import requests


class HotcoinNativeMarketSource:
    def __init__(
        self,
        base_url="https://api.hotcoinfin.com",
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

    def fetch(self):
        try:
            response = self._session.get(
                (
                    f"{self.base_url}"
                    "/v1/common/symbols"
                ),
                timeout=self._timeout_seconds,
            )

            response.raise_for_status()

            payload = response.json()

            if not isinstance(
                payload,
                dict,
            ):
                return self._failed_result()

            if payload.get(
                "code"
            ) != 200:
                return self._failed_result()

            data = payload.get(
                "data"
            )

            if not isinstance(
                data,
                list,
            ):
                return self._failed_result()

            markets = []

            for raw in data:
                if not isinstance(
                    raw,
                    dict,
                ):
                    continue

                base = str(
                    raw.get(
                        "baseCurrency",
                        "",
                    )
                    or ""
                ).strip().upper()

                quote = str(
                    raw.get(
                        "quoteCurrency",
                        "",
                    )
                    or ""
                ).strip().upper()

                if not base or not quote:
                    continue

                symbol = (
                    f"{base}/{quote}"
                )

                state = str(
                    raw.get(
                        "state",
                        "",
                    )
                    or ""
                ).strip().lower()

                markets.append({
                    "symbol": symbol,
                    "status": (
                        "TRADING"
                        if state == "enable"
                        else "SUSPENDED"
                    ),
                    "order_types": [
                        "LIMIT",
                        "MARKET",
                    ],
                    "price_precision": (
                        raw.get(
                            "pricePrecision"
                        )
                    ),
                    "amount_precision": (
                        raw.get(
                            "amountPrecision"
                        )
                    ),
                    "minimum_value": (
                        raw.get(
                            "minOrderAmount"
                        )
                    ),
                    "native_symbol": str(
                        raw.get(
                            "symbol",
                            "",
                        )
                        or ""
                    ).strip(),
                    "symbol_partition": (
                        raw.get(
                            "symbolPartition"
                        )
                    ),
                    "raw": dict(
                        raw
                    ),
                })

            return {
                "exchange_id": "hotcoin",
                "fetch_complete": True,
                "symbols": [
                    market[
                        "symbol"
                    ]
                    for market in markets
                ],
                "markets": markets,
                "market_count": len(
                    markets
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        except Exception:
            return self._failed_result()

    @staticmethod
    def _failed_result():
        return {
            "exchange_id": "hotcoin",
            "fetch_complete": False,
            "symbols": [],
            "markets": [],
            "market_count": 0,
            "paper_only": True,
            "live_order_submitted": False,
        }
