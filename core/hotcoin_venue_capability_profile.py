"""
ArbOS™
EX-227
Hotcoin Venue Capability Profile

Current verified production posture:
- public market catalogue available
- public order-book endpoint not verified/available
- funding/network metadata not production-verified
- transfer verification not production-verified

Fail closed on all unverified capabilities.
"""


def build_hotcoin_venue_capability_profile() -> dict[str, bool]:
    return {
        "market_data": True,
        "order_books": False,
        "networks": False,
        "transfer_metadata": False,
        "verification": False,
    }
