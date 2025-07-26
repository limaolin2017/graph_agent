"""
Gradio Web UI for Web Testing Agent
Intelligent agent with database storage and multi-turn conversation memory
"""

import gradio as gr
import asyncio
import re
import uuid
import time
from typing import List, Dict
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


def format_message_history(history: List[Dict]) -> List[Dict]:
    """Format message history for display in Chatbot component using OpenAI-style messages"""
    formatted = []
    current_bot_msgs = []
    
    for msg in history:
        if msg["type"] == "user":
            # If we have accumulated bot messages, add them first
            if current_bot_msgs:
                combined_bot_msg = "\n\n".join(current_bot_msgs)
                formatted.append({"role": "assistant", "content": combined_bot_msg})
                current_bot_msgs = []
            
            # Add user message
            formatted.append({"role": "user", "content": msg["content"]})
            
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
    
    # Add any remaining bot messages
    if current_bot_msgs:
        combined_bot_msg = "\n\n".join(current_bot_msgs)
        formatted.append({"role": "assistant", "content": combined_bot_msg})
    
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


async def respond_stream_async(query, history):
    """Async version of streaming response for better performance"""
    if not query.strip():
        yield history, history
        return
    
    # Add user message to history
    history = history.copy() if history else []
    history.append({"role": "user", "content": query})
    
    # Initialize assistant message
    history.append({"role": "assistant", "content": "🤔 Thinking..."})
    yield history, history
    
    try:
        # Get agent
        agent = get_agent()
        
        # Simple config
        config = {"configurable": {"thread_id": "simple_chat"}}
        
        # Track response components
        response_parts = []
        current_ai_content = ""
        
        # Stream the agent execution
        async for step in agent.astream(
            {"messages": [HumanMessage(content=query)]},
            config,
            stream_mode="values"
        ):
            if "messages" in step and step["messages"]:
                last_message = step["messages"][-1]
                
                # Skip user messages (HumanMessage)
                if hasattr(last_message, 'type') and last_message.type == 'human':
                    continue
                
                # Handle tool calls
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    for tool_call in last_message.tool_calls:
                        tool_name = tool_call["name"]
                        tool_args = tool_call.get("args", {})
                        tool_info = f"🛠️ **Tool Call:** {tool_name}"
                        if tool_args:
                            # Format args nicely
                            args_str = ", ".join([f"{k}={v}" for k, v in tool_args.items()])
                            tool_info += f"\n   Args: {args_str}"
                        
                        response_parts.append(tool_info)
                        
                        # Update display
                        full_response = "\n\n".join(response_parts)
                        if current_ai_content:
                            full_response += f"\n\n🤖 **AI Response:**\n{current_ai_content}"
                        
                        history[-1]["content"] = full_response
                        yield history, history
                        await asyncio.sleep(0.1)  # Small delay for better UX
                
                # Handle tool results
                elif hasattr(last_message, 'tool_call_id'):
                    result_content = getattr(last_message, 'content', str(last_message))
                    # Truncate very long results
                    if len(result_content) > 500:
                        result_content = result_content[:500] + "..."
                    
                    tool_result = f"📊 **Tool Result:**\n{result_content}"
                    response_parts.append(tool_result)
                    
                    # Update display
                    full_response = "\n\n".join(response_parts)
                    if current_ai_content:
                        full_response += f"\n\n🤖 **AI Response:**\n{current_ai_content}"
                    
                    history[-1]["content"] = full_response
                    yield history, history
                    await asyncio.sleep(0.1)  # Small delay for better UX
                
                # Handle AI responses
                else:
                    content = getattr(last_message, 'content', '')
                    if content and content != query:  # Make sure it's not the user query
                        current_ai_content = content
                        
                        # Update display
                        full_response = "\n\n".join(response_parts)
                        if current_ai_content:
                            full_response += f"\n\n🤖 **AI Response:**\n{current_ai_content}"
                        
                        history[-1]["content"] = full_response
                        yield history, history
                        await asyncio.sleep(0.05)  # Smaller delay for AI responses
        
        # Final yield with complete response
        if not response_parts and not current_ai_content:
            history[-1]["content"] = "❌ Agent didn't return a response"
        
        yield history, history
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        history[-1]["content"] = error_msg
        yield history, history

