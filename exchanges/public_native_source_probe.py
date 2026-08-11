"""
ArbOS™
EX-188
Public Native Source Probe

Executes one explicitly selected public native market-catalogue
method and records the raw response shape.

Public API probing only.
No authentication.
No transfers.
No live orders.
"""


class PublicNativeSourceProbe:
    def probe(
        self,
        exchange,
        method_name,
    ):
        if exchange is None:
            raise ValueError(
                "exchange is required"
            )

        if (
            method_name is None
            or not str(method_name).strip()
        ):
            raise ValueError(
                "method_name is required"
            )

        exchange_id = str(
            getattr(
                exchange,
                "id",
                "",
            )
            or ""
        ).strip().lower()

        method_name = str(
            method_name
        ).strip()

        method = getattr(
            exchange,
            method_name,
            None,
        )

        if not callable(method):
            return {
                "exchange_id": exchange_id,
                "method": method_name,
                "probe_success": False,
                "response_type": None,
                "response": None,
                "error_type": (
                    "MethodUnavailable"
                ),
                "error": (
                    "selected public method unavailable"
                ),
                "public_api_called": False,
                "live_order_submitted": False,
            }

        try:
            response = method()
        except Exception as exc:
            return {
                "exchange_id": exchange_id,
                "method": method_name,
                "probe_success": False,
                "response_type": None,
                "response": None,
                "error_type": type(
                    exc
                ).__name__,
                "error": str(exc),
                "public_api_called": True,
                "live_order_submitted": False,
            }

        return {
            "exchange_id": exchange_id,
            "method": method_name,
            "probe_success": True,
            "response_type": type(
                response
            ).__name__,
            "response": response,
            "error_type": None,
            "error": None,
            "public_api_called": True,
            "live_order_submitted": False,
        }
