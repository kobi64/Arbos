"""
ArbOS™
EX-233
OKX Venue Capability Profile

Declares the verified read-only production capabilities
currently implemented for OKX.

Verified public capabilities:
- SPOT market metadata
- SPOT order books
- market-data verification

Important:
OKX currency / chain metadata requires authentication on the
verified endpoint, so public network discovery and transfer
metadata remain unavailable in this integration.

Paper-safe only.
No live orders.
No withdrawal submission.
No transfer submission.
"""


def build_okx_venue_capability_profile() -> dict[str, bool]:
    return {
        "market_data": True,
        "order_books": True,
        "networks": False,
        "transfer_metadata": False,
        "verification": True,
    }
