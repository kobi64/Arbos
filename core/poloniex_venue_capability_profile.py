"""
ArbOS™
EX-218
Poloniex Venue Capability Profile

Declares the verified read-only production capabilities
currently available for Poloniex.

Poloniex now provides:
- public market data
- public order books
- network metadata
- transfer metadata
- verification support

Paper-safe only.
No live orders.
"""


def build_poloniex_venue_capability_profile():
    return {
        "market_data": True,
        "order_books": True,
        "networks": True,
        "transfer_metadata": True,
        "verification": True,
    }
