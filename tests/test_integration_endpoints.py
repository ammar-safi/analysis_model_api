"""
Integration tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import patch, Mock

from main import app
from app.services.sentiment_service import SentimentResult
from app.services.stance_service import StanceResult


class TestSentimentAnalysisEndpoint:
    """Integration tests for sentiment analysis endpoint"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        self.endpoint = "/sentiment-analysis"
    
    def test_sentiment_analysis_positive_text(self):
        """Test sentiment analysis endpoint with positive text"""
        request_data = {
            "text": "I love this product! It's amazing and wonderful."
        }
        
        response = self.client.post(self.endpoint, json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "sentiment" in data
        assert "confidence" in data
        assert "request_id" in data
        assert "timestamp" in data
        
        # Verify data types and values
        assert data["sentiment"] in ["positive", "negative", "normal"]
        assert isinstance(data["confidence"], float)
        assert 0.0 <= data["confidence"] <= 1.0
        assert isinstance(data["request_id"], str)
        assert len(data["request_id"]) > 0
        
        # Verify timestamp format
        timestamp = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
        assert isinstance(timestamp, datetime)
    
    def test_sentiment_analysis_negative_text(self):
        """Test sentiment analysis endpoint with negative text"""
        request_data = {
            "text": "I hate this product! It's terrible and awful."
        }
        
        response = self.client.post(self.endpoint, json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["sentiment"] in ["positive", "negative", "normal"]
        assert isinstance(data["confidence"], float)
        assert 0.0 <= data["confidence"] <= 1.0
    
    def test_sentiment_analysis_neutral_text(self):
        """Test sentiment analysis endpoint with neutral text"""
        request_data = {
            "text": "This is a product. It exists in the market."
        }
        
        response = self.client.post(self.endpoint, json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["sentiment"] in ["positive", "negative", "normal"]
        assert isinstance(data["confidence"], float)
        assert 0.0 <= data["confidence"] <= 1.0
    
    def test_sentiment_analysis_empty_text(self):
        """Test sentiment analysis endpoint with empty text"""
        request_data = {
            "text": ""
        }
        
        response = self.client.post(self.endpoint, json=request_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        
        assert "error" in data
        assert "message" in data
        assert "request_id" in data
        assert "timestamp" in data
    
    def test_sentiment_analysis_whitespace_only_text(self):
        """Test sentiment analysis endpoint with whitespace-only text"""
        request_data = {
            "text": "   \n\t  "
        }
        
        response = self.client.post(self.endpoint, json=request_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        
        assert "error" in data
        assert "whitespace" in data["message"].lower()
    
    def test_sentiment_analysis_too_long_text(self):
        """Test sentiment analysis endpoint with text that's too long"""
        request_data = {
            "text": "This is a test. " * 400  # Over 5000 characters
        }
        
        response = self.client.post(self.endpoint, json=request_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        
        assert "error" in data
        assert "message" in data
    
    def test_sentiment_analysis_missing_text_field(self):
        """Test sentiment analysis endpoint with missing text field"""
        request_data = {}
        
        response = self.client.post(self.endpoint, json=request_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        
        assert "error" in data
        assert "message" in data
    
    def test_sentiment_analysis_invalid_json(self):
        """Test sentiment analysis endpoint with invalid JSON"""
        response = self.client.post(
            self.endpoint,
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_sentiment_analysis_wrong_content_type(self):
        """Test sentiment analysis endpoint with wrong content type"""
        response = self.client.post(
            self.endpoint,
            data="text=test",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 422
    
    def test_sentiment_analysis_get_method_not_allowed(self):
        """Test sentiment analysis endpoint with GET method (should not be allowed)"""
        response = self.client.get(self.endpoint)
        
        assert response.status_code == 405  # Method not allowed
    
    @patch('app.routers.sentiment.SentimentService')
    def test_sentiment_analysis_service_error(self, mock_service_class):
        """Test sentiment analysis endpoint when service raises an error"""
        mock_service = Mock()
        mock_service.analyze_sentiment.side_effect = Exception("Service error")
        mock_service_class.return_value = mock_service
        
        request_data = {
            "text": "This is a test"
        }
        
        response = self.client.post(self.endpoint, json=request_data)
        
        assert response.status_code == 422  # Processing error
        data = response.json()
        
        assert "error" in data
        assert "message" in data
        assert "request_id" in data


class TestStanceAnalysisEndpoint:
    """Integration tests for stance analysis endpoint"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        self.endpoint = "/stance-analysis"
    
    def test_stance_analysis_supportive_text(self):
        """Test stance analysis endpoint with supportive text"""
        request_data = {
            "text": "I love Apple products! They make amazing phones and computers.",
            "target": "Apple"
        }
        
        response = self.client.post(self.endpoint, json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "stance" in data
        assert "confidence" in data
        assert "target" in data
        assert "request_id" in data
        assert "timestamp" in data
        
        # Verify data types and values
        assert data["stance"] in ["supportive", "opposing", "neutral"]
        assert isinstance(data["confidence"], float)
        assert 0.0 <= data["confidence"] <= 1.0
        assert data["target"] == "Apple"
        assert isinstance(data["request_id"], str)
        assert len(data["request_id"]) > 0
        
        # Verify timestamp format
        timestamp = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
        assert isinstance(timestamp, datetime)
    
    def test_stance_analysis_opposing_text(self):
        """Test stance analysis endpoint with opposing text"""
        request_data = {
            "text": "I hate Microsoft products! They are terrible and overpriced.",
            "target": "Microsoft"
        }
        
        response = self.client.post(self.endpoint, json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["stance"] in ["supportive", "opposing", "neutral"]
        assert isinstance(data["confidence"], float)
        assert 0.0 <= data["confidence"] <= 1.0
        assert data["target"] == "Microsoft"
    
    def test_stance_analysis_neutral_text(self):
        """Test stance analysis endpoint with neutral text"""
        request_data = {
            "text": "Google is a technology company based in California.",
            "target": "Google"
        }
        
        response = self.client.post(self.endpoint, json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["stance"] in ["supportive", "opposing", "neutral"]
        assert isinstance(data["confidence"], float)
        assert 0.0 <= data["confidence"] <= 1.0
        assert data["target"] == "Google"
    
    def test_stance_analysis_target_not_found(self):
        """Test stance analysis endpoint when target is not found in text"""
        request_data = {
            "text": "This is a great product from a wonderful company.",
            "target": "Apple"
        }
        
        response = self.client.post(self.endpoint, json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should still return a response, likely neutral with low confidence
        assert data["stance"] in ["supportive", "opposing", "neutral"]
        assert isinstance(data["confidence"], float)
        assert data["target"] == "Apple"
    
    def test_stance_analysis_empty_text(self):
        """Test stance analysis endpoint with empty text"""
        request_data = {
            "text": "",
            "target": "Apple"
        }
        
        response = self.client.post(self.endpoint, json=request_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        
        assert "error" in data
        assert "message" in data
        assert "request_id" in data
    
    def test_stance_analysis_empty_target(self):
        """Test stance analysis endpoint with empty target"""
        request_data = {
            "text": "This is a test",
            "target": ""
        }
        
        response = self.client.post(self.endpoint, json=request_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        
        assert "error" in data
        assert "message" in data
    
    def test_stance_analysis_whitespace_only_text(self):
        """Test stance analysis endpoint with whitespace-only text"""
        request_data = {
            "text": "   \n\t  ",
            "target": "Apple"
        }
        
        response = self.client.post(self.endpoint, json=request_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        
        assert "error" in data
        assert "whitespace" in data["message"].lower()
    
    def test_stance_analysis_whitespace_only_target(self):
        """Test stance analysis endpoint with whitespace-only target"""
        request_data = {
            "text": "This is a test",
            "target": "   \n\t  "
        }
        
        response = self.client.post(self.endpoint, json=request_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        
        assert "error" in data
        assert "target" in data["message"].lower()
    
    def test_stance_analysis_too_long_text(self):
        """Test stance analysis endpoint with text that's too long"""
        request_data = {
            "text": "Apple is great! " * 400,  # Over 5000 characters
            "target": "Apple"
        }
        
        response = self.client.post(self.endpoint, json=request_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        
        assert "error" in data
        assert "message" in data
    
    def test_stance_analysis_too_long_target(self):
        """Test stance analysis endpoint with target that's too long"""
        request_data = {
            "text": "This is a test",
            "target": "A" * 250  # Over 200 characters
        }
        
        response = self.client.post(self.endpoint, json=request_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        
        assert "error" in data
        assert "message" in data
    
    def test_stance_analysis_missing_fields(self):
        """Test stance analysis endpoint with missing fields"""
        # Missing text
        response = self.client.post(self.endpoint, json={"target": "Apple"})
        assert response.status_code == 422
        
        # Missing target
        response = self.client.post(self.endpoint, json={"text": "Test"})
        assert response.status_code == 422
        
        # Missing both
        response = self.client.post(self.endpoint, json={})
        assert response.status_code == 422
    
    def test_stance_analysis_get_method_not_allowed(self):
        """Test stance analysis endpoint with GET method (should not be allowed)"""
        response = self.client.get(self.endpoint)
        
        assert response.status_code == 405  # Method not allowed
    
    @patch('app.routers.stance.StanceService')
    def test_stance_analysis_service_error(self, mock_service_class):
        """Test stance analysis endpoint when service raises an error"""
        mock_service = Mock()
        mock_service.analyze_stance.side_effect = Exception("Service error")
        mock_service_class.return_value = mock_service
        
        request_data = {
            "text": "This is a test",
            "target": "Apple"
        }
        
        response = self.client.post(self.endpoint, json=request_data)
        
        assert response.status_code == 422  # Processing error
        data = response.json()
        
        assert "error" in data
        assert "message" in data
        assert "request_id" in data


class TestHealthEndpoint:
    """Integration tests for health check endpoint"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        self.endpoint = "/health"
    
    def test_health_check_success(self):
        """Test health check endpoint returns healthy status"""
        response = self.client.get(self.endpoint)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert "services" in data
        assert "uptime_seconds" in data
        
        # Verify data types and values
        assert data["status"] in ["healthy", "unhealthy"]
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0
        assert isinstance(data["services"], dict)
        assert isinstance(data["uptime_seconds"], (int, float))
        assert data["uptime_seconds"] >= 0
        
        # Verify timestamp format
        timestamp = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
        assert isinstance(timestamp, datetime)
        
        # Verify services are checked
        assert "sentiment_service" in data["services"]
        assert "stance_service" in data["services"]
        assert data["services"]["sentiment_service"] in ["healthy", "unhealthy"]
        assert data["services"]["stance_service"] in ["healthy", "unhealthy"]
    
    def test_health_check_post_method_not_allowed(self):
        """Test health check endpoint with POST method (should not be allowed)"""
        response = self.client.post(self.endpoint, json={})
        
        assert response.status_code == 405  # Method not allowed
    
    @patch('app.routers.health.SentimentService')
    def test_health_check_sentiment_service_unhealthy(self, mock_service_class):
        """Test health check when sentiment service is unhealthy"""
        mock_service = Mock()
        mock_service.analyze_sentiment.side_effect = Exception("Service error")
        mock_service_class.return_value = mock_service
        
        response = self.client.get(self.endpoint)
        
        assert response.status_code == 200  # Health endpoint should still return 200
        data = response.json()
        
        assert data["status"] == "unhealthy"
        assert data["services"]["sentiment_service"] == "unhealthy"
    
    @patch('app.routers.health.StanceService')
    def test_health_check_stance_service_unhealthy(self, mock_service_class):
        """Test health check when stance service is unhealthy"""
        mock_service = Mock()
        mock_service.analyze_stance.side_effect = Exception("Service error")
        mock_service_class.return_value = mock_service
        
        response = self.client.get(self.endpoint)
        
        assert response.status_code == 200  # Health endpoint should still return 200
        data = response.json()
        
        assert data["status"] == "unhealthy"
        assert data["services"]["stance_service"] == "unhealthy"
    
    @patch('app.routers.health.SentimentService')
    @patch('app.routers.health.StanceService')
    def test_health_check_all_services_unhealthy(self, mock_stance_service_class, mock_sentiment_service_class):
        """Test health check when all services are unhealthy"""
        mock_sentiment_service = Mock()
        mock_sentiment_service.analyze_sentiment.side_effect = Exception("Service error")
        mock_sentiment_service_class.return_value = mock_sentiment_service
        
        mock_stance_service = Mock()
        mock_stance_service.analyze_stance.side_effect = Exception("Service error")
        mock_stance_service_class.return_value = mock_stance_service
        
        response = self.client.get(self.endpoint)
        
        assert response.status_code == 200  # Health endpoint should still return 200
        data = response.json()
        
        assert data["status"] == "unhealthy"
        assert data["services"]["sentiment_service"] == "unhealthy"
        assert data["services"]["stance_service"] == "unhealthy"


class TestRootEndpoint:
    """Integration tests for root endpoint"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint returns welcome message"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0


class TestErrorHandling:
    """Integration tests for error handling across endpoints"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
    
    def test_404_not_found(self):
        """Test 404 error for non-existent endpoints"""
        response = self.client.get("/non-existent-endpoint")
        
        assert response.status_code == 404
    
    def test_405_method_not_allowed_sentiment(self):
        """Test 405 error for wrong HTTP method on sentiment endpoint"""
        response = self.client.get("/sentiment-analysis")
        
        assert response.status_code == 405
    
    def test_405_method_not_allowed_stance(self):
        """Test 405 error for wrong HTTP method on stance endpoint"""
        response = self.client.get("/stance-analysis")
        
        assert response.status_code == 405
    
    def test_422_validation_error_format(self):
        """Test that validation errors have consistent format"""
        response = self.client.post("/sentiment-analysis", json={})
        
        assert response.status_code == 422
        data = response.json()
        
        # Check error response format
        assert "error" in data
        assert "message" in data
        assert "request_id" in data
        assert "timestamp" in data
        assert "details" in data
        
        # Verify timestamp format
        timestamp = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
        assert isinstance(timestamp, datetime)


class TestConcurrentRequests:
    """Integration tests for concurrent request handling"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
    
    def test_concurrent_sentiment_requests(self):
        """Test handling multiple concurrent sentiment requests"""
        import concurrent.futures
        import threading
        
        def make_request():
            request_data = {
                "text": f"This is a test from thread {threading.current_thread().ident}"
            }
            return self.client.post("/sentiment-analysis", json=request_data)
        
        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "sentiment" in data
            assert "request_id" in data
        
        # All request IDs should be unique
        request_ids = [response.json()["request_id"] for response in responses]
        assert len(set(request_ids)) == len(request_ids)
    
    def test_concurrent_stance_requests(self):
        """Test handling multiple concurrent stance requests"""
        import concurrent.futures
        import threading
        
        def make_request():
            request_data = {
                "text": f"Apple is great from thread {threading.current_thread().ident}",
                "target": "Apple"
            }
            return self.client.post("/stance-analysis", json=request_data)
        
        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "stance" in data
            assert "request_id" in data
        
        # All request IDs should be unique
        request_ids = [response.json()["request_id"] for response in responses]
        assert len(set(request_ids)) == len(request_ids)