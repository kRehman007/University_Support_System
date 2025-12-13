# langGraphFun.py
"""
University Support System - LangGraph Agent Entry Point

This is the main entry point for the agent. The actual implementation
is modularized across the following packages:

- core/
  - config.py   : Keywords and configuration constants
  - state.py    : AgentState dataclass
  - prompts.py  : LLM prompt templates

- graph/
  - nodes.py    : Node functions (classify, retrieve, generate, etc.)
  - routing.py  : Conditional routing logic
  - builder.py  : Graph construction

Usage:
    from langGraphFun import app, State
    result = app.invoke({"query": "Tell me about admissions"})
"""

from graph.builder import create_agent_graph
from core.state import AgentState

# Create and compile the agent graph
app = create_agent_graph()

# Export State for backwards compatibility with main.py
State = AgentState

__all__ = ["app", "State", "AgentState"]
