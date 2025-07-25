from langchain_core.tools import tool
from .utils import scrape_with_firecrawl, generate_gherkin_tests, generate_cypress_js_tests
from database import search_artifacts_advanced


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
def show_status() -> str:
    """Display workflow status"""
    return "📊 Analyzing message history for workflow status..."


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
