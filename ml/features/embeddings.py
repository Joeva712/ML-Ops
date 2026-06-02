import numpy as np
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class TextVectorizer:
    def __init__(self):
        # Char n-grams are extremely effective for typo-resilient product matches and OEM codes
        self.vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=1,
            lowercase=True
        )
        self.is_fitted = False

    def fit(self, texts: List[str]):
        if not texts:
            return
        self.vectorizer.fit(texts)
        self.is_fitted = True

    def transform(self, texts: List[str]) -> np.ndarray:
        if not self.is_fitted:
            # Fallback fit
            self.fit(texts)
        return self.vectorizer.transform(texts).toarray()

    def get_similarity(self, text_a: str, text_b: str) -> float:
        """Returns the cosine similarity between two text strings."""
        if not self.is_fitted:
            self.fit([text_a, text_b])
        
        vecs = self.vectorizer.transform([text_a, text_b]).toarray()
        sim = cosine_similarity([vecs[0]], [vecs[1]])[0][0]
        return float(sim)

# Singleton helper instance
text_vectorizer = TextVectorizer()
