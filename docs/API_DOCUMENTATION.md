# API Documentation

## Overview

The Sentiment and Stance Analysis API provides powerful text analysis capabilities through RESTful endpoints. This document provides comprehensive information about all available endpoints, request/response formats, and usage examples.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.example.com`

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Rate Limiting

No rate limiting is currently implemented, but it's recommended to implement it in production environments.

## Content Type

All requests must use `Content-Type: application/json` for POST requests.

## Response Format

All responses follow a consistent JSON format with appropriate HTTP status codes.

### Success Response Structure

```json
{
  "field1": "value1",
  "field2": "value2",
  "request_id": "req_1234567890",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Error Response Structure

```json
{
  "error": "Error Type",
  "message": "Detailed error message",
  "details": {
    "field": "additional_info"
  },
  "request_id": "req_1234567890",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Endpoints

### 1. Sentiment Analysis

Analyze the sentiment of English text.

#### Endpoint
```
POST /sentiment-analysis
```

#### Request Body

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| text | string | Yes | 1-5000 characters | The English text to analyze |

#### Example Request

```json
{
  "text": "I absolutely love this new smartphone! The camera quality is amazing and the battery life is excellent."
}
```

#### Response

| Field | Type | Description |
|-------|------|-------------|
| sentiment | string | Classification: "positive", "negative", or "normal" |
| confidence | number | Confidence score between 0.0 and 1.0 |
| request_id | string | Unique request identifier |
| timestamp | string | ISO 8601 timestamp |

#### Example Response

```json
{
  "sentiment": "positive",
  "confidence": 0.89,
  "request_id": "req_1704110400123",
  "timestamp": "2024-01-01T12:00:00.123Z"
}
```

#### Status Codes

- `200 OK`: Successful analysis
- `400 Bad Request`: Invalid input (empty text, too long, etc.)
- `422 Unprocessable Entity`: Processing error
- `500 Internal Server Error`: Server error

#### cURL Example

```bash
curl -X POST "http://localhost:8000/sentiment-analysis" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "This product exceeded my expectations!"
     }'
```

### 2. Stance Analysis

Analyze the stance of text towards a specific target entity.

#### Endpoint
```
POST /stance-analysis
```

#### Request Body

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| text | string | Yes | 1-5000 characters | The English text to analyze |
| target | string | Yes | 1-200 characters | The target entity to analyze stance towards |

#### Example Request

```json
{
  "text": "Apple has been making some questionable design decisions with their recent iPhone models, but their build quality remains top-notch.",
  "target": "Apple"
}
```

#### Response

| Field | Type | Description |
|-------|------|-------------|
| stance | string | Classification: "supportive", "opposing", or "neutral" |
| confidence | number | Confidence score between 0.0 and 1.0 |
| target | string | The target entity that was analyzed |
| request_id | string | Unique request identifier |
| timestamp | string | ISO 8601 timestamp |

#### Example Response

```json
{
  "stance": "neutral",
  "confidence": 0.65,
  "target": "Apple",
  "request_id": "req_1704110400124",
  "timestamp": "2024-01-01T12:00:00.124Z"
}
```

#### Status Codes

- `200 OK`: Successful analysis
- `400 Bad Request`: Invalid input (empty text/target, too long, etc.)
- `422 Unprocessable Entity`: Processing error
- `500 Internal Server Error`: Server error

#### cURL Example

```bash
curl -X POST "http://localhost:8000/stance-analysis" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Microsoft has been doing great work with their cloud services",
       "target": "Microsoft"
     }'
```

### 3. Health Check

Check the health status of the API.

#### Endpoint
```
GET /health
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| detailed | boolean | false | Include detailed health information |

#### Example Response

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "services": {
    "sentiment_service": "healthy",
    "stance_service": "healthy",
    "cache_service": "healthy"
  }
}
```

#### cURL Example

```bash
curl -X GET "http://localhost:8000/health?detailed=true"
```

### 4. Performance Metrics

Get detailed performance metrics for monitoring and optimization.

#### Endpoint
```
GET /metrics/performance
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| detailed | boolean | false | Include detailed request history |
| limit | integer | 100 | Maximum number of recent requests (1-1000) |

