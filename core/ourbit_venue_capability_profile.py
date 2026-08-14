"""
ArbOS™
EX-220
Ourbit Venue Capability Profile

Declares the currently verified read-only capabilities
for Ourbit.

Current verified state:
- public market data: available
- public order books: available
- network metadata: unavailable without credentials
- authenticated signing contract: not yet verified
- transfer verification: unavailable

No live orders.
No withdrawals.
No transfers.
"""


def build_ourbit_venue_capability_profile():
    return {
        "market_data": True,
        "order_books": True,
        "networks": False,
        "transfer_metadata": False,
        "verification": False,
    }
