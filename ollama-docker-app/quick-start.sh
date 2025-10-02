#!/bin/bash
# Quick Start Script - Fastest Setup

# Check if first argument is "rebuild-ui"
if [ "$1" = "rebuild-ui" ]; then
    echo "🔨 Rebuilding UI Docker container..."
    echo ""

    echo "📦 Rebuilding UI service with latest changes..."
    docker-compose build ui

    echo ""
    echo "🚀 Restarting UI service..."
    docker-compose up -d ui

    echo ""
    echo "✅ UI container rebuilt and restarted successfully!"
    echo "🌐 UI is available at: http://localhost:3000"
    exit 0
fi

echo "🚀 Setting up Ollama with fastest configuration..."
echo ""

# Stop any running containers
docker-compose down 2>/dev/null || true
docker-compose -f docker-compose.yml down 2>/dev/null || true

echo "📦 Starting Ollama with official image..."
docker-compose -f docker-compose.yml up -d

echo ""
echo "⏳ Waiting for Ollama server to be ready..."

# Wait for server to be healthy
for i in {1..30}; do
    if docker-compose -f docker-compose.yml exec -T ollama ollama list >/dev/null 2>&1; then
        echo "✅ Ollama server is ready!"
        break
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "📥 Checking if model qwen3:1.7b is available..."

# Check if model exists
if docker-compose -f docker-compose.yml exec -T ollama ollama list | grep -q "qwen3:1.7b"; then
    echo "✅ Model qwen3:1.7b already cached!"
else
    echo "📦 Model not found. Downloading qwen3:1.7b (this may take 2-5 minutes on first run)..."
    docker-compose -f docker-compose.yml exec -T ollama ollama pull qwen3:1.7b
    echo "✅ Model downloaded successfully!"
fi

echo ""
echo "📊 Available models:"
docker-compose -f docker-compose.yml exec -T ollama ollama list

echo ""
echo "✨ Setup complete!"
echo ""
echo "🎯 You can now use main.py to interact with the API:"
echo "   python3 main.py"
echo ""
echo "💡 Next time you run 'docker-compose -f docker-compose.yml up -d'"
echo "   it will start in just 5-10 seconds!"
echo ""
echo "🔧 Additional commands:"
echo "   ./quick-start.sh rebuild-ui  # Rebuild UI Docker container with latest code changes"
