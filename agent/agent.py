"""
LangGraph-based ReAct agent - 2025 best practices
Uses create_react_agent for simplified implementation, supports RAG retrieval and multi-turn conversation memory
"""

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import ChatOpenAI
from config import MODEL_CONFIG
from agent.tools import scrape_url, generate_requirements, generate_test_code, show_status, search_experience
from agent.prompt import AGENT_SYSTEM_PROMPT
from agent.state import AgentState


def get_agent(checkpointer=None):
    """Get agent instance - supports RAG and multi-turn conversation memory"""
    model = ChatOpenAI(**MODEL_CONFIG)
    checkpointer = checkpointer or InMemorySaver()

    return create_react_agent(
        model=model,
        tools=[scrape_url, generate_requirements, generate_test_code, show_status, search_experience],
        prompt=AGENT_SYSTEM_PROMPT,
        checkpointer=checkpointer,
        state_schema=AgentState
    )
