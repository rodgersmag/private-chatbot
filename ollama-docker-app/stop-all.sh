#!/bin/bash
# Stop All Services - Unified Ollama + SelfDB

echo "🛑 Stopping all Ollama + SelfDB services..."
echo ""

# Stop all containers
docker-compose down

echo ""
echo "✅ All services stopped successfully!"
echo ""
echo "💡 Services that were stopped:"
echo "   - Ollama AI Service"
echo "   - Ollama UI"
echo "   - SelfDB Backend API"
echo "   - SelfDB Frontend"
echo "   - SelfDB Storage Service"
echo "   - PostgreSQL Database"
echo "   - Deno Runtime"
echo ""
echo "🔄 To start services again, run: ./start-all.sh"