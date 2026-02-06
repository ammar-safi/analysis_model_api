"""
Unit tests for StanceService
"""
import pytest
from unittest.mock import Mock, patch
from app.services.stance_service import StanceService, StanceResult


class TestStanceService:
    """Test cases for StanceService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = StanceService()
    
    def test_analyze_stance_supportive(self):
        """Test stance analysis for supportive text"""
        text = "I love Apple products! They make amazing phones and computers."
        target = "Apple"
        result = self.service.analyze_stance(text, target)
        
        assert isinstance(result, StanceResult)
        assert result.stance == 'supportive'
        assert result.confidence > 0.3
        assert result.target == target
        assert result.target_mentions > 0
        assert result.fallback_used is False
    
    def test_analyze_stance_opposing(self):
        """Test stance analysis for opposing text"""
        text = "I hate Microsoft products! They are terrible and overpriced."
        target = "Microsoft"
        result = self.service.analyze_stance(text, target)
        
        assert result.stance == 'opposing'
        assert result.confidence > 0.3
        assert result.target == target
        assert result.target_mentions > 0
        assert result.combined_score < 0
    
    def test_analyze_stance_neutral(self):
        """Test stance analysis for neutral text"""
        text = "Google is a technology company based in California."
        target = "Google"
        result = self.service.analyze_stance(text, target)
        
        assert result.stance == 'neutral'
        assert result.confidence >= 0.1
        assert result.target == target
        assert result.target_mentions > 0
    
    def test_analyze_stance_empty_text(self):
        """Test stance analysis for empty text"""
        result = self.service.analyze_stance("", "Apple")
        
        assert result.stance == 'neutral'
        assert result.confidence == 0.1
        assert result.fallback_used is True
        assert "Empty or whitespace-only text" in result.warning
    
    def test_analyze_stance_empty_target(self):
        """Test stance analysis for empty target"""
        result = self.service.analyze_stance("This is a test", "")
        
        assert result.stance == 'neutral'
        assert result.confidence == 0.1
        assert result.fallback_used is True
        assert "Empty or whitespace-only target" in result.warning
    
    def test_analyze_stance_none_inputs(self):
        """Test stance analysis for None inputs"""
        result = self.service.analyze_stance(None, None)
        
        assert result.stance == 'neutral'
        assert result.confidence == 0.1
        assert result.fallback_used is True
    
    def test_analyze_stance_target_not_found(self):
        """Test stance analysis when target is not found in text"""
        text = "This is a great product from a wonderful company."
        target = "Apple"
        result = self.service.analyze_stance(text, target)
        
        assert result.stance == 'neutral'
        assert result.confidence == 0.1
        assert result.target_mentions == 0
        assert result.fallback_used is True
        assert "not found in the provided text" in result.warning
    
    def test_analyze_stance_very_short_text(self):
        """Test stance analysis for very short text"""
        result = self.service.analyze_stance("Hi", "Apple")
        
        assert result.stance == 'neutral'
        assert result.confidence == 0.1
        assert result.fallback_used is True
        assert "Text too short" in result.warning
    
    def test_analyze_stance_very_long_text(self):
        """Test stance analysis for very long text"""
        long_text = "Apple makes great products! " * 300  # Over 5000 chars
        target = "Apple"
        result = self.service.analyze_stance(long_text, target)
        
        assert result.stance in ['supportive', 'opposing', 'neutral']
        assert result.confidence >= 0.1
        assert result.fallback_used is True
        assert "Text truncated" in result.warning
    
    def test_analyze_stance_multiple_mentions(self):
        """Test stance analysis with multiple target mentions"""
        text = "Apple makes great phones. I love Apple products. Apple is innovative."
        target = "Apple"
        result = self.service.analyze_stance(text, target)
        
        assert result.target_mentions >= 3
        assert result.stance == 'supportive'
        assert result.confidence > 0.4  # Higher confidence due to multiple mentions
    
    def test_preprocess_text(self):
        """Test text preprocessing"""
        text = "  This   is    a   TEST!  "
        processed = self.service._preprocess_text(text)
        
        assert processed == "This is a TEST!"
        assert processed.count(' ') == 3  # Single spaces only
    
    def test_preprocess_target(self):
        """Test target preprocessing"""
        target = "  Apple Inc.  "
        processed = self.service._preprocess_target(target)
        
        assert processed == "Apple Inc."
        assert processed == processed.strip()
    
    def test_find_target_mentions_exact_match(self):
        """Test finding exact target mentions"""
        text = "Apple makes great products. I love Apple."
        target = "Apple"
        positions = self.service._find_target_mentions(text.lower(), target.lower())
        
        assert len(positions) == 2
        assert all(isinstance(pos, int) for pos in positions)
    
    def test_find_target_mentions_case_insensitive(self):
        """Test finding target mentions case insensitively"""
        text = "apple makes great products. I love APPLE."
        target = "Apple"
        positions = self.service._find_target_mentions(text.lower(), target.lower())
        
        assert len(positions) == 2
    
    def test_find_target_mentions_word_boundary(self):
        """Test that target mentions respect word boundaries"""
        text = "Pineapple is good but Apple is better."
        target = "Apple"
        positions = self.service._find_target_mentions(text.lower(), target.lower())
        
        # Should find "Apple" but not "apple" in "Pineapple"
        assert len(positions) == 1
    
    def test_find_target_mentions_multi_word_target(self):
        """Test finding mentions of multi-word targets"""
        text = "Microsoft Corporation makes good software. I like Microsoft Corporation."
        target = "Microsoft Corporation"
        positions = self.service._find_target_mentions(text.lower(), target.lower())
        
        assert len(positions) >= 1  # Should find at least the exact matches
    
    def test_find_target_mentions_partial_matches(self):
        """Test finding partial matches for multi-word targets"""
        text = "Microsoft makes good software. I like their products."
        target = "Microsoft Corporation"
        positions = self.service._find_target_mentions(text.lower(), target.lower())
        
        assert len(positions) >= 1  # Should find "Microsoft"
    
    def test_is_word_boundary_match_valid(self):
        """Test word boundary matching for valid cases"""
        text = "Apple is great"
        target = "Apple"
        position = 0
        
        assert self.service._is_word_boundary_match(text.lower(), target.lower(), position) is True
    
    def test_is_word_boundary_match_invalid(self):
        """Test word boundary matching for invalid cases"""
        text = "Pineapple is good"
        target = "apple"
        position = 4  # Position of "apple" in "Pineapple"
        
        assert self.service._is_word_boundary_match(text.lower(), target.lower(), position) is False
    
    def test_analyze_context_sentiment_positive(self):
        """Test context sentiment analysis for positive context"""
        text = "I really love Apple products because they are amazing"
        positions = [12]  # Position of "Apple"
        sentiment = self.service._analyze_context_sentiment(text, positions)
        
        assert sentiment > 0.2  # Should be positive
    
    def test_analyze_context_sentiment_negative(self):
        """Test context sentiment analysis for negative context"""
        text = "I hate Apple products because they are terrible"
        positions = [7]  # Position of "Apple"
        sentiment = self.service._analyze_context_sentiment(text, positions)
        
        assert sentiment < -0.2  # Should be negative
    
    def test_analyze_context_sentiment_neutral(self):
        """Test context sentiment analysis for neutral context"""
        text = "Apple is a technology company"
        positions = [0]  # Position of "Apple"
        sentiment = self.service._analyze_context_sentiment(text, positions)
        
        assert -0.2 <= sentiment <= 0.2  # Should be neutral
    
    def test_analyze_keyword_based_stance_positive(self):
        """Test keyword-based stance analysis for positive stance"""
        text = "I love Apple products they are excellent and amazing"
        positions = [7]  # Position of "Apple"
        score = self.service._analyze_keyword_based_stance(text, positions)
        
        assert score > 0.1  # Should be positive due to "love", "excellent", "amazing"
    
    def test_analyze_keyword_based_stance_negative(self):
        """Test keyword-based stance analysis for negative stance"""
        text = "I hate Apple products they are terrible and awful"
        positions = [7]  # Position of "Apple"
        score = self.service._analyze_keyword_based_stance(text, positions)
        
        assert score < -0.1  # Should be negative due to "hate", "terrible", "awful"
    
    def test_calculate_keyword_score_with_intensifiers(self):
        """Test keyword score calculation with intensifiers"""
        words = ["I", "really", "love", "Apple", "products"]
        target_pos = 3
        score = self.service._calculate_keyword_score(words, target_pos)
        
        assert score > 0.1  # Should be positive and boosted by "really"
    
    def test_calculate_keyword_score_with_negation(self):
        """Test keyword score calculation with negation"""
        words = ["I", "don't", "love", "Apple", "products"]
        target_pos = 3
        score = self.service._calculate_keyword_score(words, target_pos)
        
        assert score < 0  # Should be negative due to negation
    
    def test_apply_modifiers_intensifier(self):
        """Test applying intensifier modifiers"""
        words = ["very", "good", "product"]
        word_idx = 1  # "good"
        base_score = 0.5
        modified_score = self.service._apply_modifiers(words, word_idx, base_score)
        
        assert modified_score > base_score  # Should be intensified
    
    def test_apply_modifiers_diminisher(self):
        """Test applying diminisher modifiers"""
        words = ["somewhat", "good", "product"]
        word_idx = 1  # "good"
        base_score = 0.5
        modified_score = self.service._apply_modifiers(words, word_idx, base_score)
        
        assert modified_score < base_score  # Should be diminished
    
    def test_apply_negation_positive_to_negative(self):
        """Test applying negation to flip positive to negative"""
        words = ["not", "good", "product"]
        word_idx = 1  # "good"
        base_score = 0.5
        negated_score = self.service._apply_negation(words, word_idx, base_score)
        
        assert negated_score == -base_score  # Should be flipped
    
    def test_apply_negation_no_negation(self):
        """Test applying negation when no negation words present"""
        words = ["very", "good", "product"]
        word_idx = 1  # "good"
        base_score = 0.5
        score = self.service._apply_negation(words, word_idx, base_score)
        
        assert score == base_score  # Should remain unchanged
    
    def test_combine_stance_signals_agreeing(self):
        """Test combining stance signals when they agree"""
        sentiment_score = 0.6
        keyword_score = 0.8
        combined = self.service._combine_stance_signals(sentiment_score, keyword_score)
        
        assert combined > 0.5  # Should be positive and boosted
        assert combined <= 1.0
    
    def test_combine_stance_signals_disagreeing(self):
        """Test combining stance signals when they disagree"""
        sentiment_score = 0.3
        keyword_score = -0.3
        combined = self.service._combine_stance_signals(sentiment_score, keyword_score)
        
        assert -0.2 <= combined <= 0.2  # Should be close to neutral
    
    def test_check_stance_consistency_single_mention(self):
        """Test stance consistency check for single mention"""
        text = "Apple is great"
        positions = [0]
        consistency = self.service._check_stance_consistency(text, positions)
        
        assert consistency == 1.0  # Single mention is always consistent
    
    def test_check_stance_consistency_consistent_mentions(self):
        """Test stance consistency check for consistent mentions"""
        text = "Apple is great. Apple is amazing. Apple is wonderful."
        positions = [0, 16, 32]  # Approximate positions
        consistency = self.service._check_stance_consistency(text, positions)
        
        assert consistency > 0.7  # Should be highly consistent
    
    def test_classify_stance_supportive(self):
        """Test stance classification for supportive score"""
        score = 0.5
        stance = self.service._classify_stance(score)
        assert stance == 'supportive'
    
    def test_classify_stance_opposing(self):
        """Test stance classification for opposing score"""
        score = -0.5
        stance = self.service._classify_stance(score)
        assert stance == 'opposing'
    
    def test_classify_stance_neutral(self):
        """Test stance classification for neutral score"""
        score = 0.05
        stance = self.service._classify_stance(score)
        assert stance == 'neutral'
    
    def test_calculate_confidence_high_score(self):
        """Test confidence calculation for high combined score"""
        combined_score = 0.8
        mention_count = 2
        text = "This is a good test text"
        target = "test"
        confidence = self.service._calculate_confidence(combined_score, mention_count, text, target)
        
        assert confidence > 0.7
        assert confidence <= 1.0
    
    def test_calculate_confidence_low_score(self):
        """Test confidence calculation for low combined score"""
        combined_score = 0.1
        mention_count = 1
        text = "This is a test"
        target = "test"
        confidence = self.service._calculate_confidence(combined_score, mention_count, text, target)
        
        assert confidence >= 0.1
        assert confidence < 0.5
    
    def test_calculate_confidence_multiple_mentions(self):
        """Test confidence calculation with multiple mentions"""
        combined_score = 0.5
        mention_count = 3
        text = "This is a good test with multiple test mentions for test"
        target = "test"
        confidence = self.service._calculate_confidence(combined_score, mention_count, text, target)
        
        # Should be boosted due to multiple mentions
        single_mention_confidence = self.service._calculate_confidence(combined_score, 1, text, target)
        assert confidence >= single_mention_confidence
    
    def test_calculate_confidence_no_mentions(self):
        """Test confidence calculation with no mentions"""
        combined_score = 0.5
        mention_count = 0
        text = "This is a test"
        target = "missing"
        confidence = self.service._calculate_confidence(combined_score, mention_count, text, target)
        
        assert confidence == 0.1  # Should return minimum confidence
    
    def test_calculate_confidence_short_text(self):
        """Test confidence calculation for short text"""
        combined_score = 0.5
        mention_count = 1
        text = "Good"
        target = "Good"
        confidence = self.service._calculate_confidence(combined_score, mention_count, text, target)
        
        # Should be reduced due to short text
        assert confidence >= 0.1
        assert confidence < 0.5
    
    def test_calculate_confidence_long_text(self):
        """Test confidence calculation for long text"""
        combined_score = 0.5
        mention_count = 1
        long_text = "This is a very long text " * 10
        target = "text"
        confidence = self.service._calculate_confidence(combined_score, mention_count, long_text, target)
        
        # Should be boosted due to long text
        short_confidence = self.service._calculate_confidence(combined_score, mention_count, "Short text", target)
        assert confidence >= short_confidence
    
    def test_calculate_confidence_multi_word_target(self):
        """Test confidence calculation for multi-word target"""
        combined_score = 0.5
        mention_count = 1
        text = "Microsoft Corporation is a good company"
        target = "Microsoft Corporation"
        confidence = self.service._calculate_confidence(combined_score, mention_count, text, target)
        
        # Should be boosted due to specific target
        single_word_confidence = self.service._calculate_confidence(combined_score, mention_count, text, "Microsoft")
        assert confidence >= single_word_confidence
    
    def test_calculate_confidence_very_clear_stance(self):
        """Test confidence calculation for very clear stance"""
        combined_score = 0.9
        mention_count = 1
        text = "This is a test"
        target = "test"
        confidence = self.service._calculate_confidence(combined_score, mention_count, text, target)
        
        # Should be boosted due to very clear stance
        assert confidence > 0.8
    
    def test_calculate_confidence_with_consistency(self):
        """Test confidence calculation with consistency factor"""
        combined_score = 0.5
        mention_count = 2
        text = "This is a test"
        target = "test"
        consistency = 0.8
        confidence = self.service._calculate_confidence(combined_score, mention_count, text, target, consistency)
        
        # Should be affected by consistency
        assert confidence >= 0.1
        assert confidence <= 1.0
    
    @patch('app.utils.cache_manager.get_cache_manager')
    def test_analyze_stance_uses_cache(self, mock_cache_manager):
        """Test that stance analysis uses caching"""
        mock_cache = Mock()
        mock_cache_manager.return_value = mock_cache
        mock_cache.get.return_value = None  # Cache miss
        mock_cache.generate_stance_key.return_value = "test_key"
        
        service = StanceService()
        text = "Apple is great"
        target = "Apple"
        result = service.analyze_stance(text, target)
        
        # Verify cache was checked and result was stored
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()
        mock_cache.generate_stance_key.assert_called_once_with(text, target)
    
    @patch('app.utils.cache_manager.get_cache_manager')
    def test_analyze_stance_cache_hit(self, mock_cache_manager):
        """Test that stance analysis returns cached result"""
        mock_cache = Mock()
        mock_cache_manager.return_value = mock_cache
        
        # Mock cached result
        cached_result = StanceResult('supportive', 0.8, 'Apple')
        mock_cache.get.return_value = cached_result
        mock_cache.generate_stance_key.return_value = "test_key"
        
        service = StanceService()
        text = "Apple is great"
        target = "Apple"
        result = service.analyze_stance(text, target)
        
        # Should return cached result
        assert result == cached_result
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_not_called()  # Should not store when cache hit


class TestStanceResult:
    """Test cases for StanceResult class"""
    
    def test_stance_result_creation(self):
        """Test StanceResult object creation"""
        result = StanceResult('supportive', 0.8, 'Apple')
        
        assert result.stance == 'supportive'
        assert result.confidence == 0.8
        assert result.target == 'Apple'
        assert result.target_mentions == 0  # Default value
        assert result.fallback_used is False
        assert result.warning is None
    
    def test_stance_result_with_all_parameters(self):
        """Test StanceResult with all parameters"""
        result = StanceResult(
            stance='opposing',
            confidence=0.6,
            target='Microsoft',
            target_mentions=2,
            context_sentiment=-0.5,
            keyword_score=-0.7,
            combined_score=-0.6,
            consistency=0.9,
            fallback_used=True,
            warning="Test warning"
        )
        
        assert result.stance == 'opposing'
        assert result.confidence == 0.6
        assert result.target == 'Microsoft'
        assert result.target_mentions == 2
        assert result.context_sentiment == -0.5
        assert result.keyword_score == -0.7
        assert result.combined_score == -0.6
        assert result.consistency == 0.9
        assert result.fallback_used is True
        assert result.warning == "Test warning"