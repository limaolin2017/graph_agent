from langchain_core.tools import tool
from langsmith import Client
from .utils import scrape_with_firecrawl, generate_gherkin_tests, generate_cypress_js_tests
from database import search_artifacts_advanced
import os


@tool
def scrape_url(url: str) -> str:
    """Scrape web page content"""
    result = scrape_with_firecrawl(url)
    return f"✅ Scraped {url}\n\n{result}" if result else f"❌ Failed to scrape {url}"


@tool
def generate_requirements() -> str:
    """Generate functional requirements from recently scraped HTML content in conversation history"""
    return "✅ I'll analyze the HTML content from the recent scraping results to generate functional requirements."


@tool
def generate_test_code(format_type: str = "gherkin") -> str:
    """Generate test code from requirements in conversation history"""
    return f"✅ I'll generate {format_type} test code based on the requirements from our conversation."


@tool
def show_status(metric_name: str = None) -> str:
    """Display latest evaluation metrics from LangSmith evaluators project."""
    ls_api_key = os.getenv("LANGSMITH_API_KEY")
    if not ls_api_key:
        return "❌ LANGSMITH_API_KEY not found in environment variables."
    
    try:
        client = Client(api_key=ls_api_key)
        runs = list(client.list_runs(project_name="evaluators", limit=20))
        
        if not runs:
            return "No runs found in 'evaluators' project."
        
        # Find runs with numeric outputs (potential metrics)
        for run in runs:
            if not run.outputs:
                continue
                
            # Extract numeric outputs as potential metrics
            metrics = {k: v for k, v in run.outputs.items() if isinstance(v, (int, float))}
            
            if metrics:
                # Build response
                lines = [
                    f"📊 Latest Evaluation Results (Run ID: {run.id}):",
                    f"Run Name: {run.name}",
                    f"Run Type: {run.run_type}",
                    f"Start Time: {run.start_time}",
                    "\nMetrics:"
                ]
                
                if metric_name:
                    # Search for specific metric
                    matching_metrics = {k: v for k, v in metrics.items() 
                                      if metric_name.lower() in k.lower()}
                    if matching_metrics:
                        for key, value in matching_metrics.items():
                            lines.append(f"- {key}: {value}")
                    else:
                        return f"Metric '{metric_name}' not found. Available: {list(metrics.keys())}"
                else:
                    # Show all metrics
                    for key, value in metrics.items():
                        lines.append(f"- {key}: {value}")
                
                # Check for feedback
                feedback = list(client.list_feedback(run_ids=[run.id]))
                if feedback:
                    lines.append("\nFeedback:")
                    for fb in feedback:
                        lines.append(f"- {fb.key}: {fb.score}")
                        if fb.comment:
                            lines.append(f"  Comment: {fb.comment}")
                
                return "\n".join(lines)
        
        return "No evaluation metrics found in recent runs."
        
    except Exception as e:
        return f"❌ Error accessing LangSmith: {str(e)}"


@tool
def search_experience(query: str) -> str:
    """Search historical experiences"""
    results = search_artifacts_advanced(query, k=5)
    if not results:
        return f"🔍 No experience found for '{query}'"
    
    formatted = []
    for i, result in enumerate(results, 1):
        distance = result.get('metadata', {}).get('distance', 0)
        if distance > 0.8:
            continue
        formatted.append(f"**{i}.** {result.get('summary', '')[:100]}...")
    
    return f"📚 Found {len(formatted)} experiences:\n" + "\n".join(formatted) if formatted else f"🔍 No relevant experience for '{query}'"
