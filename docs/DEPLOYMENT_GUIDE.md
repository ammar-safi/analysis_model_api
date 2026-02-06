# Deployment Guide

This guide covers various deployment options for the Sentiment and Stance Analysis API, from development to production environments.

## Table of Contents

- [Development Deployment](#development-deployment)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Environment Configuration](#environment-configuration)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Considerations](#security-considerations)
- [Performance Tuning](#performance-tuning)

## Development Deployment

### Quick Start with Startup Script

The easiest way to start the API is using the provided startup scripts:

1. **Using the Shell Script (Linux/Mac)**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd sentiment-stance-api
   
   # Make the script executable
   chmod +x start.sh
   
   # Start development server (auto-installs dependencies)
   ./start.sh --install-deps
   
   # Or start with custom settings
   ./start.sh --mode dev --port 8080 --log-level debug
   ```

2. **Using the Python Script (Cross-platform)**
   ```bash
   # Start development server
   python scripts/start.py --mode dev --install-deps
   
   # With custom configuration
   python scripts/start.py --mode dev --port 8080 --log-level debug --no-reload
   
   # Check environment without starting
   python scripts/start.py --check-only
   ```

3. **Startup Script Options**
   ```bash
   --mode MODE           # dev or prod (default: dev)
   --host HOST           # Host to bind to (default: 0.0.0.0)
   --port PORT           # Port to bind to (default: 8000)
   --workers NUM         # Number of workers for prod mode (default: 4)
   --log-level LEVEL     # debug, info, warning, error (default: info)
   --install-deps        # Install/update dependencies
   --force-deps          # Force reinstall dependencies
   --check-only          # Only check environment
   --no-reload           # Disable auto-reload in dev mode
   ```

### Manual Setup (Alternative)

1. **Setup Environment**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd sentiment-stance-api
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env with your settings
   nano .env
   ```

3. **Run Development Server**
   ```bash
   # Basic development server
   uvicorn main:app --reload --port 8000
   
   # With custom host and port
   uvicorn main:app --reload --host 0.0.0.0 --port 8080
   
   # With debug logging
   uvicorn main:app --reload --log-level debug
   ```

4. **Access the API**
   - API: `http://localhost:8000`
   - Documentation: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`

## Production Deployment

### Using the Startup Script (Recommended)

The provided startup script handles production deployment with proper configuration:

```bash
# Start production server with default settings (4 workers)
./start.sh --mode prod

# Or using Python script
python scripts/start.py --mode prod

# With custom worker count
./start.sh --mode prod --workers 8 --port 8000

# With custom configuration
python scripts/start.py --mode prod --workers 8 --log-level warning
```

The startup script automatically:
- Checks Python version compatibility
- Verifies virtual environment
- Validates dependencies
- Configures environment variables
- Performs health checks after startup
- Uses Gunicorn with Uvicorn workers for production

### Using Gunicorn + Uvicorn Workers (Manual)

Recommended for production environments.

1. **Install Production Dependencies**
   ```bash
   pip install gunicorn
   ```

2. **Create Gunicorn Configuration**
   
   Create `gunicorn.conf.py`:
   ```python
   # Gunicorn configuration file
   bind = "0.0.0.0:8000"
   workers = 4
   worker_class = "uvicorn.workers.UvicornWorker"
   worker_connections = 1000
   max_requests = 1000
   max_requests_jitter = 100
   timeout = 30
   keepalive = 2
   
   # Logging
   accesslog = "/var/log/sentiment-api/access.log"
   errorlog = "/var/log/sentiment-api/error.log"
   loglevel = "info"
   
   # Process naming
   proc_name = "sentiment-stance-api"
   
   # Worker recycling
   preload_app = True
   ```

3. **Run with Gunicorn**
   ```bash
   # Using configuration file
   gunicorn main:app -c gunicorn.conf.py
   
   # Or with command line options
   gunicorn main:app \
     --workers 4 \
     --worker-class uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8000 \
     --timeout 30 \
     --access-logfile /var/log/sentiment-api/access.log \
     --error-logfile /var/log/sentiment-api/error.log
   ```

### Using Uvicorn (Alternative)

```bash
# Production with multiple workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# With SSL (if you have certificates)
uvicorn main:app --host 0.0.0.0 --port 443 --ssl-keyfile key.pem --ssl-certfile cert.pem
```

### Systemd Service (Linux)

Create `/etc/systemd/system/sentiment-api.service`:

```ini
[Unit]
Description=Sentiment and Stance Analysis API
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/sentiment-stance-api
Environment=PATH=/opt/sentiment-stance-api/venv/bin
ExecStart=/opt/sentiment-stance-api/venv/bin/gunicorn main:app -c gunicorn.conf.py
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable sentiment-api
sudo systemctl start sentiment-api
sudo systemctl status sentiment-api
```

## Docker Deployment

### Quick Start with Docker Compose (Recommended)

The project includes pre-configured Docker files for easy deployment:

1. **Setup Environment**
   ```bash
   # Copy environment file
   cp .env.example .env
   
   # Edit environment variables as needed
   nano .env
   ```

2. **Build and Run**
   ```bash
   # Build and start the service
   docker-compose up -d
   
   # View logs
   docker-compose logs -f api
   
   # Check status
   docker-compose ps
   
   # Stop the service
   docker-compose down
   ```

3. **Access the API**
   - API: `http://localhost:8000`
   - Documentation: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`

### Docker Configuration Files

The project includes:
- `Dockerfile` - Multi-stage build for optimized production image
- `docker-compose.yml` - Complete orchestration with optional services
- `.dockerignore` - Optimized build context

### Using Docker Directly

### Dockerfile

Create `Dockerfile`:

```dockerfile
# Use Python 3.10 slim image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  sentiment-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=info
      - CACHE_MAX_SIZE=1000
      - CACHE_DEFAULT_TTL=3600
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - sentiment-api
    restart: unless-stopped

volumes:
  logs:
```

### Build and Run

```bash
# Build the image
docker build -t sentiment-stance-api .

# Run single container
docker run -d -p 8000:8000 --name sentiment-api sentiment-stance-api

# Or use docker-compose
docker-compose up -d

# View logs
docker-compose logs -f sentiment-api

# Scale the service
docker-compose up -d --scale sentiment-api=3
```

## Cloud Deployment

### AWS Deployment

#### Using AWS ECS

1. **Create Task Definition**
   ```json
   {
     "family": "sentiment-stance-api",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "512",
     "memory": "1024",
     "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "sentiment-api",
         "image": "your-account.dkr.ecr.region.amazonaws.com/sentiment-stance-api:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "LOG_LEVEL",
             "value": "info"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/sentiment-stance-api",
             "awslogs-region": "us-west-2",
             "awslogs-stream-prefix": "ecs"
           }
         },
         "healthCheck": {
           "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
           "interval": 30,
           "timeout": 5,
           "retries": 3,
           "startPeriod": 60
         }
       }
     ]
   }
   ```

2. **Create Service**
   ```bash
   aws ecs create-service \
     --cluster sentiment-cluster \
     --service-name sentiment-api-service \
     --task-definition sentiment-stance-api:1 \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
   ```

#### Using AWS Lambda (Serverless)

Create `lambda_handler.py`:
```python
from mangum import Mangum
from main import app

