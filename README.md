# 🤖 Web Testing Automation Agent (2025 Edition)

Modern ReAct intelligent agent built with LangGraph, focused on web testing automation. Utilizes the latest PostgreSQL + PGVector technology stack with enterprise-grade code quality.

**✅ Completed Features:**
- 🧠 Intelligent Agent Automation (LangGraph ReAct Architecture)
- 🔍 Advanced Semantic Search (PostgreSQL + PGVector + OpenAI embeddings)
- 💾 Data Persistence & LangGraph Checkpoints (2025 Standard)
- 🌐 Web Scraping and Test Code Generation
- 🔧 Clean Code Architecture (Zero Code Duplication)
- 📊 Multi-turn Conversation Memory
- 🎯 Experience-based Learning (RAG)
- 🐳 Docker Containerized Deployment
- 🌐 Gradio Web Interface + CLI Command Line Interface

## ✨ Core Features

### 🧰 Five Core Tools

1. **🌐 scrape_url()** - Web Scraping
   - Extract HTML content from specified URLs
   - Supports Firecrawl integration for enhanced scraping capabilities
   - Returns structured page content and metadata

2. **📋 generate_requirements()** - Requirements Analysis  
   - Uses AI to analyze HTML content
   - Extracts functional requirements from page elements
   - Identifies forms, navigation, buttons, and interactive elements

3. **🧪 generate_test_code()** - Test Code Generation
   - Generates Cypress tests based on requirements
   - Supports Gherkin and JavaScript formats
   - Includes common UI interaction patterns

4. **📊 show_status()** - Evaluation Metrics Display
   - Fetches latest evaluation metrics from LangSmith
   - Displays metrics like step_completed from evaluator runs
   - Supports querying specific metrics by name

5. **🔍 search_experience()** - Historical Experience Search
   - Performs semantic search on past test cases using PGVector
   - Utilizes previous work to avoid repetition
   - RAG-driven knowledge retrieval

### 🌐 Dual Interface Support

- **Gradio Web Interface**: User-friendly graphical interface with real-time streaming responses
- **CLI Command Line Interface**: Command-line tool for advanced users

## 🚀 Quick Start

### Method 1: Docker Deployment (Recommended)

```bash
# 1. Clone the project
git clone <repository-url>
cd web-testing-agent

# 2. Configure environment variables
cp .env.example .env
# Edit .env file to set your OPENAI_API_KEY

# 3. Start all services
docker-compose up -d

# 4. Access the application
# Web interface: http://localhost:7861
# Database: localhost:5432
```

### Method 2: Local Installation

```bash
# 1. Install dependencies (2025 version)
pip install -r requirements.txt

# 2. Configure API keys
# Create .env file or set environment variables:
export OPENAI_API_KEY="your-openai-api-key"
export DATABASE_URL="postgresql://user:pass@localhost:5432/web_testing"
# Optional: Use Firecrawl for enhanced scraping
export FIRECRAWL_API_KEY="your-firecrawl-api-key"

# 3. Run the application
# Main program - Gradio Web interface (user-friendly interface)
python main.py

# Command line interface (advanced users)
python cli.py

# Test database connection and PGVector search
python tests/test_db.py

# Basic functionality test
python tests/simple_test.py
```

### CLI Interaction Commands
After running, you can use the following commands:
- `quit` or `q` - Exit the program
- `history` or `h` - View recent test run records
- `new` or `n` - Start a new conversation session
- `reset` or `r` - Reset the current conversation

## 💡 Usage Examples

### 1. Complete Web Testing Workflow
```
"Help me test this website: https://example.com/login"
```
The agent will automatically:
1. Scrape webpage content
2. Generate functional requirements
3. Create Cypress test code
4. Display status and metrics

### 2. Individual Tool Usage
```
"Scrape the HTML of https://example.com/contact"
"Generate requirements for the scraped HTML"
"Generate Cypress test code in JavaScript format"
"Show current status"
```

### 3. Experience-based Learning
```
"Search for previous login form tests"
"Find similar e-commerce test examples"
```

### 4. Multi-turn Conversations
The agent remembers context across interactions:
```
User: "Scrape https://shop.example.com"
Agent: [Scrapes and analyzes the page]
User: "Now generate tests for the checkout process"
Agent: [Uses previous context to generate relevant tests]
```

### 5. Docker Environment Usage
```bash
# View service status
docker-compose ps

# View application logs
docker logs web_testing_agent

# Restart application (after code updates)
docker-compose restart agent

# Enter container for debugging
docker exec -it web_testing_agent bash
```

## 🎬 Actual Runtime Effects

### Web Interface Features
- **Real-time Streaming Responses**: See the agent's complete thought process
- **Tool Call Visualization**: Display each tool call and result
- **Multi-turn Conversation Memory**: Support for context-related continuous conversations
- **Multilingual Support**: Interface and responses support both Chinese and English

