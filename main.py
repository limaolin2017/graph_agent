"""
Gradio Web UI for Web Testing Agent
Intelligent agent with database storage and multi-turn conversation memory
"""

import os
import sys
import re
import uuid
import asyncio
from typing import Optional, List, Dict, Any, Tuple

import gradio as gr
import psycopg

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agent import get_agent
from database import init_database, db
from config import setup_environment

# Constants
AGENT = get_agent()
URL_PATTERN = r'https?://[^\s]+'
DEFAULT_URL = "unknown"
MAX_DESCRIPTION_LENGTH = 100


def extract_url(query: str) -> str:
    """Extract URL from query string."""
    match = re.search(URL_PATTERN, query)
    return match.group(0) if match else DEFAULT_URL


def format_tool_info(tool_name: str, tool_args: dict) -> str:
    """Format tool call information for display."""
    info = f"**{tool_name}**"
    if 'url' in tool_args:
        info += f"\nURL: `{tool_args['url']}`"
    elif 'query' in tool_args:
        info += f"\nQuery: `{tool_args['query']}`"
    elif 'format_type' in tool_args:
        info += f"\nFormat: `{tool_args['format_type']}`"
    return info


def truncate_content(content: str, max_length: int = 500) -> str:
    """Truncate long content for display."""
    return content[:max_length] + "\n\n... (result truncated)" if len(content) > max_length else content


def add_summary_notification(reasoning_steps: List[str], summary: str):
    """Add formatted summary notification."""
    if not summary:
        return
        
    lines = summary.split('\n')
    request = action = result = ""
    
    for line in lines:
        if line.startswith('REQUEST: '):
            request = line.replace('REQUEST: ', '')
        elif line.startswith('ACTION: '):
            action = line.replace('ACTION: ', '')
        elif line.startswith('RESULT: '):
            result = line.replace('RESULT: ', '')
    
    notification = "🔔 **Tool Call Summary Recorded**"
    if request:
        notification += f"\n  • Request: {request[:60]}{'...' if len(request) > 60 else ''}"
    if action:
        notification += f"\n  • Action: {action}"
    if result:
        notification += f"\n  • Result: {result[:60]}{'...' if len(result) > 60 else ''}"
        
    reasoning_steps.append(notification)


async def record_artifact(run_id: str, artifact_type: str, content: str, 
                         user_request: str, url: str, tool_name: str = ""):
    """Record artifact to database."""
    if run_id:
        return await db.save_artifact(run_id, artifact_type, content, url, user_request, tool_name or artifact_type)
    return False, ""


def clear_history() -> Tuple[List, List, str]:
    """Clear chat history and reset thread_id."""
    return [], [], str(uuid.uuid4())


def update_history(history: List[Dict], reasoning_steps: List[str]) -> List[Dict]:
    """Update history with current reasoning steps."""
    if history:
        history[-1]["content"] = "\n\n".join(reasoning_steps)
    return history


async def respond_stream(query: str, history: List[Dict], thread_id: str):
    """Main conversation handler with streaming support."""
    if not query.strip():
        yield history, history, thread_id
        return
    
    # Initialize
    url = extract_url(query)
    run_id = await db.create_run(url, description=query[:MAX_DESCRIPTION_LENGTH])
    thread_id = thread_id or str(uuid.uuid4())
    history = (history or []).copy()
    
    # Add user message and thinking indicator
    history.append({"role": "user", "content": query})
    history.append({"role": "assistant", "content": "🤔 Thinking..."})
    yield history, history, thread_id
    
    try:
        config = {"configurable": {"thread_id": thread_id}}
        reasoning_steps = []
        
        async for step in AGENT.astream(
            {"messages": [{"role": "user", "content": query}], "run_id": run_id},
            config, stream_mode="values"
        ):
            if not (step.get("messages") and step["messages"]):
                continue
                
            last_message = step["messages"][-1]
            
            # Skip user messages
            if getattr(last_message, 'type', None) == 'human':
                continue
            
            # Handle tool calls
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                for tool_call in last_message.tool_calls:
                    tool_info = format_tool_info(tool_call["name"], tool_call.get("args", {}))
                    reasoning_steps.append(f"---\n\n🔧 **Executing**: {tool_info}")
                    
                    # Record tool call
                    args_preview = str(tool_call.get("args", {}))[:200]
                    call_info = f"Tool: {tool_call['name']}, Args: {args_preview}"
                    success, summary = await record_artifact(run_id, "tool_call", call_info, query, url, tool_call["name"])
                    
                    if success:
                        add_summary_notification(reasoning_steps, summary)
                    
                    yield update_history(history, reasoning_steps), history, thread_id
            
            # Handle tool results
            elif hasattr(last_message, 'tool_call_id'):
                result_content = truncate_content(getattr(last_message, 'content', str(last_message)))
                reasoning_steps.append(f"✅ **Result**:\n```\n{result_content}\n```")
                
                success, summary = await record_artifact(run_id, "tool_result", result_content, query, url)
                if success:
                    add_summary_notification(reasoning_steps, summary)
                
                yield update_history(history, reasoning_steps), history, thread_id
            
            # Handle AI analysis
            else:
                content = getattr(last_message, 'content', '')
                if content and content != query:
                    reasoning_steps.append(f"---\n\n🤖 **Analysis**:\n{content}")
                    yield update_history(history, reasoning_steps), history, thread_id
        
        # Finalize response
        if not reasoning_steps:
            history[-1]["content"] = "❌ No response received, please retry"
            if run_id:
                await db.update_run_status(run_id, "error")
        else:
            history[-1]["content"] = "\n\n".join(reasoning_steps) + "\n\n---\n\n✨ **Complete**"
            if run_id:
                await db.update_run_status(run_id, "completed")
        
        yield history, history, thread_id
        
    except Exception as e:
        history[-1]["content"] = f"❌ Error: {str(e)}"
        if run_id:
            await db.update_run_status(run_id, "error")
        yield history, history, thread_id


