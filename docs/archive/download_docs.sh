#!/bin/bash
# Download FastAPI documentation for RAG dataset

BASE_URL="https://raw.githubusercontent.com/tiangolo/fastapi/master/docs/en/docs"
DOCS_DIR="data/documents"

echo "📥 Downloading FastAPI documentation..."

# Core documentation files
docs=(
    "index.md"
    "tutorial/index.md"
    "tutorial/first-steps.md"
    "tutorial/path-params.md"
    "tutorial/query-params.md"
    "tutorial/body.md"
    "tutorial/response-model.md"
    "tutorial/dependencies/index.md"
    "tutorial/security/index.md"
    "advanced/index.md"
    "deployment/index.md"
    "features.md"
)

count=0
for doc in "${docs[@]}"; do
    filename=$(basename "$doc")
    # Create subdirectory structure if needed
    subdir=$(dirname "$doc")
    mkdir -p "$DOCS_DIR/$subdir"
    
    echo "Downloading: $doc"
    curl -s -o "$DOCS_DIR/$doc" "$BASE_URL/$doc"
    
    if [ -f "$DOCS_DIR/$doc" ]; then
        ((count++))
        echo "✅ Saved: $DOCS_DIR/$doc"
    else
        echo "❌ Failed: $doc"
    fi
done

echo ""
echo "✅ Downloaded $count FastAPI documentation files"
echo "📁 Location: $DOCS_DIR"
