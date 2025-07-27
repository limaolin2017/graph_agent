# Web Testing Automation Agent - Usage Examples

## 🌐 Web Interface Input/Output Example

### Starting the Application
```bash
# Start the web interface
python main.py
# Then open http://localhost:7861 in your browser
```

### Input Example
In the web interface input box, type:
```
Help me test this website: https://httpbin.org/get
```

### Output Example
The agent will execute the following workflow and display:

```
🤔 Thinking...

---

🔧 Executing: search_experience
Query: website testing httpbin

✅ Result:
📚 Found 2 experiences:
1. HTTP request testing with API endpoints...
2. Basic website functionality testing...

---

🔧 Executing: scrape_url
URL: https://httpbin.org/get

✅ Result:
✅ Scraped https://httpbin.org/get

📄 **HTTPBin API - Get Request**
🔗 **https://httpbin.org/get**

# Get Request Endpoint
This endpoint returns JSON data about your request...

---

🔧 Executing: generate_requirements

✅ Result:
Based on the scraped content, here are the functional requirements:
- API should return JSON response with request data
- Response should include headers, origin, and URL information
- Status code should be 200 for successful requests
- Content-type should be application/json

---

🔧 Executing: generate_test_code
Format: gherkin

✅ Result:
Feature: Web Page Testing

Scenario: API should return JSON response with request data
  Given I am on the page
  When I interact with the element
  Then I should see the expected behavior

Scenario: Response should include headers and origin information
  Given I am on the page
  When I interact with the element
  Then I should see the expected behavior

---

✨ Complete
```

## Show Status Example

### Input
```
Show me status
```

### Output
```
🔧 Executing: show_status

✅ Result:
📊 Latest Evaluation Results (Run ID: abc12345-def6-7890-ghij-klmnopqrstuv):
Run Name: web_testing_evaluation
Run Type: llm
Start Time: 2025-01-27T20:00:00.123456

Metrics:
- step_completed: 1
- accuracy_score: 0.95
- test_coverage: 0.87

Feedback:
- correctness: 8
  Comment: Generated tests cover most scenarios
- completeness: 7
  Comment: Minor edge cases could be added
```

## 🖥️ CLI Interface Input/Output Example

### Starting the Application
```bash
python cli.py
```

### Input/Output Example
```bash
🚀 Web Testing Agent
==================================================
💬 Enter your query (type 'quit' to exit, 'history' for history, 'new' for new session, 'reset' to reset):

🤖 > Test this login page: https://example.com/login

🤖 Test this login page: https://example.com/login
📝 Run ID: 12345678-1234-5678-9012-123456789abc
💬 Session ID: New session
🆕 New conversation started, session ID: abcd1234-5678-90ef-1234-567890abcdef

================================== Ai Message ==================================

I'll help you test the login page. Let me start by searching for relevant testing patterns and then analyze the page.

================================== Tool Message ==================================
Tool: search_experience(query='login page testing')

🔧 Search experience: login page testing

================================== Tool Message ==================================

📚 Found 3 experiences:
1. Login form validation with username and password fields...
2. Authentication testing with success and error scenarios...
3. Session management and redirect after login...

================================== Tool Message ==================================
Tool: scrape_url(url='https://example.com/login')

🔧 Call tool: scrape_url

================================== Tool Message ==================================

✅ Scraped https://example.com/login

📄 **Login Page**
🔗 **https://example.com/login**

# Login Form
- Username input field
- Password input field  
- Login button
- "Forgot password" link

================================== Tool Message ==================================
Tool: generate_requirements()

🔧 Call tool: generate_requirements

================================== Tool Message ==================================

✅ Requirements generated:
- Validate login form with username and password fields
- Test successful login with valid credentials
- Test error handling for invalid credentials
- Verify redirect behavior after successful login
- Test "forgot password" functionality

================================== Tool Message ==================================
Tool: generate_test_code(format_type='gherkin')

🔧 Call tool: generate_test_code

================================== Tool Message ==================================

✅ Test code generated:

Feature: Web Page Testing

Scenario: Validate login form with username and password fields
  Given I am on the login page
  When I enter valid credentials
  And I click the login button
  Then I should be logged in successfully

Scenario: Test error handling for invalid credentials
  Given I am on the login page
  When I enter invalid credentials
  And I click the login button
  Then I should see an error message

Scenario: Test forgot password functionality
  Given I am on the login page
  When I click the "forgot password" link
  Then I should be redirected to password reset page

================================== Ai Message ==================================

Perfect! I've successfully analyzed the login page and generated comprehensive test scenarios. The testing workflow included:

1. **Experience Search**: Found relevant login testing patterns from previous tests
2. **Web Scraping**: Successfully extracted the login page structure
3. **Requirements Analysis**: Identified key testing scenarios for the login functionality
4. **Test Code Generation**: Created Gherkin-style test scenarios

The generated tests cover the main login functionality including form validation, successful authentication, error handling, and user flow verification.

✅ Run completed: 12345678-1234-5678-9012-123456789abc
```

## 🛠️ Core Features Overview

This intelligent agent system includes 5 core tools:

1. **🔍 search_experience** - Search historical experiences and testing patterns
2. **🌐 scrape_url** - Extract webpage content
3. **📋 generate_requirements** - Analyze functional requirements
4. **🧪 generate_test_code** - Generate test code (supports Gherkin and JavaScript formats)
5. **📊 show_status** - Display status and evaluation metrics

## 🎯 Usage Recommendations

- **Web Interface**: Suitable for general users, provides real-time streaming responses with visualization
- **CLI Interface**: Suitable for advanced users, supports session management and history records
- **Complete Workflow**: System automatically calls tools in sequence to complete testing workflow
- **Multi-turn Conversations**: Supports context memory for continuous dialogue

Choose the appropriate interface based on your needs to use this intelligent testing agent!
