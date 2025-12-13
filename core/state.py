# core/state.py
"""Agent state definition for the LangGraph workflow."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AgentState:
    """
    State object passed through the LangGraph workflow.
    
    Attributes:
        query: The user's input question
        intent: Classified intent category (admissions, undergraduate, etc.)
        is_casual: Whether the query is casual/greeting (skips RAG)
        needs_web_search: Whether the query needs fresh data from web
        docs: Retrieved documents from vector store
        web_results: Results from web search
        low_confidence: Whether the answer confidence is low (triggers fallback)
        answer: The generated answer to return to user
    """
    query: str
    intent: Optional[str] = None
    is_casual: bool = False
    needs_web_search: bool = False
    docs: List = field(default_factory=list)
    web_results: List = field(default_factory=list)
    low_confidence: bool = False
    answer: Optional[str] = None
