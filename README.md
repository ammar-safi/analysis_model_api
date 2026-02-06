# Sentiment and Stance Analysis API

A high-performance FastAPI-based REST API for analyzing sentiment and stance in English texts. This API provides two main services: sentiment analysis (positive, negative, neutral) and stance analysis (supportive, opposing, neutral) towards specific targets.

## 🚀 Features

- **Sentiment Analysis**: Classify text sentiment as positive, negative, or neutral with confidence scores
- **Stance Analysis**: Determine stance towards specific targets (people, organizations, topics)
- **High Performance**: Built-in caching, performance monitoring, and optimized processing
- **Robust Error Handling**: Comprehensive error handling with detailed error messages
- **Real-time Monitoring**: Performance metrics, system monitoring, and cache statistics
- **Auto-generated Documentation**: Interactive Swagger/OpenAPI documentation
- **Production Ready**: Comprehensive logging, health checks, and monitoring endpoints

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Performance Monitoring](#performance-monitoring)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

## 🛠 Installation

### Quick Start (Recommended)

The easiest way to get started:

```bash
# Clone the repository
git clone <repository-url>
cd sentiment-stance-api

# Make startup script executable (Linux/Mac)
chmod +x start.sh

# Start with automatic setup
./start.sh --install-deps
```

See [QUICKSTART.md](QUICKSTART.md) for more quick start options.

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Docker (optional, for containerized deployment)

### Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sentiment-stance-api
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment (optional)**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run the application**
   ```bash
   # Development mode
   python scripts/start.py --mode dev
   
   # Or manually with uvicorn
   python -m uvicorn main:app --reload --port 8000
   ```

The API will be available at `http://localhost:8000`

## 🚀 Quick Start

### Using Startup Scripts

```bash
# Development mode (auto-reload enabled)
./start.sh --mode dev

# Production mode with 4 workers
./start.sh --mode prod --workers 4

# Custom port
./start.sh --port 8080

# Check environment without starting
./start.sh --check-only
```

### Using Docker

```bash
# Copy environment file
cp .env.example .env

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f api
```

### Basic Usage

1. **Start the server**
   ```bash
   # Using startup script
   ./start.sh
   
   # Or manually
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. **Access the interactive documentation**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

3. **Test the API**
   ```bash
   # Sentiment Analysis
   curl -X POST "http://localhost:8000/sentiment-analysis" \
        -H "Content-Type: application/json" \
        -d '{"text": "I love this product!"}'
   
   # Stance Analysis
   curl -X POST "http://localhost:8000/stance-analysis" \
        -H "Content-Type: application/json" \
        -d '{"text": "Apple makes great phones", "target": "Apple"}'
   ```

For more detailed quick start instructions, see [QUICKSTART.md](QUICKSTART.md).

## 📚 API Endpoints

### Core Analysis Endpoints

#### POST `/sentiment-analysis`
Analyze sentiment of English text.

**Request Body:**
```json
{
  "text": "Your text here (1-5000 characters)"
}
```

**Response:**
```json
{
  "sentiment": "positive|negative|normal",
  "confidence": 0.85,
  "request_id": "req_123456789",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### POST `/stance-analysis`
Analyze stance towards a specific target.

**Request Body:**
```json
{
  "text": "Your text here (1-5000 characters)",
  "target": "Target entity (1-200 characters)"
}
```

**Response:**
```json
{
  "stance": "supportive|opposing|neutral",
  "confidence": 0.75,
  "target": "Apple",
  "request_id": "req_123456789",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Monitoring Endpoints

#### GET `/health`
Check API health status.

#### GET `/metrics/performance`
Get detailed performance metrics.

#### GET `/metrics/cache`
Get cache performance statistics.

#### GET `/metrics/system`
Get system resource usage.

### Cache Management

#### GET `/cache/stats`
Get cache statistics.

#### POST `/cache/clear`
Clear all cached results.

#### POST `/metrics/cache/optimize`
Optimize cache performance.

## 💡 Usage Examples

### Python Client Example

```python
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def analyze_sentiment(text):
    """Analyze sentiment of text"""
    response = requests.post(
        f"{BASE_URL}/sentiment-analysis",
        json={"text": text}
    )
    return response.json()

def analyze_stance(text, target):
    """Analyze stance towards target"""
    response = requests.post(
        f"{BASE_URL}/stance-analysis",
        json={"text": text, "target": target}
    )
    return response.json()

# Examples
sentiment_result = analyze_sentiment("I love this new smartphone!")
print(f"Sentiment: {sentiment_result['sentiment']} (confidence: {sentiment_result['confidence']})")

stance_result = analyze_stance("Apple makes innovative products", "Apple")
print(f"Stance: {stance_result['stance']} (confidence: {stance_result['confidence']})")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

async function analyzeSentiment(text) {
    try {
        const response = await axios.post(`${BASE_URL}/sentiment-analysis`, {
            text: text
        });
        return response.data;
    } catch (error) {
        console.error('Error:', error.response.data);
        throw error;
    }
}

async function analyzeStance(text, target) {
    try {
        const response = await axios.post(`${BASE_URL}/stance-analysis`, {
            text: text,
            target: target
        });
        return response.data;
    } catch (error) {
        console.error('Error:', error.response.data);
        throw error;
    }
}

// Usage
(async () => {
    const sentiment = await analyzeSentiment("This is amazing!");
    console.log(`Sentiment: ${sentiment.sentiment} (${sentiment.confidence})`);
    
    const stance = await analyzeStance("Microsoft has great products", "Microsoft");
    console.log(`Stance: ${stance.stance} (${stance.confidence})`);
})();
```

### cURL Examples

```bash
# Sentiment Analysis
curl -X POST "http://localhost:8000/sentiment-analysis" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "I absolutely love this new feature! It works perfectly."
     }'

# Stance Analysis
curl -X POST "http://localhost:8000/stance-analysis" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Google has been making questionable decisions lately",
       "target": "Google"
     }'

