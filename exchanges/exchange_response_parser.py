"""
ArbOS™
EX-052
Exchange Response Parser

Normalises exchange API responses
into a consistent ArbOS™ format.
"""


class ExchangeResponseParser:

    def parse(
        self,
        exchange,
        response
    ):

        if response is None:

            return {
                "success": False,
                "reason": "invalid_response",
            }

        status = response.get("status")

        if status == "error":

            return {
                "success": False,
                "exchange": exchange,
                "reason": "exchange_error",
            }

        return {
            "success": True,
            "exchange": exchange,
            "data": response.get("data"),
        }

    def extract_order_id(
        self,
        response
    ):

        return response.get("id")

    def normalise_error(
        self,
        error
    ):

        mapping = {
            "INVALID_KEY": "AUTH_ERROR",
        }

        return {
            "error": mapping.get(
                error,
                error
            )
        }

    def extract_balance(
        self,
        response
    ):

        return response.get("balance")
