"""
ArbOS™
EX-130
Bridge Conversion Quote Engine
"""


class BridgeConversionQuoteEngine:
    def __init__(
        self,
        spot_quote_provider,
        convert_quote_provider,
    ):
        self._spot_quote_provider = spot_quote_provider
        self._convert_quote_provider = convert_quote_provider

    def quote(
        self,
        from_asset,
        to_asset,
        amount,
    ):
        if amount <= 0:
            raise ValueError("amount must be positive")

        spot_quote = self._spot_quote_provider.quote(
            from_asset=from_asset,
            to_asset=to_asset,
            amount=amount,
        )

        if spot_quote is not None:
            result = dict(spot_quote)
            result["available"] = True
            return result

        convert_quote = self._convert_quote_provider.quote(
            from_asset=from_asset,
            to_asset=to_asset,
            amount=amount,
        )

        if convert_quote is not None:
            result = dict(convert_quote)
            result["available"] = True
            return result

        return {
            "available": False,
            "from_asset": str(from_asset).strip().upper(),
            "to_asset": str(to_asset).strip().upper(),
            "input_amount": float(amount),
            "output_amount": None,
            "method": None,
            "reason": "conversion_quote_unavailable",
        }
