# 🤖 Web Testing Automation Agent (2025 Edition)

A clean, modern ReAct agent built with LangGraph for web testing automation. Features the latest PostgreSQL + PGVector technology stack with enterprise-grade code quality.

**✅ Completed Features:**
- 🧠 Intelligent Agent Automation (LangGraph ReAct)
- 🔍 Advanced Semantic Search (PostgreSQL + PGVector + OpenAI embeddings)
- 💾 Data Persistence & LangGraph Checkpoints (2025 Standards)
- 🌐 Web Scraping and Test Code Generation
- 🔧 Clean Code Architecture (Zero Code Duplication)
- 📊 Multi-turn Conversation Memory
- 🎯 Experience-based Learning (RAG)

## ✨ Features

### 🧰 Five Core Tools

1. **🌐 scrape_url()** - Web Page Scraping
   - Extracts HTML content from specified URLs
   - Supports Firecrawl integration for enhanced scraping
   - Returns structured page content with metadata

2. **📋 generate_requirements()** - Requirements Analysis  
   - Analyzes HTML content using AI
   - Extracts functional requirements from page elements
   - Identifies forms, navigation, buttons, and interactions

3. **🧪 generate_test_code()** - Test Code Generation
   - Generates Cypress tests based on requirements
   - Supports both Gherkin and JavaScript formats
   - Includes common UI interaction patterns

4. **📊 show_status()** - Status and Metrics Display
   - Shows current workflow progress
   - Displays processing metrics and results
   - Can be called anytime during execution

5. **🔍 search_experience()** - Historical Experience Search
   - Semantic search through past test cases using PGVector
   - Leverages previous work to avoid duplication
   - RAG-powered knowledge retrieval

## 🚀 Quick Start

### Install Dependencies (2025 Version)
```bash
pip install -r requirements.txt
```

### Configure API Keys
Create a `.env` file or set environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export DATABASE_URL="postgresql://user:pass@localhost:5432/web_testing"
# Optional: Enhanced scraping with Firecrawl
export FIRECRAWL_API_KEY="your-firecrawl-api-key"
```

### Run Examples
```bash
# Main program - unified entry point
python main.py

# Test database connection and PGVector search
python tests/test_db.py

