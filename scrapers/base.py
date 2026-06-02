from abc import ABC, abstractmethod
from typing import List, Dict, Any
from schemas.product import UnifiedProduct
from schemas.price_record import PriceRecord

class BaseScraper(ABC):
    source_name: str
    source_type: str  # "consumer", "b2b", "industrial", "direct"

    def __init__(self):
        pass

    @abstractmethod
    async def search(self, query: str, category_leaf: str) -> List[Dict[str, Any]]:
        """
        Searches the source platform for products matching query and category.
        Returns a list of raw product dicts matching the UnifiedProduct spec format.
        """
        pass

    @abstractmethod
    async def get_price(self, source_id: str) -> Dict[str, Any]:
        """
        Retrieves the latest price record for a given product source ID.
        """
        pass
