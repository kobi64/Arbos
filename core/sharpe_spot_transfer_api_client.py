"""
ArbOS™
EX-212
Sharpe Spot Transfer API Client

Reads Sharpe's public CEX spot-transfer arbitrage feed.

SPOT TRANSFER ONLY.

Perpetual, futures, derivatives and funding-rate
arbitrage payloads are not accepted by this client.

External intelligence only.
No authentication.
No transfers.
No live orders.
"""

import requests


class SharpeSpotTransferAPIClient:
    DEFAULT_URL = (
        "https://www.sharpe.ai/"
        "api/arbitrage/cex-spot-transfer"
    )

    EXPECTED_KIND = "cex-spot-transfer"

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

    def fetch(
        self,
        notional_usd=300.0,
        limit=10,
    ):
        notional_usd = float(
            notional_usd
        )

        if notional_usd <= 0:
            raise ValueError(
                "notional_usd must be positive"
            )

        limit = int(
            limit
        )

        if limit <= 0:
            raise ValueError(
                "limit must be positive"
            )

        try:
            response = self._session.get(
                self._url,
                params={
                    "notional": notional_usd,
                    "limit": limit,
                },
                timeout=self._timeout_seconds,
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

        data = payload.get(
            "data"
        )

        meta = payload.get(
            "meta"
        )

        if (
            not isinstance(data, list)
            or not isinstance(meta, dict)
        ):
            return self._failure(
                reason="invalid_payload",
            )

        kind = str(
            meta.get(
                "kind",
                "",
            )
            or ""
        ).strip().lower()

        # Hard EX-212 safety boundary:
        # this integration accepts spot-transfer
        # intelligence only.
        if kind != self.EXPECTED_KIND:
            return self._failure(
                reason=(
                    "non_spot_transfer_payload"
                ),
                kind=kind,
            )

        return {
            "fetch_complete": True,
            "source": "sharpe",
            "kind": kind,
            "results": data,
            "result_count": len(
                data
            ),
            "generated_at": meta.get(
                "generatedAt"
            ),
            "updated_at": meta.get(
                "updatedAt"
            ),
            "stale": bool(
                meta.get(
                    "stale",
                    False,
                )
            ),
            "freshness_sla_seconds": (
                meta.get(
                    "freshnessSlaSeconds"
                )
            ),
            "source_status": meta.get(
                "status"
            ),
            "source_mode": meta.get(
                "source"
            ),
            "notional_usd": meta.get(
                "notionalUsd",
                notional_usd,
            ),
            "warnings": list(
                meta.get(
                    "warnings"
                )
                or []
            ),
            "pagination": (
                payload.get(
                    "pagination"
                )
                or {}
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def _failure(
        self,
        reason,
        error=None,
        kind=None,
    ):
        result = {
            "fetch_complete": False,
            "source": "sharpe",
            "kind": kind,
            "reason": reason,
            "results": [],
            "result_count": 0,
            "paper_only": True,
            "live_order_submitted": False,
        }

        if error is not None:
            result[
                "error"
            ] = error

        return result