def create_ui():
    """Create Gradio interface."""
    with gr.Blocks(
        title="Web Testing Agent",
        analytics_enabled=False,
        theme=gr.themes.Soft(),
        css="""
        .gradio-container { max-width: 1200px !important; }
        .chat-message { font-size: 14px; }
        """
    ) as demo:
        # Header
        gr.Markdown("# 🚀 Web Testing Agent")
        gr.Markdown("🤖 Intelligent agent with database storage and multi-turn conversation memory, supporting real-time streaming responses")
        
        # State management
        history_state = gr.State([])
        thread_id_state = gr.State(str(uuid.uuid4()))
        
        # Main components
        chatbot = gr.Chatbot(
            label="💬 Conversation",
            height=600,
            type='messages',
            show_copy_button=True,
            avatar_images=("User", "AI")
        )
        
        with gr.Row():
            user_input = gr.Textbox(
                label="💭 Your Question",
                placeholder="Enter your question to start testing a website... (e.g., Help me test https://example.com)",
                lines=2, scale=8, max_lines=5
            )
            submit_btn = gr.Button("🚀 Send", variant="primary", scale=1, size="lg")
        
        with gr.Row():
            clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
            gr.Markdown("💡 **Tip:** Supports real-time streaming responses - you can see the agent's thinking process")
        
        # Event handlers
        stream_inputs = [user_input, history_state, thread_id_state]
        stream_outputs = [chatbot, history_state, thread_id_state]
        
        # Submit and enter key handlers
        for trigger in [submit_btn.click, user_input.submit]:
            trigger(
                fn=respond_stream,
                inputs=stream_inputs,
                outputs=stream_outputs,
                show_progress="minimal",
            ).then(lambda: "", inputs=[], outputs=[user_input])
        
        # Clear button
        clear_btn.click(
            fn=clear_history,
            inputs=[],
            outputs=[history_state, chatbot, thread_id_state]
        )
    
    return demo


async def wait_for_db(conn_str: str, tries: int = 20, delay: float = 0.5) -> bool:
    """Wait for database to be ready."""
    for i in range(tries):
        try:
            with psycopg.connect(conn_str) as _:
                return True
        except Exception as e:
            print(f"DB not ready ({i+1}/{tries}): {e}")
            await asyncio.sleep(delay)
    return False


async def bootstrap():
    """Bootstrap the application."""
    setup_environment()
    
    conn_str = os.environ["DATABASE_URL"]
    if not await wait_for_db(conn_str):
        raise RuntimeError("Database connection failed")
    
    init_database()
    await db.connect()
    
    port = int(os.environ.get("GRADIO_SERVER_PORT", 7861))
    demo = create_ui()
    
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        show_api=True,
        show_error=True,
        prevent_thread_lock=False
    )


if __name__ == "__main__":
    print("🚀 Starting Web Testing Agent...")
    print("🌐 Open your browser to http://localhost:7861")
    print("💡 To use the CLI version, run: python cli.py")
    
    asyncio.run(bootstrap())
