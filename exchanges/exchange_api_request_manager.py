"""
ArbOS™
EX-051
Exchange API Request Manager

Controls exchange API request creation,
retry handling, timeout handling, and
error normalisation.
"""


class ExchangeAPIRequestManager:

    def __init__(self):

        self._history = []

    def create_request(
        self,
        exchange,
        endpoint,
        method
    ):

        if not exchange:

            return {
                "success": False,
                "reason": "missing_exchange",
            }

        request = {
            "success": True,
            "exchange": exchange,
            "endpoint": endpoint,
            "method": method,
        }

        self._history.append(request)

        return request

    def handle_timeout(
        self,
        exchange
    ):

        return {
            "exchange": exchange,
            "status": "TIMEOUT",
        }

    def retry_request(
        self,
        request_id
    ):

        return {
            "request_id": request_id,
            "retry": True,
        }

    def normalise_error(
        self,
        error
    ):

        mapping = {
            "API_LIMIT": "RATE_LIMIT",
        }

        return {
            "error": mapping.get(
                error,
                error
            )
        }

    def get_history(self):

        return self._history
