# graph/nodes.py
"""Node functions for the LangGraph workflow."""

from langchain_core.messages import SystemMessage, HumanMessage

from core.state import AgentState
from core.config import UNCERTAINTY_PHRASES, MIN_CONTEXT_LENGTH
from core.classifier import get_classifier
from core.prompts import (
    get_casual_prompt,
    get_rag_prompt,
    get_rag_with_fallback_prompt,
    get_hybrid_prompt,
    get_web_fallback_prompt
)
from langChainFun import llm, retriever
from webSearch import search_university_website, format_web_results


# =============================================================================
# CLASSIFICATION NODE
# =============================================================================
def classify_query(state: AgentState) -> AgentState:
    """
    Classify query intent using ML-based zero-shot classification.
    
    Uses HuggingFace's DeBERTa model for accurate intent detection.
    Falls back to keyword matching if API fails.
    
    Sets:
        - state.is_casual: True if query is a greeting/casual message
        - state.needs_web_search: True if query needs fresh web data
        - state.intent: Category for retrieval filtering
    """
    classifier = get_classifier()
    intent, is_casual, needs_web = classifier.classify(state.query)
    
    state.intent = intent
    state.is_casual = is_casual
    state.needs_web_search = needs_web
    
    return state


# =============================================================================
# CASUAL MESSAGE NODE
# =============================================================================
def handle_casual_message(state: AgentState) -> AgentState:
    """Handle casual/greeting messages directly without RAG."""
    messages = [
        SystemMessage(content=get_casual_prompt()),
        HumanMessage(content=state.query),
    ]
    
    result = llm.invoke(messages)
    state.answer = result.content
    return state


# =============================================================================
# RETRIEVAL NODES
# =============================================================================
def retrieve_from_vector_store(state: AgentState) -> AgentState:
    """Retrieve relevant documents from vector store."""
    state.docs = retriever.invoke(state.query)
    return state


def retrieve_from_web(state: AgentState) -> AgentState:
    """Fetch latest info from university website."""
    state.web_results = search_university_website(state.query)
    return state


# =============================================================================
# ANSWER GENERATION NODES
# =============================================================================
def generate_hybrid_answer(state: AgentState) -> AgentState:
    """Generate answer using both vector store and web context."""
    vector_context = "\n\n".join([d.page_content for d in state.docs])
    web_context = format_web_results(state.web_results)
    
    if web_context:
        prompt = get_hybrid_prompt(vector_context, web_context)
    else:
        prompt = get_rag_prompt(vector_context)

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=state.query),
    ]

    result = llm.invoke(messages)
    state.answer = result.content
    return state


def generate_answer_with_fallback_check(state: AgentState) -> AgentState:
    """Generate answer and check if we need to fallback to web search."""
    vector_context = "\n\n".join([d.page_content for d in state.docs])
    
    # Check if we have enough context
    if len(state.docs) == 0 or len(vector_context) < MIN_CONTEXT_LENGTH:
        state.low_confidence = True
        state.answer = None
        return state
    
    messages = [
        SystemMessage(content=get_rag_with_fallback_prompt(vector_context)),
        HumanMessage(content=state.query),
    ]

    result = llm.invoke(messages)
    state.answer = result.content
    
    # Check for uncertainty in the answer
    state.low_confidence = any(
        phrase in state.answer.lower() 
        for phrase in UNCERTAINTY_PHRASES
    )
    return state


def web_search_fallback(state: AgentState) -> AgentState:
    """Fallback to web search when vector store doesn't have the answer."""
    state.web_results = search_university_website(state.query)
    
    if not state.web_results:
        if not state.answer:
            state.answer = "I couldn't find information about this. Please contact the university directly."
        return state
    
    vector_context = "\n\n".join([d.page_content for d in state.docs])
    web_context = format_web_results(state.web_results)
    
    messages = [
        SystemMessage(content=get_web_fallback_prompt(vector_context, web_context)),
        HumanMessage(content=state.query),
    ]

    result = llm.invoke(messages)
    state.answer = result.content
    state.low_confidence = False
    return state


# =============================================================================
# UTILITY NODES
# =============================================================================
def check_parallel_routing(state: AgentState) -> AgentState:
    """Passthrough node for routing decision after vector retrieval."""
    return state


def escalate_if_needed(state: AgentState) -> AgentState:
    """Check if we need to escalate to human support."""
    from core.config import MIN_ANSWER_LENGTH
    
    answer = (state.answer or "").lower()
    
    if "i don't know" in answer or len(answer) < MIN_ANSWER_LENGTH or state.low_confidence:
        state.answer = "ESCALATE"
    
    return state
