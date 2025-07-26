"""
Configuration Management Module
Manages API keys and other configuration items
"""

import os
from typing import Optional


class ConfigManager:
    """Configuration manager for API keys and environment setup"""
    
    @staticmethod
    def load_env_file():
        """Load environment variables from .env file"""
        env_file = ".env"
        if not os.path.exists(env_file):
            return
            
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip('"\'')
                    # Only set if not already in environment (don't override Docker env vars)
                    if key not in os.environ:
                        os.environ[key] = value

    @staticmethod
    def get_api_key(key_name: str, required: bool = True) -> Optional[str]:
        """Get API key with validation"""
        ConfigManager.load_env_file()

        api_key = os.getenv(key_name)
        placeholder = f"your-{key_name.lower().replace('_', '-')}-here"
        
        if api_key and api_key != placeholder:
            print(f"✅ {key_name} loaded from environment")
            return api_key

        if not required:
            print(f"⚠️ {key_name} not found (optional)")
            return None

        print(f"❌ Valid {key_name} not found")
        print(f"Please set {key_name} in .env file or enter manually")
        
        api_key = input(f"Enter your {key_name}: ").strip()
        if api_key:
            os.environ[key_name] = api_key
            print(f"✅ {key_name} set successfully")
            return api_key
        
        print("❌ No API key provided, application may not work properly")
        return None


def setup_environment() -> bool:
    """Setup runtime environment"""
    print("🔧 Configuring runtime environment...")

    if not ConfigManager.get_api_key("OPENAI_API_KEY", required=True):
        return False

    firecrawl_available = bool(ConfigManager.get_api_key("FIRECRAWL_API_KEY", required=False))
    if firecrawl_available:
        print("🔥 Firecrawl integration enabled")
    else:
        print("⚠️ Firecrawl integration disabled, using basic requests")

    # Check if LangSmith tracing is enabled
    if os.getenv("LANGCHAIN_TRACING_V2") == "true":
        print("📊 LangSmith tracing enabled via .env configuration")
    else:
        print("⚠️ LangSmith tracing disabled")

    print("🎯 Environment configuration complete!")
    return True

# Model configuration
MODEL_CONFIG = {
    "model": "gpt-4o",
    "temperature": 0,
    "max_tokens": 1000,
}

# Agent configuration
AGENT_CONFIG = {
    "max_iterations": 10,
    "verbose": True,
    "stream_mode": "values",
    "use_memory": True,
    "checkpointer_type": "memory"
}
