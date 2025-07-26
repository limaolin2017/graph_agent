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
    """清除聊天历史并重置thread_id"""
    return [], [], str(uuid.uuid4())

def respond_stream(query, history, thread_id):
    """主要的对话处理函数 - 保持历史记录"""
    if not query.strip():
        yield history, history, thread_id
        return
    
    # 确保有thread_id
    if not thread_id:
        thread_id = str(uuid.uuid4())
    
    # 添加用户消息到历史记录
    history = history.copy() if history else []
    history.append({"role": "user", "content": query})
    
    # 添加思考中的消息
    history.append({"role": "assistant", "content": "🤔 思考中..."})
    yield history, history, thread_id
    
    try:
        # 使用全局agent实例保持对话记忆
        config = {"configurable": {"thread_id": thread_id}}
        
        # 流式处理agent响应
        final_content = ""
        for step in GLOBAL_AGENT.stream(
            {"messages": [HumanMessage(content=query)]},
            config,
            stream_mode="values"
        ):
            if "messages" in step and step["messages"]:
                last_message = step["messages"][-1]
                
                # 跳过用户消息
                if hasattr(last_message, 'type') and last_message.type == 'human':
                    continue
                
                # 获取AI响应内容
                content = getattr(last_message, 'content', '')
                if content and content != query:
                    final_content = content
                    history[-1]["content"] = content
                    yield history, history, thread_id
        
        # 如果没有响应，显示错误
        if not final_content:
            history[-1]["content"] = "❌ 没有收到响应，请重试"
        
        yield history, history, thread_id
        
    except Exception as e:
        history[-1]["content"] = f"❌ 错误: {str(e)}"
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
