# Gradio Web Testing Agent - API Endpoints

## Overview

**Base URL:** `http://localhost:7861`  
**API Base Path:** `/gradio_api`  
**Version:** Gradio 5.38.2

## Core Endpoints

### GET `/config`
Get application configuration and info.

**Response:** Application settings, components, and API structure.

### POST `/gradio_api/queue/join`
**Join processing queue to execute functions.**

**Parameters:**
- `fn_index` (integer): Function index (0 for respond_stream)
- `data` (array): Input parameters [query, state1, state2]
- `session_hash` (string): Unique session identifier

**Request Example:**
```bash
curl -X POST "http://localhost:7861/gradio_api/queue/join" \
  -H "Content-Type: application/json" \
  -d '{
    "fn_index": 0,
    "data": ["help me test：https://example.com", null, null],
    "session_hash": "unique_session_123"
  }'
```

**Response:**
```json
{"event_id": "716a4660b365443f9c2af5bb9e707249"}
```

### GET `/gradio_api/queue/data`
**Monitor streaming results via Server-Sent Events.**

**Parameters:**
- `session_hash` (string): Session identifier from queue/join

**Request Example:**
```bash
curl -N -H "Accept: text/event-stream" \
  "http://localhost:7861/gradio_api/queue/data?session_hash=unique_session_123"
```

### POST `/gradio_api/clear_history`
Clear chat history and reset conversation.

**Request Example:**
```bash
curl -X POST "http://localhost:7861/gradio_api/clear_history" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### GET `/gradio_api/queue/status`
Get current processing queue status.

**Response:**
```json
{
  "msg": "estimation",
  "queue_size": 0
}
```

## Complete Workflow Example

### 1. Start Website Testing
```bash
# Join queue for testing
curl -X POST "http://localhost:7861/gradio_api/queue/join" \
  -H "Content-Type: application/json" \
  -d '{
    "fn_index": 0,
    "data": ["Test https://httpbin.org/get", null, null],
    "session_hash": "test_session_456"
  }'
```

### 2. Monitor Real-time Results
```bash
# Stream results
curl -N -H "Accept: text/event-stream" \
  "http://localhost:7861/gradio_api/queue/data?session_hash=test_session_456"
```

### 3. Clear Session
```bash
# Clear history when done
curl -X POST "http://localhost:7861/gradio_api/clear_history" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Agent Workflow

The agent automatically executes this workflow:
1. **search_experience** - Find relevant testing patterns
2. **scrape_url** - Extract website content  
3. **generate_requirements** - Analyze and create requirements
4. **generate_test_code** - Create Gherkin-style test cases

## Key Features

- **Streaming responses** via Server-Sent Events
- **Database integration** for conversation history
- **Queue system** for request management
- **Real-time processing** with 0.5s intervals
- **Tool summary generation** and storage

## Error Responses

**Input Parameter Error:**
```json
{
  "error": "An event handler (respond_stream) didn't receive enough input values (needed: 3, got: 1)"
}
```

**404 Not Found:**
```json
{"detail": "Not Found"}
```

**File Access Denied:**
```json
{"detail": "File not allowed: <path>"}
``` 