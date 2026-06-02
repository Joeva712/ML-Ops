from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class PriceRecord(BaseModel):
    id: Optional[int] = None
    product_id: str = Field(..., description="Foreign key reference to products.id")
    source: str = Field(..., description="Tokopedia, Shopee, Alibaba, etc.")
    price: float = Field(..., description="Price in original currency")
    currency: str = Field("USD", description="Currency symbol, e.g., IDR, USD")
    price_usd: float = Field(..., description="Normalized price in USD")
    price_per_unit: Optional[float] = None
    unit_of_measure: Optional[str] = "piece"
    min_order_qty: Optional[int] = 1
    price_tiers: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Tiered pricing for MOQ, e.g., [{'qty': 100, 'price': 5.0}]")
    shipping_cost: Optional[float] = None
    discount_pct: Optional[float] = None
    is_promo: bool = False
    stock_status: str = "in_stock" # in_stock, out_of_stock, quote_required
    recorded_at: Optional[datetime] = None
