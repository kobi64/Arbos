"""
ArbOS™
EX-098
Capital Reservation Manager
"""


class CapitalReservationManager:
    def __init__(self):
        self._reservations = {}

    def reserve(self, reservation_id, amount, available_capital):
        if reservation_id is None or not str(reservation_id).strip():
            raise ValueError("reservation_id is required")

        if amount <= 0:
            raise ValueError("amount must be positive")

        reservation_id = str(reservation_id).strip()

        if reservation_id in self._reservations:
            raise ValueError("reservation_id already exists")

        if amount > available_capital:
            return {
                "reserved": False,
                "reason": "insufficient_available_capital",
            }

        record = {
            "reservation_id": reservation_id,
            "amount": float(amount),
        }

        self._reservations[reservation_id] = record

        return {
            "reserved": True,
            "reason": None,
            "reservation_id": reservation_id,
            "amount": float(amount),
            "remaining_available_capital": (
                float(available_capital) - float(amount)
            ),
        }

    def release(self, reservation_id):
        record = self._reservations.pop(reservation_id, None)

        if record is None:
            raise ValueError("reservation not found")

        return {
            "released": True,
            "reservation_id": reservation_id,
            "amount": record["amount"],
        }

    def get_reservation(self, reservation_id):
        record = self._reservations.get(reservation_id)
        if record is None:
            raise ValueError("reservation not found")
        return dict(record)

    def total_reserved(self):
        return sum(
            record["amount"]
            for record in self._reservations.values()
        )
