# graph/routing.py
"""Routing functions for conditional edges in the LangGraph workflow."""

from typing import Literal
from core.state import AgentState


def route_after_classify(state: AgentState) -> Literal["casual", "parallel_retrieve", "vector_only"]:
    """
    Decide routing path after query classification.
    
    Returns:
        - "casual": Skip RAG, go directly to casual response
        - "parallel_retrieve": Query needs web search (time-sensitive)
        - "vector_only": Standard RAG with vector store only
    """
    if state.is_casual:
        return "casual"
    return "parallel_retrieve" if state.needs_web_search else "vector_only"


def route_after_vector_retrieval(state: AgentState) -> Literal["do_web_search", "vector_only_resolve"]:
    """
    Decide whether to also do web search after vector retrieval.
    
    Returns:
        - "do_web_search": Fetch fresh data from web
        - "vector_only_resolve": Proceed with vector context only
    """
    return "do_web_search" if state.needs_web_search else "vector_only_resolve"


def route_after_fallback_check(state: AgentState) -> Literal["web_fallback", "escalate"]:
    """
    Decide whether to fallback to web search based on answer confidence.
    
    Returns:
        - "web_fallback": Low confidence, try web search
        - "escalate": Proceed to escalation check
    """
    return "web_fallback" if state.low_confidence else "escalate"
