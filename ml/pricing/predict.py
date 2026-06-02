import numpy as np
import structlog
from typing import Dict, List, Any, Optional
from db import supabase_client

logger = structlog.get_logger(__name__)

def estimate_fair_price(category_leaf: str, brand: Optional[str] = None, specs: Dict[str, Any] = {}, quantity: int = 1) -> Dict[str, Any]:
    """
    Predicts the low (P10), fair (P50), and high (P90) prices for a product.
    Dynamically loads market data from the database and performs a spec-adjusted quantile estimation.
    """
    logger.info("Estimating fair price", category=category_leaf, brand=brand, specs=specs)
    
    # 1. Fetch historical prices from DB for this category
    all_products = supabase_client.get_latest_prices(category=category_leaf)
    
    if not all_products:
        # Fallback to category default base prices if DB is empty
        fallbacks = {
            "Smartphones": {"base": 400.0, "unit": "piece"},
            "Pistons": {"base": 80.0, "unit": "piece"},
            "Laundry Detergent": {"base": 12.0, "unit": "unit"},
            "Interior Paint": {"base": 45.0, "unit": "unit"},
            "Tempered Glass": {"base": 25.0, "unit": "m²"},
            "Steel Sheet": {"base": 2.0, "unit": "kg"}
        }
        fallback = fallbacks.get(category_leaf, {"base": 50.0, "unit": "piece"})
        base_price = fallback["base"]
        unit = fallback["unit"]
        
        # Simulate range
        low = base_price * 0.8
        fair = base_price
        high = base_price * 1.3
        
        return {
            "price_range": {"low": round(low, 2), "fair": round(fair, 2), "high": round(high, 2), "currency": "USD", "unit": unit},
            "confidence": "low (no db data)",
            "comparable_products": 0,
            "model_used": "global_fallback",
            "price_factors": {}
        }
        
    # Extract prices in USD
    prices_usd = [float(p["price_usd"]) for p in all_products if p.get("price_usd") is not None]
    
    if not prices_usd:
        prices_usd = [100.0] # safety default
        
    # 2. Filter products of same brand if available
    brand_products = []
    if brand:
        brand_lower = brand.strip().lower()
        brand_products = [p for p in all_products if p.get("brand") and p["brand"].lower() == brand_lower]
        
    matching_set = brand_products if len(brand_products) >= 2 else all_products
    matching_prices = [float(p["price_usd"]) for p in matching_set if p.get("price_usd") is not None]
    
    # 3. Spec adjustments (e.g. adjust smartphone price based on RAM/storage, or piston based on diameter)
    adjustment_factor = 1.0
    price_factors = {}
    
    if category_leaf == "Smartphones" and specs:
        # RAM adjustment (e.g., median RAM is 8GB)
        ram = specs.get("ram")
        if ram:
            try:
                # parse number
                import re
                ram_num = float(re.findall(r"\d+", str(ram))[0])
                if ram_num > 8:
                    pct = (ram_num - 8) * 0.05
                    adjustment_factor += pct
                    price_factors["ram_premium"] = f"+{int(pct*100)}%"
                elif ram_num < 8:
                    pct = (8 - ram_num) * 0.08
                    adjustment_factor -= pct
                    price_factors["ram_discount"] = f"-{int(pct*100)}%"
            except Exception:
                pass
                
        # Storage adjustment (median 256GB)
        storage = specs.get("storage")
        if storage:
            try:
                storage_num = float(re.findall(r"\d+", str(storage))[0])
                if storage_num > 256:
                    pct = (storage_num / 256.0 - 1.0) * 0.15
                    adjustment_factor += pct
                    price_factors["storage_premium"] = f"+{int(pct*100)}%"
                elif storage_num < 256:
                    pct = (1.0 - storage_num / 256.0) * 0.20
                    adjustment_factor -= pct
                    price_factors["storage_discount"] = f"-{int(pct*100)}%"
            except Exception:
                pass
                
    elif category_leaf == "Pistons" and specs:
        # Material adjustment
        mat = str(specs.get("material") or "").lower()
        if mat == "forged_steel":
            adjustment_factor += 1.50
            price_factors["material_forged_steel"] = "+150% (High Strength)"
        elif mat == "cast_iron":
            adjustment_factor -= 0.15
            price_factors["material_cast_iron"] = "-15% (Standard Heavy)"
            
    # Calculate quantiles
    p10 = float(np.percentile(matching_prices, 10)) * adjustment_factor
    p50 = float(np.percentile(matching_prices, 50)) * adjustment_factor
    p90 = float(np.percentile(matching_prices, 90)) * adjustment_factor
    
    # 4. Quantity Discount (FOB bulk purchase)
    if quantity >= 100:
        discount = 0.15 if quantity >= 1000 else 0.08
        p10 *= (1.0 - discount)
        p50 *= (1.0 - discount)
        p90 *= (1.0 - discount)
        price_factors["quantity_discount"] = f"-{int(discount*100)}%"
        
    unit = all_products[0].get("unit_of_measure") or "piece"
    
    return {
        "price_range": {
            "low": round(max(0.1, p10), 2),
            "fair": round(max(0.2, p50), 2),
            "high": round(max(0.3, p90), 2),
            "currency": "USD",
            "unit": unit
        },
        "confidence": "high" if len(matching_set) >= 5 else "medium",
        "comparable_products": len(matching_set),
        "model_used": f"quantile_regression:{category_leaf.lower()}",
        "price_factors": price_factors
    }
