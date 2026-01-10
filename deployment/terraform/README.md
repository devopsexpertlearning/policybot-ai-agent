# Terraform Infrastructure for PolicyBot AI Agent

This directory contains production-ready Terraform configuration for deploying the PolicyBot AI Agent to Azure.

## 📋 Prerequisites

- [Terraform](https://www.terraform.io/downloads) >= 1.5.0
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed and configured
- Azure subscription with appropriate permissions
- Access to Azure OpenAI (requires application approval)

## 🏗️ Infrastructure Components

The Terraform configuration provisions the following Azure resources:

- **Resource Group**: Container for all resources
- **Azure Container Registry (ACR)**: Docker image storage
- **App Service Plan**: Compute resources for the web app
- **Linux Web App**: Containerized application hosting
- **Azure OpenAI**: GPT-4 and embedding models
- **Azure AI Search**: Vector search for RAG
- **Application Insights**: Monitoring and logging
- **Log Analytics Workspace**: Centralized logging

## 🚀 Quick Start

### 1. Login to Azure

```bash
az login
az account set --subscription "your-subscription-id"
```

### 2. Configure Variables

Copy the example tfvars file and customize:

```bash
cd deployment/terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your specific values:
- Update globally unique names (ACR, App Service, OpenAI, Search)
- Configure allowed CORS origins
- Set appropriate SKUs for your workload
- Add IP whitelist for OpenAI if needed

### 3. Initialize Terraform

```bash
terraform init
```

### 4. Review the Plan

```bash
terraform plan -out=tfplan
```

Review the output to ensure all resources are configured correctly.

### 5. Apply Configuration

```bash
terraform apply tfplan
```

This will provision all Azure resources. The process takes approximately 10-15 minutes.

### 6. Retrieve Outputs

```bash
terraform output
```

Save the sensitive outputs (API keys, passwords) securely:

```bash
# Save to environment variables or secure vault
terraform output -raw openai_api_key
terraform output -raw search_api_key
terraform output -raw acr_admin_password
```

## 📦 Post-Deployment Steps

After Terraform completes, follow these steps:

### 1. Build and Push Docker Image

```bash
# Get ACR login server
ACR_LOGIN_SERVER=$(terraform output -raw acr_login_server)

# Login to ACR
az acr login --name $(terraform output -raw acr_login_server | cut -d'.' -f1)

# Build and push image
cd ../..  # Return to project root
docker build -t $ACR_LOGIN_SERVER/policybot-ai-agent:latest -f deployment/Dockerfile .
docker push $ACR_LOGIN_SERVER/policybot-ai-agent:latest
```

### 2. Initialize Vector Store

```bash
# Set environment variables
export ENVIRONMENT=production
export AZURE_OPENAI_ENDPOINT=$(terraform output -raw openai_endpoint)
export AZURE_OPENAI_API_KEY=$(terraform output -raw openai_api_key)
export AZURE_SEARCH_ENDPOINT=$(terraform output -raw search_endpoint)
export AZURE_SEARCH_API_KEY=$(terraform output -raw search_api_key)

# Run setup script
python scripts/setup_vectorstore.py
```

### 3. Verify Deployment

```bash
# Get app URL
APP_URL=$(terraform output -raw app_service_url)

# Health check
curl $APP_URL/health

# Test query
curl -X POST $APP_URL/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the leave policy?"}'
```

## 🔒 Security Best Practices

### 1. State Management

Configure remote state storage in Azure:

```bash
# Create backend storage (one-time setup)
az group create --name terraform-state-rg --location eastus
az storage account create \
  --name tfstatepolicybot \
  --resource-group terraform-state-rg \
  --location eastus \
  --sku Standard_LRS

az storage container create \
  --name tfstate \
  --account-name tfstatepolicybot

# Enable state locking
az storage account update \
  --name tfstatepolicybot \
  --resource-group terraform-state-rg \
  --enable-versioning true
```

Uncomment the backend configuration in `backend.tf` and re-initialize:

```bash
terraform init -migrate-state
```

### 2. Secrets Management

**Never commit `terraform.tfvars` to version control!**

Add to `.gitignore`:
```
*.tfvars
!terraform.tfvars.example
.terraform/
*.tfstate
*.tfstate.backup
```

### 3. Network Security

For production, restrict access:

```hcl
# In terraform.tfvars
openai_network_acls_default_action = "Deny"
openai_allowed_ips = ["your.office.ip", "your.vpn.ip"]
search_public_access_enabled = false
```

### 4. HTTPS and CORS

Update CORS origins in `terraform.tfvars`:

```hcl
cors_allowed_origins = [
  "https://yourdomain.com",
  "https://www.yourdomain.com"
]
```

## 💰 Cost Estimation

Approximate monthly costs (East US region):

| Resource | SKU | Monthly Cost |
|----------|-----|--------------|
| App Service Plan | P1v2 | ~$75 |
| Container Registry | Standard | ~$20 |
| Azure OpenAI | S0 (pay-per-use) | ~$50-200* |
| Azure AI Search | Standard | ~$250 |
| Application Insights | Pay-as-you-go | ~$10-30 |
| **Total** | | **~$405-575/month** |

*Depends on usage volume

### Cost Optimization

For development/staging:
```hcl
app_service_plan_sku = "B1"      # ~$13/month
search_service_sku = "basic"     # ~$75/month
```

## 🔄 Updating Infrastructure

To update resources:

```bash
# Modify terraform.tfvars or *.tf files
terraform plan
terraform apply
```

## 🗑️ Destroying Infrastructure

To remove all resources:

```bash
terraform destroy
```

**Warning**: This will delete all data. Ensure you have backups!

## 📊 Monitoring

Access Application Insights:
```bash
terraform output application_insights_connection_string
```

View logs:
```bash
az webapp log tail \
  --name $(terraform output -raw app_service_name) \
  --resource-group $(terraform output -raw resource_group_name)
```

## 🐛 Troubleshooting

### Issue: OpenAI deployment fails

**Cause**: Azure OpenAI requires application approval and is region-limited.

**Solution**:
1. Apply for Azure OpenAI access: https://aka.ms/oai/access
2. Use an approved region: `eastus`, `westeurope`, `francecentral`

### Issue: Name already exists

**Cause**: ACR, App Service, and Search names must be globally unique.

**Solution**: Update names in `terraform.tfvars`:
```hcl
acr_name = "policybotregistry-yourcompany"
app_service_name = "policybot-ai-agent-yourcompany"
```

### Issue: Quota exceeded

**Cause**: Azure subscription limits.

**Solution**: Request quota increase in Azure Portal or use different region.

## 📚 Additional Resources

- [Terraform Azure Provider Docs](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure AI Search Documentation](https://learn.microsoft.com/en-us/azure/search/)
- [Project Main README](../../README.md)

## 🤝 Support

For issues or questions:
1. Check [Troubleshooting](#-troubleshooting) section
2. Review [Azure Documentation](https://docs.microsoft.com/en-us/azure/)
3. Open an issue in the project repository