### Typical Workflow Demonstration
1. **User Input**: "Help me test the login functionality of https://example.com"
2. **Agent Thinking**: Displays "🤔 Thinking..."
3. **Tool Execution**: 
   - 🔧 **Executing**: scrape_url
   - ✅ **Result**: Webpage content successfully scraped
   - 🔧 **Executing**: generate_requirements  
   - ✅ **Result**: Functional requirements analysis completed
   - 🔧 **Executing**: generate_test_code
   - ✅ **Result**: Cypress test code generated
4. **Final Output**: Complete test code and explanation

### CLI Interface Features
- **Session Management**: Supports multi-turn conversation memory
- **History Records**: View previous test runs
- **Database Integration**: Automatically saves all artifacts to PostgreSQL
- **Semantic Search**: Intelligent recommendations based on historical experience

## 📁 Project Structure

```
├── main.py                 # Main entry point (Gradio Web interface + application bootstrap)
├── cli.py                  # Command line interface
├── config.py              # Configuration management (ConfigManager class)
├── requirements.txt        # Python dependencies (2025 version)
├── Dockerfile             # Docker image build file
├── docker-compose.yml     # Docker orchestration configuration
├── deploy.md              # Deployment guide and status
├── agent/                 # Intelligent agent module
│   ├── __init__.py        # Agent module exports
│   ├── agent.py           # LangGraph ReAct agent creation
│   ├── state.py           # Agent state pattern (TypedDict)
│   ├── tools.py           # Five core tool implementations
│   ├── utils.py           # Utility functions (scraping, test generation)
│   └── prompt.py          # System prompts and templates
├── database/              # Database module
│   └── __init__.py        # PostgreSQL + PGVector integration
├── tests/                 # Test module
│   ├── simple_test.py     # Basic functionality test
│   └── test_db.py         # Database and semantic search test
└── README.md              # Project documentation
```

## 🔧 Core Architecture

### Agent Creation
```python
# Clean, modern agent setup
def get_agent(checkpointer=None):
    model = ChatOpenAI(**MODEL_CONFIG)
    checkpointer = checkpointer or InMemorySaver()
    
    return create_react_agent(
        model=model,
        tools=[scrape_url, generate_requirements, generate_test_code, 
               show_status, search_experience],
        prompt=AGENT_SYSTEM_PROMPT,
        checkpointer=checkpointer,
        state_schema=AgentState
    )
```

### Session Management
```python
class SessionManager:
    def __init__(self):
        self.current_thread_id: Optional[str] = None
        self.agent = None
    
    def get_or_create_session(self) -> Tuple[dict, object]:
        if not self.current_thread_id:
            self.current_thread_id = str(uuid.uuid4())
            self.agent = get_agent()
        return {"configurable": {"thread_id": self.current_thread_id}}, self.agent
```

### Database Integration
```python
# PostgreSQL + PGVector semantic search
def search_artifacts_advanced(query: str, k: int = 5) -> List[dict]:
    embeddings = get_embeddings()
    query_vector = embeddings.embed_query(query)
    # Use pgvector for vector similarity search
    return results
```

### Gradio Web Interface
```python
# Web interface supporting real-time streaming responses
def respond_stream(query, history, thread_id):
    """Main conversation handler with history persistence"""
    # Stream process agent responses, displaying thought process in real-time
    for step in GLOBAL_AGENT.stream(...):
        # Process tool calls and results
        yield history, history, thread_id
```

## 🎯 Workflow

### Automated Toolchain
1. **Input URL** → Agent calls `scrape_url(url)`
2. **Analyze Content** → Agent calls `generate_requirements()` 
3. **Generate Tests** → Agent calls `generate_test_code(format_type)`
4. **Display Results** → Agent calls `show_status()`
5. **Learn from History** → Agent uses `search_experience(query)` as needed

### State Management
- Tools share data through agent state (no manual parameter passing)
- HTML content flows from scraping to requirements generation
- Requirements flow to test code generation
- All artifacts are stored in PostgreSQL with vector embeddings

### Memory and Learning
- Multi-turn conversations maintain context
- Historical test cases can be searched via semantic similarity
- Previous solutions guide new test generation
- Experience accumulates over time for better results

### Docker Deployment Architecture
- **Application Container**: Runs Web Testing Agent
- **Database Container**: PostgreSQL + PGVector extension
- **Management Interface**: pgAdmin (optional)
- **Network**: Docker internal network ensures service communication
- **Volume Mounting**: Supports hot code updates

## 🌟 Core Features

