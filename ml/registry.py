import structlog
from typing import Dict, Any, Optional

logger = structlog.get_logger(__name__)

# Simulator for MLflow Model Registry
_MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "product_matching": {
        "production": {"version": "1.0.0", "metrics": {"precision": 0.94, "recall": 0.72}},
        "staging": None
    },
    "price_estimator": {
        "production": {"version": "1.0.0", "metrics": {"mape": 0.12, "calibration": 0.81}},
        "staging": None
    }
}

def register_model(model_name: str, version: str, metrics: Dict[str, float]) -> None:
    """Registers a newly trained model in the registry as staging."""
    logger.info("Registering model in staging registry", name=model_name, version=version, metrics=metrics)
    if model_name in _MODEL_REGISTRY:
        _MODEL_REGISTRY[model_name]["staging"] = {
            "version": version,
            "metrics": metrics
        }

def promote_model_to_production(model_name: str) -> bool:
    """Promotes the current staging model to production if it beats the champion."""
    if model_name not in _MODEL_REGISTRY:
        return False
        
    staging = _MODEL_REGISTRY[model_name]["staging"]
    production = _MODEL_REGISTRY[model_name]["production"]
    
    if not staging:
        logger.info("No staging model found to promote", name=model_name)
        return False
        
    if not production:
        # No champion yet, promote staging immediately
        _MODEL_REGISTRY[model_name]["production"] = staging
        _MODEL_REGISTRY[model_name]["staging"] = None
        logger.info("Staging model promoted to production (first model)", name=model_name, version=staging["version"])
        return True
        
    # Evaluate promotion criteria
    promoted = False
    if model_name == "product_matching":
        # Precision must be >= production precision
        if staging["metrics"]["precision"] >= production["metrics"]["precision"]:
            promoted = True
    elif model_name == "price_estimator":
        # MAPE (Mean Absolute Percentage Error) must be <= production MAPE
        if staging["metrics"]["mape"] <= production["metrics"]["mape"]:
            promoted = True
            
    if promoted:
        logger.info("Staging model promoted to production (beat champion!)", 
                    name=model_name, 
                    old_version=production["version"], 
                    new_version=staging["version"])
        _MODEL_REGISTRY[model_name]["production"] = staging
        _MODEL_REGISTRY[model_name]["staging"] = None
        return True
    else:
        logger.info("Staging model did not beat champion. Rejected.", 
                    name=model_name, 
                    staging_metrics=staging["metrics"], 
                    production_metrics=production["metrics"])
        return False

def get_production_model(model_name: str) -> Optional[Dict[str, Any]]:
    """Returns details of the production champion model."""
    if model_name in _MODEL_REGISTRY:
        return _MODEL_REGISTRY[model_name]["production"]
    return None
