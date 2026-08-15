def build_kraken_venue_capability_profile() -> dict[str, bool]:
    """
    Return the currently verified Kraken venue capability profile.

    Market-data capabilities are enabled because they are supported by the
    Kraken integration already under test.

    Transfer-related capabilities remain fail-closed until Kraken network,
    transfer-metadata, and verification support have been explicitly
    implemented and validated.
    """
    return {
        "market_data": True,
        "order_books": True,
        "networks": False,
        "transfer_metadata": False,
        "verification": False,
    }
