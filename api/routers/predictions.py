from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from taxonomy.input_corrector import InputCorrector
from ml.pricing.predict import estimate_fair_price
from ml.matching.predict import predict_match, find_matches
from db import supabase_client

router = APIRouter()

class PricePredictionRequest(BaseModel):
    category_path: List[str]
    brand: Optional[str] = None
    specifications: Dict[str, Any] = {}
    oem_part_number: Optional[str] = None
    description: Optional[str] = ""
    quantity: Optional[int] = 1

class MatchPredictionRequest(BaseModel):
    product_a: Dict[str, Any]
    product_b: Dict[str, Any]

@router.post("/predict/price")
async def predict_price(request: PricePredictionRequest):
    # 1. Feed input into InputCorrector to correct brand/specs
    raw_payload = request.dict()
    corrected_res = InputCorrector.correct_input(raw_payload)
    
    corrected_req = corrected_res["corrected_request"]
    leaf_category = corrected_req["category_path"][-1] if corrected_req.get("category_path") else ""
    
    # 2. Get predictions using corrected input
    price_pred = estimate_fair_price(
        category_leaf=leaf_category,
        brand=corrected_req["brand"],
        specs=corrected_req["specifications"],
        quantity=request.quantity
    )
    
    # 3. Compile response envelope
    response = {
        "price_range": price_pred["price_range"],
        "confidence": price_pred["confidence"],
        "comparable_products": price_pred["comparable_products"],
        "model_used": price_pred["model_used"],
        "price_factors": price_pred["price_factors"]
    }
    
    # Only include corrections list if issues were found
    if "corrections" in corrected_res:
        response["corrections"] = corrected_res["corrections"]
        
    return response

@router.post("/predict/match")
async def match_products(request: MatchPredictionRequest):
    is_match, confidence = predict_match(request.product_a, request.product_b)
    return {
        "is_match": is_match,
        "confidence": round(confidence, 2)
    }

@router.post("/predict/find-matches")
async def find_catalog_matches(product: Dict[str, Any] = Body(...)):
    # Retrieve all products in the same category leaf to compare
    leaf_cat = product.get("category_leaf")
    if not leaf_cat:
        raise HTTPException(status_code=400, detail="category_leaf is required to scan matches")
        
    candidates = supabase_client.get_latest_prices(category=leaf_cat)
    matches_res = find_matches(product, candidates)
    
    serialized_matches = []
    for cand, conf in matches_res:
        serialized_matches.append({
            "product": {
                "id": cand.get("id"),
                "title": cand.get("title"),
                "brand": cand.get("brand"),
                "price": cand.get("price"),
                "currency": cand.get("currency"),
                "source": cand.get("source"),
                "source_url": cand.get("source_url")
            },
            "confidence": round(conf, 2)
        })
        
    return {"matches": serialized_matches}