- ✅ **Clean Architecture**: Modular design with zero code duplication
- ✅ **Intelligent Decision Making**: ReAct architecture with automatic tool selection
- ✅ **Complete Workflow**: End-to-end process from webpage to test code
- ✅ **Flexible Output**: Multiple test formats (Gherkin, JavaScript)
- ✅ **Memory and Learning**: Multi-turn conversations with experience retention
- ✅ **Semantic Search**: PGVector-driven historical knowledge retrieval
- ✅ **Enterprise Ready**: Comprehensive error handling, logging, and configuration management
- ✅ **Easy to Extend**: Template-based approach to add new test types
- ✅ **Database Integration**: PostgreSQL with vector embedding persistence
- ✅ **Containerized Deployment**: Docker support for one-click deployment
- ✅ **Dual Interface Support**: Web interface + CLI command line
- ✅ **Real-time Streaming Responses**: Visualization of agent thinking process
- ✅ **Hot Code Updates**: Supports real-time code modifications in Docker environment

## 📚 Technology Stack

### Core Frameworks
- **LangGraph**: Agent framework with state management
- **LangChain**: LLM application development toolkit
- **OpenAI GPT-4o**: Primary reasoning language model
- **OpenAI GPT-4o-mini**: Efficient model for requirements analysis

### Database and Search
- **PostgreSQL**: Main database for runs and artifacts
- **PGVector**: Vector similarity search for semantic retrieval
- **OpenAI Embeddings**: text-embedding-3-small for vector generation
- **psycopg3**: Modern PostgreSQL driver

### Web Scraping
- **Firecrawl**: Enhanced web scraping (optional)
- **Requests**: HTTP client for basic scraping
- **Markdown**: Content format for scraped pages

### User Interface
- **Gradio**: Modern web interface framework
- **Real-time Streaming Responses**: Supports visualization of agent thinking process
- **Multilingual Support**: Chinese and English interfaces

### Deployment and Operations
- **Docker**: Containerized deployment
- **Docker Compose**: Multi-service orchestration
- **pgAdmin**: Database management interface (optional)
- **Health Checks**: Service status monitoring

### Development and Testing
- **Python 3.11**: Modern Python with type hints
- **asyncio**: Asynchronous programming support
- **pytest**: Test framework (for future test expansion)

## 🔄 Latest Improvements (Code Cleanup)

### Architecture Enhancements
- **Session Management**: Replaced global variables with `SessionManager` class
- **Configuration Management**: Introduced `ConfigManager` for centralized configuration handling
- **Error Handling**: Standardized error patterns using helper functions
- **Template Organization**: Centralized test templates for improved maintainability

### Code Quality
- **Language Consistency**: Standardized to English throughout the codebase
- **Function Decomposition**: Broke down large functions into focused helper functions
- **Type Safety**: Added comprehensive type hints
- **Documentation**: Improved docstrings and inline comments

### Performance and Reliability
- **Database Operations**: Optimized PostgreSQL queries and connection handling
- **Vector Search**: Enhanced PGVector integration with fallback mechanisms
- **Memory Management**: Improved asynchronous processing and resource cleanup
- **Testing**: Enhanced test coverage and validation

### Dockerized Deployment
- **Containerization**: Full Docker support including multi-service orchestration
- **Hot Code Updates**: Supports real-time code modifications during development
- **Health Checks**: Automatic service status monitoring
- **Network Isolation**: Secure container-to-container communication

### User Experience
- **Real-time Streaming Responses**: Gradio interface supports visualization of agent thinking process
- **Multi-interface Support**: Web interface and CLI coexist
- **Chinese Localization**: Supports Chinese user interface and documentation

## 🐳 Docker Deployment Details

### Service Components
- **web_testing_agent**: Main application container (port 7861)
- **postgres**: PostgreSQL database + PGVector (port 5432)
- **pgadmin**: Database management interface (port 8080, optional)

### Deployment Commands
```bash
# Start all services
docker-compose up -d

# View service status
docker-compose ps

# View application logs
docker logs web_testing_agent

# Restart application (after code updates)
docker-compose restart agent

# Stop all services
docker-compose down
```

### Environment Configuration
Configure in `.env` file:
```bash
OPENAI_API_KEY=your-openai-api-key
FIRECRAWL_API_KEY=your-firecrawl-api-key  # optional
LANGSMITH_API_KEY=your-langsmith-key      # optional
LANGCHAIN_TRACING_V2=true                 # optional
```

## 🤝 Contributing

Contributions are welcome! Feel free to submit Issues and Pull Requests.

### Development Environment Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up PostgreSQL and PGVector extension
4. Configure environment variables
5. Run tests: `python tests/simple_test.py`

### Docker Development Environment
```bash
# Use Docker for development
docker-compose up -d
# Code modifications take effect automatically without rebuilding images
```

## 📄 License

MIT License - See LICENSE file for details