handler = Mangum(app)
```

Add to `requirements.txt`:
```
mangum==0.17.0
```

Deploy using AWS SAM or Serverless Framework.

### Google Cloud Platform

#### Using Cloud Run

1. **Build and Push Image**
   ```bash
   # Build for Cloud Run
   docker build -t gcr.io/PROJECT_ID/sentiment-stance-api .
   
   # Push to Container Registry
   docker push gcr.io/PROJECT_ID/sentiment-stance-api
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy sentiment-stance-api \
     --image gcr.io/PROJECT_ID/sentiment-stance-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 1Gi \
     --cpu 1 \
     --concurrency 100 \
     --max-instances 10
   ```

### Azure Deployment

#### Using Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name sentiment-stance-api \
  --image your-registry.azurecr.io/sentiment-stance-api:latest \
  --cpu 1 \
  --memory 1 \
  --ports 8000 \
  --environment-variables LOG_LEVEL=info \
  --restart-policy Always
```

## Environment Configuration

### Using the Environment File

The project includes a comprehensive `.env.example` file with all available configuration options:

1. **Create Your Environment File**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit with your settings
   nano .env
   ```

2. **Key Configuration Sections**

   The `.env.example` file includes:
   - **Server Configuration**: Host, port, workers, log level
   - **Cache Configuration**: Cache size, TTL, enable/disable
   - **Performance Monitoring**: Metrics window, memory thresholds
   - **Text Processing**: Max/min text lengths, target length limits
   - **API Configuration**: Title, version, contact info, license
   - **CORS Configuration**: Origins, methods, headers
   - **Security Configuration**: API keys, rate limiting
   - **Logging Configuration**: Log files, formats, request logging
   - **Health Check Configuration**: Paths, detailed info
   - **Metrics Configuration**: Enable/disable, endpoint prefix
   - **Deployment Configuration**: Environment, app name, region

3. **Loading Environment Variables**

   The startup scripts automatically load environment variables from:
   - System environment variables
   - `.env` file in project root
   - Command-line arguments (override .env values)

### Environment Variables

Create `.env` file:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Application Settings
LOG_LEVEL=info
DEBUG=false

# Cache Configuration
CACHE_MAX_SIZE=1000
CACHE_DEFAULT_TTL=3600

# Performance Monitoring
PERFORMANCE_WINDOW_MINUTES=60
MEMORY_THRESHOLD_MB=500

# Security (if implemented)
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database (if needed for future features)
DATABASE_URL=postgresql://user:pass@localhost/dbname

# External Services (if integrated)
REDIS_URL=redis://localhost:6379/0
```

