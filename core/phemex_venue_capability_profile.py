"""
ArbOS™
EX-232
Phemex Venue Capability Profile

Declares the verified read-only production capabilities
currently implemented for Phemex.

Phemex provides:
- public market data
- public spot order books
- public network discovery / status metadata
- verification support

Important:
The public chain-settings endpoint does not provide enough
information to verify transfer execution metadata such as:
- withdrawal fees
- withdrawal minimums
- deposit minimums
- confirmations
- separate deposit/withdraw enablement

Therefore transfer metadata remains unavailable / fail-closed.

Paper-safe only.
No live orders.
No withdrawal submission.
No transfer submission.
"""


def build_phemex_venue_capability_profile() -> dict[str, bool]:
    return {
        "market_data": True,
        "order_books": True,
        "networks": True,
        "transfer_metadata": False,
        "verification": True,
    }
