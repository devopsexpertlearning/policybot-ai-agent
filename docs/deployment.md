# Deployment Guide

## Overview

This guide covers deployment for both local development and Azure production environments.

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- **For local development (default)**: Google Gemini API key (free from https://makersuite.google.com/app/apikey)
- **For local development (optional)**: Azure OpenAI access (endpoint, API key, deployment names)

### Step 1: Environment Setup

```powershell
# Clone and navigate to project
cd policybot-ai-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configuration

```powershell
# Copy environment template
copy .env.example .env
```

Edit `.env` and configure your LLM provider:

**Option 1: Google Gemini (Default - Free)**
```bash
ENVIRONMENT=local
LLM_PROVIDER=gemini
GOOGLE_GEMINI_API_KEY=your_actual_key_here
```

**Option 2: Azure OpenAI (Alternative)**
```bash
ENVIRONMENT=local
LLM_PROVIDER=azure
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
```

### Step 3: Initialize Vector Store

```powershell
python scripts\setup_vectorstore.py
```

This processes all documents in `data/documents/` and creates FAISS embeddings.

### Step 4: Run Application

```powershell
# Option A: Direct Python
python -m app.main

# Option B: Uvicorn with reload
uvicorn app.main:app --reload

# Option C: Docker
cd deployment
docker-compose up --build
```

### Step 5: Test

- **Interactive**: http://localhost:8000/docs
- **CLI**: `python scripts\test_agent.py`
- **API**: 
  ```bash
  curl http://localhost:8000/health
  ```

---

## Docker Deployment

### Local Docker

```bash
cd deployment
docker-compose up --build
```

Services:
- AI Agent API: http://localhost:8000

### Docker Build Only

```bash
docker build -t policybot-ai-agent -f deployment/Dockerfile .
docker run -p 8000:8000 --env-file .env policybot-ai-agent
```

---

## Azure Production Deployment

### Prerequisites

1. **Azure CLI** installed and configured
2. **Azure subscription** with:
   - Azure OpenAI access
   - Azure AI Search service
3. **GitHub repository** (for CI/CD)
4. **Terraform** (for Infrastructure as Code deployment)

---

### Option A: Terraform (Recommended)

**Infrastructure as Code** - Production-ready, version-controlled infrastructure.

#### Why Terraform?
- ✅ **Reproducible**: Infrastructure defined as code
- ✅ **Version Controlled**: Track infrastructure changes in Git
- ✅ **Idempotent**: Safe to run multiple times
- ✅ **State Management**: Track resource state
- ✅ **Production Ready**: Industry standard for IaC

#### Quick Start

```bash
# Navigate to Terraform directory
cd deployment/terraform

# Copy and configure variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your specific values

# Initialize Terraform
terraform init

# Review planned changes
terraform plan

# Apply configuration
terraform apply
```

#### What Gets Provisioned

- **Resource Group**: Container for all resources
- **Azure Container Registry**: Docker image storage
- **App Service Plan + Web App**: Application hosting
- **Azure OpenAI**: GPT-4 and embedding models
- **Azure AI Search**: Vector search service
- **Application Insights**: Monitoring and logging
- **Log Analytics Workspace**: Centralized logging

#### Post-Deployment

After Terraform completes:

```bash
# 1. Build and push Docker image
ACR_LOGIN_SERVER=$(terraform output -raw acr_login_server)
az acr login --name $(echo $ACR_LOGIN_SERVER | cut -d'.' -f1)
docker build -t $ACR_LOGIN_SERVER/policybot-ai-agent:latest -f deployment/Dockerfile .
docker push $ACR_LOGIN_SERVER/policybot-ai-agent:latest

# 2. Initialize vector store
export ENVIRONMENT=production
export AZURE_OPENAI_ENDPOINT=$(terraform output -raw openai_endpoint)
export AZURE_OPENAI_API_KEY=$(terraform output -raw openai_api_key)
export AZURE_SEARCH_ENDPOINT=$(terraform output -raw search_endpoint)
export AZURE_SEARCH_API_KEY=$(terraform output -raw search_api_key)
python scripts/setup_vectorstore.py

# 3. Verify deployment
APP_URL=$(terraform output -raw app_service_url)
curl $APP_URL/health
```

**→ See [deployment/terraform/README.md](../deployment/terraform/README.md) for complete Terraform guide**

---

### Option B: Manual Deployment Script

#### Step 1: Set Environment Variables

```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your_key"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"
export AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-ada-002"
export AZURE_SEARCH_ENDPOINT="https://your-search.search.windows.net"
export AZURE_SEARCH_API_KEY="your_key"
```

#### Step 2: Run Deployment Script

```bash
cd deployment/azure
chmod +x deploy.sh
./deploy.sh
```

The script will:
1. Create resource group
2. Create Azure Container Registry
3. Build and push Docker image
4. Create App Service Plan
5. Deploy Web App
6. Configure Application Insights
7. Set environment variables

#### Step 3: Verify Deployment

```bash
# Test health endpoint
curl https://your-app.azurewebsites.net/health

# Test query
curl -X POST https://your-app.azurewebsites.net/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the leave policy?"}'
```

### Option C: GitHub Actions CI/CD

#### Step 1: Setup GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

- `AZURE_CREDENTIALS` - Service principal JSON
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT_NAME`
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`
- `AZURE_SEARCH_ENDPOINT`
- `AZURE_SEARCH_API_KEY`

#### Step 2: Get Azure Credentials

```bash
az ad sp create-for-rbac \
  --name "policybot-ai-agent-deploy" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/policybot-ai-agent-rg \
  --sdk-auth
```

Copy the JSON output to `AZURE_CREDENTIALS` secret.

#### Step 3: Trigger Deployment

```bash
# Push to main branch
git add .
git commit -m "Deploy to Azure"
git push origin main
```

GitHub Actions will automatically:
1. Build Docker image
2. Push to Azure Container Registry
3. Deploy to Azure App Service
4. Run health checks

---

## Azure Resources Setup

### 1. Create Azure OpenAI Resource

```bash
az cognitiveservices account create \
  --name your-openai-resource \
  --resource-group policybot-ai-agent-rg \
  --kind OpenAI \
  --sku S0 \
  --location eastus
```

### 2. Deploy Models

```bash
# Deploy GPT-4
az cognitiveservices account deployment create \
  --name your-openai-resource \
  --resource-group policybot-ai-agent-rg \
  --deployment-name gpt-4 \
  --model-name gpt-4 \
  --model-version "1106-Preview" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name "Standard"

# Deploy Embedding Model
az cognitiveservices account deployment create \
  --name your-openai-resource \
  --resource-group policybot-ai-agent-rg \
  --deployment-name text-embedding-ada-002 \
  --model-name text-embedding-ada-002 \
  --model-version "2" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name "Standard"
```

### 3. Create Azure AI Search

```bash
az search service create \
  --name your-search-service \
  --resource-group policybot-ai-agent-rg \
  --sku Standard \
  --location eastus
```

### 4. Initialize Search Index

After deployment, run the setup script to create the search index:

```python
# Update config to use Azure
# Set ENVIRONMENT=production in App Service configuration

# Run from Azure Cloud Shell or locally
python scripts/setup_vectorstore.py
```

---

## Monitoring

### Application Insights

Access metrics and logs:
1. Go to Azure Portal
2. Navigate to your App Service
3. Select "Application Insights"
4. View:
   - Request rates
   - Response times
   - Failures
   - Live metrics

### Logs

```bash
# Stream logs
az webapp log tail \
  --name policybot-ai-agent-app \
  --resource-group policybot-ai-agent-rg

# Download logs
az webapp log download \
  --name policybot-ai-agent-app \
  --resource-group policybot-ai-agent-rg \
  --log-file logs.zip
```

---

## Scaling

### Vertical Scaling

```bash
# Upgrade App Service Plan
az appservice plan update \
  --name policybot-ai-agent-plan \
  --resource-group policybot-ai-agent-rg \
  --sku P1V2
```

### Horizontal Scaling

```bash
# Add more instances
az appservice plan update \
  --name policybot-ai-agent-plan \
  --resource-group policybot-ai-agent-rg \
  --number-of-workers 3
```

---

## Troubleshooting

### Common Issues

**Issue**: "Configuration validation failed"
- **Solution**: Check all required environment variables are set

**Issue**: "Vector store empty"
- **Solution**: Run `python scripts/setup_vectorstore.py`

**Issue**: "Azure OpenAI quota exceeded"
- **Solution**: Check quota limits in Azure Portal, request increase if needed

**Issue**: "Container fails to initialize running"
- **Solution**: Check logs with `az webapp log tail`, verify environment variables

### Health Checks

```bash
# Local
curl http://localhost:8000/health

# Azure
curl https://your-app.azurewebsites.net/health
```

---

## Security Best Practices

1. **Never commit `.env` file** - Always in `.gitignore`
2. **Use Azure Key Vault** for production secrets
3. **Enable HTTPS only** in App Service
4. **Restrict CORS** to known origins
5. **Enable Application Insights** for monitoring
6. **Regular security updates** - Update dependencies

---

## Cost Optimization

### Local Development
- **Free**: Google Gemini API (generous free tier)
- **Free**: FAISS (local storage)

### Azure Production
- **AI Azure OpenAI**: Pay-per-token
- **Azure AI Search**: ~$250/month (Standard tier)
- **App Service**: ~$75/month (B1 Basic tier)
- **Application Insights**: First 5GB free, then $2.30/GB

**Total Estimated Cost**: ~$325-400/month for production

### Cost Reduction Tips
1. Use Free or Basic tier App Service for development
2. Enable autoscaling to scale down during low traffic
3. Use reserved capacity pricing for OpenAI if high volume
4. Consider Azure AI Search Free tier for development

---

## Backup and Recovery

### Backup Vector Store

```bash
# FAISS (local)
cp -r data/vector_stores/ backup/

# Azure AI Search
# Indexes are managed by Azure with automatic backup
```

### Backup Documents

```bash
# Documents are in source control
git push origin main
```

### Disaster Recovery

1. All code in GitHub
2. Vector stores can be regenerated from documents
3. Azure resources can be redeployed with scripts
4. Configuration in environment variables (documented)

**Recovery Time Objective (RTO)**: < 1 hour
**Recovery Point Objective (RPO)**: Latest git commit

---

For additional help, see:
- [Architecture Documentation](architecture.md)
- [API Documentation](api.md)
- [Main README](../README.md)