### Configuration Management

Create `config.py`:

```python
import os
from typing import List

class Settings:
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    WORKERS: int = int(os.getenv("WORKERS", "4"))
    
    # Application
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Cache
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "1000"))
    CACHE_DEFAULT_TTL: int = int(os.getenv("CACHE_DEFAULT_TTL", "3600"))
    
    # Performance
    PERFORMANCE_WINDOW_MINUTES: int = int(os.getenv("PERFORMANCE_WINDOW_MINUTES", "60"))
    MEMORY_THRESHOLD_MB: float = float(os.getenv("MEMORY_THRESHOLD_MB", "500"))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
    ALLOWED_HOSTS: List[str] = os.getenv("ALLOWED_HOSTS", "localhost").split(",")

settings = Settings()
```

## Monitoring and Logging

### Logging Configuration

Create `logging.conf`:

```ini
[loggers]
keys=root,uvicorn,app

[handlers]
keys=console,file,error_file

[formatters]
keys=default,detailed

[logger_root]
level=INFO
handlers=console,file

[logger_uvicorn]
level=INFO
handlers=console,file
qualname=uvicorn
propagate=0

[logger_app]
level=INFO
handlers=console,file
qualname=app
propagate=0

[handler_console]
class=StreamHandler
level=INFO
formatter=default
args=(sys.stdout,)

[handler_file]
class=handlers.RotatingFileHandler
level=INFO
formatter=detailed
args=('/var/log/sentiment-api/app.log', 'a', 10485760, 5)

[handler_error_file]
class=handlers.RotatingFileHandler
level=ERROR
formatter=detailed
args=('/var/log/sentiment-api/error.log', 'a', 10485760, 5)

[formatter_default]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s

[formatter_detailed]
format=%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(funcName)s - %(message)s
```

### Monitoring Setup

#### Prometheus Metrics (Optional)

Add to `requirements.txt`:
```
prometheus-client==0.18.0
```

Create `metrics.py`:
```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Metrics
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
ACTIVE_REQUESTS = Gauge('api_active_requests', 'Active requests')
CACHE_HITS = Counter('api_cache_hits_total', 'Cache hits')
CACHE_MISSES = Counter('api_cache_misses_total', 'Cache misses')

def get_metrics():
    return generate_latest()
```

