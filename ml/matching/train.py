import structlog
from typing import List, Dict, Any
from sklearn.linear_model import LogisticRegression
from ml.matching.predict import compute_matching_features

logger = structlog.get_logger(__name__)

def train_matching_model(labeled_pairs: List[Tuple[Dict[str, Any], Dict[str, Any], int]]):
    """
    Trains a Logistic Regression model to classify whether two products match.
    labeled_pairs is a list of tuples: (prod_a, prod_b, is_match_label)
    """
    logger.info("Starting matching model training", samples_count=len(labeled_pairs))
    
    X = []
    y = []
    
    for prod_a, prod_b, label in labeled_pairs:
        features = compute_matching_features(prod_a, prod_b)
        # Convert dictionary features to feature vector
        vector = [
            features["oem_match"],
            features["title_similarity"],
            features["brand_match"],
            features["category_match"],
            features["spec_similarity"]
        ]
        X.append(vector)
        y.append(label)
        
    if not X:
        logger.warning("No training pairs found.")
        return None
        
    model = LogisticRegression()
    model.fit(X, y)
    
    logger.info("Matching model training completed", 
                coef=model.coef_.tolist(), 
                intercept=model.intercept_.tolist())
    return model
