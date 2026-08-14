"""
ArbOS™
EX-219
MEXC Venue Capability Profile

Declares the verified read-only production capabilities
currently implemented for MEXC.

Notes:
- public market data and order books are available anonymously
- network / transfer metadata verification is implemented
  through the read-only signed metadata path
- when read-only metadata credentials are absent,
  ArbOS™ fails closed and reports verification unavailable

No live orders.
No withdrawal submission.
No transfer submission.
"""


def build_mexc_venue_capability_profile():
    return {
        "market_data": True,
        "order_books": True,
        "networks": True,
        "transfer_metadata": True,
        "verification": True,
    }
