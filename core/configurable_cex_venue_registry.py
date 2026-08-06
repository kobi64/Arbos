"""
ArbOS™
EX-123
Configurable CEX Venue Registry
"""


class ConfigurableCEXVenueRegistry:
    def __init__(self):
        self._venues = {}

    def register(self, exchange_id, factory, enabled=True):
        exchange_id = str(exchange_id).strip().lower()

        if not exchange_id:
            raise ValueError("exchange_id is required")

        if not callable(factory):
            raise ValueError("factory must be callable")

        self._venues[exchange_id] = {
            "factory": factory,
            "enabled": bool(enabled),
        }

    def create(self, exchange_id):
        exchange_id = str(exchange_id).strip().lower()
        venue = self._venues.get(exchange_id)

        if venue is None:
            raise ValueError("venue not registered")

        if not venue["enabled"]:
            raise ValueError("venue is disabled")

        return venue["factory"]()

    def set_enabled(self, exchange_id, enabled):
        exchange_id = str(exchange_id).strip().lower()
        venue = self._venues.get(exchange_id)

        if venue is None:
            raise ValueError("venue not registered")

        venue["enabled"] = bool(enabled)

    def enabled_exchange_ids(self):
        return sorted(
            exchange_id
            for exchange_id, venue in self._venues.items()
            if venue["enabled"]
        )
