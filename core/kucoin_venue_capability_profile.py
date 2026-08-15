"""
ArbOS™
EX-225
KuCoin Venue Capability Profile

Current verified production posture:
- native public market data available
- verified native order books available
- funding/network metadata not yet production-verified
- transfer verification not yet production-verified

Fail closed on transfer-related capabilities.
"""


def build_kucoin_venue_capability_profile() -> dict[str, bool]:
    return {
        "market_data": True,
        "order_books": True,
        "networks": False,
        "transfer_metadata": False,
        "verification": False,
    }
