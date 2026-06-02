import structlog
import numpy as np
from typing import List, Dict, Any

logger = structlog.get_logger(__name__)

def train_pricing_model(prices_usd: List[float], category: str):
    """
    Fits statistical distribution model parameters (P10, P50, P90) for a leaf category.
    """
    logger.info("Training pricing model", category=category, size=len(prices_usd))
    
    if not prices_usd:
        logger.warning("No price data for category", category=category)
        return None
        
    arr = np.array(prices_usd)
    p10 = float(np.percentile(arr, 10))
    p50 = float(np.percentile(arr, 50))
    p90 = float(np.percentile(arr, 90))
    
    logger.info("Pricing model calibrated", 
                category=category, 
                p10=p10, 
                p50=p50, 
                p90=p90)
                
    return {
        "p10": p10,
        "p50": p50,
        "p90": p90,
        "sample_size": len(prices_usd)
    }
