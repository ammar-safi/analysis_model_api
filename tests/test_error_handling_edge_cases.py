"""
Tests for error handling and edge cases
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json

from main import app
from app.services.sentiment_service import SentimentService, SentimentResult
from app.services.stance_service import StanceService, StanceResult
from app.utils.text_processor import TextProcessor


class TestValidationErrors:
    """Test validation error handling"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
    
    def test_sentiment_analysis_text_too_short(self):
        """Test sentiment analysis with text that's too short (below min_length)"""
        # Note: Pydantic validation requires min_length=1, but our service handles very short texts
        request_data = {"text": ""}
        
        response = self.client.post("/sentiment-analysis", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert "message" in data
        assert "request_id" in data
        assert "timestamp" in data
    
    def test_sentiment_analysis_text_too_long(self):
        """Test sentiment analysis with text that exceeds max_length"""
        long_text = "A" * 5001  # Exceeds 5000 character limit
        request_data = {"text": long_text}
        
        response = self.client.post("/sentiment-analysis", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert "validation" in data["error"].lower() or "length" in data["message"].lower()
    
    def test_stance_analysis_text_too_short(self):
        """Test stance analysis with text that's too short"""
        request_data = {"text": "", "target": "Apple"}
        
        response = self.client.post("/stance-analysis", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert "message" in data
    
    def test_stance_analysis_text_too_long(self):
        """Test stance analysis with text that exceeds max_length"""
        long_text = "Apple is great! " * 400  # Exceeds 5000 character limit
        request_data = {"text": long_text, "target": "Apple"}
        
        response = self.client.post("/stance-analysis", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
    
    def test_stance_analysis_target_too_short(self):
        """Test stance analysis with target that's too short"""
        request_data = {"text": "This is a test", "target": ""}
        
        response = self.client.post("/stance-analysis", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
    
    def test_stance_analysis_target_too_long(self):
        """Test stance analysis with target that exceeds max_length"""
        long_target = "A" * 201  # Exceeds 200 character limit
        request_data = {"text": "This is a test", "target": long_target}
        
        response = self.client.post("/stance-analysis", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
    
    def test_invalid_json_format(self):
        """Test endpoints with invalid JSON format"""
        invalid_json = '{"text": "test", "invalid": }'
        
        response = self.client.post(
            "/sentiment-analysis",
            data=invalid_json,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self):
        """Test endpoints with missing required fields"""
        # Sentiment analysis missing text
        response = self.client.post("/sentiment-analysis", json={})
        assert response.status_code == 422
        
        # Stance analysis missing text
        response = self.client.post("/stance-analysis", json={"target": "Apple"})
        assert response.status_code == 422
        
        # Stance analysis missing target
        response = self.client.post("/stance-analysis", json={"text": "Test"})
        assert response.status_code == 422
    
    def test_wrong_field_types(self):
        """Test endpoints with wrong field types"""
        # Text as number
        response = self.client.post("/sentiment-analysis", json={"text": 123})
        assert response.status_code == 422
        
        # Text as array
        response = self.client.post("/sentiment-analysis", json={"text": ["test"]})
        assert response.status_code == 422
        
        # Target as number
        response = self.client.post("/stance-analysis", json={"text": "test", "target": 123})
        assert response.status_code == 422


class TestEdgeCasesText:
    """Test edge cases with different types of text input"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
    
    def test_sentiment_analysis_only_whitespace(self):
        """Test sentiment analysis with only whitespace characters"""
        whitespace_texts = [
            "   ",
            "\n\n\n",
            "\t\t\t",
            "   \n\t  \r  ",
            " " * 100
        ]
        
        for text in whitespace_texts:
            request_data = {"text": text}
            response = self.client.post("/sentiment-analysis", json=request_data)
            
            assert response.status_code == 422
            data = response.json()
            assert "whitespace" in data["message"].lower()
    
    def test_stance_analysis_only_whitespace(self):
        """Test stance analysis with only whitespace characters"""
        # Whitespace text
        request_data = {"text": "   \n\t  ", "target": "Apple"}
        response = self.client.post("/stance-analysis", json=request_data)
        assert response.status_code == 422
        
        # Whitespace target
        request_data = {"text": "This is a test", "target": "   \n\t  "}
        response = self.client.post("/stance-analysis", json=request_data)
        assert response.status_code == 422
    
    def test_sentiment_analysis_special_characters(self):
        """Test sentiment analysis with special characters and symbols"""
        special_texts = [
            "!@#$%^&*()_+{}|:<>?[]\\;'\",./ good",
            "😀😃😄😁😆😅😂🤣☺️😊",
            "Ñoño piñata jalapeño",
            "Здравствуй мир",  # Non-English text
            "🚀 This is amazing! 🎉",
            "Price: $99.99 - Great deal!!!",
            "Email: test@example.com Phone: +1-555-0123"
        ]
        
        for text in special_texts:
            request_data = {"text": text}
            response = self.client.post("/sentiment-analysis", json=request_data)
            
            # Should handle gracefully, either succeed or return appropriate error
            assert response.status_code in [200, 422]
            
            if response.status_code == 200:
                data = response.json()
                assert "sentiment" in data
                assert data["sentiment"] in ["positive", "negative", "normal"]
    
    def test_stance_analysis_special_characters(self):
        """Test stance analysis with special characters"""
        special_cases = [
            {"text": "!@#$%^&*() Apple is good !@#$%^&*()", "target": "Apple"},
            {"text": "😀 Apple 😃 is 😄 great 😁", "target": "Apple"},
            {"text": "Apple's iPhone costs $999.99", "target": "Apple"},
            {"text": "Contact Apple at support@apple.com", "target": "Apple"},
            {"text": "Apple Inc. (NASDAQ: AAPL) stock", "target": "Apple Inc."}
        ]
        
        for case in special_cases:
            response = self.client.post("/stance-analysis", json=case)
            
            # Should handle gracefully
            assert response.status_code in [200, 422]
            
            if response.status_code == 200:
                data = response.json()
                assert "stance" in data
                assert data["stance"] in ["supportive", "opposing", "neutral"]
    
    def test_sentiment_analysis_very_short_meaningful_text(self):
        """Test sentiment analysis with very short but meaningful text"""
        short_texts = [
            "Good",
            "Bad",
            "OK",
            "Wow!",
            "Meh",
            "Love it",
            "Hate it",
            "So-so"
        ]
        
        for text in short_texts:
            request_data = {"text": text}
            response = self.client.post("/sentiment-analysis", json=request_data)
            
            # Should succeed but might have low confidence
            assert response.status_code == 200
            data = response.json()
            assert "sentiment" in data
            assert data["sentiment"] in ["positive", "negative", "normal"]
            assert isinstance(data["confidence"], float)
    
    def test_stance_analysis_target_not_in_text(self):
        """Test stance analysis when target is not mentioned in text"""
        request_data = {
            "text": "This is a great product from a wonderful company with excellent service.",
            "target": "Apple"
        }
        
        response = self.client.post("/stance-analysis", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["stance"] == "neutral"  # Should be neutral when target not found
        assert data["confidence"] <= 0.2  # Should have low confidence
    
    def test_stance_analysis_multiple_targets_in_text(self):
        """Test stance analysis with multiple mentions of target"""
        request_data = {
            "text": "Apple makes great phones. I love Apple products. Apple is innovative and Apple customer service is excellent.",
            "target": "Apple"
        }
        
        response = self.client.post("/stance-analysis", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "stance" in data
        # Should have higher confidence due to multiple mentions
        assert data["confidence"] > 0.3
    
    def test_sentiment_analysis_mixed_sentiments(self):
        """Test sentiment analysis with mixed sentiments in same text"""
        mixed_texts = [
            "I love the design but hate the price",
            "Great product, terrible customer service",
            "Amazing features, but too expensive and complicated",
            "Good quality, bad delivery, excellent packaging"
        ]
        
        for text in mixed_texts:
            request_data = {"text": text}
            response = self.client.post("/sentiment-analysis", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "sentiment" in data
            # Mixed sentiments might result in normal classification
            assert data["sentiment"] in ["positive", "negative", "normal"]
    
    def test_stance_analysis_conflicting_stances(self):
        """Test stance analysis with conflicting stances in same text"""
        request_data = {
            "text": "Apple makes great phones but I hate their pricing policy. Apple innovation is amazing but Apple customer service is terrible.",
            "target": "Apple"
        }
        
        response = self.client.post("/stance-analysis", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "stance" in data
        # Conflicting stances might result in neutral or lower confidence
        assert data["stance"] in ["supportive", "opposing", "neutral"]


class TestProcessingErrors:
    """Test processing error handling"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
    
    @patch('app.services.sentiment_service.SentimentService.analyze_sentiment')
    def test_sentiment_service_processing_error(self, mock_analyze):
        """Test handling of processing errors in sentiment service"""
        mock_analyze.side_effect = Exception("Internal processing error")
        
        request_data = {"text": "This is a test"}
        response = self.client.post("/sentiment-analysis", json=request_data)
        
        assert response.status_code == 422  # Processing error
        data = response.json()
        assert "error" in data
        assert "ProcessingError" in data["error"]
        assert "request_id" in data
        assert "timestamp" in data
    
    @patch('app.services.stance_service.StanceService.analyze_stance')
    def test_stance_service_processing_error(self, mock_analyze):
        """Test handling of processing errors in stance service"""
        mock_analyze.side_effect = Exception("Internal processing error")
        
        request_data = {"text": "This is a test", "target": "Apple"}
        response = self.client.post("/stance-analysis", json=request_data)
        
        assert response.status_code == 422  # Processing error
        data = response.json()
        assert "error" in data
        assert "ProcessingError" in data["error"]
        assert "request_id" in data
    
    @patch('app.services.sentiment_service.SentimentService.__init__')
    def test_sentiment_service_initialization_error(self, mock_init):
        """Test handling of service initialization errors"""
        mock_init.side_effect = Exception("Failed to initialize service")
        
        request_data = {"text": "This is a test"}
        response = self.client.post("/sentiment-analysis", json=request_data)
        
        assert response.status_code == 500  # Internal server error
    
    @patch('app.services.stance_service.StanceService.__init__')
    def test_stance_service_initialization_error(self, mock_init):
        """Test handling of service initialization errors"""
        mock_init.side_effect = Exception("Failed to initialize service")
        
        request_data = {"text": "This is a test", "target": "Apple"}
        response = self.client.post("/stance-analysis", json=request_data)
        
        assert response.status_code == 500  # Internal server error


class TestServiceEdgeCases:
    """Test edge cases in service layer"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.sentiment_service = SentimentService()
        self.stance_service = StanceService()
        self.text_processor = TextProcessor()
    
    def test_sentiment_service_none_input(self):
        """Test sentiment service with None input"""
        result = self.sentiment_service.analyze_sentiment(None)
        
        assert isinstance(result, SentimentResult)
        assert result.sentiment == 'normal'
        assert result.confidence == 0.1
        assert result.fallback_used is True
        assert result.warning is not None
    
    def test_stance_service_none_inputs(self):
        """Test stance service with None inputs"""
        # None text
        result = self.stance_service.analyze_stance(None, "Apple")
        assert result.stance == 'neutral'
        assert result.fallback_used is True
        
        # None target
        result = self.stance_service.analyze_stance("Test", None)
        assert result.stance == 'neutral'
        assert result.fallback_used is True
        
        # Both None
        result = self.stance_service.analyze_stance(None, None)
        assert result.stance == 'neutral'
        assert result.fallback_used is True
    
    def test_sentiment_service_extremely_long_text(self):
        """Test sentiment service with extremely long text"""
        # Create text longer than max limit
        long_text = "This is a great product! " * 1000  # Much longer than 5000 chars
        result = self.sentiment_service.analyze_sentiment(long_text)
        
        assert isinstance(result, SentimentResult)
        assert result.fallback_used is True
        assert "truncated" in result.warning.lower()
        assert result.confidence < 1.0  # Should be reduced due to truncation
    
    def test_stance_service_extremely_long_text(self):
        """Test stance service with extremely long text"""
        long_text = "Apple is great! " * 1000  # Much longer than 5000 chars
        result = self.stance_service.analyze_stance(long_text, "Apple")
        
        assert isinstance(result, StanceResult)
        assert result.fallback_used is True
        assert "truncated" in result.warning.lower()
    
    def test_sentiment_service_high_symbol_ratio(self):
        """Test sentiment service with high symbol to text ratio"""
        symbol_heavy_text = "!@#$%^&*()_+{}|:<>?[]\\;'\",./ good !@#$%^&*()_+{}|:<>?[]\\;'\",./"
        result = self.sentiment_service.analyze_sentiment(symbol_heavy_text)
        
        assert isinstance(result, SentimentResult)
        assert result.fallback_used is True
        assert "symbol ratio" in result.warning.lower()
        assert result.confidence <= 0.7  # Should be reduced due to high symbol ratio
    
    def test_sentiment_service_only_symbols(self):
        """Test sentiment service with only symbols"""
        only_symbols = "!@#$%^&*()_+{}|:<>?[]\\;'\",./"
        result = self.sentiment_service.analyze_sentiment(only_symbols)
        
        assert isinstance(result, SentimentResult)
        assert result.sentiment == 'normal'
        assert result.fallback_used is True
        assert ("too many symbols" in result.warning.lower() or 
                "high symbol ratio" in result.warning.lower())
    
    def test_stance_service_case_sensitivity(self):
        """Test stance service case sensitivity"""
        # Test different cases of target
        text = "apple makes great products. APPLE is innovative. Apple rocks!"
        
        result_lower = self.stance_service.analyze_stance(text, "apple")
        result_upper = self.stance_service.analyze_stance(text, "APPLE")
        result_title = self.stance_service.analyze_stance(text, "Apple")
        
        # All should find the target mentions
        assert result_lower.target_mentions > 0
        assert result_upper.target_mentions > 0
        assert result_title.target_mentions > 0
    
    def test_text_processor_language_detection_edge_cases(self):
        """Test text processor language detection with edge cases"""
        edge_cases = [
            "",  # Empty string
            "   ",  # Only whitespace
            "123456789",  # Only numbers
            "!@#$%^&*()",  # Only symbols
            "a",  # Single character
            "OK",  # Very short
            "123 test 456",  # Mixed numbers and text
        ]
        
        for text in edge_cases:
            # Should not raise exceptions
            result = self.text_processor.is_english_text(text)
            assert isinstance(result, bool)
    
    def test_text_processor_cleaning_edge_cases(self):
        """Test text processor cleaning with edge cases"""
        edge_cases = [
            "",  # Empty string
            "   ",  # Only whitespace
            "\n\t\r",  # Only whitespace characters
            "a" * 10000,  # Very long text
            "!@#$%^&*()",  # Only symbols
            "http://example.com",  # Only URL
            "@username #hashtag",  # Only social media
            "test@example.com",  # Only email
        ]
        
        for text in edge_cases:
            # Should not raise exceptions
            cleaned = self.text_processor.clean_text(text)
            assert isinstance(cleaned, str)
    
    def test_sentiment_service_repeated_characters(self):
        """Test sentiment service with repeated characters"""
        repeated_texts = [
            "Thissssss isssss amazinggggggg!!!!!!!",
            "Noooooooo wayyyyyy",
            "Yessssssss!!!!!!",
            "Sooooooo badddddd",
            "Okayyyyyy I guessssss"
        ]
        
        for text in repeated_texts:
            result = self.sentiment_service.analyze_sentiment(text)
            assert isinstance(result, SentimentResult)
            assert result.sentiment in ["positive", "negative", "normal"]
    
    def test_stance_service_punctuation_heavy(self):
        """Test stance service with punctuation-heavy text"""
        punctuation_texts = [
            "Apple!!! Is!!! The!!! Best!!!",
            "Apple??? Really??? I don't think so...",
            "Apple... well... it's... okay... I guess...",
            "Apple: great phones, terrible prices!!!",
            "Apple (the company) makes phones, tablets, etc."
        ]
        
        for text in punctuation_texts:
            result = self.stance_service.analyze_stance(text, "Apple")
            assert isinstance(result, StanceResult)
            assert result.stance in ["supportive", "opposing", "neutral"]


class TestCacheEdgeCases:
    """Test caching edge cases"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
    
    def test_sentiment_analysis_identical_requests(self):
        """Test that identical sentiment requests return consistent results"""
        request_data = {"text": "This is a test for caching"}
        
        # Make multiple identical requests
        responses = []
        for _ in range(3):
            response = self.client.post("/sentiment-analysis", json=request_data)
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
        
        # Sentiment should be consistent (though request_id and timestamp will differ)
        sentiments = [response.json()["sentiment"] for response in responses]
        confidences = [response.json()["confidence"] for response in responses]
        
        # All sentiments should be the same
        assert len(set(sentiments)) == 1
        # Confidences should be very similar (allowing for small floating point differences)
        assert max(confidences) - min(confidences) < 0.01
    
    def test_stance_analysis_identical_requests(self):
        """Test that identical stance requests return consistent results"""
        request_data = {"text": "Apple makes great products", "target": "Apple"}
        
        # Make multiple identical requests
        responses = []
        for _ in range(3):
            response = self.client.post("/stance-analysis", json=request_data)
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
        
        # Stance should be consistent
        stances = [response.json()["stance"] for response in responses]
        confidences = [response.json()["confidence"] for response in responses]
        
        # All stances should be the same
        assert len(set(stances)) == 1
        # Confidences should be very similar
        assert max(confidences) - min(confidences) < 0.01


class TestMemoryAndPerformance:
    """Test memory usage and performance edge cases"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
    
    def test_large_batch_requests(self):
        """Test handling of many requests in sequence"""
        # Make many requests to test memory usage
        for i in range(50):
            request_data = {"text": f"This is test number {i} for memory testing"}
            response = self.client.post("/sentiment-analysis", json=request_data)
            assert response.status_code == 200
    
    def test_varying_text_lengths(self):
        """Test with varying text lengths to test memory management"""
        text_lengths = [10, 100, 500, 1000, 2000, 4000, 4999]  # Various lengths up to limit
        
        for length in text_lengths:
            text = "A" * length
            request_data = {"text": text}
            response = self.client.post("/sentiment-analysis", json=request_data)
            
            # Should handle all lengths up to the limit
            assert response.status_code == 200
            data = response.json()
            assert "sentiment" in data