# Production Deployment Guide

## Overview
This guide covers the complete production deployment process for the PolicyBot AI Agent to Azure.

## Prerequisites
- Azure CLI installed and authenticated (`az login`)
- Terraform installed
- Python 3.11+

## Deployment Steps

### 1. Deploy Infrastructure with Terraform

```bash
cd deployment/terraform
terraform init
terraform plan
terraform apply
```

This creates:
- Azure App Service (F1 tier)
- Azure OpenAI (GPT-4o + Embeddings)
- Azure AI Search
- Application Insights

### 2. Deploy Application Code

```bash
cd /home/ubuntu/Desktop/policybot-ai-agent

# Create deployment package
zip -r app.zip app/ data/documents/ scripts/setup_vectorstore.py requirements.txt -x "*__pycache__*" -x "*.pyc"

# Deploy to Azure
az webapp deployment source config-zip \
  --resource-group policybot-ai-agent-rg \
  --name $(cd deployment/terraform && terraform output -raw app_service_name) \
  --src app.zip
```

### 3. Populate Vector Store (ONE-TIME SETUP)

**Option A: Using the automated script (Recommended)**
```bash
./scripts/setup_vectorstore_prod.sh
```

**Option B: Manual setup**
```bash
# Get credentials from Terraform
cd deployment/terraform
terraform output

# Update your local .env with the Azure credentials
# Then run:
cd ../..
python scripts/setup_vectorstore.py
```

### 4. Verify Deployment

```bash
# Get the app URL
cd deployment/terraform
APP_URL=$(terraform output -raw app_service_url)

# Test health endpoint
curl $APP_URL/health

# Test the API
curl -X POST $APP_URL/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the leave policy?"}'
```

## Important Notes

### Vector Store Initialization
- **Must be run once** after initial deployment
- Processes all documents in `data/documents/`
- Creates embeddings and uploads to Azure AI Search
- Takes ~2-5 minutes depending on document count

### Updating Documents
To add or update policy documents:
1. Add/modify files in `data/documents/`
2. Re-run `./scripts/setup_vectorstore_prod.sh`

### Monitoring
View logs:
```bash
az webapp log tail \
  --resource-group policybot-ai-agent-rg \
  --name $(cd deployment/terraform && terraform output -raw app_service_name)
```

Access Application Insights:
```bash
cd deployment/terraform
terraform output deployment_instructions
```

## Troubleshooting

### App not responding
```bash
# Restart the app
az webapp restart \
  --resource-group policybot-ai-agent-rg \
  --name $(cd deployment/terraform && terraform output -raw app_service_name)
```

### Vector store errors
- Ensure Azure Search credentials are correct
- Check that documents exist in `data/documents/`
- Verify OpenAI deployment is active in Azure Portal

## Cost Optimization
Current setup uses:
- **F1 App Service**: Free tier
- **Azure OpenAI**: Pay-per-token (S0)
- **Azure AI Search**: Standard tier (~$250/month)

To reduce costs, consider:
- Using FAISS instead of Azure Search for dev/test
- Scaling down to Basic tier for Search if traffic is low
