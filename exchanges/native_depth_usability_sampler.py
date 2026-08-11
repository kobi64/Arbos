"""
ArbOS™
EX-186
Native Depth Usability Sampler

Samples verified RAW_ONLY markets through a public order-book provider
and measures whether usable bid/ask depth is available.

Research/public market-data infrastructure only.
No authentication.
No transfers.
No live orders.
"""


class NativeDepthUsabilitySampler:
    def sample(
        self,
        symbols,
        provider,
        sample_size=10,
    ):
        if symbols is None:
            raise ValueError(
                "symbols are required"
            )

        if provider is None:
            raise ValueError(
                "provider is required"
            )

        if sample_size is None or int(sample_size) <= 0:
            raise ValueError(
                "sample_size must be positive"
            )

        selected = list(
            symbols
        )[:int(sample_size)]

        usable_symbols = []
        failed_symbols = []

        for symbol in selected:
            try:
                book = provider.snapshot(
                    symbol
                )

                bids = book.get(
                    "bids",
                    [],
                )

                asks = book.get(
                    "asks",
                    [],
                )

                if bids and asks:
                    usable_symbols.append(
                        symbol
                    )
                else:
                    failed_symbols.append(
                        symbol
                    )

            except Exception:
                failed_symbols.append(
                    symbol
                )

        sampled_count = len(
            selected
        )

        usable_count = len(
            usable_symbols
        )

        failed_count = len(
            failed_symbols
        )

        ratio = (
            usable_count / sampled_count
            if sampled_count
            else 0.0
        )

        return {
            "sampled_count": sampled_count,
            "usable_depth_count": (
                usable_count
            ),
            "failed_depth_count": (
                failed_count
            ),
            "usable_depth_ratio": ratio,
            "usable_symbols": (
                usable_symbols
            ),
            "failed_symbols": (
                failed_symbols
            ),
            "sampling_complete": True,
            "live_order_submitted": False,
        }
