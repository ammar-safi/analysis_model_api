# Postman Guide - Sentiment and Stance Analysis API

Complete guide for testing the API using Postman.

## Table of Contents

- [Quick Setup](#quick-setup)
- [API Endpoints](#api-endpoints)
- [Sentiment Analysis](#sentiment-analysis)
- [Stance Analysis](#stance-analysis)
- [Health Check](#health-check)
- [Metrics Endpoints](#metrics-endpoints)
- [Cache Management](#cache-management)
- [Troubleshooting](#troubleshooting)

## Quick Setup

### 1. Base URL Configuration

Set up your base URL in Postman:

1. Open Postman
2. Create a new Collection called "Sentiment & Stance API"
3. Click on the collection → Variables tab
4. Add a variable:
   - **Variable**: `base_url`
   - **Initial Value**: `http://localhost:8000`
   - **Current Value**: `http://localhost:8000`

Now you can use `{{base_url}}` in all your requests.

### 2. Environment Setup (Optional)

Create environments for different deployments:

**Development Environment:**
- `base_url`: `http://localhost:8000`

**Production Environment:**
- `base_url`: `https://your-production-domain.com`

## API Endpoints

### Base Information

- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`
- **Response Format**: JSON

---

## Sentiment Analysis

Analyze the sentiment of English text (positive, negative, or neutral).

### Endpoint Details

- **Method**: `POST`
- **URL**: `{{base_url}}/sentiment-analysis`
- **Headers**: 
  - `Content-Type: application/json`

### Request Body

```json
{
  "text": "Your text here (1-5000 characters)"
}
```

### Postman Setup Steps

1. **Create New Request**
   - Click "New" → "HTTP Request"
   - Name it "Sentiment Analysis"
   - Save to your collection

2. **Configure Request**
   - Method: `POST`
   - URL: `{{base_url}}/sentiment-analysis`

3. **Set Headers**
   - Go to "Headers" tab
   - Add: `Content-Type: application/json`

4. **Set Body**
   - Go to "Body" tab
   - Select "raw"
   - Select "JSON" from dropdown
   - Enter:
   ```json
   {
     "text": "I love this product! It works great!"
   }
   ```

5. **Send Request**
   - Click "Send"

### Example Requests

#### Positive Sentiment
```json
{
  "text": "I absolutely love this new feature! It works perfectly and exceeded my expectations."
}
```

#### Negative Sentiment
```json
{
  "text": "This is terrible. I'm very disappointed with the quality and service."
}
```

#### Neutral Sentiment
```json
{
  "text": "The product arrived on time. It has standard features."
}
```

### Expected Response

**Status Code**: `200 OK`

```json
{
  "sentiment": "positive",
  "confidence": 0.92,
  "request_id": "req_abc123def456",
  "timestamp": "2026-02-07T00:00:00.000000"
}
```

**Response Fields:**
- `sentiment`: One of "positive", "negative", or "normal"
- `confidence`: Float between 0.0 and 1.0
- `request_id`: Unique identifier for the request
- `timestamp`: ISO 8601 timestamp

---

## Stance Analysis

Analyze the stance towards a specific target (supportive, opposing, or neutral).

### Endpoint Details

- **Method**: `POST`
- **URL**: `{{base_url}}/stance-analysis`
- **Headers**: 
  - `Content-Type: application/json`

### Request Body

```json
{
  "text": "Your text here (1-5000 characters)",
  "target": "Target entity (1-200 characters)"
}
```

### Postman Setup Steps

1. **Create New Request**
   - Click "New" → "HTTP Request"
   - Name it "Stance Analysis"
   - Save to your collection

2. **Configure Request**
   - Method: `POST`
   - URL: `{{base_url}}/stance-analysis`

3. **Set Headers**
   - Go to "Headers" tab
   - Add: `Content-Type: application/json`

4. **Set Body**
   - Go to "Body" tab
   - Select "raw"
   - Select "JSON" from dropdown
   - Enter:
   ```json
   {
     "text": "Apple makes innovative products that change the industry",
     "target": "Apple"
   }
   ```

5. **Send Request**
   - Click "Send"

### Example Requests

#### Supportive Stance
```json
{
  "text": "Microsoft has been doing an excellent job with their cloud services. Azure is fantastic!",
  "target": "Microsoft"
}
```

#### Opposing Stance
```json
{
  "text": "I strongly disagree with Google's recent privacy policies. They are concerning.",
  "target": "Google"
}
```

#### Neutral Stance
```json
{
  "text": "Amazon is a large e-commerce company founded in 1994.",
  "target": "Amazon"
}
```

### Expected Response

**Status Code**: `200 OK`

```json
{
  "stance": "مؤيد",
  "confidence": 0.85,
  "target": "Apple",
  "request_id": "req_xyz789abc123",
  "timestamp": "2026-02-07T00:00:00.000000"
}
```

**Response Fields:**
- `stance`: One of "مؤيد" (supportive), "معارض" (opposing), or "محايد" (neutral)
- `confidence`: Float between 0.0 and 1.0
- `target`: The target entity that was analyzed
- `request_id`: Unique identifier for the request
- `timestamp`: ISO 8601 timestamp

---

## Health Check

Check if the API is running and healthy.

### Endpoint Details

- **Method**: `GET`
- **URL**: `{{base_url}}/health`

### Postman Setup

1. **Create New Request**
   - Method: `GET`
   - URL: `{{base_url}}/health`
   - No body or special headers needed

2. **Send Request**

### Expected Response

**Status Code**: `200 OK`

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-07T00:00:00.000000",
  "services": {
    "sentiment_service": "healthy",
    "stance_service": "healthy",
    "cache_service": "healthy"
  },
  "uptime_seconds": 3600.5
}
```

---

## Metrics Endpoints

### Performance Metrics

Get detailed performance statistics.

- **Method**: `GET`
- **URL**: `{{base_url}}/metrics/performance`
- **Query Parameters** (optional):
  - `detailed=true` - Include detailed metrics
  - `limit=100` - Limit number of recent requests

**Example URL**: `{{base_url}}/metrics/performance?detailed=true&limit=50`

### Cache Statistics

Get cache performance data.

- **Method**: `GET`
- **URL**: `{{base_url}}/metrics/cache`
- **Query Parameters** (optional):
  - `detailed=true` - Include detailed cache info

**Example URL**: `{{base_url}}/metrics/cache?detailed=true`

### System Metrics

Get system resource usage.

- **Method**: `GET`
- **URL**: `{{base_url}}/metrics/system`

---

## Cache Management

### Get Cache Stats

- **Method**: `GET`
- **URL**: `{{base_url}}/cache/stats`

### Clear Cache

- **Method**: `POST`
- **URL**: `{{base_url}}/cache/clear`
- **Body**: None required

### Optimize Cache

- **Method**: `POST`
- **URL**: `{{base_url}}/metrics/cache/optimize`
- **Body**: None required

---

## Error Responses

### Validation Error (400)

When input validation fails:

```json
{
  "error": "ValidationError",
  "message": "Invalid input data",
  "details": {
    "field": "text",
    "error": "Text must be between 1 and 5000 characters"
  },
  "request_id": "err_abc123",
  "timestamp": "2026-02-07T00:00:00.000000"
}
```

### Processing Error (422)

When processing fails:

```json
{
  "error": "ProcessingError",
  "message": "Failed to analyze sentiment. Please try again.",
  "details": {
    "request_id": "req_xyz789"
  },
  "request_id": "err_def456",
  "timestamp": "2026-02-07T00:00:00.000000"
}
```

### Server Error (500)

When an internal error occurs:

```json
{
  "error": "InternalServerError",
  "message": "An unexpected error occurred",
  "request_id": "err_ghi789",
  "timestamp": "2026-02-07T00:00:00.000000"
}
```

---

## Postman Collection

### Import Pre-configured Collection

You can create a Postman collection with all endpoints:

1. **Create Collection**
   - Click "New" → "Collection"
   - Name: "Sentiment & Stance API"

2. **Add Requests**
   - Add all the requests mentioned above
   - Organize into folders:
     - Analysis (Sentiment, Stance)
     - Monitoring (Health, Metrics)
     - Cache Management

3. **Export Collection**
   - Click "..." on collection → "Export"
   - Save as JSON file
   - Share with team

### Collection Variables

Set these variables in your collection:

| Variable | Value | Description |
|----------|-------|-------------|
| `base_url` | `http://localhost:8000` | API base URL |
| `content_type` | `application/json` | Content type header |

---

## Testing Workflow

### 1. Basic Health Check

```
GET {{base_url}}/health
```

Verify the API is running.

### 2. Test Sentiment Analysis

```
POST {{base_url}}/sentiment-analysis
Body: {"text": "I love this!"}
```

### 3. Test Stance Analysis

```
POST {{base_url}}/stance-analysis
Body: {"text": "Apple makes great products", "target": "Apple"}
```

### 4. Check Performance

```
GET {{base_url}}/metrics/performance?detailed=true
```

### 5. View Cache Stats

```
GET {{base_url}}/cache/stats
```

---

## Advanced Features

### Using Pre-request Scripts

Add this to your collection's Pre-request Script to log requests:

```javascript
console.log('Request to:', pm.request.url.toString());
console.log('Method:', pm.request.method);
console.log('Body:', pm.request.body.raw);
```

### Using Tests

Add this to your request's Tests tab to validate responses:

```javascript
// Check status code
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Check response time
pm.test("Response time is less than 500ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(500);
});

// Check response structure
pm.test("Response has required fields", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('request_id');
    pm.expect(jsonData).to.have.property('timestamp');
});

// For sentiment analysis
pm.test("Sentiment is valid", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.sentiment).to.be.oneOf(['positive', 'negative', 'normal']);
    pm.expect(jsonData.confidence).to.be.within(0, 1);
});
```

### Environment Variables

Create different environments:

**Development:**
```json
{
  "base_url": "http://localhost:8000",
  "timeout": "5000"
}
```

**Production:**
```json
{
  "base_url": "https://api.production.com",
  "timeout": "10000"
}
```

---

## Troubleshooting

### Connection Refused

**Error**: `Could not get any response`

**Solution**:
1. Verify the API is running: `curl http://localhost:8000/health`
2. Check the port number is correct (default: 8000)
3. Ensure no firewall is blocking the connection

### 404 Not Found

**Error**: `404 Not Found`

**Solution**:
1. Check the endpoint URL is correct
2. Verify the API version matches
3. Check for typos in the URL

### 400 Bad Request

**Error**: `400 Bad Request` or `422 Unprocessable Entity`

**Solution**:
1. Verify JSON syntax is correct
2. Check required fields are present
3. Ensure text length is within limits (1-5000 characters)
4. For stance analysis, ensure target is provided

### Timeout

**Error**: Request timeout

**Solution**:
1. Increase timeout in Postman settings
2. Check server performance
3. Try with shorter text

---

## Quick Reference

### Sentiment Analysis
```
POST {{base_url}}/sentiment-analysis
Content-Type: application/json

{
  "text": "Your text here"
}
```

### Stance Analysis
```
POST {{base_url}}/stance-analysis
Content-Type: application/json

{
  "text": "Your text here",
  "target": "Target entity"
}
```

### Health Check
```
GET {{base_url}}/health
```

### Performance Metrics
```
GET {{base_url}}/metrics/performance?detailed=true
```

---

## Additional Resources

- **Interactive Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **API Documentation**: See `docs/API_DOCUMENTATION.md`
- **Deployment Guide**: See `docs/DEPLOYMENT_GUIDE.md`

---

**Happy Testing! 🚀**
