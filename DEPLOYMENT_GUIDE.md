# Complete Azure Deployment Guide - PolicyBot AI Agent

## 📋 Overview
This guide provides step-by-step instructions to deploy the PolicyBot AI Agent (or any RAG-based AI agent) to Azure using Terraform and Azure AI Search.

## 🎯 What Gets Deployed
- **Azure App Service** (F1 Free tier) - Hosts the FastAPI application
- **Azure OpenAI** - GPT-4o for responses + text-embedding-ada-002 for vectors
- **Azure AI Search** - Vector database for document storage and semantic search
- **Application Insights** - Monitoring and logging
- **Log Analytics Workspace** - Centralized logging

## ✅ Prerequisites
- Azure CLI installed and authenticated (`az login`)
- Terraform installed (v1.0+)
- Python 3.11+
- Git (for version control)

---

## 🚀 Deployment Steps

### Step 1: Provision Azure Infrastructure with Terraform

```bash
cd deployment/terraform

# Initialize Terraform
terraform init

# Review the infrastructure plan
terraform plan

# Deploy infrastructure (takes ~5-10 minutes)
terraform apply
```

**What this creates:**
- Resource Group: `policybot-ai-agent-rg`
- App Service Plan (F1 tier)
- Linux Web App
- Azure OpenAI with GPT-4o and embeddings
- Azure AI Search (Standard tier)
- Application Insights + Log Analytics

### Step 2: Deploy Application Code

```bash
# Return to project root
cd /home/ubuntu/Desktop/policybot-ai-agent

# Create deployment package
zip -r app.zip app/ data/documents/ scripts/setup_vectorstore.py requirements.txt \
  -x "*__pycache__*" -x "*.pyc"

# Get the app service name from Terraform
APP_NAME=$(cd deployment/terraform && terraform output -raw app_service_name)

# Deploy to Azure App Service
az webapp deployment source config-zip \
  --resource-group policybot-ai-agent-rg \
  --name $APP_NAME \
  --src app.zip
```

**Deployment takes ~3-4 minutes**. The app will be available at:
`https://<app-name>.azurewebsites.net`

### Step 3: Initialize Vector Store (CRITICAL - ONE-TIME SETUP)

This step processes your documents and uploads them to Azure AI Search.

**Option A: Automated Script (Recommended)**
```bash
./scripts/setup_vectorstore_prod.sh
```

**Option B: Manual Setup**
```bash
# Get Azure credentials from Terraform
cd deployment/terraform
terraform output

# Update your .env file with:
# - AZURE_OPENAI_ENDPOINT
# - AZURE_OPENAI_API_KEY
# - AZURE_SEARCH_ENDPOINT
# - AZURE_SEARCH_API_KEY
# - AZURE_SEARCH_INDEX_NAME

# Run the setup script
cd ../..
source venv/bin/activate
python scripts/setup_vectorstore.py
```

**What this does:**
- Reads all documents from `data/documents/` (PDF, DOCX, TXT)
- Chunks documents into manageable pieces
- Generates embeddings using Azure OpenAI
- Creates Azure AI Search index schema
- Uploads 161 document chunks (for current dataset)
- **Takes ~10-15 minutes** due to Azure OpenAI rate limits

### Step 4: Verify Deployment

```bash
# Get the app URL
cd deployment/terraform
APP_URL=$(terraform output -raw app_service_url)

# Test health endpoint
curl $APP_URL/health

# Test the API with a policy question
curl -X POST $APP_URL/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the leave policy?"}'

# Test with a custom session ID
curl -X POST $APP_URL/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "How many vacation days do employees get?", "session_id": "test-session"}'

# Test follow-up question (context-aware)
curl -X POST $APP_URL/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "And how many after 4 years?", "session_id": "test-session"}'
```

---

## 📝 Adding or Updating Documents

To add new documents or update existing ones:

1. **Add files** to `data/documents/` directory
   - Supported formats: PDF, DOCX, TXT
   - No size limit (chunking handles large files)

2. **Re-run the vector store setup**:
   ```bash
   ./scripts/setup_vectorstore_prod.sh
   ```

