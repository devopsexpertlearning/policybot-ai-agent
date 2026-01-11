# General Variables
variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "policybot-ai-agent-rg"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "PolicyBot AI Agent"
    Environment = "Production"
    ManagedBy   = "Terraform"
  }
}



# App Service Variables
variable "app_service_plan_name" {
  description = "Name of the App Service Plan"
  type        = string
  default     = "policybot-ai-agent-plan"
}

variable "app_service_plan_sku" {
  description = "SKU for App Service Plan"
  type        = string
  default     = "F1"
  
  validation {
    condition     = can(regex("^(F1|B[1-3]|S[1-3]|P[1-3]v[2-3]|I[1-3]v2)$", var.app_service_plan_sku))
    error_message = "Invalid App Service Plan SKU. Must be F1, B1-B3, S1-S3, P1v2-P3v3, or I1v2-I3v2."
  }
}

variable "app_service_name" {
  description = "Name of the App Service (must be globally unique)"
  type        = string
  default     = "policybot-ai-agent-app"
}

variable "app_service_always_on" {
  description = "Keep the app always on"
  type        = bool
  default     = false
}

variable "cors_allowed_origins" {
  description = "List of allowed CORS origins"
  type        = list(string)
  default     = ["*"]
}

variable "log_level" {
  description = "Application log level"
  type        = string
  default     = "INFO"
  
  validation {
    condition     = contains(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], var.log_level)
    error_message = "Log level must be DEBUG, INFO, WARNING, ERROR, or CRITICAL."
  }
}

# Azure OpenAI Variables
variable "openai_account_name" {
  description = "Name of the Azure OpenAI account (must be globally unique)"
  type        = string
  default     = "policybot-openai"
}

variable "openai_location" {
  description = "Azure region for OpenAI (limited availability)"
  type        = string
  default     = "eastus"
  
  validation {
    condition     = contains(["eastus", "eastus2", "southcentralus", "westeurope", "francecentral", "uksouth", "swedencentral"], var.openai_location)
    error_message = "OpenAI is only available in specific regions."
  }
}


variable "openai_sku" {
  description = "SKU for Azure OpenAI"
  type        = string
  default     = "S0"
}

variable "openai_network_acls_default_action" {
  description = "Default network action for OpenAI"
  type        = string
  default     = "Allow"
  
  validation {
    condition     = contains(["Allow", "Deny"], var.openai_network_acls_default_action)
    error_message = "Network ACLs default action must be Allow or Deny."
  }
}

variable "openai_allowed_ips" {
  description = "List of allowed IP addresses for OpenAI access"
  type        = list(string)
  default     = []
}

variable "openai_deployment_name" {
  description = "Name of the GPT-4 deployment"
  type        = string
  default     = "gpt-4o"
}

variable "openai_model_name" {
  description = "OpenAI model name for chat"
  type        = string
  default     = "gpt-4o"
}

variable "openai_model_version" {
  description = "OpenAI model version for chat"
  type        = string
  default     = "2024-05-13"
}

variable "openai_deployment_capacity" {
  description = "Capacity for GPT-4 deployment (in thousands of tokens per minute)"
  type        = number
  default     = 10
  
  validation {
    condition     = var.openai_deployment_capacity >= 1 && var.openai_deployment_capacity <= 1000
    error_message = "Deployment capacity must be between 1 and 1000."
  }
}

variable "openai_embedding_deployment_name" {
  description = "Name of the embedding deployment"
  type        = string
  default     = "text-embedding-ada-002"
}

variable "openai_embedding_model_name" {
  description = "OpenAI embedding model name"
  type        = string
  default     = "text-embedding-ada-002"
}

variable "openai_embedding_model_version" {
  description = "OpenAI embedding model version"
  type        = string
  default     = "2"
}

variable "openai_embedding_capacity" {
  description = "Capacity for embedding deployment"
  type        = number
  default     = 10
  
  validation {
    condition     = var.openai_embedding_capacity >= 1 && var.openai_embedding_capacity <= 1000
    error_message = "Embedding capacity must be between 1 and 1000."
  }
}

# Azure AI Search Variables
variable "search_service_name" {
  description = "Name of the Azure AI Search service (must be globally unique)"
  type        = string
  default     = "policybot-search"
}

variable "search_service_sku" {
  description = "SKU for Azure AI Search"
  type        = string
  default     = "standard"
  
  validation {
    condition     = contains(["free", "basic", "standard", "standard2", "standard3", "storage_optimized_l1", "storage_optimized_l2"], var.search_service_sku)
    error_message = "Invalid Search Service SKU."
  }
}

variable "search_replica_count" {
  description = "Number of replicas for search service"
  type        = number
  default     = 1
  
  validation {
    condition     = var.search_replica_count >= 1 && var.search_replica_count <= 12
    error_message = "Replica count must be between 1 and 12."
  }
}

variable "search_partition_count" {
  description = "Number of partitions for search service"
  type        = number
  default     = 1
  
  validation {
    condition     = contains([1, 2, 3, 4, 6, 12], var.search_partition_count)
    error_message = "Partition count must be 1, 2, 3, 4, 6, or 12."
  }
}

variable "search_public_access_enabled" {
  description = "Enable public network access to search service"
  type        = bool
  default     = true
}

variable "search_index_name" {
  description = "Name of the search index"
  type        = string
  default     = "company-policies"
}

# Monitoring Variables
variable "log_retention_days" {
  description = "Number of days to retain logs"
  type        = number
  default     = 30
  
  validation {
    condition     = var.log_retention_days >= 30 && var.log_retention_days <= 730
    error_message = "Log retention must be between 30 and 730 days."
  }
}