def respond_stream(query, history):
    """Process user query with streaming response"""
    if not query.strip():
        yield history, history
        return
    
    # Add user message to history
    history = history.copy() if history else []
    history.append({"role": "user", "content": query})
    
    # Initialize assistant message with thinking indicator
    history.append({"role": "assistant", "content": "🤔 Thinking..."})
    yield history, history
    
    try:
        # Get agent
        agent = get_agent()
        
        # Simple config with unique thread ID for each conversation
        thread_id = f"chat_{int(time.time())}"
        config = {"configurable": {"thread_id": thread_id}}
        
        # Track response components
        response_parts = []
        current_ai_content = ""
        step_count = 0
        
        # Stream the agent execution
        for step in agent.stream(
            {"messages": [HumanMessage(content=query)]},
            config,
            stream_mode="values"
        ):
            step_count += 1
            
            if "messages" in step and step["messages"]:
                last_message = step["messages"][-1]
                
                # Skip user messages (HumanMessage)
                if hasattr(last_message, 'type') and last_message.type == 'human':
                    continue
                
                # Handle tool calls
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    for tool_call in last_message.tool_calls:
                        tool_name = tool_call["name"]
                        tool_args = tool_call.get("args", {})
                        
                        # Create a more user-friendly tool display
                        tool_display_names = {
                            "scrape_url": "Web Scraping",
                            "generate_requirements": "Generate Requirements",
                            "generate_test_code": "Generate Test Code",
                            "show_status": "Show Status",
                            "search_experience": "Search Experience"
                        }
                        
                        display_name = tool_display_names.get(tool_name, tool_name)
                        tool_info = f"🛠️ **Executing:** {display_name}"
                        
                        if tool_args:
                            # Format args nicely, but don't show all details
                            if 'url' in tool_args:
                                tool_info += f"\n   🌐 URL: {tool_args['url']}"
                            elif 'query' in tool_args:
                                tool_info += f"\n   🔍 Query: {tool_args['query']}"
                        
                        response_parts.append(tool_info)
                        
                        # Update display
                        full_response = "\n\n".join(response_parts)
                        if current_ai_content:
                            full_response += f"\n\n🤖 **AI Analysis:**\n{current_ai_content}"
                        
                        history[-1]["content"] = full_response
                        yield history, history
                
                # Handle tool results
                elif hasattr(last_message, 'tool_call_id'):
                    result_content = getattr(last_message, 'content', str(last_message))
                    
                    # Truncate very long results and make them more readable
                    if len(result_content) > 800:
                        result_content = result_content[:800] + "\n\n... (result truncated)"
                    
                    tool_result = f"✅ **Execution Complete**\n```\n{result_content}\n```"
                    response_parts.append(tool_result)
                    
                    # Update display
                    full_response = "\n\n".join(response_parts)
                    if current_ai_content:
                        full_response += f"\n\n🤖 **AI Analysis:**\n{current_ai_content}"
                    
                    history[-1]["content"] = full_response
                    yield history, history
                
                # Handle AI responses
                else:
                    content = getattr(last_message, 'content', '')
                    if content and content != query:  # Make sure it's not the user query
                        current_ai_content = content
                        
                        # Update display
                        full_response = "\n\n".join(response_parts)
                        if current_ai_content:
                            full_response += f"\n\n🤖 **AI Analysis:**\n{current_ai_content}"
                        
                        history[-1]["content"] = full_response
                        yield history, history
        
        # Final yield with complete response
        if not response_parts and not current_ai_content:
            history[-1]["content"] = "❌ Sorry, I didn't generate any response. Please try again or check your question."
        
        # Add completion indicator
        if history[-1]["content"] and not history[-1]["content"].endswith("✨"):
            history[-1]["content"] += "\n\n✨ *Response Complete*"
        
        yield history, history
        
    except Exception as e:
        error_msg = f"❌ **Error Occurred:** {str(e)}\n\nPlease try again or contact support."
        history[-1]["content"] = error_msg
        yield history, history


# Gradio UI setup
with gr.Blocks(
    title="Web Testing Agent", 
    analytics_enabled=False,
    theme=gr.themes.Soft(),
    css="""
    .gradio-container {
        max-width: 1200px !important;
    }
    .chat-message {
        font-size: 14px;
    }
    """
) as demo:
    gr.Markdown("# 🚀 Web Testing Agent")
    gr.Markdown("🤖 Intelligent agent with database storage and multi-turn conversation memory, supporting real-time streaming responses")
    
    # Store chat history in state
    history_state = gr.State([])
    
    # Chat display with streaming support
    chatbot = gr.Chatbot(
        label="💬 Conversation",
        bubble_full_width=False,
        height=600,
        type='messages',
        show_copy_button=True,
        avatar_images=("👤", "🤖")
    )
    
    with gr.Row():
        # User input
        user_input = gr.Textbox(
            label="💭 Your Question",
            placeholder="Enter your question to start testing a website... (e.g., Help me test https://example.com)",
            lines=2,
            scale=8,
            max_lines=5
        )
        
        # Submit button
        submit_btn = gr.Button("🚀 Send", variant="primary", scale=1, size="lg")
    
    with gr.Row():
        # Clear button
        clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
        
        # Status indicator
        gr.Markdown("💡 **Tip:** Supports real-time streaming responses - you can see the agent's thinking process")
    
    # Event handlers with streaming support
    submit_btn.click(
        fn=respond_stream,
        inputs=[user_input, history_state],
        outputs=[chatbot, history_state],
        show_progress="minimal"
    ).then(
        fn=lambda: "",  # Clear input after submission
        inputs=[],
        outputs=[user_input]
    )
    
    clear_btn.click(
        fn=clear_history,
        inputs=[],
        outputs=[history_state, chatbot]
    )
    
    # Allow submitting with Enter key
    user_input.submit(
        fn=respond_stream,
        inputs=[user_input, history_state],
        outputs=[chatbot, history_state],
        show_progress="minimal"
    ).then(
        fn=lambda: "",  # Clear input after submission
        inputs=[],
        outputs=[user_input]
    )


if __name__ == "__main__":
    # Setup environment
    setup_environment()
    
    # Launch the app
    import os
    port = int(os.environ.get("GRADIO_SERVER_PORT", 7861))
    demo.launch(server_name="0.0.0.0", server_port=port, share=True)