#### Example Response

```json
{
  "performance_stats": {
    "total_requests": 1250,
    "successful_requests": 1200,
    "failed_requests": 50,
    "success_rate_percent": 96.0,
    "cache_hits": 750,
    "cache_misses": 500,
    "cache_hit_rate_percent": 60.0,
    "avg_response_time_ms": 125.5,
    "min_response_time_ms": 15.2,
    "max_response_time_ms": 450.8,
    "p95_response_time_ms": 280.3,
    "p99_response_time_ms": 380.7,
    "avg_memory_usage_mb": 85.2,
    "peak_memory_usage_mb": 120.5,
    "window_start": "2024-01-01T11:00:00Z",
    "window_end": "2024-01-01T12:00:00Z"
  },
  "system_stats": {
    "cpu_percent": 15.5,
    "memory_percent": 45.2,
    "memory_available_mb": 2048.0,
    "disk_usage_percent": 65.8,
    "last_updated": 1704110400.123
  },
  "endpoint_stats": {
    "/sentiment-analysis": {
      "total_requests": 800,
      "successful_requests": 780,
      "failed_requests": 20,
      "avg_response_time_ms": 110.2,
      "cache_hits": 480
    },
    "/stance-analysis": {
      "total_requests": 450,
      "successful_requests": 420,
      "failed_requests": 30,
      "avg_response_time_ms": 150.8,
      "cache_hits": 270
    }
  }
}
```

### 5. Cache Metrics

Get cache performance statistics and management.

#### Endpoint
```
GET /metrics/cache
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| detailed | boolean | false | Include detailed cache entry information |

#### Example Response

```json
{
  "stats": {
    "size": 450,
    "max_size": 1000,
    "hits": 2850,
    "misses": 1200,
    "hit_rate_percent": 70.37,
    "evictions": 25,
    "expired_removals": 180,
    "manual_removals": 5,
    "total_requests": 4050,
    "default_ttl_seconds": 3600
  },
  "memory_usage": {
    "total_estimated_bytes": 2048576,
    "total_estimated_mb": 1.95,
    "entry_count": 450,
    "average_entry_size_bytes": 4552.39,
    "largest_entry_size_bytes": 8192,
    "smallest_entry_size_bytes": 1024
  }
}
```

### 6. System Metrics

Get current system performance metrics.

#### Endpoint
```
GET /metrics/system
```

#### Example Response

```json
{
  "system_metrics": {
    "cpu_percent": 12.5,
    "memory_percent": 42.8,
    "memory_available_mb": 2560.0,
    "disk_usage_percent": 68.2,
    "cpu_count": 8,
    "cpu_frequency_mhz": 2400.0,
    "system_boot_time": 1704024000.0,
    "load_average": [0.5, 0.8, 1.2],
    "last_updated": 1704110400.123
  },
  "timestamp": 1704110400.123
}
```

### 7. Cache Management

#### Clear Cache
```
POST /cache/clear
```

Clear all cached results.

#### Optimize Cache
```
POST /metrics/cache/optimize
```

Optimize cache performance by removing expired and least-used entries.

#### Reset Metrics
```
POST /metrics/reset
```

Reset performance statistics and optionally cache.

##### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| reset_cache | boolean | false | Also reset cache statistics |
| reset_performance | boolean | true | Reset performance statistics |

## Error Handling

### Error Types

1. **Validation Errors (400)**
   - Empty or invalid text
   - Text too long or too short
   - Invalid target entity

2. **Processing Errors (422)**
   - Text analysis failure
   - Service unavailable

3. **Server Errors (500)**
   - Internal server error
   - Service initialization failure

### Example Error Response

```json
{
  "error": "Validation Error",
  "message": "Text cannot be empty or contain only whitespace",
  "details": {
    "field": "text",
    "provided_length": 0,
    "min_length": 1,
    "max_length": 5000
  },
  "request_id": "req_1704110400125",
  "timestamp": "2024-01-01T12:00:00.125Z"
}
```

## Performance Considerations

### Response Times

| Endpoint | Typical Response Time | Cached Response Time |
|----------|----------------------|---------------------|
| Sentiment Analysis | 50-200ms | <10ms |
| Stance Analysis | 100-300ms | <10ms |
| Health Check | <5ms | N/A |
| Metrics | 10-50ms | N/A |

### Caching

The API implements intelligent caching:
- **Cache Key**: Based on text content (and target for stance analysis)
- **TTL**: 1 hour default
- **Eviction**: LRU (Least Recently Used)
- **Hit Rate**: Typically 60-80%

### Optimization Tips

1. **Reuse identical requests** - They will be served from cache
2. **Batch processing** - Send multiple requests concurrently
3. **Monitor metrics** - Use `/metrics/performance` to track performance
4. **Cache management** - Use `/metrics/cache/optimize` periodically

## SDK Examples

### Python SDK

```python
import requests
from typing import Dict, Any

