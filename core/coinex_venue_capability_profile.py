"""
ArbOS™
EX-231
CoinEx Venue Capability Profile

Declares the verified read-only production capabilities
currently implemented for CoinEx.

CoinEx provides:
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


def build_coinex_venue_capability_profile() -> dict[str, bool]:
    return {
        "market_data": True,
        "order_books": True,
        "networks": True,
        "transfer_metadata": True,
        "verification": True,
    }
