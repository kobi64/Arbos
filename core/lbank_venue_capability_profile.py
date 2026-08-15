"""
ArbOS™
EX-221
LBank Venue Capability Profile

LBank provides native public market data plus
public network, transfer, and identity metadata.

This profile describes verification capability only.
It does not enable live order or transfer execution.
"""


def build_lbank_venue_capability_profile():
    return {
        "market_data": True,
        "order_books": True,
        "networks": True,
        "transfer_metadata": True,
        "verification": True,
    }
