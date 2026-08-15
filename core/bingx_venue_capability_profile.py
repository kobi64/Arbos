"""
ArbOS™
EX-222
BingX Venue Capability Profile

Current verified state:
- public market data available
- public order books available
- wallet/network endpoint exists
- authenticated metadata signing contract not yet verified
- transfer verification therefore fails closed

No live orders.
No withdrawals.
No transfers.
"""


def build_bingx_venue_capability_profile():
    return {
        "market_data": True,
        "order_books": True,
        "networks": False,
        "transfer_metadata": False,
        "verification": False,
    }
