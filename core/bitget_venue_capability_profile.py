"""
ArbOS™
EX-229
Bitget Venue Capability Profile

Declares the verified read-only production capabilities
currently implemented for Bitget.

Bitget provides:
- public market data
- public order books
- public network metadata
- public deposit/withdraw metadata
- verification support

Paper-safe only.
No live orders.
No withdrawal submission.
No transfer submission.
"""


def build_bitget_venue_capability_profile() -> dict[str, bool]:
    return {
        "market_data": True,
        "order_books": True,
        "networks": True,
        "transfer_metadata": True,
        "verification": True,
    }
