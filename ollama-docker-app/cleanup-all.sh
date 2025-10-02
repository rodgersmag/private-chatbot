#!/bin/bash
# Cleanup All Services - Unified Ollama + SelfDB

echo "🧹 This script will stop all containers, remove Docker volumes, and clean up Docker images and build history."
echo "WARNING: This will delete all your data and related Docker resources!"
echo "         - Ollama models will be lost"
echo "         - SelfDB database data will be lost"
echo "         - File storage will be lost"
echo "         - Cloud functions will be lost"
echo ""
echo "Make sure you have backups if needed."
read -p "Are you sure you want to continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "🛑 Operation cancelled."
    exit 1
fi

echo ""
echo "🛑 Stopping and removing containers..."
docker-compose down -v

echo "🗂️  Removing Docker volumes..."
docker volume rm ollama-docker-app_ollama-data ollama-docker-app_postgres_data ollama-docker-app_selfdb_files ollama-docker-app_functions_data 2>/dev/null || true

echo "🖼️  Removing Docker images related to the project..."
docker images | grep -E "(ollama-docker-app|selfdb|ollama/ollama)" | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true

echo "🧽 Cleaning up dangling images..."
docker image prune -f >/dev/null 2>&1

echo "🗑️  Cleaning up Docker build cache..."
docker builder prune -f >/dev/null 2>&1

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "💡 To start fresh, run: ./start-all.sh"
echo ""
echo "📋 What was cleaned up:"
echo "   - All containers stopped and removed"
echo "   - All Docker volumes removed (ollama-data, postgres_data, selfdb_files, functions_data)"
echo "   - All project-related Docker images removed"
echo "   - Docker build cache cleaned"
echo "   - Dangling images removed"