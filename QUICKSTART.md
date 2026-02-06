# Quick Start Guide

Get the Sentiment and Stance Analysis API up and running in minutes.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

## Installation

### Option 1: Quick Start (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd sentiment-stance-api

# Make startup script executable (Linux/Mac)
chmod +x start.sh

# Start with automatic dependency installation
./start.sh --install-deps
```

### Option 2: Using Python Script (Cross-platform)

```bash
# Clone the repository
git clone <repository-url>
cd sentiment-stance-api

# Start with automatic setup
python scripts/start.py --mode dev --install-deps
```

### Option 3: Docker (Easiest)

```bash
# Clone the repository
git clone <repository-url>
cd sentiment-stance-api

# Copy environment file
cp .env.example .env

# Start with Docker Compose
docker-compose up -d
```

## Verify Installation

Once started, verify the API is running:

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2024-01-01T00:00:00.000000",
#   "version": "1.0.0",
#   "uptime_seconds": 10.5
# }
```

## Access the API

- **API Base URL**: http://localhost:8000
- **Interactive Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Performance Metrics**: http://localhost:8000/metrics/performance

## Test the API

### Sentiment Analysis

```bash
curl -X POST "http://localhost:8000/sentiment-analysis" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product! It works great!"}'
```

Expected response:
```json
{
  "sentiment": "positive",
  "confidence": 0.92,
  "request_id": "abc123...",
  "timestamp": "2024-01-01T00:00:00.000000"
}
```

### Stance Analysis

```bash
curl -X POST "http://localhost:8000/stance-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Apple makes innovative products that change the industry",
    "target": "Apple"
  }'
```

Expected response:
```json
{
  "stance": "مؤيد",
  "confidence": 0.85,
  "target": "Apple",
  "request_id": "def456...",
  "timestamp": "2024-01-01T00:00:00.000000"
}
```

## Configuration

### Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Key settings to customize:

```bash
# Server
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=info

# Cache
CACHE_MAX_SIZE=1000
CACHE_DEFAULT_TTL=3600

# Performance
MEMORY_THRESHOLD_MB=500
```

### Startup Options

```bash
# Development mode (default)
./start.sh --mode dev

# Production mode with 8 workers
./start.sh --mode prod --workers 8

# Custom port
./start.sh --port 8080

# Debug logging
./start.sh --log-level debug

# Check environment without starting
./start.sh --check-only
```

## Common Commands

### Development

```bash
# Start development server with auto-reload
./start.sh --mode dev

# Install/update dependencies
./start.sh --install-deps

# Force reinstall dependencies
./start.sh --force-deps
```

### Production

```bash
# Start production server
./start.sh --mode prod --workers 4

# With custom configuration
python scripts/start.py --mode prod --workers 8 --log-level warning
```

### Docker

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Rebuild and start
docker-compose up -d --build
```

## Troubleshooting

### Port Already in Use

```bash
# Use a different port
./start.sh --port 8080
```

### Dependencies Not Installing

```bash
# Force reinstall
./start.sh --force-deps

# Or manually
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Virtual Environment Issues

```bash
# Remove and recreate
rm -rf venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Docker Issues

```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check logs
docker-compose logs -f api
```

## Next Steps

1. **Read the Full Documentation**: See `docs/API_DOCUMENTATION.md` for detailed API usage
2. **Deployment Guide**: See `docs/DEPLOYMENT_GUIDE.md` for production deployment
3. **Run Tests**: Execute `pytest` to run the test suite
4. **Explore Metrics**: Visit http://localhost:8000/metrics/performance for performance data

## Getting Help

- Check the logs: `docker-compose logs -f` or view console output
- Review the health endpoint: http://localhost:8000/health
- Read the full documentation in the `docs/` directory
- Check system requirements and dependencies

## Stopping the API

### Shell Script

```bash
# Press Ctrl+C in the terminal where the script is running
```

### Docker

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Performance Tips

1. **Enable Caching**: Set `CACHE_ENABLED=true` in `.env`
2. **Adjust Workers**: Use `(2 x CPU cores) + 1` for production
3. **Monitor Metrics**: Check `/metrics/performance` regularly
4. **Optimize Cache**: Adjust `CACHE_MAX_SIZE` and `CACHE_DEFAULT_TTL` based on usage

## Security Notes

- Change default settings in `.env` for production
- Use HTTPS in production (configure reverse proxy)
- Enable rate limiting if exposed to public internet
- Keep dependencies updated: `pip install -r requirements.txt --upgrade`

---

**Ready to go!** Your Sentiment and Stance Analysis API should now be running at http://localhost:8000
