from typing import Dict, List, Any, Tuple
from ml.features.embeddings import text_vectorizer

def clean_part_number(part_no: Any) -> str:
    """Standardizes OEM part numbers by stripping spaces, dashes, and converting to lowercase."""
    if not part_no:
        return ""
    return re.sub(r"[\s\-\_]", "", str(part_no)).lower()

import re

def compute_matching_features(prod_a: Dict[str, Any], prod_b: Dict[str, Any]) -> Dict[str, float]:
    """
    Computes a set of distance and similarity features between two products.
    """
    features = {}
    
    # 1. OEM Part Number Match (Standardized)
    oem_a = clean_part_number(prod_a.get("oem_part_number"))
    oem_b = clean_part_number(prod_b.get("oem_part_number"))
    if oem_a and oem_b:
        features["oem_match"] = 1.0 if oem_a == oem_b else 0.0
    else:
        features["oem_match"] = -1.0 # missing signal
        
    # 2. Text/Title Cosine Similarity
    title_a = prod_a.get("title", "")
    title_b = prod_b.get("title", "")
    features["title_similarity"] = text_vectorizer.get_similarity(title_a, title_b)
    
    # 3. Brand Match
    brand_a = str(prod_a.get("brand") or "").strip().lower()
    brand_b = str(prod_b.get("brand") or "").strip().lower()
    if brand_a and brand_b and brand_a != "generic" and brand_b != "generic":
        features["brand_match"] = 1.0 if brand_a == brand_b else 0.0
    else:
        features["brand_match"] = 0.5 # partial confidence if missing/generic
        
    # 4. Category Leaf Match
    cat_a = prod_a.get("category_leaf")
    cat_b = prod_b.get("category_leaf")
    features["category_match"] = 1.0 if cat_a == cat_b else 0.0
    
    # 5. Specification Similarity
    specs_a = prod_a.get("specifications", {})
    specs_b = prod_b.get("specifications", {})
    
    shared_specs_match = []
    for k in specs_a:
        if k in specs_b and specs_a[k] is not None and specs_b[k] is not None:
            val_a = specs_a[k]
            val_b = specs_b[k]
            if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                # Calculate numeric ratio similarity
                denom = max(val_a, val_b)
                ratio = min(val_a, val_b) / denom if denom > 0 else 1.0
                shared_specs_match.append(ratio)
            else:
                # String comparison
                shared_specs_match.append(1.0 if str(val_a).lower() == str(val_b).lower() else 0.0)
                
    features["spec_similarity"] = sum(shared_specs_match) / len(shared_specs_match) if shared_specs_match else 0.5
    
    return features

def predict_match(prod_a: Dict[str, Any], prod_b: Dict[str, Any]) -> Tuple[bool, float]:
    """
    Predicts if product A and product B match, returning (is_match, confidence).
    Uses a hybrid rule-based and similarity weight classifier.
    """
    features = compute_matching_features(prod_a, prod_b)
    
    # Stage 1: Deterministic OEM match
    if features["oem_match"] == 1.0:
        return True, 0.99
    if features["oem_match"] == 0.0:
        # Different part numbers -> very unlikely to match
        return False, 0.95
        
    # Stage 2: Category Leaf check
    if features["category_match"] == 0.0:
        # Different categories -> cannot match
        return False, 1.0
        
    # Stage 3: Weighted confidence score
    # Weights: Title: 0.5, Brand: 0.2, Specs: 0.3
    score = (
        features["title_similarity"] * 0.5 +
        features["brand_match"] * 0.2 +
        features["spec_similarity"] * 0.3
    )
    
    is_match = score >= 0.78
    return is_match, score

def find_matches(product: Dict[str, Any], candidates: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], float]]:
    """
    Finds all matching products in a candidate list.
    """
    matches = []
    for cand in candidates:
        if cand.get("id") == product.get("id"):
            continue
        is_match, confidence = predict_match(product, cand)
        if is_match:
            matches.append((cand, confidence))
            
    # Sort by confidence descending
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches
