"""
Gradio Web UI for Web Testing Agent - SIMPLIFIED VERSION
"""

import gradio as gr
import uuid
from typing import List, Dict
from agent import get_agent
from langchain_core.messages import HumanMessage

# 全局agent实例 - 保持对话记忆
GLOBAL_AGENT = get_agent()

def clear_history():
    """Clear chat history and reset thread_id"""
    return [], [], str(uuid.uuid4())

def respond_stream(query, history, thread_id):
    """Main conversation handler with history persistence"""
    if not query.strip():
        yield history, history, thread_id
        return
    
    # Ensure thread_id exists
    if not thread_id:
        thread_id = str(uuid.uuid4())
    
    # Add user message to history
    history = history.copy() if history else []
    history.append({"role": "user", "content": query})
    
    # Add thinking message
    history.append({"role": "assistant", "content": "🤔 Thinking..."})
    yield history, history, thread_id
    
    try:
        # Use global agent instance to maintain conversation memory
        config = {"configurable": {"thread_id": thread_id}}
        
        # Collect reasoning steps
        reasoning_steps = []
        
        # Stream agent responses
        for step in GLOBAL_AGENT.stream(
            {"messages": [HumanMessage(content=query)]},
            config,
            stream_mode="values"
        ):
            if "messages" in step and step["messages"]:
                last_message = step["messages"][-1]
                
                # Skip user messages
                if hasattr(last_message, 'type') and last_message.type == 'human':
                    continue
                
                # Handle tool calls
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    for tool_call in last_message.tool_calls:
                        tool_name = tool_call["name"]
                        tool_args = tool_call.get("args", {})
                        
                        # Format tool call info
                        tool_info = f"**{tool_name}**"
                        if 'url' in tool_args:
                            tool_info += f"\nURL: `{tool_args['url']}`"
                        elif 'query' in tool_args:
                            tool_info += f"\nQuery: `{tool_args['query']}`"
                        elif 'format_type' in tool_args:
                            tool_info += f"\nFormat: `{tool_args['format_type']}`"
                        
                        reasoning_steps.append(f"---\n\n🔧 **Executing**: {tool_info}")
                        
                        # Update display
                        full_content = "\n\n".join(reasoning_steps)
                        history[-1]["content"] = full_content
                        yield history, history, thread_id
                
                # Handle tool results
                elif hasattr(last_message, 'tool_call_id'):
                    result_content = getattr(last_message, 'content', str(last_message))
                    
                    # Truncate long results
                    if len(result_content) > 500:
                        result_content = result_content[:500] + "\n\n... (result truncated)"
                    
                    reasoning_steps.append(f"✅ **Result**:\n```\n{result_content}\n```")
                    
                    # Update display
                    full_content = "\n\n".join(reasoning_steps)
                    history[-1]["content"] = full_content
                    yield history, history, thread_id
                
                # Handle AI reasoning and final response
                else:
                    content = getattr(last_message, 'content', '')
                    if content and content != query:
                        reasoning_steps.append(f"---\n\n🤖 **Analysis**:\n{content}")
                        
                        # Update display
                        full_content = "\n\n".join(reasoning_steps)
                        history[-1]["content"] = full_content
                        yield history, history, thread_id
        
        # If no steps, show error
        if not reasoning_steps:
            history[-1]["content"] = "❌ No response received, please retry"
        else:
            # Add completion indicator
            final_content = "\n\n".join(reasoning_steps) + "\n\n---\n\n✨ **Complete**"
            history[-1]["content"] = final_content
        
        yield history, history, thread_id
        
    except Exception as e:
        history[-1]["content"] = f"❌ Error: {str(e)}"
        yield history, history, thread_id


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
    
    # Store chat history and thread ID in state
    history_state = gr.State([])
    thread_id_state = gr.State(str(uuid.uuid4()))
    
    # Chat display with streaming support
    chatbot = gr.Chatbot(
        label="💬 Conversation",
        bubble_full_width=False,
        height=600,
        type='messages',
        show_copy_button=True,
        avatar_images=("User", "AI")
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
        inputs=[user_input, history_state, thread_id_state],
        outputs=[chatbot, history_state, thread_id_state],
        show_progress="minimal"
    ).then(
        fn=lambda: "",  # Clear input after submission
        inputs=[],
        outputs=[user_input]
    )
    
    clear_btn.click(
        fn=clear_history,
        inputs=[],
        outputs=[history_state, chatbot, thread_id_state]
    )
    
    # Allow submitting with Enter key
    user_input.submit(
        fn=respond_stream,
        inputs=[user_input, history_state, thread_id_state],
        outputs=[chatbot, history_state, thread_id_state],
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
