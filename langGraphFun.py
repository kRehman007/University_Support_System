# langGraph.py
from dataclasses import dataclass, field
from typing import List, Optional

# Import LLM & retriever from langchain.py
from langChainFun import llm, retriever

from langchain_core.messages import SystemMessage, HumanMessage


# ===================== STATE ======================
@dataclass
class State:
    query: str
    intent: Optional[str] = None
    docs: List = field(default_factory=list)
    answer: Optional[str] = None


# ===================== NODES ======================
def classify_query(state: State) -> State:
    q = state.query.lower()

    # Map queries to the correct text file domain
    if any(x in q for x in ["admission", "apply", "enroll", "entrance", "scholarship"]):
        state.intent = "admissions"
    elif any(x in q for x in ["undergraduate", "bachelor", "bba", "bs"]):
        state.intent = "undergraduate"
    elif any(x in q for x in ["graduate", "master", "mba", "ms", "phd"]):
        state.intent = "graduate"
    elif any(x in q for x in ["engineering", "information technology","IT","CS","SE" "computer science", "software engineering"]):
        state.intent = "engineering_cs"
    elif any(x in q for x in ["business", "economics", "natural sciences", "math", "physics"]):
        state.intent = "business_natural"
    else:
        state.intent = "general"

    return state


def retrieve_knowledge(state: State) -> State:
    # Use retriever with the intent as filter if needed
    state.docs = retriever.invoke(state.query, category=state.intent)
    return state


def resolve_answer(state: State) -> State:
    context = "\n\n".join([d.page_content for d in state.docs])

    system_prompt = f"""
You are a helpful school/university support assistant.
Use ONLY the context below to answer the user's query.

Context:
{context}
"""
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state.query),
    ]

    result = llm.invoke(messages)
    state.answer = result.content

    return state


def escalate_if_needed(state: State) -> State:
    ans = (state.answer or "").lower()

    if "i don't know" in ans or len(ans) < 40:
        state.answer = "ESCALATE"

    return state


# ===================== GRAPH ======================
from langgraph.graph import StateGraph, END

graph = StateGraph(State)

graph.add_node("classify", classify_query)
graph.add_node("retrieve", retrieve_knowledge)
graph.add_node("resolve", resolve_answer)
graph.add_node("escalate", escalate_if_needed)

graph.set_entry_point("classify")
graph.add_edge("classify", "retrieve")
graph.add_edge("retrieve", "resolve")
graph.add_edge("resolve", "escalate")
graph.add_edge("escalate", END)

app = graph.compile()


