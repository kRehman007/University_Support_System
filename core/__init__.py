# core/__init__.py
"""Core module for the University Support System agent."""

from .state import AgentState
from .config import CASUAL_KEYWORDS, TIME_SENSITIVE_KEYWORDS, INTENT_KEYWORDS, UNCERTAINTY_PHRASES
from .classifier import IntentClassifier, get_classifier

__all__ = [
    "AgentState",
    "CASUAL_KEYWORDS",
    "TIME_SENSITIVE_KEYWORDS", 
    "INTENT_KEYWORDS",
    "UNCERTAINTY_PHRASES",
    "IntentClassifier",
    "get_classifier"
]
