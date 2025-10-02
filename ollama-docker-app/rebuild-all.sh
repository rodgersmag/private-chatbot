#!/bin/bash
# Rebuild All Services - Unified Ollama + SelfDB

echo "🔨 Rebuilding all Ollama + SelfDB containers (development mode)"
echo "This will rebuild all containers while preserving your data in Docker volumes."
echo ""

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Rebuild and start all containers
echo "📦 Rebuilding and starting all containers..."
docker-compose up -d --build

# Check if services are running
echo ""
echo "📊 Checking service status..."
docker-compose ps

echo ""
echo "✅ Rebuild complete! Your data in Docker volumes has been preserved."
echo ""
echo "🌐 Service URLs:"
echo "   📱 Ollama UI:     http://localhost:3050"
echo "   🗄️  SelfDB UI:     http://localhost:3000"
echo "   🔌 Ollama API:    http://localhost:11434"
echo "   🚀 SelfDB API:    http://localhost:8000"
echo "   💾 Storage API:   http://localhost:8001"
echo "   ⚡ Functions:     http://localhost:8090"