class SentimentStanceAPI:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        response = self.session.post(
            f"{self.base_url}/sentiment-analysis",
            json={"text": text}
        )
        response.raise_for_status()
        return response.json()
    
    def analyze_stance(self, text: str, target: str) -> Dict[str, Any]:
        """Analyze stance towards target"""
        response = self.session.post(
            f"{self.base_url}/stance-analysis",
            json={"text": text, "target": target}
        )
        response.raise_for_status()
        return response.json()
    
    def get_health(self, detailed: bool = False) -> Dict[str, Any]:
        """Get API health status"""
        response = self.session.get(
            f"{self.base_url}/health",
            params={"detailed": detailed}
        )
        response.raise_for_status()
        return response.json()

# Usage
api = SentimentStanceAPI()

# Analyze sentiment
result = api.analyze_sentiment("I love this product!")
print(f"Sentiment: {result['sentiment']} ({result['confidence']:.2f})")

# Analyze stance
result = api.analyze_stance("Apple makes great phones", "Apple")
print(f"Stance: {result['stance']} ({result['confidence']:.2f})")
```

### JavaScript SDK

```javascript
class SentimentStanceAPI {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async analyzeSentiment(text) {
        const response = await fetch(`${this.baseUrl}/sentiment-analysis`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text }),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async analyzeStance(text, target) {
        const response = await fetch(`${this.baseUrl}/stance-analysis`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text, target }),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async getHealth(detailed = false) {
        const url = new URL(`${this.baseUrl}/health`);
        if (detailed) url.searchParams.set('detailed', 'true');
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
}

// Usage
const api = new SentimentStanceAPI();

// Analyze sentiment
api.analyzeSentiment("This is amazing!")
    .then(result => {
        console.log(`Sentiment: ${result.sentiment} (${result.confidence.toFixed(2)})`);
    })
    .catch(error => {
        console.error('Error:', error);
    });
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure the server is running
   - Check the correct port (default: 8000)

2. **Validation Errors**
   - Check text length (1-5000 characters)
   - Ensure text is not empty or whitespace-only
   - For stance analysis, ensure target is provided

3. **Slow Response Times**
   - Check system resources
   - Monitor cache hit rates
   - Consider optimizing cache

4. **Memory Issues**
   - Monitor memory usage via `/metrics/system`
   - Optimize cache size if needed
   - Check for memory leaks

### Debug Information

Enable debug logging by setting the log level:

```bash
export LOG_LEVEL=DEBUG
uvicorn main:app --log-level debug
```

### Support

For additional support:
- Check the interactive documentation at `/docs`
- Monitor system health at `/health`
- Review performance metrics at `/metrics/performance`
- Submit issues to the project repository