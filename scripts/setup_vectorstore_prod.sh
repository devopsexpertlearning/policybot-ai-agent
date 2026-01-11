#!/bin/bash
set -e

echo "🚀 Production Vector Store Setup Script"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Get Azure credentials from Terraform outputs
echo "📋 Fetching Azure credentials from Terraform..."
cd deployment/terraform

AZURE_OPENAI_ENDPOINT=$(terraform output -raw openai_endpoint)
AZURE_OPENAI_API_KEY=$(terraform output -raw openai_api_key)
AZURE_SEARCH_ENDPOINT=$(terraform output -raw search_endpoint)
AZURE_SEARCH_API_KEY=$(terraform output -raw search_api_key)
AZURE_SEARCH_INDEX=$(terraform output -raw search_index_name)
OPENAI_DEPLOYMENT_NAME=$(terraform output -raw openai_deployment_name)
OPENAI_EMBEDDING_DEPLOYMENT=$(terraform output -raw openai_embedding_deployment_name)

cd ../..

echo "✅ Credentials retrieved"

# Export environment variables for the script
export ENVIRONMENT="production"
export USE_GEMINI="false"
export USE_FAISS="false"
export AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT"
export AZURE_OPENAI_API_KEY="$AZURE_OPENAI_API_KEY"
export AZURE_OPENAI_DEPLOYMENT_NAME="$OPENAI_DEPLOYMENT_NAME"
export AZURE_OPENAI_EMBEDDING_DEPLOYMENT="$OPENAI_EMBEDDING_DEPLOYMENT"
export AZURE_SEARCH_ENDPOINT="$AZURE_SEARCH_ENDPOINT"
export AZURE_SEARCH_API_KEY="$AZURE_SEARCH_API_KEY"
export AZURE_SEARCH_INDEX_NAME="$AZURE_SEARCH_INDEX"

echo ""
echo "🔧 Activating virtual environment..."
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate

echo ""
echo "🔄 Running vector store setup..."
python3 scripts/setup_vectorstore.py

echo ""
echo "✅ Production vector store setup complete!"
echo "🌐 Your application is now ready at: https://$(cd deployment/terraform && terraform output -raw app_service_url)"
