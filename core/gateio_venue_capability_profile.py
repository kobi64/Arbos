"""
ArbOS™
EX-224
Gate.io Venue Capability Profile

Current verified production posture:
- public market data available
- native order books available
- funding/network metadata not yet production-verified
- transfer verification not yet production-verified

Fail closed on transfer-related capabilities.
"""


def build_gateio_venue_capability_profile() -> dict[str, bool]:
    return {
        "market_data": True,
        "order_books": True,
        "networks": False,
        "transfer_metadata": False,
        "verification": False,
    }
