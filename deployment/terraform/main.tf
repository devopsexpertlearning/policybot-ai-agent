terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.80"
    }
  }
  
  # Using local backend for initial deployment
  # Remote backend configuration is in backend.tf (currently commented out)
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
    
    cognitive_account {
      purge_soft_delete_on_destroy = true
    }
  }
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  
  tags = var.tags
}

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}



# App Service Plan
resource "azurerm_service_plan" "main" {
  name                = var.app_service_plan_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = var.app_service_plan_sku
  
  tags = var.tags
}

# App Service (Web App for Containers)
resource "azurerm_linux_web_app" "main" {
  name                = "${var.app_service_name}-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.main.id
  
  https_only = true
  
  site_config {
    always_on = var.app_service_always_on
    
    application_stack {
      python_version = "3.11"
    }
    
    health_check_path = "/health"
    
    cors {
      allowed_origins = var.cors_allowed_origins
    }
  }
  
  app_settings = {
    ENVIRONMENT                           = "production"
    LOG_LEVEL                            = var.log_level
    AZURE_OPENAI_ENDPOINT                = azurerm_cognitive_account.openai.endpoint
    AZURE_OPENAI_API_KEY                 = azurerm_cognitive_account.openai.primary_access_key
    AZURE_OPENAI_DEPLOYMENT_NAME         = var.openai_deployment_name
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT    = var.openai_embedding_deployment_name
    AZURE_SEARCH_ENDPOINT                = "https://${azurerm_search_service.main.name}.search.windows.net"
    AZURE_SEARCH_API_KEY                 = azurerm_search_service.main.primary_key
    AZURE_SEARCH_INDEX_NAME              = var.search_index_name
    APPLICATIONINSIGHTS_CONNECTION_STRING = azurerm_application_insights.main.connection_string
    SCM_DO_BUILD_DURING_DEPLOYMENT       = "true"
    ENABLE_ORYX_BUILD                    = "true"
  }
  
  identity {
    type = "SystemAssigned"
  }
  
  logs {
    application_logs {
      file_system_level = "Information"
    }
    
    http_logs {
      file_system {
        retention_in_days = 7
        retention_in_mb   = 35
      }
    }
  }
  
  tags = var.tags
}

# Azure OpenAI Service
resource "azurerm_cognitive_account" "openai" {
  name                = "${var.openai_account_name}-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.openai_location
  kind                = "OpenAI"
  sku_name            = var.openai_sku
  
  custom_subdomain_name = "${var.openai_account_name}-${random_string.suffix.result}"
  
  network_acls {
    default_action = var.openai_network_acls_default_action
    ip_rules       = var.openai_allowed_ips
  }
  
  tags = var.tags
}

# OpenAI GPT-4 Deployment
resource "azurerm_cognitive_deployment" "gpt4" {
  name                 = var.openai_deployment_name
  cognitive_account_id = azurerm_cognitive_account.openai.id
  
  model {
    format  = "OpenAI"
    name    = var.openai_model_name
    version = var.openai_model_version
  }
  
  scale {
    type     = "Standard"
    capacity = var.openai_deployment_capacity
  }
}

# OpenAI Embedding Deployment
resource "azurerm_cognitive_deployment" "embedding" {
  name                 = var.openai_embedding_deployment_name
  cognitive_account_id = azurerm_cognitive_account.openai.id
  
  model {
    format  = "OpenAI"
    name    = var.openai_embedding_model_name
    version = var.openai_embedding_model_version
  }
  
  scale {
    type     = "Standard"
    capacity = var.openai_embedding_capacity
  }
}

# Azure AI Search
resource "azurerm_search_service" "main" {
  name                = "${var.search_service_name}-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = var.search_service_sku
  
  replica_count   = var.search_replica_count
  partition_count = var.search_partition_count
  
  public_network_access_enabled = var.search_public_access_enabled
  
  tags = var.tags
}

# Application Insights
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${var.app_service_name}-${random_string.suffix.result}-logs"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "PerGB2018"
  retention_in_days   = var.log_retention_days
  
  tags = var.tags
}

resource "azurerm_application_insights" "main" {
  name                = "${var.app_service_name}-${random_string.suffix.result}-insights"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
  
  tags = var.tags
}


