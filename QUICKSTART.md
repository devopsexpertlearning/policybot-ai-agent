# Quick Setup Guide

## Prerequisites
- Python 3.11+
- **Option 1 (Default)**: Google Gemini API key (free at https://makersuite.google.com/app/apikey)
- **Option 2 (Alternative)**: Azure OpenAI access (endpoint, API key, deployment names)

## 5-Minute Local Setup

### Step 1: Setup Environment
#### Linux / macOS
```bash
# Navigate to project
cd policybot-ai-agent

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# For testing/dev:
pip install -r requirements-dev.txt
```

#### Windows
```powershell
# Navigate to project
cd policybot-ai-agent

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
# For testing/dev:
pip install -r requirements-dev.txt
```

### Step 2: Configure API Key

**Choose your LLM provider for local development:**

#### Option 1: Google Gemini (Default - Recommended for Free Development)

##### Linux / macOS
```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your Google Gemini API key:
# ENVIRONMENT=local
# LLM_PROVIDER=gemini
# GOOGLE_GEMINI_API_KEY=your_actual_gemini_api_key_here
```

##### Windows
```powershell
# Copy environment template
copy .env.example .env

# Edit .env file and add your Google Gemini API key:
# ENVIRONMENT=local
# LLM_PROVIDER=gemini
# GOOGLE_GEMINI_API_KEY=your_actual_gemini_api_key_here
```

**Get Free Key**: https://makersuite.google.com/app/apikey

#### Option 2: Azure OpenAI (Alternative - Production-like Local Setup)

If you prefer to use Azure OpenAI for local development:

```bash
# Edit .env file with Azure credentials:
# ENVIRONMENT=local
# LLM_PROVIDER=azure
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# AZURE_OPENAI_API_KEY=your_azure_api_key
# AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
# AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
```

> **Note**: The vector store setup script will automatically create provider-specific indices (`faiss_index_gemini` or `faiss_index_azure`) to avoid embedding dimension conflicts.

### Step 3: Initialize Vector Store
#### Linux / macOS
```bash
# Process documents and create embeddings
python scripts/setup_vectorstore.py
```

#### Windows
```powershell
# Process documents and create embeddings
python scripts\setup_vectorstore.py
```

Expected output:
```
🚀 Starting vector store setup...
Environment: local
Vector store type: FAISS
✅ Processed 342 chunks from documents
✅ Generated 342 embeddings
✅ FAISS index saved
```

### Step 4: Run the Application
#### Linux / macOS
```bash
# Start FastAPI server
python -m app.main
```

#### Windows
```powershell
# Start FastAPI server
python -m app.main
```

Server runs at http://localhost:8000

### Step 5: Test the Agent

**Option A: Interactive Testing** (Recommended)
```powershell
# Open a new terminal
venv\Scripts\activate
python scripts\test_agent.py
```

**Option B: API Testing**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"What is the leave policy?\"}"
```

**Option C: Browser**
Visit http://localhost:8000/docs for interactive API documentation

---

## Sample Questions to Ask

**Policy Questions** (uses RAG):
- "How many vacation days do I get?"
- "What is the parental leave policy?"
- "What are the password requirements?"
- "What benefits does the company offer?"
- "How do I request time off?"

**General Questions** (direct LLM):
- "What is artificial intelligence?"
- "Explain machine learning in simple terms"
- "What is the capital of France?"

---

## Docker Alternative

If you prefer Docker:

```bash
cd deployment
docker-compose up --build
```

Then visit http://localhost:8000

---

## Troubleshooting

**Issue**: "GOOGLE_GEMINI_API_KEY is required"
- **Solution**: Make sure you've added your API key to the `.env` file

**Issue**: "No module named 'app'"
- **Solution**: Make sure you're in the project root directory and virtual environment is activated

**Issue**: "Index is empty" when querying
- **Solution**: Run `python scripts\setup_vectorstore.py` first

**Issue**: Import errors
- **Solution**: Ensure virtual environment is activated and dependencies installed:
  ```powershell
  venv\Scripts\activate
  pip install -r requirements.txt
  pip install -r requirements-dev.txt
  ```

---

## Next Steps

- ✅ **Local Setup Complete!**
- 📖 Check [README.md](README.md) for full documentation
- 🏗️ See [docs/architecture.md](docs/architecture.md) for system design
- 🚀 View [docs/deployment.md](docs/deployment.md) for Azure deployment

---

## API Endpoints

Once running:
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Stats**: http://localhost:8000/stats

---

## Quick Reference

```powershell
# Complete setup in one go:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# (Edit .env with your GOOGLE_GEMINI_API_KEY)
python scripts\setup_vectorstore.py
python -m app.main
```

That's it! You now have a production-ready AI agent running locally.

**Need help?** See [README.md](README.md) or [docs/](docs/) folder.