# Basic functionality tests
python tests/simple_test.py
```

### Interactive Commands
Once running, use these commands:
- `quit` or `q` - Exit the program
- `history` or `h` - View recent test runs
- `new` or `n` - Start a new conversation session
- `reset` or `r` - Reset current conversation

## 💡 Usage Examples

### 1. Complete Web Testing Workflow
```
"Test this website: https://example.com/login"
```
The agent will automatically:
1. Scrape the webpage content
2. Generate functional requirements
3. Create Cypress test code
4. Show status and metrics

### 2. Individual Tool Usage
```
"Scrape the HTML from https://example.com/contact"
"Generate requirements for the scraped HTML"
"Generate Cypress test code in JavaScript format"
"Show me the current status"
```

### 3. Experience-Based Learning
```
"Search for previous login form tests"
"Find similar e-commerce testing examples"
```

### 4. Multi-turn Conversations
The agent remembers context across interactions:
```
User: "Scrape https://shop.example.com"
Agent: [Scrapes and analyzes the page]
User: "Now generate tests for the checkout process"
Agent: [Uses previous context to generate relevant tests]
```

## 📁 Project Structure

```
├── main.py                 # Main entry point with session management
├── config.py              # Configuration management (ConfigManager class)
├── requirements.txt        # Python dependencies (2025 versions)
├── agent/
│   ├── __init__.py        # Agent module exports
│   ├── agent.py           # LangGraph ReAct agent creation
│   ├── state.py           # Agent state schema (TypedDict)
│   ├── tools.py           # Five core tools implementation
│   ├── utils.py           # Utility functions (scraping, test generation)
│   └── prompt.py          # System prompts and templates
├── database/
│   └── __init__.py        # PostgreSQL + PGVector integration
├── tests/
│   ├── simple_test.py     # Basic functionality tests
│   └── test_db.py         # Database and semantic search tests
└── README.md              # This documentation
```

## 🔧 Core Architecture

### Agent Creation
```python
# Clean, modern agent setup
def get_agent(checkpointer=None):
    model = ChatOpenAI(**MODEL_CONFIG)
    if checkpointer is None:
        checkpointer = InMemorySaver()
    
    return create_react_agent(
        model=model,
        tools=[scrape_url, generate_requirements, generate_test_code, 
               show_status, search_experience],
        prompt=AGENT_SYSTEM_PROMPT,
        checkpointer=checkpointer
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
# PostgreSQL + PGVector for semantic search
def search_artifacts_advanced(query: str, k: int = 5) -> List[dict]:
    embeddings = get_embeddings()
    query_vector = embeddings.embed_query(query)
    # Vector similarity search with pgvector
    return results
```

## 🎯 Workflow

### Automated Tool Chain
1. **Input URL** → Agent calls `scrape_url(url)`
2. **Analyze Content** → Agent calls `generate_requirements()` 
3. **Generate Tests** → Agent calls `generate_test_code(format_type)`
4. **Show Results** → Agent calls `show_status()`
5. **Learn from History** → Agent uses `search_experience(query)` as needed

### State Management
- Tools share data through agent state (no manual parameter passing)
- HTML content flows from scraping to requirements generation
- Requirements flow to test code generation
- All artifacts are stored in PostgreSQL with vector embeddings

### Memory & Learning
- Multi-turn conversations maintain context
- Historical test cases are searchable via semantic similarity
- Previous solutions inform new test generation
- Experience accumulates over time for better results

## 🌟 Key Features

- ✅ **Clean Architecture**: Modular design with zero code duplication
- ✅ **Intelligent Decision Making**: ReAct architecture with automatic tool selection
- ✅ **Complete Workflow**: End-to-end from webpage to test code
- ✅ **Flexible Output**: Multiple test formats (Gherkin, JavaScript)
- ✅ **Memory & Learning**: Multi-turn conversations with experience retention
- ✅ **Semantic Search**: PGVector-powered historical knowledge retrieval
- ✅ **Enterprise Ready**: Proper error handling, logging, and configuration management
- ✅ **Easy Extension**: Template-based approach for adding new test types
- ✅ **Database Integration**: PostgreSQL with vector embeddings for persistence

## 📚 Technology Stack

### Core Framework
- **LangGraph**: Agent framework with state management
- **LangChain**: LLM application development toolkit
- **OpenAI GPT-4o**: Primary language model for reasoning
- **OpenAI GPT-4o-mini**: Efficient model for requirements analysis

### Database & Search
- **PostgreSQL**: Primary database for runs and artifacts
- **PGVector**: Vector similarity search for semantic retrieval
- **OpenAI Embeddings**: text-embedding-3-small for vector generation
- **psycopg3**: Modern PostgreSQL driver

### Web Scraping
- **Firecrawl**: Enhanced web scraping (optional)
- **Requests**: HTTP client for basic scraping
- **Markdown**: Content format for scraped pages

### Development & Testing
- **Python 3.8+**: Modern Python with type hints
- **asyncio**: Asynchronous programming support
- **pytest**: Testing framework (for future test expansion)

## 🔄 Recent Improvements (Code Cleanup)

### Architecture Enhancements
- **Session Management**: Replaced global variables with `SessionManager` class
- **Configuration**: Introduced `ConfigManager` for centralized config handling
- **Error Handling**: Standardized error patterns with helper functions
- **Template Organization**: Centralized test templates for better maintainability

### Code Quality
- **Language Consistency**: Standardized to English throughout codebase
- **Function Decomposition**: Broke down large functions into focused helpers
- **Type Safety**: Added comprehensive type hints
- **Documentation**: Improved docstrings and inline comments

### Performance & Reliability
- **Database Operations**: Optimized PostgreSQL queries and connection handling
- **Vector Search**: Enhanced PGVector integration with fallback mechanisms
- **Memory Management**: Improved async handling and resource cleanup
- **Testing**: Enhanced test coverage and validation

## 🤝 Contributing

We welcome contributions! Please feel free to submit Issues and Pull Requests.

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up PostgreSQL with PGVector extension
4. Configure environment variables
5. Run tests: `python tests/simple_test.py`

## 📄 License

MIT License - see LICENSE file for details
