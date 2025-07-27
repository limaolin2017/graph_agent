import os
import json
from typing import Optional, Dict

try:
    from firecrawl import FirecrawlApp
    FIRECRAWL_AVAILABLE = True
except ImportError:
    FIRECRAWL_AVAILABLE = False

def scrape_with_firecrawl(url: str) -> Optional[str]:
    if not FIRECRAWL_AVAILABLE or not os.getenv("FIRECRAWL_API_KEY"):
        return None
    
    try:
        app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
        result = app.scrape_url(url, formats=['markdown'])
        
        if result and hasattr(result, 'markdown') and result.markdown:
            metadata = getattr(result, 'metadata', {})
            title = metadata.get('title', 'N/A')
            return f"📄 **{title}**\n🔗 **{url}**\n\n{result.markdown}"
        return None
    except:
        return None

# Gherkin scenario templates
GHERKIN_TEMPLATES = {
    'login': """
Scenario: {requirement}
  Given I am on the login page
  When I enter valid credentials
  And I click the login button
  Then I should be logged in successfully
""",
    'form': """
Scenario: {requirement}
  Given I am on the form page
  When I fill in all required fields
  And I submit the form
  Then I should see a success message
""",
    'navigation': """
Scenario: {requirement}
  Given I am on the homepage
  When I click on navigation links
  Then I should navigate to the correct pages
""",
    'default': """
Scenario: {requirement}
  Given I am on the page
  When I interact with the element
  Then I should see the expected behavior
"""
}

def _generate_scenario(requirement: str, template_type: str) -> str:
    """Generate a scenario based on template type"""
    template = GHERKIN_TEMPLATES.get(template_type, GHERKIN_TEMPLATES['default'])
    return template.format(requirement=requirement)


def generate_gherkin_tests(requirements: str) -> str:
    lines = [line.strip()[2:] for line in requirements.split('\n') if line.strip().startswith('- ')]
    if not lines:
        lines = ["Basic page functionality"]
    
    scenarios = []
    for req in lines:
        # Determine template type based on requirement content
        template_type = 'default'
        for keyword in ['login', 'form', 'navigation']:
            if keyword in req.lower():
                template_type = keyword
                break
        scenarios.append(_generate_scenario(req, template_type))
    
    return "Feature: Web Page Testing\n" + "\n".join(scenarios)

# Cypress test templates
CYPRESS_TEMPLATES = {
    'login': """
  it('{requirement}', () => {{
    cy.visit('/login');
    cy.get('[data-cy="username"]').type('testuser');
    cy.get('[data-cy="password"]').type('password123');
    cy.get('[data-cy="login-button"]').click();
    cy.url().should('include', '/dashboard');
  }});""",
    'form': """
  it('{requirement}', () => {{
    cy.visit('/form');
    cy.get('input[type="text"]').first().type('Test Data');
    cy.get('button[type="submit"]').click();
    cy.contains('Success').should('be.visible');
  }});""",
    'navigation': """
  it('{requirement}', () => {{
    cy.visit('/');
    cy.get('nav a').each(($link) => {{
      cy.wrap($link).click();
      cy.url().should('not.equal', 'about:blank');
      cy.go('back');
    }});
  }});""",
    'default': """
  it('{requirement}', () => {{
    cy.visit('/');
    cy.get('body').should('be.visible');
    // Add specific test steps for: {requirement}
  }});"""
}

def _generate_cypress_test(requirement: str, template_type: str) -> str:
    """Generate a Cypress test based on template type"""
    template = CYPRESS_TEMPLATES.get(template_type, CYPRESS_TEMPLATES['default'])
    return template.format(requirement=requirement)


def generate_cypress_js_tests(requirements: str) -> str:
    lines = [line.strip()[2:] for line in requirements.split('\n') if line.strip().startswith('- ')]
    if not lines:
        lines = ["should load the page successfully"]
    
    test_cases = []
    for req in lines:
        # Determine template type based on requirement content
        template_type = 'default'
        for keyword in ['login', 'form', 'navigation']:
            if keyword in req.lower():
                template_type = keyword
                break
        test_cases.append(_generate_cypress_test(req, template_type))
    
    return f"describe('Web Page Tests', () => {{\n{''.join(test_cases)}\n}});"

def generate_smart_summary(user_request: str, tool_name: str, tool_result: str) -> Dict[str, str]:
    """
    Generate a smart summary for database storage.
    
    Args:
        user_request: The original user request
        tool_name: The name of the tool that was called
        tool_result: The result from the tool
        
    Returns:
        A dictionary with request and action keys, and optionally a result key
    """
    try:
        from langchain_openai import ChatOpenAI
        from agent.prompt import SMART_SUMMARY_SYSTEM_MESSAGE, SMART_SUMMARY_USER_TEMPLATE

        client = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=60)
        input_text = SMART_SUMMARY_USER_TEMPLATE.format(
            user_request=user_request, tool_name=tool_name, tool_result_preview=tool_result[:200]
        )
        
        response = client.invoke([
            {"role": "system", "content": SMART_SUMMARY_SYSTEM_MESSAGE},
            {"role": "user", "content": input_text}
        ])
        
        # Try to parse the response as JSON
        try:
            summary_dict = json.loads(response.content)
            if 'request' in summary_dict and 'action' in summary_dict:
                return summary_dict
        except json.JSONDecodeError:
            # If JSON parsing fails, return a default summary
            pass
            
        return {"request": user_request[:50], "action": tool_name}
    except Exception as e:
        # If any error occurs, return a default summary
        return {"request": user_request[:50], "action": tool_name}

def format_summary_for_storage(summary_dict: Dict[str, str]) -> str:
    request = summary_dict.get('request', 'Unknown request')
    action = summary_dict.get('action', 'Unknown action')
    result = summary_dict.get('result', '')
    
    summary = f"REQUEST: {request}\nACTION: {action}"
    if result and str(result).strip():
        summary += f"\nRESULT: {result}"
    return summary
