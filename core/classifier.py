# core/classifier.py
"""
ML-based intent classification using HuggingFace zero-shot classification.

Uses a lightweight DeBERTa model for accurate intent classification
instead of simple keyword matching.
"""

import os
import requests
from typing import Tuple

from core.config import CASUAL_KEYWORDS, TIME_SENSITIVE_KEYWORDS


# =============================================================================
# CONFIGURATION
# =============================================================================

# Model to use for zero-shot classification
# facebook/bart-large-mnli is always available on HuggingFace Inference API
CLASSIFIER_MODEL = "MoritzLaurer/deberta-v3-xsmall-zeroshot-v1.1-all-33"
# New HuggingFace router endpoint (api-inference.huggingface.co is deprecated)
API_URL = f"https://router.huggingface.co/hf-inference/models/{CLASSIFIER_MODEL}"

# Classification labels
INTENT_LABELS = [
    "casual greeting or farewell",
    "time-sensitive query about deadlines, events, or schedules",
    "question about admissions, enrollment, or scholarships",
    "question about academic programs, courses, or degrees",
    "general university information question"
]

# Mapping from label to intent category
LABEL_TO_INTENT = {
    "casual greeting or farewell": ("casual", True, False),
    "time-sensitive query about deadlines, events, or schedules": ("time_sensitive", False, True),
    "question about admissions, enrollment, or scholarships": ("admissions", False, False),
    "question about academic programs, courses, or degrees": ("academic", False, False),
    "general university information question": ("general", False, False)
}

# Minimum confidence threshold for classification
MIN_CONFIDENCE = 0.4


# =============================================================================
# CLASSIFIER CLASS
# =============================================================================

class IntentClassifier:
    """
    Zero-shot intent classifier using HuggingFace Inference API.
    
    Falls back to keyword-based classification if API fails.
    """
    
    def __init__(self):
        """Initialize the classifier with HuggingFace token."""
        self.token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        self.headers = None
        self.enabled = False
        
        if self.token:
            self.headers = {"Authorization": f"Bearer {self.token}"}
            self.enabled = True
            print("✓ ML classifier initialized with HuggingFace API")
        else:
            print("⚠ HUGGINGFACEHUB_API_TOKEN not set, using keyword fallback")
    
    def classify(self, query: str) -> Tuple[str, bool, bool]:
        """
        Classify the query intent.
        
        Args:
            query: The user's input text
            
        Returns:
            Tuple of (intent, is_casual, needs_web_search)
        """
        if self.enabled and self.headers:
            try:
                return self._classify_with_ml(query)
            except Exception as e:
                print(f"⚠ ML classification failed: {e}, using fallback")
                return self._classify_with_keywords(query)
        else:
            return self._classify_with_keywords(query)
    
    def _classify_with_ml(self, query: str) -> Tuple[str, bool, bool]:
        """Classify using the zero-shot ML model via direct API call."""
        payload = {
            "inputs": query,
            "parameters": {
                "candidate_labels": INTENT_LABELS
            }
        }
        
        response = requests.post(API_URL, headers=self.headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        # Result format: list of {"label": "...", "score": 0.xx}
        # First item is the highest scoring label
        print('Results: ', result)
        top_result = result[0]
        top_label = top_result["label"]
        top_score = top_result["score"]
        
        # If confidence is too low, fall back to keywords
        if top_score < MIN_CONFIDENCE:
            return self._classify_with_keywords(query)
        
        # Map to intent
        intent, is_casual, needs_web = LABEL_TO_INTENT.get(
            top_label, 
            ("general", False, False)
        )
        
        return intent, is_casual, needs_web
    
    def _classify_with_keywords(self, query: str) -> Tuple[str, bool, bool]:
        """Fallback keyword-based classification."""
        q = query.lower().strip()
        
        # Check for casual messages
        if len(q.split()) <= 5:
            is_casual = any(kw in q for kw in CASUAL_KEYWORDS)
        else:
            is_casual = q in CASUAL_KEYWORDS or q.rstrip('!?.') in CASUAL_KEYWORDS
        
        if is_casual:
            return "casual", True, False
        
        # Check for time-sensitive queries
        needs_web = any(kw in q for kw in TIME_SENSITIVE_KEYWORDS)
        
        # Basic intent classification
        if any(x in q for x in ["admission", "apply", "enroll", "entrance", "scholarship"]):
            return "admissions", False, needs_web
        elif any(x in q for x in ["program", "course", "degree", "curriculum", "major"]):
            return "academic", False, needs_web
        else:
            return "general", False, needs_web


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

# Create a single instance to reuse the connection
_classifier_instance = None

def get_classifier() -> IntentClassifier:
    """Get or create the singleton classifier instance."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = IntentClassifier()
    return _classifier_instance
