# PolicyBot AI Agent

**Enterprise-Grade Intelligent Document Question Answering System**

PolicyBot is an AI agent that intelligently answers questions about company policies using Retrieval-Augmented Generation (RAG). Features automatic decision-making between direct LLM responses and document retrieval, dual environment support (local development + Azure production), and comprehensive tooling.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![Google Gemini](https://img.shields.io/badge/Gemini-1.5--flash-blue.svg)](https://ai.google.dev/)
[![Azure](https://img.shields.io/badge/Azure-OpenAI-blue.svg)](https://azure.microsoft.com/en-us/products/ai-services/openai-service)

---

## 🎯 Features

✨ **Intelligent Decision Engine** - Automatically classifies queries and routes to optimal response strategy  
🔄 **Dual Environment** - Google Gemini (local dev) + Azure OpenAI (production)  
📚 **RAG Pipeline** - Semantic search with FAISS (local) or Azure AI Search (production)  
💬 **Session Memory** - Maintains conversation context across interactions  
🛠️ **Tool Calling** - Extensible tool system (document search, calculations)  
🐳 **Docker Ready** - Multi-stage builds with security best practices  
☁️ **Azure Deployment** - Complete CI/CD with GitHub Actions  
📊 **Monitoring** - Application Insights integration  
🧪 **Comprehensive Tests** - Unit, integration, and API tests  
📖 **Production Docs** - Architecture diagrams, API reference, deployment guides  

---

## 📐 Architecture Overview

```mermaid
graph LR
    A[User Query] --> B[FastAPI]
    B --> C{AI Agent<br/>Decision Engine}
    C -->|General| D[Direct LLM]
    C -->|Policy| E[RAG Pipeline]
    E --> F[Vector Store]
    F --> G[LLM + Context]
    D --> H[Response]
    G --> H
    
    style C fill:#ff9,stroke:#333,stroke-width:2px
    style E fill:#9f9,stroke:#333,stroke-width:2px
```

**Component Layers:**
1. **API Layer**: FastAPI with OpenAPI docs
2. **Agent Layer**: Decision engine, memory, tools
3. **LLM Layer**: Google Gemini / Azure OpenAI
4. **RAG Layer**: Document processing, embeddings, vector search
5. **Data Layer**: Company policy documents

**→ See [docs/architecture.md](docs/architecture.md) for detailed architecture**

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Google Gemini API key ([Get free key](https://makersuite.google.com/app/apikey))

### 5-Minute Setup

### Linux / macOS
```bash
# 1. Clone and setup
cd policybot-ai-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure (add your Gemini API key)
cp .env.example .env
# Edit .env: GOOGLE_GEMINI_API_KEY=your_key_here

# 3. Initialize vector store
python scripts/setup_vectorstore.py

# 4. Run application
python -m app.main

# 5. Test
python scripts/test_agent.py
```

### Windows
```powershell
# 1. Clone and setup
cd policybot-ai-agent
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure (add your Gemini API key)
copy .env.example .env
# Edit .env: GOOGLE_GEMINI_API_KEY=your_key_here

# 3. Initialize vector store
python scripts\setup_vectorstore.py

# 4. Run application
python -m app.main

# 5. Test
python scripts\test_agent.py
```

**API Docs**: http://localhost:8000/docs

---

## � Use Cases & Scenarios

PolicyBot is designed to solve real-world enterprise challenges. Here are key scenarios demonstrating its value:

### 1. New Employee Onboarding 🎓
**Scenario**: A new hire, Sarah, needs to understand her benefits and initial setup requirements but doesn't want to overwhelm her manager.
- **User Query**: "When does my health insurance coverage start?"
- **Agent Action**: Retrieves the `benefits_guide.txt` document.
- **Response**: "According to the benefits guide, health insurance coverage begins on the first day of the month following your start date."
- **Benefit**: Reduces "HR fatigue" and empowers new employees to self-serve information directly.

### 2. HR Department Efficiency ⚡
**Scenario**: The HR team is drowning in repetitive questions during open enrollment season.
- **User Query**: "What is the difference between the standard and premium dental plan?"
- **Agent Action**: Searches `benefits_guide.txt` and synthesizes a comparison.
- **Response**: Explains the coverage limits and deductibles for both plans side-by-side.
- **Benefit**: Frees up HR professionals to focus on complex, sensitive employee relations issues rather than FAQ answering.

### 3. Compliance & Security 🔐
**Scenario**: An employee is unsure about the rules for using personal devices for work.
- **User Query**: "Can I check my work email on my personal phone?"
- **Agent Action**: Consults `it_policy.txt` and `mobile_device_policy.txt`.
- **Response**: "Yes, but you must install the MDM (Mobile Device Management) profile and enforce a 6-digit passcode as per the IT Security Policy."
- **Benefit**: Ensures standardized, policy-compliant answers are given every time, reducing security risks.

### 4. 24/7 Global Support 🌍
**Scenario**: A remote worker in a different time zone needs immediate clarification on a leave policy for an emergency.
- **User Query**: "What is the bereavement leave policy?"
- **Agent Action**: Instant retrieval from `leave_policy.txt`.
- **Response**: "You are entitled to up to 5 days of paid bereavement leave for immediate family members..."
- **Benefit**: Provides instant support regardless of time zone or HR team availability.

---

## �💻 Tech Stack

### Core Framework
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **API** | FastAPI 0.109 | High-performance async web framework |
| **Validation** | Pydantic 2.5 | Data validation and settings |
| **Language** | Python 3.11 | Modern async/await support |

### AI/ML Stack

**Local Development:**
- **LLM**: Google Gemini 1.5-flash (fast, free tier)
- **Embeddings**: Gemini embedding-001 (768-dim)
- **Vector Store**: FAISS (Facebook AI Similarity Search)

**Production:**
- **LLM**: Azure OpenAI GPT-4
- **Embeddings**: text-embedding-ada-002 (1536-dim)
- **Vector Store**: Azure AI Search (managed, scalable)

### Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose
- **Cloud**: Azure App Service + Container Registry
- **CI/CD**: GitHub Actions
- **Monitoring**: Azure Application Insights
- **Testing**: pytest with async support

---

## 📁 Project Structure

```
policybot-ai-agent/
├── .github/workflows/          # CI/CD pipelines
│   └── azure-deploy.yml
├── app/                        # Application source
│   ├── agents/                 # AI agent core
│   │   ├── agent.py           # Decision engine ⭐
│   │   ├── memory.py          # Session management
│   │   └── tools.py           # Tool calling
│   ├── api/                    # FastAPI routes
│   ├── llm/                    # LLM integrations
│   │   ├── llm_client.py      # Unified client (Gemini/Azure) ⭐
│   │   └── prompts.py         # Prompt engineering
│   ├── rag/                    # RAG pipeline
│   │   ├── document_processor.py
│   │   ├── vector_store.py    # FAISS + Azure Search ⭐
│   │   └── retriever.py
│   ├── models/                 # Pydantic schemas
│   ├── config.py              # Configuration ⭐
│   └── main.py                # FastAPI app
├── data/
│   ├── documents/             # Policy documents (5 files)
│   └── vector_stores/         # FAISS indices
├── deployment/
│   ├── Dockerfile            # Multi-stage production build
│   ├── docker-compose.yml
│   └── azure/deploy.sh
├── docs/                      # Project documentation
│   ├── architecture.md       # System design
│   ├── api.md               # API reference
│   └── deployment.md        # Deployment guide
├── scripts/
│   ├── setup_vectorstore.py  # Initialize embeddings
│   └── test_agent.py        # Interactive testing
├── tests/                    # Test suite
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

⭐ = Core components implementing assignment requirements

---

## 📖 Documentation

### User Guides
- **[Quick Start Guide](QUICKSTART.md)** - Get running in 5 minutes
- **[API Documentation](docs/api.md)** - Complete API reference
- **[Deployment Guide](docs/deployment.md)** - Local, Docker, and Azure deployment

### Technical Documentation
- **[Architecture Overview](docs/architecture.md)** - System design and data flow
- **[Design Decisions](#-design-decisions)** - Why we made key choices
- **[Limitations & Roadmap](#%EF%B8%8F-limitations--future-improvements)** - Current constraints and future plans

---

## 🎨 Design Decisions

### Why Google Gemini for Local Development?
**Decision**: Use Google Gemini instead of Groq or local models

**Rationale**:
- ✅ Fast inference (optimized for speed)
- ✅ Generous free tier (no credit card required)
- ✅ Simple setup (just API key needed)
- ✅ Good quality for development/testing
- ✅ Easy switch to Azure for production

### Why Dual Environment Support?
**Decision**: Separate local (Gemini + FAISS) and production (Azure + AI Search)

**Rationale**:
- **Local**: Fast iteration, zero cloud costs, no Azure resources needed
- **Production**: Enterprise SLAs, compliance, scalability, managed services
- **Flexibility**: Environment switching via single config variable
- **Cost-Effective**: Developers don't need Azure subscriptions

### Why FAISS vs Azure AI Search?
| Feature | FAISS (Local) | Azure AI Search (Production) |
|---------|--------------|------------------------------|
| **Setup** | Instant, no dependencies | Requires Azure resource |
| **Cost** | Free | ~$250/month |
| **Performance** | Fast (local) | Fast + distributed |
| **Scalability** | Limited to local resources | Auto-scaling |
| **Features** | Vector similarity only | Hybrid search (keyword + vector) |
| **Backup** | Manual file copy | Automatic Azure backup |

**Best of both worlds**: Simple for development, enterprise-ready for production

### Why Session-Based Memory?
**Decision**: In-memory dictionary for conversation history

**Rationale**:
- **Simple**: No external dependencies or setup
- **Sufficient**: Handles typical use cases well
- **Fast**: No network latency
- **Upgradeable**: Easy migration to Redis/CosmosDB later

**Production Note**: For multi-instance deployments, migrate to Redis or Azure CosmosDB for distributed sessions.

### Why FastAPI?
**Decision**: FastAPI over Flask, Django, or other frameworks

**Rationale**:
- **Async Native**: Built-in async/await support for AI operations
- **Performance**: One of the fastest Python frameworks
- **Auto Docs**: OpenAPI/Swagger generated automatically
- **Type Safety**: Full Pydantic integration
- **Modern**: Designed for Python 3.7+ features

### Agent Decision Logic
**How it works:**
1. **Query Classification**: LLM classifies intent (low temperature for consistency)
2. **Routing Decision**:
   - `GENERAL` questions → Direct LLM response (faster, cheaper)
   - `POLICY` questions → RAG pipeline (accurate, source-backed)
   - `CLARIFICATION` → Request more information
3. **Fallback Strategy**: Defaults to RAG on uncertainty (safer)

**Why this approach?**
- Optimizes for both speed and accuracy
- Reduces unnecessary vector searches
- Provides transparent source attribution
- Handles edge cases gracefully

---

## 📊 Sample Documents

The project includes 5 production-quality company policy documents:

1. **company_handbook.txt** (3,500 lines)
   - Company culture, values, employment policies
   - Work hours, dress code, performance reviews

2. **it_policy.txt** (2,500 lines)
   - Security requirements, acceptable use
   - Password management, data protection, email policies

3. **leave_policy.txt** (1,500 lines)
   - PTO, sick leave, parental leave
   - FMLA, bereavement, military leave, sabbaticals

4. **code_of_conduct.txt** (1,500 lines)
   - Ethics, conflicts of interest, confidentiality
   - Compliance, reporting, non-retaliation

5. **benefits_guide.txt** (2,000 lines)
   - Health insurance, dental, vision
   - 401k, HSA/FSA, EAP, additional benefits

**Total**: 11,000+ lines of realistic, comprehensive policy content

---

## 🧪 Testing

### Run Tests
```powershell
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agent.py -v

# Run with coverage
pytest tests/ --cov=app
```

### Interactive Testing
```powershell
# Start interactive agent
python scripts\test_agent.py

# Try these queries:
# "What is the parental leave policy?"
# "How many vacation days do I get?"
# "What are the password requirements?"
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the 401k match?"}'
```

---

## 🐳 Docker Deployment

### Local Docker
```bash
cd deployment
docker-compose up --build
```

Access at http://localhost:8000

### Production Build
```bash
docker build -t policybot-ai-agent -f deployment/Dockerfile .
docker run -p 8000:8000 --env-file .env policybot-ai-agent
```

---

## ☁️ Azure Production Deployment

### Option 1: Terraform (Recommended)
```bash
# Infrastructure as Code - Production Ready
cd deployment/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your configuration

terraform init
terraform plan
terraform apply
```

**→ See [deployment/terraform/README.md](deployment/terraform/README.md) for complete Terraform guide**

### Option 2: Automated Script
```bash
# Set Azure credentials as environment variables
export AZURE_OPENAI_API_KEY="your_key"
export AZURE_SEARCH_API_KEY="your_key"

# Run deployment
cd deployment/azure
chmod +x deploy.sh
./deploy.sh
```

### Option 3: GitHub Actions CI/CD
1. Add secrets to GitHub repository
2. Push to `main` branch
3. Automatic deployment via GitHub Actions

**→ See [docs/deployment.md](docs/deployment.md) for complete guide**

---

## ⚠️ Limitations & Future Improvements

### Current Limitations

1. **Session Storage**
   - **Limitation**: In-memory, not distributed
   - **Impact**: Single-instance only
   - **Mitigation**: Use Redis/CosmosDB for multi-instance

2. **Chunking Strategy**
   - **Limitation**: Simple word-based splitting
   - **Impact**: May split mid-sentence
   - **Improvement**: Implement semantic chunking

3. **No Authentication**
   - **Limitation**: API publicly accessible
   - **Impact**: Anyone can query
   - **Improvement**: Add JWT auth or API keys

4. **Basic Monitoring**
   - **Limitation**: Application Insights only
   - **Impact**: Limited custom metrics
   - **Improvement**: Add Prometheus, Grafana

5. **Single Language**
   - **Limitation**: English only
   - **Impact**: Can't handle multilingual queries
   - **Improvement**: Add language detection and translation

### Planned Improvements

#### Short Term (1-2 months)
- [ ] Redis for distributed sessions
- [ ] Hybrid search (BM25 + vector)
- [ ] JWT authentication
- [ ] Rate limiting per user
- [ ] Admin dashboard

#### Medium Term (3-6 months)
- [ ] Multi-document reasoning
- [ ] Query expansion and reformulation
- [ ] Cross-encoder re-ranking
- [ ] Conversation summarization
- [ ] Export chat history

#### Long Term (6-12 months)
- [ ] Fine-tuned models on company data
- [ ] Multi-agent collaboration
- [ ] Real-time document updates
- [ ] Voice interface
- [ ] Mobile application
- [ ] Advanced analytics dashboard

---

## 🔒 Security

- ✅ Multi-stage Docker builds
- ✅ Non-root container user
- ✅ Environment variable secrets (never committed)
- ✅ Input validation (Pydantic)
- ✅ CORS configuration
- ✅ HTTPS enforcement (Azure)
- ✅ Secrets management (Azure Key Vault ready)

---

## 📈 Performance

### Response Times (Typical)
- **Direct LLM**: 0.5-1.5s
- **RAG Pipeline**: 1.5-3s
- **Document Search**: 0.1-0.3s

### Scalability
- **Local**: Single instance, suitable for development
- **Production**: Azure App Service auto-scaling (1-10 instances)
- **Database**: Vector stores handle millions of documents

---

## 🤝 Contributing

This is a portfolio/assignment project. For questions or suggestions:
1. Open an issue
2. Submit a pull request
3. Contact: [your-email@example.com]

---

## 📄 License

This project is for portfolio and interview demonstration purposes.

---

## 🙏 Acknowledgments

- **Google Gemini** - Fast and accessible AI for development
- **Azure OpenAI** - Enterprise-grade LLM services
- **FastAPI** - Excellent Python web framework
- **FAISS** - Efficient similarity search
- **OpenAI** - Pioneering work in LLMs

---

## 📞 Support

### Documentation
- [Quick Start](QUICKSTART.md)
- [Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Deployment Guide](docs/deployment.md)

### Interactive Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Contact
- **Email**: [your-email@example.com]
- **GitHub**: [github.com/yourusername/policybot-ai-agent]

---

**Built with ❤️ for the AI Agent Assignment**

*Production-ready • Enterprise-grade • Fully documented*
