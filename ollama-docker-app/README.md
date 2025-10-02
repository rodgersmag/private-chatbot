# Ollama + SelfDB Unified App

## Overview
This project provides a unified Dockerized environment that combines:
- **Ollama AI Service**: Runs the `qwen3:1.7b` model for AI chat capabilities
- **SelfDB Backend**: A full-stack database and API platform with PostgreSQL, FastAPI backend, React frontend, and cloud functions

The setup includes all necessary configurations and scripts to run both services seamlessly together.

## Project Structure
```
ollama-docker-app/
├── docker-compose.yml          # Unified Docker Compose configuration
├── start-all.sh               # Unified startup script
├── quick-start.sh             # Legacy script (now redirects to start-all.sh)
├── .env                       # Environment variables for all services
├── main.py                    # Python script to interact with Ollama API
├── ui/                        # Ollama UI (React app)
├── SelfDB/                    # SelfDB backend platform
│   ├── backend/               # FastAPI backend
│   ├── frontend/              # React frontend
│   ├── storage_service/       # File storage service
│   ├── functions/             # Cloud functions (Deno)
│   └── tests/                 # Test suites
└── README.md
```

## Prerequisites
- Docker installed on your machine
- Docker Compose installed on your machine
- At least 8GB RAM recommended for running both services

## Getting Started

### Quick Start
The easiest way to get everything running:

```bash
./start-all.sh
```

This will:
1. Set up environment variables and generate API keys
2. Start all services (Ollama, SelfDB backend, databases, etc.)
3. Download the qwen3:1.7b model if not present
4. Wait for all services to be healthy
5. Display service URLs

### Manual Setup

#### 1. Environment Configuration
Copy and configure the environment file:
```bash
cp SelfDB/.env.example .env
# Edit .env with your preferred settings
```

#### 2. Build and Run
```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

## Service URLs

Once running, the following services will be available:

| Service | URL | Description |
|---------|-----|-------------|
| Ollama UI | http://localhost:3050 | Web interface for Ollama chat |
| SelfDB UI | http://localhost:3000 | SelfDB admin interface |
| Ollama API | http://localhost:11434 | Direct API access to Ollama |
| SelfDB API | http://localhost:8000 | SelfDB REST API |
| Storage API | http://localhost:8001 | File storage service |
| Functions | http://localhost:8090 | Cloud functions runtime |

## Usage

### Interacting with Ollama
Use the provided Python script:
```bash
python3 main.py
```

Or use curl directly:
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen3:1.7b", "prompt": "Hello, how are you?"}'
```

### Using SelfDB
1. Open http://localhost:3000 in your browser
2. Use the admin interface to create databases, tables, and manage data
3. Access the API at http://localhost:8000/docs for API documentation

## Management Commands

### Rebuilding Services
```bash
# Rebuild UI services only
./start-all.sh rebuild-ui

# Rebuild backend services only
./start-all.sh rebuild-backend

# Rebuild specific service
docker-compose build <service_name>
```

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ollama
docker-compose logs -f backend
```

### Stopping Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️  destroys data)
docker-compose down -v
```

### Checking Status
```bash
# Service status
docker-compose ps

# Resource usage
docker stats
```

## Configuration

### Environment Variables
Key variables in `.env`:

- **Database**: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- **Security**: `SECRET_KEY`, `ANON_KEY`
- **Ports**: `API_PORT`, `FRONTEND_PORT`
- **URLs**: `REACT_APP_API_URL`, `STORAGE_SERVICE_EXTERNAL_URL`

### Volumes
The setup uses named Docker volumes for data persistence:
- `ollama-data`: Ollama models
- `postgres_data`: PostgreSQL database
- `selfdb_files`: File storage
- `functions_data`: Cloud functions

## Troubleshooting

### Common Issues

**Services not starting:**
```bash
# Check logs
docker-compose logs

# Check resource usage
docker system df
```

**Ollama model not downloading:**
```bash
# Manual download
docker-compose exec ollama ollama pull qwen3:1.7b
```

**Database connection issues:**
```bash
# Check PostgreSQL
docker-compose exec postgres pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}
```

**Port conflicts:**
- Ensure ports 11434, 3050, 3000, 8000, 8001, 8090, 5432 are available
- Modify ports in `docker-compose.yml` if needed

### Performance Tips
- Allocate at least 4GB RAM to Docker
- Use SSD storage for better performance
- Consider using Docker Desktop with increased resources

## Development

### Hot Reloading
The setup includes volume mounts for development:
- Backend code changes reload automatically
- Frontend changes require rebuild: `./start-all.sh rebuild-ui`

### Adding New Services
1. Add service definition to `docker-compose.yml`
2. Update environment variables in `.env`
3. Add health checks and dependencies
4. Update `start-all.sh` if needed

## Additional Resources
- [Ollama Documentation](https://ollama.com)
- [SelfDB Documentation](./SelfDB/README.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)