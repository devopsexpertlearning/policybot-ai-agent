# API Documentation

## Base URL

- **Local**: `http://localhost:8000`
- **Production**: `https://your-app.azurewebsites.net`

---

## Endpoints

### POST /ask

Submit a query to the AI agent.

**Request:**
```json
{
  "query": "string (required, 1-1000 chars)",
  "session_id": "string (optional, UUID format)"
}
```

**Response (200 OK):**
```json
{
  "answer": "string",
  "source": ["document1.txt", "document2.txt"],
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "metadata": {
    "query_type": "POLICY|GENERAL|CLARIFICATION",
    "method": "rag|direct",
    "processing_time": 1.42,
    "provider": "gemini|azure",
    "environment": "local|production"
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the parental leave policy?"}'
```

### GET /health

Health check endpoint.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "environment": "local",
  "llm_provider": "gemini",
  "vector_store": "faiss",
  "timestamp": "2026-01-10T16:00:00Z"
}
```

### GET /ready

Readiness probe for Kubernetes/container orchestration.

**Response (200 OK):**
```json
{
  "status": "ready"
}
```

### GET /stats

Get agent statistics and memory usage.

**Response (200 OK):**
```json
{
  "memory": {
    "total_sessions": 5,
    "total_messages": 42,
    "active_sessions": 2
  },
  "provider": "gemini",
  "environment": "local"
}
```

### GET /session/{session_id}

Get information about a specific session.

**Response (200 OK):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-10T15:00:00Z",
  "last_activity": "2026-01-10T15:30:00Z",
  "message_count": 8
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Session abc-123 not found"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error details"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "query"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "detail": "Error details (local env only)"
}
```

---

## Interactive Documentation

Visit these URLs when the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Both provide interactive API testing capabilities.
