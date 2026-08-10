"""
ArbOS™
EX-176
Exchange Market Completeness Validator

Compares a normalized market catalogue with an independently
obtained native/raw exchange market catalogue.

The validator is exchange-agnostic. It does not fetch market
data itself and contains no exchange-specific API logic.

It classifies markets as:

- MATCHED
- CCXT_ONLY
- RAW_ONLY

This module performs validation only.
It never submits exchange orders.
"""


class ExchangeMarketCompletenessValidator:
    def validate(
        self,
        exchange_id,
        ccxt_symbols,
        raw_symbols,
    ):
        if exchange_id is None or not str(exchange_id).strip():
            raise ValueError("exchange_id is required")

        if ccxt_symbols is None:
            raise ValueError("ccxt_symbols is required")

        if raw_symbols is None:
            raise ValueError("raw_symbols is required")

        exchange_id = str(exchange_id).strip().lower()

        ccxt = self._normalize_symbols(ccxt_symbols)
        raw = self._normalize_symbols(raw_symbols)

        matched = sorted(ccxt & raw)
        ccxt_only = sorted(ccxt - raw)
        raw_only = sorted(raw - ccxt)

        all_symbols = sorted(ccxt | raw)

        records = []

        for symbol in all_symbols:
            if symbol in ccxt and symbol in raw:
                status = "MATCHED"
            elif symbol in ccxt:
                status = "CCXT_ONLY"
            else:
                status = "RAW_ONLY"

            records.append({
                "exchange_id": exchange_id,
                "symbol": symbol,
                "status": status,
                "ccxt_present": symbol in ccxt,
                "raw_present": symbol in raw,
            })

        discrepancy_count = (
            len(ccxt_only)
            + len(raw_only)
        )

        complete_match = discrepancy_count == 0

        return {
            "exchange_id": exchange_id,
            "ccxt_market_count": len(ccxt),
            "raw_market_count": len(raw),
            "combined_market_count": len(all_symbols),
            "matched_count": len(matched),
            "ccxt_only_count": len(ccxt_only),
            "raw_only_count": len(raw_only),
            "discrepancy_count": discrepancy_count,
            "complete_match": complete_match,
            "matched": matched,
            "ccxt_only": ccxt_only,
            "raw_only": raw_only,
            "markets": records,
            "validation_complete": True,
            "live_order_submitted": False,
        }

    @staticmethod
    def _normalize_symbols(symbols):
        normalized = set()

        for value in symbols:
            if value is None:
                continue

            symbol = str(value).strip().upper()

            if not symbol:
                continue

            # Accept common raw forms such as:
            # BTC_USDT, BTC-USDT and BTC/USDT.
            symbol = symbol.replace("_", "/")
            symbol = symbol.replace("-", "/")

            parts = [
                part.strip()
                for part in symbol.split("/")
                if part.strip()
            ]

            if len(parts) != 2:
                continue

            normalized.add(
                f"{parts[0]}/{parts[1]}"
            )

        return normalized
