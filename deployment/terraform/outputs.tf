# Resource Group Outputs
output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Location of the resource group"
  value       = azurerm_resource_group.main.location
}

# App Service Outputs
output "app_service_name" {
  description = "Name of the App Service"
  value       = azurerm_linux_web_app.main.name
}

output "app_service_url" {
  description = "URL of the deployed application"
  value       = "https://${azurerm_linux_web_app.main.default_hostname}"
}

output "app_service_principal_id" {
  description = "Principal ID of the App Service managed identity"
  value       = azurerm_linux_web_app.main.identity[0].principal_id
}

# Azure OpenAI Outputs
output "openai_endpoint" {
  description = "Endpoint for Azure OpenAI"
  value       = azurerm_cognitive_account.openai.endpoint
}

output "openai_api_key" {
  description = "Primary API key for Azure OpenAI"
  value       = azurerm_cognitive_account.openai.primary_access_key
  sensitive   = true
}

output "openai_deployment_name" {
  description = "Name of the GPT deployment"
  value       = var.openai_deployment_name
}

output "openai_embedding_deployment_name" {
  description = "Name of the embedding deployment"
  value       = var.openai_embedding_deployment_name
}

# Azure AI Search Outputs
output "search_service_name" {
  description = "Name of the Azure AI Search service"
  value       = azurerm_search_service.main.name
}

output "search_endpoint" {
  description = "Endpoint for Azure AI Search"
  value       = "https://${azurerm_search_service.main.name}.search.windows.net"
}

output "search_api_key" {
  description = "Primary API key for Azure AI Search"
  value       = azurerm_search_service.main.primary_key
  sensitive   = true
}

output "search_index_name" {
  description = "Name of the search index"
  value       = var.search_index_name
}

# Application Insights Outputs
output "application_insights_instrumentation_key" {
  description = "Instrumentation key for Application Insights"
  value       = azurerm_application_insights.main.instrumentation_key
  sensitive   = true
}

output "application_insights_connection_string" {
  description = "Connection string for Application Insights"
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}

# Deployment Instructions
output "deployment_instructions" {
  description = "Next steps for deployment"
  value       = <<-EOT
    ✅ Infrastructure provisioned successfully!
    
    Next steps:
    1. Deploy Python code via ZIP:
       cd /home/ubuntu/Desktop/policybot-ai-agent
       zip -r app.zip app/ data/ scripts/ requirements.txt
       az webapp deployment source config-zip \
         --resource-group ${azurerm_resource_group.main.name} \
         --name ${azurerm_linux_web_app.main.name} \
         --src app.zip
    
    2. Initialize vector store:
       python scripts/setup_vectorstore.py
    
    3. Access your application:
       https://${azurerm_linux_web_app.main.default_hostname}
    
    4. Monitor with Application Insights:
       https://portal.azure.com/#resource${azurerm_application_insights.main.id}
  EOT
}
