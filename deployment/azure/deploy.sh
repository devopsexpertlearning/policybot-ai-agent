#!/bin/bash
# Azure deployment script

set -e

# Configuration
RESOURCE_GROUP="policybot-ai-agent-rg"
LOCATION="eastus"
APP_NAME="policybot-ai-agent-app"
APP_SERVICE_PLAN="policybot-ai-agent-plan"
ACR_NAME="policybotregistry"
IMAGE_NAME="policybot-ai-agent"
IMAGE_TAG="latest"

echo "🚀 Starting Azure deployment..."

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo "❌  Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

# Create resource group
echo "📦 Creating resource group..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION

# Create Azure Container Registry
echo "🐳 Creating Azure Container Registry..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)

# Build and push Docker image
echo "🔨 Building Docker image..."
cd ..
docker build -t $IMAGE_NAME:$IMAGE_TAG -f deployment/Dockerfile .

echo "📤 Pushing image to ACR..."
az acr login --name $ACR_NAME
docker tag $IMAGE_NAME:$IMAGE_TAG $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG
docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG

# Create App Service Plan
echo "📋 Creating App Service Plan..."
az appservice plan create \
    --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --is-linux \
    --sku B1

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)

# Create Web App
echo "🌐 Creating Web App..."
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --name $APP_NAME \
    --deployment-container-image-name $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG

# Configure container registry credentials
az webapp config container set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --docker-custom-image-name $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG \
    --docker-registry-server-url https://$ACR_LOGIN_SERVER \
    --docker-registry-server-user $ACR_USERNAME \
    --docker-registry-server-password $ACR_PASSWORD

# Configure application settings (environment variables)
echo "⚙️  Configuring application settings..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
        ENVIRONMENT=production \
        LOG_LEVEL=INFO \
        AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT \
        AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY \
        AZURE_OPENAI_DEPLOYMENT_NAME=$AZURE_OPENAI_DEPLOYMENT_NAME \
        AZURE_OPENAI_EMBEDDING_DEPLOYMENT=$AZURE_OPENAI_EMBEDDING_DEPLOYMENT \
        AZURE_SEARCH_ENDPOINT=$AZURE_SEARCH_ENDPOINT \
        AZURE_SEARCH_API_KEY=$AZURE_SEARCH_API_KEY

# Enable Application Insights
echo "📊 Enabling Application Insights..."
az monitor app-insights component create \
    --app $APP_NAME-insights \
    --location $LOCATION \
    --resource-group $RESOURCE_GROUP \
    --application-type web

APPINSIGHTS_KEY=$(az monitor app-insights component show \
    --app $APP_NAME-insights \
    --resource-group $RESOURCE_GROUP \
    --query instrumentationKey \
    --output tsv)

az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=$APPINSIGHTS_KEY"

# Get the app URL
APP_URL=$(az webapp show \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query defaultHostName \
    --output tsv)

echo "✅ Deployment complete!"
echo "🌐 Application URL: https://$APP_URL"
echo "📊 Application Insights: $APP_NAME-insights"
echo ""
echo "Test with:"
echo "curl -X POST https://$APP_URL/ask -H 'Content-Type: application/json' -d '{\"query\":\"What is the leave policy?\"}'"
