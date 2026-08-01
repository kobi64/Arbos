"""
ArbOS™
EX-001
Base Exchange Interface
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseExchange(ABC):

    def __init__(self, name: str):
        self.name = name
        self.connected = False
        self.authenticated = False

    @abstractmethod
    async def connect(self) -> bool:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass

    @abstractmethod
    async def authenticate(self) -> bool:
        pass

    @abstractmethod
    async def health(self) -> Dict:
        pass

    @abstractmethod
    async def get_markets(self) -> List[Dict]:
        pass

    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict:
        pass

    @abstractmethod
    async def get_orderbook(
        self,
        symbol: str,
        depth: int = 20
    ) -> Dict:
        pass

    @abstractmethod
    async def get_balances(self) -> Dict:
        pass

    @abstractmethod
    async def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None
    ) -> Dict:
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        pass

    @abstractmethod
    async def withdraw(
        self,
        coin: str,
        amount: float,
        address: str,
        network: str
    ) -> Dict:
        pass

    @abstractmethod
    async def deposit_status(self, txid: str) -> Dict:
        pass

    @abstractmethod
    async def get_fees(self) -> Dict:
        pass

    @abstractmethod
    async def get_networks(self, coin: str) -> List[Dict]:
        pass
