# Terraform Backend Configuration
# 
# This file configures remote state storage in Azure Storage Account.
# Uncomment and configure for production use.

# terraform {
#   backend "azurerm" {
#     resource_group_name  = "terraform-state-rg"
#     storage_account_name = "tfstatepolicybot"
#     container_name       = "tfstate"
#     key                  = "policybot-ai-agent.tfstate"
#   }
# }

# To create the backend storage:
# 1. Create resource group:
#    az group create --name terraform-state-rg --location eastus
#
# 2. Create storage account:
#    az storage account create \
#      --name tfstatepolicybot \
#      --resource-group terraform-state-rg \
#      --location eastus \
#      --sku Standard_LRS \
#      --encryption-services blob
#
# 3. Create blob container:
#    az storage container create \
#      --name tfstate \
#      --account-name tfstatepolicybot
#
# 4. Initialize Terraform with backend:
#    terraform init -backend-config="backend.tf"
