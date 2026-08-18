"""
ArbOS™
EX-098
Capital Reservation Manager
"""

import math


def _finite_number(value, field, *, positive=False, non_negative=False):
    if isinstance(value, bool):
        raise ValueError(
            f"{field} must be a finite "
            f"{'positive' if positive else 'non-negative'} number"
        )

    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError(
            f"{field} must be a finite "
            f"{'positive' if positive else 'non-negative'} number"
        ) from None

    if not math.isfinite(number):
        raise ValueError(
            f"{field} must be a finite "
            f"{'positive' if positive else 'non-negative'} number"
        )

    if positive and number <= 0:
        raise ValueError(
            f"{field} must be positive"
        )

    if non_negative and number < 0:
        raise ValueError(
            f"{field} must be a finite non-negative number"
        )

    return number


class CapitalReservationManager:
    def __init__(self):
        self._reservations = {}

    def reserve(self, reservation_id, amount, available_capital):
        if reservation_id is None or not str(reservation_id).strip():
            raise ValueError("reservation_id is required")

        amount = _finite_number(
            amount,
            "amount",
            positive=True,
        )
        available_capital = _finite_number(
            available_capital,
            "available_capital",
            non_negative=True,
        )

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
            "amount": amount,
        }

        self._reservations[reservation_id] = record

        return {
            "reserved": True,
            "reason": None,
            "reservation_id": reservation_id,
            "amount": amount,
            "remaining_available_capital": (
                available_capital - amount
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
