"""
Gradio Web UI for Web Testing Agent
Intelligent agent with database storage and multi-turn conversation memory
"""

import gradio as gr
import asyncio
import re
import uuid
from typing import List, Dict, Tuple
from agent import get_agent
from database import db
from config import setup_environment
from langchain_core.messages import HumanMessage

# Constants
URL_PATTERN = r'https?://[^\s]+'
DEFAULT_URL = "unknown"
MAX_DESCRIPTION_LENGTH = 100


def extract_url_from_query(query: str) -> str:
    """Extract URL from query string"""
    match = re.search(URL_PATTERN, query)
    return match.group(0) if match else DEFAULT_URL


def escape_markdown(text: str) -> str:
    """Escape markdown special characters"""
    if not text:
        return text
    # Escape backslashes first
    text = text.replace("\\", "\\\\")
    # Escape other markdown characters
    for char in "*_`~>#|-{}[].!+()":
        text = text.replace(char, "\\" + char)
    return text


def format_message_history(history: List[Dict]) -> List[Tuple[str, str]]:
    """Format message history for display in Chatbot component"""
    formatted = []
    for msg in history:
        # Skip user messages as Gradio handles them automatically
        if msg["type"] == "ai":
            formatted.append((None, escape_markdown(msg["content"])))  # AI message
        elif msg["type"] == "tool_call":
            # Format tool call with special styling
            tool_content = f"🛠️ **Tool Call:** {msg['content']}"
            formatted.append((None, tool_content))  # Tool call message
        elif msg["type"] == "tool_result":
            # Format tool result with special styling
            tool_content = f"📊 **Tool Result:** {msg['content']}"
            formatted.append((None, tool_content))  # Tool result message
        elif msg["type"] == "system":
            # Format system messages with special styling
            system_content = f"⚙️ **System:** {msg['content']}"
            formatted.append((None, system_content))  # System message
    return formatted


async def process_user_query(query: str, history: List[Dict], thread_id: str):
    """
    Process user query through the agent and yield updated history
    Yields: (response_text, updated_history)
    """
    # Don't add user message to history as Gradio handles this automatically
    history = history.copy() if history else []
    
    url = extract_url_from_query(query)
    
    # Create run in database
    run_id = await db.create_run(url, description=query[:MAX_DESCRIPTION_LENGTH])
    
    if not run_id:
        system_msg = "⚠️ Database unavailable, running agent only"
        history.append({"type": "system", "content": system_msg})
        yield format_message_history(history), history
        return
    
    try:
        # Create a new agent instance for each message
        agent = get_agent()
        
        # Use the provided thread ID for conversation continuity
        config = {"configurable": {"thread_id": thread_id}}
        
        # Stream agent responses
        async for step in agent.astream(
            {"messages": [HumanMessage(content=query)], "run_id": run_id},
            config,
            stream_mode="values"
        ):
            if "messages" in step and step["messages"]:
                last_message = step["messages"][-1]
                
                # Handle different types of messages
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    # Handle tool calls
                    for tool_call in last_message.tool_calls:
                        tool_name = tool_call["name"]
                        tool_args = tool_call.get("args", {})
                        call_info = f"Tool: {tool_name}, Args: {tool_args}"
                        history.append({"type": "tool_call", "content": call_info})
                        
                        # Record artifact
                        await db.save_artifact(run_id, "tool_call", call_info, url, query, tool_name)
                
                elif hasattr(last_message, 'tool_call_id'):
                    # Handle tool results
                    result_content = getattr(last_message, 'content', str(last_message))
                    history.append({"type": "tool_result", "content": result_content})
                    
                    # Record artifact
                    await db.save_artifact(run_id, "tool_result", result_content, url, query)
                
                else:
                    # Handle regular AI response
                    content = getattr(last_message, 'content', '')
                    if content:
                        history.append({"type": "ai", "content": content})
                        
                        # Record artifact
                        await db.save_artifact(run_id, "ai_response", content, url, query)
                
                # Yield updated history after each step
                yield format_message_history(history), history
        
        # Update run status
        await db.update_run_status(run_id, "completed")
        yield format_message_history(history), history
            
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        history.append({"type": "system", "content": error_msg})
        
        # Update run status
        await db.update_run_status(run_id, "error")
        
        yield format_message_history(history), history


def clear_history():
    """Clear the chat history"""
    return [], []


def respond(query, history):
    """Process user query and yield response"""
    # Generate a new thread ID for each conversation
    thread_id = str(uuid.uuid4())
    
    try:
        # Create a new event loop if needed
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the async function synchronously
        async_gen = process_user_query(query, history, thread_id)
        while True:
            try:
                response_text, updated_history = loop.run_until_complete(async_gen.__anext__())
                yield response_text, updated_history
            except StopAsyncIteration:
                break
    except Exception as e:
        yield f"❌ Error: {str(e)}", history


# Gradio UI setup
with gr.Blocks(title="Web Testing Agent", analytics_enabled=False) as demo:
    gr.Markdown("# 🚀 Web Testing Agent")
    gr.Markdown("Intelligent agent with database storage and multi-turn conversation memory")
    
    # Store chat history in state
    history_state = gr.State([])
    
    # Chat display
    chatbot = gr.Chatbot(
        label="Conversation",
        bubble_full_width=False,
        height=500
    )
    
    with gr.Row():
        # User input
        user_input = gr.Textbox(
            label="Your Query",
            placeholder="Enter your query to start testing a website...",
            lines=3,
            scale=9
        )
        
        # Submit button
        submit_btn = gr.Button("Submit", variant="primary", scale=1)
    
    # Clear button
    clear_btn = gr.Button("Clear Chat")
    
    # Event handlers
    submit_btn.click(
        fn=respond,
        inputs=[user_input, history_state],
        outputs=[chatbot, history_state],
        queue=False
    )
    
    clear_btn.click(
        fn=clear_history,
        inputs=[],
        outputs=[history_state, chatbot],
        queue=False
    )
    
    # Allow submitting with Enter key
    user_input.submit(
        fn=respond,
        inputs=[user_input, history_state],
        outputs=[chatbot, history_state],
        queue=False
    )


if __name__ == "__main__":
    # Setup environment
    setup_environment()
    
    # Launch the app
    import os
    port = int(os.environ.get("GRADIO_SERVER_PORT", 7861))
    demo.launch(server_name="0.0.0.0", server_port=port, share=True)
