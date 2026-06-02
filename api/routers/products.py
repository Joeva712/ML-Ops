from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from db import supabase_client
from taxonomy.categories import get_flat_categories

router = APIRouter()

@router.get("/products")
async def list_products(
    category: Optional[str] = Query(None, description="Filter by leaf category name"),
    q: Optional[str] = Query(None, description="Search query in title, brand, or OEM part number")
):
    products = supabase_client.get_latest_prices(category=category, query=q)
    return {"data": products, "count": len(products)}

@router.get("/products/{product_id}")
async def get_product_detail(product_id: str):
    products = supabase_client.get_latest_prices()
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"data": product}

@router.get("/products/{product_id}/price-history")
async def get_product_price_history(product_id: str):
    history = supabase_client.get_price_history(product_id)
    return {"data": history}

@router.get("/categories")
async def list_categories():
    categories = get_flat_categories()
    # Format categories nicely for display in dropdown/tree
    formatted = []
    for top, sub, leaf in categories:
        formatted.append({
            "path": [top, sub, leaf],
            "display": f"{top} > {sub} > {leaf}",
            "leaf": leaf
        })
    return {"data": formatted}
