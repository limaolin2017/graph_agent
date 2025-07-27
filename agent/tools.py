from langchain_core.tools import tool
from langsmith import Client
from .utils import scrape_with_firecrawl, generate_gherkin_tests, generate_cypress_js_tests, format_run_header, format_feedback
from database import search_artifacts_advanced, search_experience_advanced
import os


@tool
def scrape_url(url: str) -> str:
    """Scrape web page content"""
    result = scrape_with_firecrawl(url)
    return f"✅ Scraped {url}\n\n{result}" if result else f"❌ Error: Failed to scrape {url}"


@tool
def generate_requirements() -> str:
    """Generate functional requirements from recently scraped HTML content in conversation history"""
    return """✅ TASK: Analyze the scraped HTML content and generate functional requirements.

INSTRUCTIONS:
1. Look for the most recent scrape_url result in the message history above
2. Analyze the actual HTML/content that was scraped
3. Generate specific requirements based on what you actually see in the scraped content
4. DO NOT make up features that don't exist (like search if there's no search box)

Generate a numbered list of functional requirements based ONLY on elements present in the scraped content:
- Book listing and display
- Navigation elements actually present
- Interactive elements (buttons, links)
- Data shown for each item
- Page structure and layout

Now analyzing the scraped content from the message history..."""


@tool
def generate_test_code(format_type: str = "gherkin") -> str:
    """Generate test code from requirements in conversation history"""
    if format_type.lower() not in ["gherkin", "cypress", "js", "javascript"]:
        return f"❌ Error: Unsupported format type '{format_type}'. Please use 'gherkin' or 'cypress'."
    
    format_name = "Cypress" if format_type.lower() in ["cypress", "js", "javascript"] else "Gherkin"
    
    return f"""✅ TASK: Generate {format_name} test code based on the functional requirements.

INSTRUCTIONS:
1. Look for the functional requirements generated earlier in the message history
2. If no requirements found, look for the scraped content and derive requirements first
3. Create test scenarios ONLY for features that actually exist
4. DO NOT include tests for features not mentioned in the requirements/scraped content

{"Format: Use Feature, Scenario, Given-When-Then structure" if format_type.lower() == "gherkin" else "Format: Use describe() and it() blocks with cy commands"}

Generate {format_name} test code that covers:
- Each functional requirement identified
- Real user workflows based on actual page elements
- Only features that exist in the scraped content

Now converting the requirements into {format_name} test code..."""


@tool
def show_status(metric_name: str = None) -> str:
    """Display latest evaluation metrics from LangSmith evaluators project."""
    ls_api_key = os.getenv("LANGSMITH_API_KEY")
    if not ls_api_key:
        return "❌ Error: LANGSMITH_API_KEY not found in environment variables."
    
    try:
        client = Client(api_key=ls_api_key)
        runs = list(client.list_runs(project_name="evaluators", limit=20))
        
        if not runs:
            return "No runs found in 'evaluators' project."
        
        # Find first run with numeric outputs
        for run in runs:
            if not run.outputs:
                continue
                
            metrics = {k: v for k, v in run.outputs.items() if isinstance(v, (int, float))}
            if not metrics:
                continue
            
            # Build response header
            lines = [format_run_header(run), "\nMetrics:"]
            
            # Add metrics
            if metric_name:
                matching = {k: v for k, v in metrics.items() if metric_name.lower() in k.lower()}
                if not matching:
                    return f"Metric '{metric_name}' not found. Available: {list(metrics.keys())}"
                metrics = matching
            
            lines.extend(f"- {k}: {v}" for k, v in metrics.items())
            
            # Add feedback if available
            feedback = list(client.list_feedback(run_ids=[run.id]))
            if feedback:
                lines.extend(format_feedback(feedback))
            
            return "\n".join(lines)
        
        return "No evaluation metrics found in recent runs."
        
    except Exception as e:
        return f"❌ Error accessing LangSmith: {str(e)}"


@tool
def search_experience(query: str) -> str:
    """Search historical testing experiences and workflow patterns"""
    # Use dedicated function to search only tool execution records
    results = search_experience_advanced(query, k=5)
    if not results:
        return f"🔍 No experience found for '{query}'"
    
    # Filter by distance and format results
    experience_results = []
    for result in results:
        distance = result.get('metadata', {}).get('distance', 0)
        if distance > 0.8:
            continue
        experience_results.append(result)
    
    if not experience_results:
        return f"🔍 No testing experience found for '{query}'"
    
    formatted = []
    for i, result in enumerate(experience_results, 1):
        summary = result.get('summary', '')[:100]
        formatted.append(f"**{i}.** {summary}...")
    
    return f"📚 Found {len(formatted)} testing experiences:\n" + "\n".join(formatted)


@tool
def search_artifacts(query: str) -> str:
    """Search for specific content artifacts like requirements and test code
    
    Use this tool to find similar requirements, test code, or other generated content.
    Extract key elements from scraped pages to search for similar artifacts.
    
    Examples:
    - After scraping a book store: search_artifacts("book title price add cart button listing")
    - After generating requirements: search_artifacts("login form validation error handling")
    """
    results = search_artifacts_advanced(query, k=8)
    if not results:
        return f"🔍 No artifacts found for '{query}'"
    
    # Classify results
    requirements_results = []
    test_code_results = []
    other_content = []
    
    for result in results:
        distance = result.get('metadata', {}).get('distance', 0)
        if distance > 0.9:  # Relaxed threshold for better search results
            continue
            
        content = result.get('content', '')
        
        # Check if it's requirements content
        if ('functional requirements' in content.lower() or 
            (content.count('- ') >= 2 and content.count('\n') >= 3)):
            requirements_results.append(result)
        # Check if it's test code
        elif any(keyword in content.lower() for keyword in 
                ['scenario:', 'given', 'when', 'then', 'feature:', 'describe(', 'it(', 'cy.']):
            test_code_results.append(result)
        else:
            other_content.append(result)
    
    # Build return results
    formatted = []
    
    if requirements_results:
        formatted.append("📋 **Found Requirements:**")
        for i, req in enumerate(requirements_results[:3], 1):
            url = req.get('metadata', {}).get('url', 'unknown')
            content_preview = req.get('content', '')[:250].replace('\n', ' ')
            formatted.append(f"\n{i}. URL: {url}")
            formatted.append(f"   {content_preview}...")
    
    if test_code_results:
        formatted.append("\n🧪 **Found Test Code:**")
        for i, test in enumerate(test_code_results[:3], 1):
            url = test.get('metadata', {}).get('url', 'unknown')
            content_preview = test.get('content', '')[:250].replace('\n', ' ')
            formatted.append(f"\n{i}. URL: {url}")
            formatted.append(f"   {content_preview}...")
    
    if other_content and len(formatted) < 8:
        formatted.append("\n📄 **Other Content:**")
        for i, other in enumerate(other_content[:2], 1):
            summary = other.get('summary', '')[:100]
            formatted.append(f"{i}. {summary}...")
    
    return "\n".join(formatted) if formatted else f"🔍 No relevant artifacts found for '{query}'"