#### Health Check Endpoint Enhancement

```python
@router.get("/health/detailed")
async def detailed_health():
    """Detailed health check for monitoring systems"""
    try:
        # Check services
        sentiment_healthy = check_sentiment_service()
        stance_healthy = check_stance_service()
        cache_healthy = check_cache_service()
        
        # System metrics
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        
        status = "healthy" if all([sentiment_healthy, stance_healthy, cache_healthy]) else "unhealthy"
        
        return {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "services": {
                "sentiment_service": "healthy" if sentiment_healthy else "unhealthy",
                "stance_service": "healthy" if stance_healthy else "unhealthy",
                "cache_service": "healthy" if cache_healthy else "unhealthy"
            },
            "system": {
                "cpu_usage_percent": cpu_usage,
                "memory_usage_percent": memory_usage,
                "disk_usage_percent": disk_usage
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
```

## Security Considerations

### Basic Security Measures

1. **HTTPS Only**
   ```python
   # Add to main.py
   from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
   
   if not settings.DEBUG:
       app.add_middleware(HTTPSRedirectMiddleware)
   ```

2. **CORS Configuration**
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=settings.ALLOWED_HOSTS,
       allow_credentials=True,
       allow_methods=["GET", "POST"],
       allow_headers=["*"],
   )
   ```

3. **Rate Limiting** (using slowapi)
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   from slowapi.errors import RateLimitExceeded
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
   
   @limiter.limit("100/minute")
   @router.post("/sentiment-analysis")
   async def analyze_sentiment(request: Request, ...):
       # endpoint implementation
   ```

### Reverse Proxy Configuration (Nginx)

Create `nginx.conf`:

```nginx
upstream sentiment_api {
    server sentiment-api:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://sentiment_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Health check endpoint (no rate limiting)
    location /health {
        proxy_pass http://sentiment_api;
        proxy_set_header Host $host;
    }
}
```

## Performance Tuning

### Application Level

1. **Worker Configuration**
   ```python
   # Calculate optimal worker count
   import multiprocessing
   
   workers = multiprocessing.cpu_count() * 2 + 1
   ```

2. **Cache Optimization**
   ```python
   # Adjust cache settings based on usage
   CACHE_MAX_SIZE = 2000  # Increase for high-traffic
   CACHE_DEFAULT_TTL = 7200  # 2 hours for stable results
   ```

3. **Memory Management**
   ```python
   # Monitor and optimize memory usage
   import gc
   
   # Periodic garbage collection
   gc.collect()
   ```

### System Level

1. **File Descriptors**
   ```bash
   # Increase file descriptor limits
   echo "* soft nofile 65536" >> /etc/security/limits.conf
   echo "* hard nofile 65536" >> /etc/security/limits.conf
   ```

2. **TCP Settings**
   ```bash
   # Optimize TCP settings
   echo "net.core.somaxconn = 65536" >> /etc/sysctl.conf
   echo "net.ipv4.tcp_max_syn_backlog = 65536" >> /etc/sysctl.conf
   sysctl -p
   ```

### Database Optimization (Future)

If you add database support:

```python
# Connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   - Monitor cache size
   - Check for memory leaks
   - Adjust worker count

2. **Slow Response Times**
   - Check cache hit rates
   - Monitor system resources
   - Optimize worker configuration

3. **Connection Issues**
   - Verify firewall settings
   - Check port availability
   - Review proxy configuration

### Debugging Commands

```bash
# Check service status
systemctl status sentiment-api

# View logs
journalctl -u sentiment-api -f

# Monitor resources
htop
iotop
netstat -tulpn

# Test endpoints
curl -f http://localhost:8000/health
curl -X POST http://localhost:8000/sentiment-analysis -d '{"text":"test"}'

# Docker debugging
docker logs sentiment-api
docker exec -it sentiment-api /bin/bash
```

This deployment guide provides comprehensive instructions for deploying the Sentiment and Stance Analysis API in various environments, from development to production-scale deployments.