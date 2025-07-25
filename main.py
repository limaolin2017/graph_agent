"""
Web Testing Agent - Main Entry Point
Intelligent agent with database storage and multi-turn conversation memory
"""

import asyncio
import re
import uuid
from typing import Optional, Tuple
from agent import get_agent
from database import db
from config import setup_environment

# Constants
URL_PATTERN = r'https?://[^\s]+'
DEFAULT_URL = "unknown"
MAX_DESCRIPTION_LENGTH = 100
SEPARATOR_LINE = "=" * 50

def extract_url_from_query(query: str) -> str:
    """Extract URL from query string"""
    match = re.search(URL_PATTERN, query)
    return match.group(0) if match else DEFAULT_URL


class SessionManager:
    """Simplified session management"""
    
    def __init__(self):
        self.current_thread_id: Optional[str] = None
        self.agent = None
    
    def get_or_create_session(self) -> Tuple[dict, object]:
        """Get or create session"""
        if not self.current_thread_id:
            self.current_thread_id = str(uuid.uuid4())
            self.agent = get_agent()
            print(f"🆕 New conversation started, session ID: {self.current_thread_id}")
        return {"configurable": {"thread_id": self.current_thread_id}}, self.agent
    
    def reset_session(self):
        """Reset session"""
        self.current_thread_id = None
        self.agent = None
        print("🔄 Conversation reset")


session_manager = SessionManager()


async def record_artifact(
    run_id: str, 
    artifact_type: str, 
    content: str, 
    user_request: str, 
    url: str, 
    tool_name: str = ""
):
    """Record artifact to database"""
    if run_id:
        await db.save_artifact(run_id, artifact_type, content, url, user_request, tool_name or artifact_type)


async def run_with_database(query: str):
    """Run agent and save to database with multi-turn conversation memory"""
    url = extract_url_from_query(query)
    run_id = await db.create_run(url, description=query[:MAX_DESCRIPTION_LENGTH])

    print(f"\n🤖 {query}")
    print(f"📝 Run ID: {run_id}")
    print(f"💬 Session ID: {session_manager.current_thread_id or 'New session'}")

    if not run_id:
        print("⚠️ Database unavailable, running agent only")

    try:
        config, session_agent = session_manager.get_or_create_session()
        
        async for step in session_agent.astream(
            {"messages": [{"role": "user", "content": query}], "run_id": run_id},
            config,
            stream_mode="values"
        ):
            await _process_agent_step(step, run_id, query, url)

        if run_id:
            await db.update_run_status(run_id, "completed")
            print(f"✅ Run completed: {run_id}")

    except Exception as e:
        print(f"❌ Error: {e}")
        if run_id:
            await db.update_run_status(run_id, "error")


async def _process_agent_step(step: dict, run_id: str, query: str, url: str):
    """Process individual agent step"""
    if "messages" not in step:
        return
        
    last_message = step["messages"][-1]
    last_message.pretty_print()
    
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        await _handle_tool_calls(last_message.tool_calls, run_id, query, url)
    elif hasattr(last_message, 'tool_call_id'):
        await record_artifact(run_id, "tool_result", last_message.content, query, url)


async def _handle_tool_calls(tool_calls: list, run_id: str, query: str, url: str):
    """Handle tool calls and record artifacts"""
    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call.get("args", {})
        args_preview = str(tool_args)[:200]
        call_info = f"Tool: {tool_name}, Args: {args_preview}"
        
        await record_artifact(run_id, "tool_call", call_info, query, url, tool_name)
        
        display_name = (
            f"Search experience: {tool_args.get('query', 'unknown')}" 
            if tool_name == "search_experience" 
            else f"Call tool: {tool_name}"
        )
        print(f"🔧 {display_name}")

async def show_recent_runs():
    """Display recent run records"""
    runs = await db.get_recent_runs(5)
    
    print("\n📊 Recent runs:")
    print("-" * 60)
    for run in runs:
        status_emoji = {"completed": "✅", "error": "❌"}.get(run['status'], "⏳")
        print(f"{status_emoji} ID:{run['run_id']} | {run['url']} | {run['status']} | {run['start_ts']}")

async def main():
    """Main function"""
    setup_environment()
    await db.connect()

    print("🚀 Web Testing Agent")
    print(SEPARATOR_LINE)

    try:
        await _interactive_mode()
    finally:
        await db.close()


def _is_quit_command(user_input: str) -> bool:
    """Check if user input is a quit command"""
    return user_input.lower() in ('quit', 'exit', 'q')

def _is_history_command(user_input: str) -> bool:
    """Check if user input is a history command"""
    return user_input.lower() in ('history', 'h')

def _is_new_session_command(user_input: str) -> bool:
    """Check if user input is a new session command"""
    return user_input.lower() in ('new', 'n')

def _is_reset_command(user_input: str) -> bool:
    """Check if user input is a reset command"""
    return user_input.lower() in ('reset', 'r')


async def _interactive_mode():
    """Interactive mode handler"""
    print("💬 Enter your query (type 'quit' to exit, 'history' for history, 'new' for new session, 'reset' to reset):")

    while True:
        user_input = input("\n🤖 > ").strip()
        
        if not user_input:
            continue
            
        # Handle commands using helper functions
        if _is_quit_command(user_input):
            print("👋 Goodbye!")
            break
        elif _is_history_command(user_input):
            await show_recent_runs()
        elif _is_new_session_command(user_input):
            session_manager.get_or_create_session()
        elif _is_reset_command(user_input):
            session_manager.reset_session()
        else:
            await run_with_database(user_input)

if __name__ == "__main__":
    asyncio.run(main())