# Health Check
curl -X GET "http://localhost:8000/health"

# Performance Metrics
curl -X GET "http://localhost:8000/metrics/performance"
```

## 📊 Performance Monitoring

The API includes comprehensive performance monitoring:

### Real-time Metrics
- Response times (average, min, max, P95, P99)
- Request success/failure rates
- Cache hit/miss rates
- Memory usage tracking
- System resource monitoring

### Monitoring Endpoints

```bash
# Get performance metrics
GET /metrics/performance?detailed=true&limit=100

# Get cache statistics
GET /metrics/cache?detailed=true

# Get system metrics
GET /metrics/system

# Reset metrics (admin)
POST /metrics/reset?reset_cache=true&reset_performance=true
```

### Performance Headers

Each response includes performance headers:
- `X-Response-Time`: Request processing time in milliseconds
- `X-Request-ID`: Unique request identifier
- `X-Cache-Hit`: Whether result was served from cache
- `X-Memory-Usage`: Current memory usage
- `X-Memory-Delta`: Memory change during request

## ⚙️ Configuration

### Environment Variables

The API can be configured using environment variables. Copy `.env.example` to `.env` and customize:

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration
nano .env
```

Key configuration options:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4
LOG_LEVEL=info

# Cache Configuration
CACHE_MAX_SIZE=1000
CACHE_DEFAULT_TTL=3600
CACHE_ENABLED=true

# Performance Monitoring
PERFORMANCE_WINDOW_MINUTES=60
MEMORY_THRESHOLD_MB=500
PERFORMANCE_MONITORING_ENABLED=true

# Text Processing
MAX_TEXT_LENGTH_SENTIMENT=5000
MAX_TEXT_LENGTH_STANCE=5000
MIN_TEXT_LENGTH=1
MAX_TARGET_LENGTH=200
```

See `.env.example` for all available configuration options.

### Startup Script Options

```bash
./start.sh [OPTIONS]

Options:
  --mode MODE           Server mode: dev or prod (default: dev)
  --host HOST           Host to bind to (default: 0.0.0.0)
  --port PORT           Port to bind to (default: 8000)
  --workers NUM         Number of workers for prod mode (default: 4)
  --log-level LEVEL     Log level: debug, info, warning, error (default: info)
  --install-deps        Install/update dependencies
  --force-deps          Force reinstall dependencies
  --check-only          Only check environment
  --no-reload           Disable auto-reload in dev mode
```

### Cache Settings

The API uses intelligent caching to improve performance:
- **Default TTL**: 1 hour (configurable via `CACHE_DEFAULT_TTL`)
- **Max Size**: 1000 entries (configurable via `CACHE_MAX_SIZE`)
- **Eviction Policy**: LRU (Least Recently Used)
- **Automatic Cleanup**: Every 5 minutes

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/test_sentiment_service.py
pytest tests/test_stance_service.py
pytest tests/test_integration_endpoints.py
```

