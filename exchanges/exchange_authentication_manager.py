"""
ArbOS™
EX-050
Exchange Authentication Manager

Handles exchange API credential management
and authentication state.
"""


class ExchangeAuthenticationManager:

    def __init__(self):

        self._credentials = {}

    def add_credentials(
        self,
        exchange,
        api_key,
        secret
    ):

        if not api_key or not secret:

            return {
                "success": False,
                "reason": "invalid_credentials",
            }

        self._credentials[exchange] = {
            "api_key": api_key,
            "secret": secret,
        }

        return {
            "success": True,
            "exchange": exchange,
        }

    def validate(self, exchange):

        return exchange in self._credentials

    def remove_credentials(self, exchange):

        if exchange not in self._credentials:

            return {
                "success": False,
                "reason": "exchange_not_found",
            }

        del self._credentials[exchange]

        return {
            "success": True,
        }

    def get_context(self, exchange):

        if not self.validate(exchange):

            return {
                "success": False,
            }

        return {
            "exchange": exchange,
            "authenticated": True,
        }

    def supported_exchanges(self):

        return list(self._credentials.keys())
