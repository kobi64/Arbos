"""
ArbOS™
EX-142
Live Order Book Provider Adapter
"""


class LiveOrderBookProviderAdapter:
    def __init__(self, snapshot_engine):
        self._snapshot_engine = snapshot_engine

    def get_order_book(self, symbol):
        return self._snapshot_engine.snapshot(symbol)