### Test Categories

- **Unit Tests**: Individual service testing
- **Integration Tests**: End-to-end API testing
- **Performance Tests**: Load and stress testing
- **Edge Case Tests**: Error handling and boundary conditions

### Example Test

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_sentiment_analysis():
    response = client.post(
        "/sentiment-analysis",
        json={"text": "I love this product!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] == "positive"
    assert 0.0 <= data["confidence"] <= 1.0
```

## 🚀 Deployment

### Quick Deployment Options

1. **Using Startup Script (Recommended)**
   ```bash
   # Production mode with 4 workers
   ./start.sh --mode prod --workers 4
   
   # Or using Python script
   python scripts/start.py --mode prod --workers 8
   ```

2. **Using Docker Compose (Easiest)**
   ```bash
   # Copy environment file
   cp .env.example .env
   
   # Start services
   docker-compose up -d
   
   # Scale if needed
   docker-compose up -d --scale api=3
   ```

3. **Using Docker**
   ```bash
   # Build image
   docker build -t sentiment-stance-api .
   
   # Run container
   docker run -d -p 8000:8000 \
     -e LOG_LEVEL=info \
     -e WORKERS=4 \
     sentiment-stance-api
   ```

### Production Deployment

For production environments:

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn + Uvicorn workers
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 30 \
  --access-logfile /var/log/sentiment-api/access.log \
  --error-logfile /var/log/sentiment-api/error.log
```

### Deployment Files

The project includes comprehensive deployment configuration:

- **`start.sh`**: Shell script for easy startup (Linux/Mac)
- **`scripts/start.py`**: Cross-platform Python startup script
- **`Dockerfile`**: Multi-stage Docker build configuration
- **`docker-compose.yml`**: Complete Docker orchestration
- **`.dockerignore`**: Optimized Docker build context
- **`.env.example`**: Complete environment configuration template

### Health Checks

The API provides health check endpoints for monitoring:

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health with system info
curl http://localhost:8000/health?detailed=true
```

### Deployment Documentation

For comprehensive deployment instructions including:
- Cloud deployment (AWS, GCP, Azure)
- Kubernetes deployment
- Systemd service configuration
- Nginx reverse proxy setup
- SSL/TLS configuration
- Monitoring and logging setup
- Performance tuning
- Security best practices

See the complete [Deployment Guide](docs/DEPLOYMENT_GUIDE.md).

## 📈 Performance Characteristics

### Typical Response Times
- **Sentiment Analysis**: 50-200ms (cached: <10ms)
- **Stance Analysis**: 100-300ms (cached: <10ms)
- **Health Check**: <5ms
- **Metrics**: 10-50ms

### Throughput
- **Concurrent Requests**: 100+ requests/second
- **Cache Hit Rate**: 60-80% (typical usage)
- **Memory Usage**: 50-200MB (depending on cache size)

### Scalability
- Stateless design for horizontal scaling
- In-memory caching for single instance performance
- Redis support for distributed caching (future enhancement)

## 🔧 Development

### Project Structure

```
sentiment-stance-api/
├── app/
│   ├── middleware/          # Performance and logging middleware
│   ├── models/             # Pydantic models
│   ├── routers/            # API endpoints
│   ├── services/           # Business logic
│   ├── utils/              # Utilities and helpers
│   └── exceptions.py       # Custom exceptions
├── tests/                  # Test suite
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
└── README.md              # This file
```

### Adding New Features

1. **Create service** in `app/services/`
2. **Add models** in `app/models/`
3. **Create router** in `app/routers/`
4. **Add tests** in `tests/`
5. **Update documentation**

### Code Style

- **Formatting**: Black
- **Linting**: Flake8
- **Type Hints**: Required for all functions
- **Docstrings**: Google style

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black app/ tests/

# Run linting
flake8 app/ tests/

# Run type checking
mypy app/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)

## 🙏 Acknowledgments

- **VADER Sentiment**: For sentiment analysis capabilities
- **FastAPI**: For the excellent web framework
- **TextBlob**: For additional NLP utilities
- **Contributors**: Thanks to all contributors who helped build this API

---

**Built with ❤️ using FastAPI and Python**