#!/bin/bash
set -e

# Check if vector store exists
VECTOR_STORE_PATH="/app/data/vector_stores/faiss_index.faiss"

if [ ! -f "$VECTOR_STORE_PATH" ]; then
    echo "⚠️ Vector store not found at $VECTOR_STORE_PATH"
    echo "🚀 Initializing vector store..."
    python scripts/setup_vectorstore.py
else
    echo "✅ Vector store found."
fi

# Run the main command
exec "$@"
