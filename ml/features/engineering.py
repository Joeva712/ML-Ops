import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from taxonomy.categories import find_category_path
from taxonomy.spec_registry import get_spec_schema

def extract_product_features(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts flat features from a single product dict.
    Converts category, brand, specs, and text metadata into model-ready features.
    """
    features = {}
    
    # 1. Text Features
    features["title_len"] = len(product.get("title", ""))
    features["desc_len"] = len(product.get("description", "")) if product.get("description") else 0
    features["has_oem_part_number"] = 1 if product.get("oem_part_number") else 0
    
    # 2. Categorical Features
    features["source"] = product.get("source", "unknown")
    features["seller_type"] = product.get("seller_type", "distributor")
    features["product_type"] = product.get("product_type", "finished_good")
    features["brand"] = product.get("brand", "generic").lower()
    features["category_leaf"] = product.get("category_leaf", "unknown")
    
    # 3. Numeric Features
    features["seller_rating"] = product.get("seller_rating") or 4.5
    
    # 4. Spec features based on leaf category
    specs = product.get("specifications", {})
    schema = get_spec_schema(product.get("category_leaf", ""))
    
    # Pre-populate common specifications as numeric features
    if schema:
        # Check numeric required/optional fields and convert to features
        for field, definition in {**schema.get("required", {}), **schema.get("optional", {})}.items():
            if definition["type"] in ("float", "int"):
                val = specs.get(field)
                if isinstance(val, (int, float)):
                    features[f"spec_{field}"] = float(val)
                else:
                    # Impute typical median
                    typical = definition.get("typical_range", [0, 0])
                    features[f"spec_{field}"] = float(sum(typical) / 2)
            elif definition["type"] == "enum":
                val = specs.get(field)
                features[f"spec_{field}"] = str(val).lower() if val else "none"
            elif definition["type"] == "bool":
                val = specs.get(field)
                features[f"spec_{field}"] = 1 if val else 0
                
    return features

def build_feature_matrix(products: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Converts a list of product records into a pandas DataFrame of features.
    """
    flat_features = [extract_product_features(p) for p in products]
    df = pd.DataFrame(flat_features)
    
    # Fill missing numeric values with medians
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median() if not df[col].isna().all() else 0.0)
        
    # Fill missing categorical values
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns
    for col in categorical_cols:
        df[col] = df[col].fillna("unknown")
        
    return df
