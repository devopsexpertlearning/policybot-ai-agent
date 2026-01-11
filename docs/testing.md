# Testing Guide

## Overview

This project has comprehensive test coverage (80%+) with unit tests, integration tests, and performance tests. All tests use mocked LLM calls to ensure fast, reliable, and cost-effective testing.

## Quick Start

### Install Test Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
# Run all tests with coverage
pytest -v --cov=app --cov-report=html

# Run only unit tests
pytest tests/unit -v -m unit

# Run only integration tests
pytest tests/integration -v -m integration

# Run tests in parallel (faster)
pytest -n auto
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and mocks
├── factories.py             # Test data factories
├── unit/                    # Unit tests (80%+ coverage)
│   ├── test_config.py
│   ├── test_llm_client.py
│   ├── test_agent.py
│   ├── test_memory.py
│   └── test_document_processor.py
├── integration/             # Integration tests
│   └── test_end_to_end.py
├── performance/             # Performance tests
│   └── locustfile.py
├── test_api.py             # API endpoint tests
└── test_rag.py             # RAG component tests
```

## Test Categories

### Unit Tests (`tests/unit/`)

Fast, isolated tests with mocked dependencies.

```bash
# Run all unit tests
pytest tests/unit -v

# Run specific test file
pytest tests/unit/test_agent.py -v

# Run specific test
pytest tests/unit/test_agent.py::TestAIAgent::test_classify_query_policy -v
```

**Coverage:**
- Configuration management
- LLM client (mocked)
- AI agent logic
- Memory management
- Document processing
- RAG components

### Integration Tests (`tests/integration/`)

End-to-end workflow tests with mocked LLM calls.

```bash
# Run integration tests
pytest tests/integration -v -m integration
```

**Coverage:**
- Complete query workflows
- Session management
- Multi-turn conversations
- API endpoint integration

### Performance Tests (`tests/performance/`)

Load testing with Locust.

```bash
# Install locust
pip install locust

# Run load test (10 users, 30 seconds)
locust -f tests/performance/locustfile.py --headless -u 10 -r 2 -t 30s --host=http://localhost:8000

# Run with web UI
locust -f tests/performance/locustfile.py --host=http://localhost:8000
# Then open http://localhost:8089
```

## Coverage Reports

### Generate Coverage Report

```bash
# Run tests with coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# Open HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage Requirements

- **Minimum**: 80% overall coverage
- **Target**: 85%+ coverage
- **CI/CD**: Fails if coverage drops below 80%

## Test Fixtures

### Available Fixtures (from `conftest.py`)

- `test_settings` - Test configuration
- `mock_llm_client` - Mocked LLM client
- `mock_embedding` - Mock embedding vector
- `mock_vector_store` - Mocked vector store
- `memory` - Fresh conversation memory
- `agent_with_mocks` - Agent with mocked dependencies
- `sample_text` - Sample document text
- `sample_chunks` - Sample document chunks
- `api_client` - FastAPI test client

### Using Fixtures

```python
def test_example(mock_llm_client, memory):
    """Example test using fixtures."""
    session_id = memory.create_session()
    # Test code here
```

## Test Data Factories

Use factories to generate realistic test data:

```python
from tests.factories import QueryFactory, DocumentFactory, ResponseFactory

# Generate test queries
general_query = QueryFactory.general_query()
policy_query = QueryFactory.policy_query()

# Generate test documents
chunks = DocumentFactory.create_chunks(count=5)

# Generate test responses
response = ResponseFactory.agent_response()
```

## Mocking LLM Calls

All tests mock LLM calls to avoid:
- Real API costs
- Network dependencies
- Slow test execution
- Flaky tests

### Example Mock

```python
@pytest.fixture
def mock_llm_client():
    client = Mock()
    client.generate = AsyncMock(return_value="POLICY")
    client.generate_embedding = AsyncMock(return_value=[0.1] * 1536)
    return client
```

## Running Specific Tests

### By Marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only slow tests
pytest -m slow
```

### By Pattern

```bash
# Run tests matching pattern
pytest -k "test_agent"

# Run tests NOT matching pattern
pytest -k "not slow"
```

### By File

```bash
# Run specific file
pytest tests/unit/test_config.py

# Run multiple files
pytest tests/unit/test_config.py tests/unit/test_agent.py
```

## Debugging Tests

### Verbose Output

```bash
# Show print statements
pytest -v -s

# Show local variables on failure
pytest -v -l

# Stop on first failure
pytest -x
```

### Debug with pdb

```python
def test_example():
    import pdb; pdb.set_trace()
    # Test code
```

## CI/CD Integration

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests

### GitHub Actions Workflow

See `example/github-actions-tests.yml` for the complete workflow.

**Workflow includes:**
- Python 3.11 and 3.12 testing
- Linting (ruff, black)
- Type checking (mypy)
- Unit tests with coverage
- Integration tests
- Coverage reporting to Codecov
- Security scanning (safety, bandit)

## Best Practices

### Writing Tests

1. **Use descriptive names**
   ```python
   def test_agent_classifies_policy_query_correctly():
       # Clear what is being tested
   ```

2. **Follow AAA pattern**
   ```python
   def test_example():
       # Arrange
       agent = AIAgent()
       
       # Act
       result = agent.classify_query("test")
       
       # Assert
       assert result == QueryType.POLICY
   ```

3. **Mock external dependencies**
   ```python
   @patch('app.agents.agent.llm_client')
   def test_with_mock(mock_llm):
       # Test code
   ```

4. **Use fixtures for setup**
   ```python
   @pytest.fixture
   def setup_data():
       return {"key": "value"}
   ```

### Test Coverage

- Aim for 80%+ coverage
- Focus on critical paths
- Don't test third-party libraries
- Test edge cases and error handling

### Performance

- Keep unit tests fast (< 1s each)
- Use mocks to avoid I/O
- Run tests in parallel with `pytest-xdist`

## Troubleshooting

### Common Issues

**Issue**: Tests fail with "GOOGLE_GEMINI_API_KEY required"
```bash
# Solution: Set test API key
export GOOGLE_GEMINI_API_KEY=test_key_for_testing
```

**Issue**: Coverage below 80%
```bash
# Solution: Check coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

**Issue**: Slow tests
```bash
# Solution: Run in parallel
pytest -n auto
```

**Issue**: Import errors
```bash
# Solution: Install in development mode
pip install -e .
```

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Locust documentation](https://docs.locust.io/)
- [Testing best practices](https://docs.python-guide.org/writing/tests/)

## Contact

For questions about testing:
- Open an issue on GitHub
- Check existing test examples
- Review this guide
