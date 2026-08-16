"""
ArbOS™
EX-235
Coinbase Venue Capability Profile

Declares the verified read-only production capabilities
currently implemented for Coinbase Exchange.

Verified public capabilities:
- SPOT market metadata
- Level-2 order books
- independent ticker verification
- supported network metadata
- transfer-related network metadata

Important:
transfer_metadata means read-only metadata such as network
availability, withdrawal limits, confirmations, contract
addresses, and destination-tag requirements.

It does NOT mean ArbOS™ can submit withdrawals or transfers.

Paper-safe only.
No live orders.
No withdrawal submission.
No transfer submission.
"""


def build_coinbase_venue_capability_profile() -> dict[str, bool]:
    return {
        "market_data": True,
        "order_books": True,
        "networks": True,
        "transfer_metadata": True,
        "verification": True,
    }
