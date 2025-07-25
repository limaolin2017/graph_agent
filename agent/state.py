"""
State.py
Simplified LangGraph state using messages-only architecture
All tool calls and results flow through the messages channel for better context management
"""

from typing import Annotated, List
from typing_extensions import TypedDict, NotRequired
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Simplified state schema - messages-only architecture"""

    # Core message flow - all tool calls and results go here
    messages: Annotated[List[AnyMessage], add_messages]
    remaining_steps: int  # Required by create_react_agent to prevent infinite loops

    # Minimal metadata (only what's truly needed outside of messages)
    run_id: NotRequired[str]  # Current run ID for database operations