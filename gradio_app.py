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


def format_message_history(history: List[Dict]) -> List[Tuple[str, str]]:
    """Format message history for display in Chatbot component"""
    formatted = []
    current_user_msg = None
    current_bot_msgs = []
    
    for msg in history:
        if msg["type"] == "user":
            # If we have accumulated bot messages, add them with the previous user message
            if current_user_msg is not None and current_bot_msgs:
                combined_bot_msg = "\n\n".join(current_bot_msgs)
                formatted.append((current_user_msg, combined_bot_msg))
                current_bot_msgs = []
            
            # Start a new user message
            current_user_msg = msg["content"]
            
        elif msg["type"] == "ai":
            current_bot_msgs.append(msg["content"])
        elif msg["type"] == "tool_call":
            # Format tool call with special styling
            tool_content = f"🛠️ **Tool Call:** {msg['content']}"
            current_bot_msgs.append(tool_content)
        elif msg["type"] == "tool_result":
            # Format tool result with special styling
            tool_content = f"📊 **Tool Result:** {msg['content']}"
            current_bot_msgs.append(tool_content)
        elif msg["type"] == "system":
            # Format system messages with special styling
            system_content = f"⚙️ **System:** {msg['content']}"
            current_bot_msgs.append(system_content)
    
    # Add any remaining messages
    if current_user_msg is not None:
        if current_bot_msgs:
            combined_bot_msg = "\n\n".join(current_bot_msgs)
            formatted.append((current_user_msg, combined_bot_msg))
        else:
            # If no bot response yet, add empty response
            formatted.append((current_user_msg, ""))
    
    return formatted


async def process_user_query(query: str, history: List[Dict], thread_id: str):
    """
    Process user query through the agent and yield updated history
    Yields: (response_text, updated_history)
    """
    # Add user message to history
    history = history.copy() if history else []
    history.append({"type": "user", "content": query})
    
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
    # Reset thread ID when clearing history
    if hasattr(respond, 'thread_id'):
        respond.thread_id = str(uuid.uuid4())
    return [], []


def respond(query, history):
    """Process user query and yield response"""
    if not query.strip():
        return history, history
    
    try:
        # Get agent
        agent = get_agent()
        
        # Simple config
        config = {"configurable": {"thread_id": "simple_chat"}}
        
        # Stream the agent execution to capture all steps
        full_response = []
        
        for step in agent.stream(
            {"messages": [HumanMessage(content=query)]},
            config,
            stream_mode="values"
        ):
            if "messages" in step and step["messages"]:
                last_message = step["messages"][-1]
                
                # Handle tool calls
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    for tool_call in last_message.tool_calls:
                        tool_name = tool_call["name"]
                        tool_args = tool_call.get("args", {})
                        full_response.append(f"🛠️ **Tool Call:** {tool_name}")
                        if tool_args:
                            full_response.append(f"   Args: {tool_args}")
                
                # Handle tool results
                elif hasattr(last_message, 'tool_call_id'):
                    result_content = getattr(last_message, 'content', str(last_message))
                    full_response.append(f"📊 **Tool Result:**")
                    full_response.append(f"   {result_content}")
                
                # Handle AI responses
                else:
                    content = getattr(last_message, 'content', '')
                    if content:
                        full_response.append(f"🤖 **AI Response:**")
                        full_response.append(f"   {content}")
        
        # Combine all responses
        combined_response = "\n\n".join(full_response) if full_response else "No response from agent"
        
        # Add to history
        history.append([query, combined_response])
        return history, history
        
    except Exception as e:
        history.append([query, f"❌ Error: {str(e)}"])
        return history, history


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
