# graph/builder.py
"""Graph builder for constructing the LangGraph workflow."""

from langgraph.graph import StateGraph, END

from core.state import AgentState
from graph.nodes import (
    classify_query,
    handle_casual_message,
    retrieve_from_vector_store,
    retrieve_from_web,
    generate_hybrid_answer,
    generate_answer_with_fallback_check,
    web_search_fallback,
    check_parallel_routing,
    escalate_if_needed
)
from graph.routing import (
    route_after_classify,
    route_after_vector_retrieval,
    route_after_fallback_check
)


def create_agent_graph() -> StateGraph:
    """
    Build and compile the agent workflow graph.
    
    Flow:
        1. Classify query intent
        2. Route based on classification:
           - Casual → Direct LLM response → END
           - Time-sensitive → Vector + Web search → Hybrid answer
           - Standard → Vector search → Answer with fallback check
        3. If low confidence, fallback to web search
        4. Escalate if still unable to answer
    
    Returns:
        Compiled StateGraph ready for invocation
    """
    graph = StateGraph(AgentState)
    
    # =========================================================================
    # ADD NODES
    # =========================================================================
    graph.add_node("classify", classify_query)
    graph.add_node("handle_casual", handle_casual_message)
    graph.add_node("retrieve_vector", retrieve_from_vector_store)
    graph.add_node("retrieve_web", retrieve_from_web)
    graph.add_node("check_parallel", check_parallel_routing)
    graph.add_node("resolve_hybrid", generate_hybrid_answer)
    graph.add_node("resolve_with_fallback", generate_answer_with_fallback_check)
    graph.add_node("web_fallback", web_search_fallback)
    graph.add_node("escalate", escalate_if_needed)
    
    # =========================================================================
    # SET ENTRY POINT
    # =========================================================================
    graph.set_entry_point("classify")
    
    # =========================================================================
    # CLASSIFICATION ROUTING
    # =========================================================================
    graph.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "casual": "handle_casual",
            "parallel_retrieve": "retrieve_vector",
            "vector_only": "retrieve_vector"
        }
    )
    
    # Casual messages go directly to END
    graph.add_edge("handle_casual", END)
    
    # =========================================================================
    # VECTOR RETRIEVAL → PARALLEL CHECK
    # =========================================================================
    graph.add_edge("retrieve_vector", "check_parallel")
    
    graph.add_conditional_edges(
        "check_parallel",
        route_after_vector_retrieval,
        {
            "do_web_search": "retrieve_web",
            "vector_only_resolve": "resolve_with_fallback"
        }
    )
    
    # =========================================================================
    # WEB RETRIEVAL → HYBRID ANSWER
    # =========================================================================
    graph.add_edge("retrieve_web", "resolve_hybrid")
    graph.add_edge("resolve_hybrid", "escalate")
    
    # =========================================================================
    # VECTOR-ONLY → FALLBACK CHECK
    # =========================================================================
    graph.add_conditional_edges(
        "resolve_with_fallback",
        route_after_fallback_check,
        {
            "web_fallback": "web_fallback",
            "escalate": "escalate"
        }
    )
    
    graph.add_edge("web_fallback", "escalate")
    
    # =========================================================================
    # END
    # =========================================================================
    graph.add_edge("escalate", END)
    
    return graph.compile()