3. **Done!** The agent will now answer questions from the new documents.

---

## 🔍 Monitoring & Troubleshooting

### View Application Logs
```bash
az webapp log tail \
  --resource-group policybot-ai-agent-rg \
  --name $(cd deployment/terraform && terraform output -raw app_service_name)
```

### Restart the Application
```bash
az webapp restart \
  --resource-group policybot-ai-agent-rg \
  --name $(cd deployment/terraform && terraform output -raw app_service_name)
```

### Check Azure AI Search Index
```bash
# Get search endpoint
cd deployment/terraform
terraform output -raw search_endpoint

# View in Azure Portal:
# portal.azure.com → Search Services → policybot-search-* → Indexes
```

### Common Issues

**Issue: "I don't have information about that"**
- **Cause**: Vector store not initialized or documents not indexed
- **Fix**: Run `./scripts/setup_vectorstore_prod.sh`

**Issue: App returns 500 errors**
- **Cause**: Missing environment variables or Azure credentials
- **Fix**: Check App Service Configuration in Azure Portal

**Issue: Rate limit errors (429)**
- **Cause**: Azure OpenAI S0 tier has rate limits
- **Expected**: The setup script handles retries automatically

---

## 💰 Cost Optimization

### Current Setup Costs (Monthly Estimate)
- **App Service (F1)**: **FREE**
- **Azure OpenAI (S0)**: ~$10-50 (pay-per-token, depends on usage)
- **Azure AI Search (Standard)**: ~$250/month
- **Application Insights**: ~$5-10/month
- **Total**: ~$265-310/month

### Cost Reduction Options

1. **Use FAISS for Development**:
   - Set `USE_FAISS=true` in local `.env`
   - Free, file-based vector storage
   - Not suitable for production (no persistence across deployments)

2. **Downgrade Azure AI Search**:
   - Change to Basic tier in `terraform/main.tf`
   - Reduces cost to ~$75/month
   - Lower performance and capacity

3. **Use Azure OpenAI Pay-As-You-Go**:
   - Only pay for actual usage
   - Current setup already uses this model

---

## 🔄 Redeployment & Updates

### Update Application Code Only
```bash
# Make code changes
# Then redeploy:
zip -r app.zip app/ data/documents/ scripts/setup_vectorstore.py requirements.txt \
  -x "*__pycache__*" -x "*.pyc"

az webapp deployment source config-zip \
  --resource-group policybot-ai-agent-rg \
  --name $(cd deployment/terraform && terraform output -raw app_service_name) \
  --src app.zip
```

### Update Infrastructure
```bash
cd deployment/terraform

# Make changes to .tf files
# Then apply:
terraform plan
terraform apply
```

### Destroy Everything (Clean Up)
```bash
cd deployment/terraform
terraform destroy
```

---

## 🌍 Adapting for Different Use Cases

This agent is **domain-agnostic** and can be used for:
- IT Support Knowledge Base
- Product Documentation
- Legal Document Q&A
- Medical Research Assistant
- Customer Support Bot
- Internal Wiki/Knowledge Management

**To adapt:**
1. Replace documents in `data/documents/` with your content
2. (Optional) Update prompts in `app/llm/prompts.py` to match your domain
3. Run vector store setup
4. Done!

---

## 📚 Additional Resources

- **Terraform Outputs**: `cd deployment/terraform && terraform output`
- **Azure Portal**: https://portal.azure.com
- **Application Insights**: Check Terraform outputs for direct link
- **API Documentation**: `https://<your-app>.azurewebsites.net/docs`

---

## ✅ Deployment Checklist

- [ ] Azure CLI authenticated (`az login`)
- [ ] Terraform installed
- [ ] Python 3.11+ with venv
- [ ] Run `terraform apply`
- [ ] Deploy app code with `az webapp deployment`
- [ ] Run `./scripts/setup_vectorstore_prod.sh`
- [ ] Test with `curl` commands
- [ ] Verify in Azure Portal
- [ ] Set up monitoring alerts (optional)

---

## 🎉 Success!

Your AI agent is now live and ready to answer questions from your documents!

**Test URL**: `https://<app-name>.azurewebsites.net/ask`
