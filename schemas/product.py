from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class UnifiedProduct(BaseModel):
    id: Optional[str] = None
    source: str = Field(..., description="E.g., tokopedia, shopee, alibaba, supplier")
    source_id: str = Field(..., description="Unique product ID from source platform")
    source_url: str = Field(..., description="URL to the product listing")
    title: str = Field(..., description="Original product title")
    title_en: Optional[str] = None
    category_path: List[str] = Field(..., description="Hierarchical taxonomy path")
    category_leaf: str = Field(..., description="Leaf category name, e.g., Pistons")
    brand: Optional[str] = None
    oem_part_number: Optional[str] = None
    product_type: str = Field("finished_good", description="finished_good, component, raw_material")
    specifications: Dict[str, Any] = Field(default_factory=dict, description="Normalized specifications in SI units")
    specifications_raw: Dict[str, Any] = Field(default_factory=dict, description="Original unprocessed specs")
    description: Optional[str] = None
    images: List[str] = Field(default_factory=list, description="List of image URLs")
    seller_name: Optional[str] = None
    seller_type: Optional[str] = "distributor" # manufacturer, wholesaler, distributor, retailer
    seller_rating: Optional[float] = None
    seller_location: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
