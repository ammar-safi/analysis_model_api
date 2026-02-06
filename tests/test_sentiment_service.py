"""
Unit tests for SentimentService
"""
import pytest
from unittest.mock import Mock, patch
from app.services.sentiment_service import SentimentService, SentimentResult


class TestSentimentService:
    """Test cases for SentimentService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = SentimentService()
    
    def test_analyze_sentiment_positive_text(self):
        """Test sentiment analysis for positive text"""
        text = "I love this product! It's amazing and wonderful."
        result = self.service.analyze_sentiment(text)
        
        assert isinstance(result, SentimentResult)
        assert result.sentiment == 'positive'
        assert result.confidence > 0.5
        assert result.scores is not None
        assert 'compound' in result.scores
        assert result.fallback_used is False
        assert result.warning is None
    
    def test_analyze_sentiment_negative_text(self):
        """Test sentiment analysis for negative text"""
        text = "I hate this product! It's terrible and awful."
        result = self.service.analyze_sentiment(text)
        
        assert result.sentiment == 'negative'
        assert result.confidence > 0.5
        assert result.scores['compound'] < 0
        assert result.fallback_used is False
    
    def test_analyze_sentiment_neutral_text(self):
        """Test sentiment analysis for neutral text"""
        text = "This is a product. It exists."
        result = self.service.analyze_sentiment(text)
        
        assert result.sentiment == 'normal'
        assert result.confidence >= 0.1
        assert abs(result.scores['compound']) <= 0.05
    
    def test_analyze_sentiment_empty_text(self):
        """Test sentiment analysis for empty text"""
        result = self.service.analyze_sentiment("")
        
        assert result.sentiment == 'normal'
        assert result.confidence == 0.1
        assert result.fallback_used is True
        assert "Empty or whitespace-only text" in result.warning
    
    def test_analyze_sentiment_whitespace_only(self):
        """Test sentiment analysis for whitespace-only text"""
        result = self.service.analyze_sentiment("   \n\t  ")
        
        assert result.sentiment == 'normal'
        assert result.confidence == 0.1
        assert result.fallback_used is True
        assert "Empty or whitespace-only text" in result.warning
    
    def test_analyze_sentiment_none_text(self):
        """Test sentiment analysis for None text"""
        result = self.service.analyze_sentiment(None)
        
        assert result.sentiment == 'normal'
        assert result.confidence == 0.1
        assert result.fallback_used is True
    
    def test_analyze_sentiment_very_short_text(self):
        """Test sentiment analysis for very short text"""
        result = self.service.analyze_sentiment("Hi")
        
        assert result.sentiment in ['positive', 'negative', 'normal']
        assert result.confidence == 0.1
        assert result.fallback_used is True
        assert "Text too short" in result.warning
    
    def test_analyze_sentiment_very_long_text(self):
        """Test sentiment analysis for very long text"""
        long_text = "This is a great product! " * 300  # Over 5000 chars
        result = self.service.analyze_sentiment(long_text)
        
        assert result.sentiment in ['positive', 'negative', 'normal']
        assert result.confidence >= 0.1
        assert result.fallback_used is True
        assert "Text truncated" in result.warning
    
    def test_analyze_sentiment_high_symbol_ratio(self):
        """Test sentiment analysis for text with high symbol ratio"""
        text = "!@#$%^&*()_+{}|:<>?[]\\;'\",./ good !@#$%^&*()_+"
        result = self.service.analyze_sentiment(text)
        
        assert result.sentiment in ['positive', 'negative', 'normal']
        assert result.confidence >= 0.1
        assert result.fallback_used is True
        assert "High symbol ratio" in result.warning
    
    def test_analyze_sentiment_mostly_symbols(self):
        """Test sentiment analysis for text that's mostly symbols"""
        text = "!@#$%^&*()_+{}|:<>?[]\\;'\",./"
        result = self.service.analyze_sentiment(text)
        
        assert result.sentiment == 'normal'
        assert result.confidence == 0.1
        assert result.fallback_used is True
        assert ("too many symbols" in result.warning.lower() or 
                "high symbol ratio" in result.warning.lower())
    
    def test_analyze_sentiment_few_words(self):
        """Test sentiment analysis for text with very few words"""
        text = "Good bad"
        result = self.service.analyze_sentiment(text)
        
        assert result.sentiment in ['positive', 'negative', 'normal']
        assert result.confidence >= 0.1
        assert result.fallback_used is True
        assert "Very short text" in result.warning
    
    def test_preprocess_text_basic(self):
        """Test basic text preprocessing"""
        text = "  This   is    a   test!  "
        processed = self.service._preprocess_text(text)
        
        assert processed == "This is a test!"
        assert processed.count(' ') == 3  # Single spaces only
    
    def test_preprocess_text_repeated_characters(self):
        """Test preprocessing of repeated characters"""
        text = "Thissss isssss amazinggggg!!!!"
        processed = self.service._preprocess_text(text)
        
        # Should limit repeated characters to 3
        assert "ssss" not in processed
        assert "gggg" not in processed
    
    def test_preprocess_text_empty(self):
        """Test preprocessing of empty text"""
        assert self.service._preprocess_text("") == ""
        assert self.service._preprocess_text(None) == ""
        assert self.service._preprocess_text("   ") == ""
    
    def test_check_text_length_normal(self):
        """Test text length check for normal text"""
        text = "This is a normal length text for testing."
        result = self.service._check_text_length(text)
        
        assert result is None  # Should pass length check
    
    def test_check_text_length_too_short(self):
        """Test text length check for too short text"""
        text = "Hi"
        result = self.service._check_text_length(text)
        
        assert result is not None
        assert result.sentiment == 'normal'
        assert result.confidence == 0.1
        assert result.fallback_used is True
    
    def test_check_text_length_too_long(self):
        """Test text length check for too long text"""
        text = "This is a test. " * 400  # Over 5000 chars
        result = self.service._check_text_length(text)
        
        assert result is not None
        assert result.fallback_used is True
        assert "Text truncated" in result.warning
    
    def test_calculate_symbol_ratio(self):
        """Test symbol ratio calculation"""
        # Text with 50% symbols
        text = "Hello!@#$"  # 5 letters, 4 symbols, 1 space = 40% symbols
        ratio = self.service._calculate_symbol_ratio(text)
        assert 0.3 <= ratio <= 0.5
        
        # Text with no symbols
        text = "Hello world"
        ratio = self.service._calculate_symbol_ratio(text)
        assert ratio == 0.0
        
        # Text with all symbols
        text = "!@#$%"
        ratio = self.service._calculate_symbol_ratio(text)
        assert ratio == 1.0
    
    def test_classify_sentiment_positive(self):
        """Test sentiment classification for positive scores"""
        scores = {'compound': 0.8, 'pos': 0.7, 'neu': 0.2, 'neg': 0.1}
        sentiment = self.service._classify_sentiment(scores)
        assert sentiment == 'positive'
    
    def test_classify_sentiment_negative(self):
        """Test sentiment classification for negative scores"""
        scores = {'compound': -0.8, 'pos': 0.1, 'neu': 0.2, 'neg': 0.7}
        sentiment = self.service._classify_sentiment(scores)
        assert sentiment == 'negative'
    
    def test_classify_sentiment_neutral(self):
        """Test sentiment classification for neutral scores"""
        scores = {'compound': 0.02, 'pos': 0.3, 'neu': 0.4, 'neg': 0.3}
        sentiment = self.service._classify_sentiment(scores)
        assert sentiment == 'normal'
    
    def test_calculate_confidence_high_compound(self):
        """Test confidence calculation for high compound scores"""
        scores = {'compound': 0.9, 'pos': 0.8, 'neu': 0.1, 'neg': 0.1}
        confidence = self.service._calculate_confidence(scores, "This is a great product!", "this is a great product")
        
        assert confidence > 0.8
        assert confidence <= 1.0
    
    def test_calculate_confidence_low_compound(self):
        """Test confidence calculation for low compound scores"""
        scores = {'compound': 0.1, 'pos': 0.4, 'neu': 0.4, 'neg': 0.2}
        confidence = self.service._calculate_confidence(scores, "This is okay", "this is okay")
        
        assert confidence >= 0.1
        assert confidence < 0.5
    
    def test_calculate_confidence_short_text(self):
        """Test confidence calculation for short text"""
        scores = {'compound': 0.5, 'pos': 0.6, 'neu': 0.3, 'neg': 0.1}
        confidence = self.service._calculate_confidence(scores, "Good", "good")
        
        # Should be reduced due to short text
        assert confidence >= 0.1
        assert confidence < 0.6
    
    def test_calculate_confidence_processed_text_difference(self):
        """Test confidence calculation when processed text differs significantly"""
        scores = {'compound': 0.5, 'pos': 0.6, 'neu': 0.3, 'neg': 0.1}
        original = "!@#$%^&*() Good product !@#$%^&*()"
        processed = "Good product"
        confidence = self.service._calculate_confidence(scores, original, processed)
        
        # Should be reduced due to significant preprocessing
        assert confidence >= 0.1
        assert confidence < 0.5
    
    @patch('app.services.sentiment_service.get_cache_manager')
    def test_analyze_sentiment_uses_cache(self, mock_get_cache_manager):
        """Test that sentiment analysis uses caching"""
        mock_cache = Mock()
        mock_get_cache_manager.return_value = mock_cache
        mock_cache.get.return_value = None  # Cache miss
        mock_cache.generate_sentiment_key.return_value = "test_key"
        
        service = SentimentService()
        text = "This is a test"
        result = service.analyze_sentiment(text)
        
        # Verify cache was checked and result was stored
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()
        mock_cache.generate_sentiment_key.assert_called_once_with(text)
    
    @patch('app.services.sentiment_service.get_cache_manager')
    def test_analyze_sentiment_cache_hit(self, mock_get_cache_manager):
        """Test that sentiment analysis returns cached result"""
        mock_cache = Mock()
        mock_get_cache_manager.return_value = mock_cache
        
        # Mock cached result
        cached_result = SentimentResult('positive', 0.8, {'compound': 0.8})
        mock_cache.get.return_value = cached_result
        mock_cache.generate_sentiment_key.return_value = "test_key"
        
        service = SentimentService()
        text = "This is a test"
        result = service.analyze_sentiment(text)
        
        # Should return cached result
        assert result.sentiment == cached_result.sentiment
        assert result.confidence == cached_result.confidence
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_not_called()  # Should not store when cache hit
    
    def test_handle_special_cases_normal_text(self):
        """Test special case handling for normal text"""
        text = "This is a normal text with good content."
        processed = self.service._preprocess_text(text)
        result = self.service._handle_special_cases(text, processed)
        
        assert result is None  # No special handling needed
    
    def test_handle_special_cases_high_symbols(self):
        """Test special case handling for high symbol ratio"""
        text = "!@#$%^&*() good !@#$%^&*()"
        processed = self.service._preprocess_text(text)
        result = self.service._handle_special_cases(text, processed)
        
        assert result is not None
        assert result.fallback_used is True
        assert "High symbol ratio" in result.warning
    
    def test_handle_special_cases_few_words(self):
        """Test special case handling for very few words"""
        text = "Good bad"
        processed = self.service._preprocess_text(text)
        result = self.service._handle_special_cases(text, processed)
        
        assert result is not None
        assert result.fallback_used is True
        assert "Very short text" in result.warning


class TestSentimentResult:
    """Test cases for SentimentResult class"""
    
    def test_sentiment_result_creation(self):
        """Test SentimentResult object creation"""
        scores = {'compound': 0.5, 'pos': 0.6, 'neu': 0.3, 'neg': 0.1}
        result = SentimentResult('positive', 0.8, scores)
        
        assert result.sentiment == 'positive'
        assert result.confidence == 0.8
        assert result.scores == scores
        assert result.fallback_used is False
        assert result.warning is None
    
    def test_sentiment_result_with_fallback(self):
        """Test SentimentResult with fallback and warning"""
        scores = {'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0}
        result = SentimentResult('normal', 0.1, scores, fallback_used=True, warning="Test warning")
        
        assert result.sentiment == 'normal'
        assert result.confidence == 0.1
        assert result.fallback_used is True
        assert result.warning == "Test warning"