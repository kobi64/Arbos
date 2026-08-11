"""
ArbOS™
EX-188
Public Native Source Probe Chain

Executes approved public native catalogue methods in order,
stopping at the first successful response.

Failures are isolated and preserved for audit visibility.

Public market-data probing only.
No authentication.
No transfers.
No live orders.
"""

from exchanges.public_native_source_probe import (
    PublicNativeSourceProbe,
)


class PublicNativeSourceProbeChain:
    def probe(
        self,
        exchange,
        method_names,
    ):
        if exchange is None:
            raise ValueError(
                "exchange is required"
            )

        if method_names is None:
            raise ValueError(
                "method_names are required"
            )

        methods = [
            str(name).strip()
            for name in method_names
            if str(name).strip()
        ]

        attempts = []

        for method_name in methods:
            result = (
                PublicNativeSourceProbe()
                .probe(
                    exchange=exchange,
                    method_name=method_name,
                )
            )

            attempts.append(
                result
            )

            if result.get(
                "probe_success"
            ) is True:
                return {
                    "exchange_id": result.get(
                        "exchange_id"
                    ),
                    "probe_success": True,
                    "successful_method": (
                        method_name
                    ),
                    "attempt_count": len(
                        attempts
                    ),
                    "attempts": attempts,
                    "response_type": result.get(
                        "response_type"
                    ),
                    "response": result.get(
                        "response"
                    ),
                    "public_api_called": True,
                    "live_order_submitted": False,
                }

        exchange_id = str(
            getattr(
                exchange,
                "id",
                "",
            )
            or ""
        ).strip().lower()

        last_attempt = (
            attempts[-1]
            if attempts
            else {}
        )

        return {
            "exchange_id": exchange_id,
            "probe_success": False,
            "successful_method": None,
            "attempt_count": len(
                attempts
            ),
            "attempts": attempts,
            "response_type": None,
            "response": None,
            "error_type": last_attempt.get(
                "error_type"
            ),
            "error": last_attempt.get(
                "error"
            ),
            "public_api_called": bool(
                attempts
            ),
            "live_order_submitted": False,
        }
