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


# ============================== 
# langGraph.py
# University Support System with Web Scraping fallback
# ==============================

# from dataclasses import dataclass, field
# from typing import List, Optional
# import requests
# from bs4 import BeautifulSoup

# from langChainFun import llm, retriever
# from langchain_core.messages import SystemMessage, HumanMessage

# from langgraph.graph import StateGraph, END


# # ===================== STATE ======================
# @dataclass
# class State:
#     query: str
#     intent: Optional[str] = None
#     docs: List = field(default_factory=list)
#     answer: Optional[str] = None
#     need_scrape: bool = False


# # ===================== NODE FUNCTIONS ======================
# def classify_query(state: State) -> State:
#     print("Classifying query...")
#     q = state.query.lower()

#     if any(x in q for x in ["admission", "apply", "enroll", "entrance", "scholarship"]):
#         state.intent = "admissions"
#     elif any(x in q for x in ["undergraduate", "bachelor", "bba", "bs"]):
#         state.intent = "undergraduate"
#     elif any(x in q for x in ["graduate", "master", "mba", "ms", "phd"]):
#         state.intent = "graduate"
#     elif any(x in q for x in ["engineering", "information technology", "it", "cs", "se", "computer science", "software engineering"]):
#         state.intent = "engineering_cs"
#     elif any(x in q for x in ["business", "economics", "natural sciences", "math", "physics"]):
#         state.intent = "business_natural"
#     else:
#         state.intent = "general"

#     return state


# def retrieve_knowledge(state: State) -> State:
#     print("Retrieving knowledge...")
#     state.docs = retriever.invoke(state.query, category=state.intent)
#     return state


# def check_if_scrape_needed(state: State) -> State:
#     print("Checking if web scraping is needed...")
#     print(f"State Docs: len(state.docs)")
#     """
#     Determine if we need to scrape:
#     If retriever returned no docs OR answer is empty → scrape
#     """
#     if not state.docs:
#         print("Need to scrape web for more info.")
#         state.need_scrape = True
#     else:
#         print("No need to scrape web.")
#         state.need_scrape = False
#     return state


# def web_scrape_university(state: State) -> State:
#     print("Web scraping university website...")
#     if not state.need_scrape:
#         return state

#     base_url = "https://www.uos.edu.pk/"
#     search_pages = ["/", "importantanddates", "/aboutus", "scholarships", "/students"]

#     found_docs = []

#     for page in search_pages:
#         try:
#             url = f"{base_url}{page}"
#             response = requests.get(url, timeout=5)
#             if response.status_code == 200:
#                 soup = BeautifulSoup(response.text, "html.parser")
#                 texts = [p.get_text(strip=True) for p in soup.find_all(["p", "li"])]
#                 combined_text = "\n".join(texts)

#                 if any(word.lower() in combined_text.lower() for word in state.query.split()):
#                     # Treat scraped content as a doc for LLM
#                     found_docs.append(combined_text)
#         except Exception:
#             continue

#     if found_docs:
#         state.docs = [{"page_content": d} for d in found_docs]
#         state.need_scrape = False
#     else:
#         state.answer = "ESCALATE"

#     return state


# def resolve_answer(state: State) -> State:
#     print("Resolving answer...")
#     if not state.docs:
#         # No documents at all, cannot generate answer
#         state.answer = "ESCALATE"
#         return state

#     context = "\n\n".join([d.page_content for d in state.docs])

#     system_prompt = f"""
# You are a helpful school/university support assistant.
# Use ONLY the context below to answer the user's query.

# Context:
# {context}
# """

#     messages = [
#         SystemMessage(content=system_prompt),
#         HumanMessage(content=state.query),
#     ]

#     result = llm.invoke(messages)
#     state.answer = result.content
#     return state


# def escalate_if_needed(state: State) -> State:
#     print("Checking if escalation is needed...")
#     ans = (state.answer or "").lower()
#     if "esc" in ans:
#         state.answer = "ESCALATE"
#     return state


# # ===================== GRAPH ======================
# graph = StateGraph(State)

# # Add nodes
# graph.add_node("classify", classify_query)
# graph.add_node("retrieve", retrieve_knowledge)
# graph.add_node("check", check_if_scrape_needed)
# graph.add_node("web_scrape", web_scrape_university)
# graph.add_node("resolve", resolve_answer)
# graph.add_node("escalate", escalate_if_needed)

# # Entry point
# graph.set_entry_point("classify")

# # Normal edges
# graph.add_edge("classify", "retrieve")
# graph.add_edge("retrieve", "check")
# graph.add_edge("web_scrape", "resolve")
# graph.add_edge("resolve", "check")
# graph.add_edge("escalate", END)

# # Conditional edges
# def next_after_check(state: State):
#     return "web_scrape" if state.need_scrape else "resolve"

# graph.add_conditional_edges("check", next_after_check)

# # Compile graph into callable app
# app = graph.compile()
