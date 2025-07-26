"""
Web Testing Agent - Main Entry Point
Launches the Gradio Web UI by default
"""

import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup environment
from config import setup_environment
setup_environment()

# Import and launch the Gradio app
from gradio_app import demo

if __name__ == "__main__":
    print("🚀 Starting Web Testing Agent...")
    print("🌐 Open your browser to http://localhost:7861")
    print("💡 To use the CLI version, run: python cli.py")
    
    # Get port from environment or use default
    port = int(os.environ.get("GRADIO_SERVER_PORT", 7861))
    
    # Launch with Docker-compatible settings
    demo.launch(
        server_name="0.0.0.0",  # Allow external connections
        server_port=port,
        share=False,  # Disable share in Docker
        show_api=False,
        show_error=True
    )
