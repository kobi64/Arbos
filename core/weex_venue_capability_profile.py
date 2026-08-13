"""
ArbOS™
EX-217
WEEX Venue Capability Profile

Declares the verified read-only production capabilities
currently available for WEEX.

WEEX now provides:
- public market data
- public order books
- network metadata
- deposit/withdraw metadata
- verification support

Paper-safe only.
No live orders.
"""


def build_weex_venue_capability_profile():
    return {
        "market_data": True,
        "order_books": True,
        "networks": True,
        "transfer_metadata": True,
        "verification": True,
    }
