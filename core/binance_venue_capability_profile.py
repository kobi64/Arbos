"""
ArbOS™
EX-234
Binance Venue Capability Profile

Declares the verified read-only production capabilities
currently implemented for Binance.

Verified public capabilities:
- SPOT market metadata
- SPOT order books
- independent book-ticker verification

Important:
Binance capital / network configuration requires
authentication on the verified endpoint, so public network
discovery and transfer metadata remain unavailable in this
integration.

Paper-safe only.
No live orders.
No withdrawal submission.
No transfer submission.
"""


def build_binance_venue_capability_profile() -> dict[str, bool]:
    return {
        "market_data": True,
        "order_books": True,
        "networks": False,
        "transfer_metadata": False,
        "verification": True,
    }
