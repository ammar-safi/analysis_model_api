"""
Unit tests for TextProcessor
"""
import pytest
from unittest.mock import patch
from app.utils.text_processor import TextProcessor


class TestTextProcessor:
    """Test cases for TextProcessor"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.processor = TextProcessor()
    
    def test_is_english_text_english(self):
        """Test English text detection for English text"""
        text = "This is a sample English text for testing purposes."
        assert self.processor.is_english_text(text) is True
    
    def test_is_english_text_non_english(self):
        """Test English text detection for non-English text"""
        text = "هذا نص باللغة العربية للاختبار"
        assert self.processor.is_english_text(text) is False
    
    def test_is_english_text_empty(self):
        """Test English text detection for empty text"""
        assert self.processor.is_english_text("") is False
        assert self.processor.is_english_text("   ") is False
        assert self.processor.is_english_text(None) is False
    
    def test_is_english_text_short_english(self):
        """Test English text detection for short English text"""
        text = "Hello world"
        assert self.processor.is_english_text(text) is True
    
    def test_is_english_text_mixed_content(self):
        """Test English text detection for mixed content"""
        text = "Hello 123 !@# world"
        assert self.processor.is_english_text(text) is True
    
    @patch('app.utils.text_processor.detect')
    def test_is_english_text_detection_exception(self, mock_detect):
        """Test English text detection when langdetect raises exception"""
        mock_detect.side_effect = Exception("Detection failed")
        text = "This is a test"
        
        # Should fallback to heuristics
        result = self.processor.is_english_text(text)
        assert isinstance(result, bool)
    
    def test_is_likely_english_short_text_english_words(self):
        """Test short text English detection with common English words"""
        text = "the quick brown fox"
        assert self.processor._is_likely_english_short_text(text) is True
    
    def test_is_likely_english_short_text_non_english_words(self):
        """Test short text English detection with non-English words"""
        text = "xyz qwerty asdfgh"
        assert self.processor._is_likely_english_short_text(text) is False
    
    def test_is_likely_english_short_text_empty(self):
        """Test short text English detection with empty text"""
        assert self.processor._is_likely_english_short_text("") is False
    
    def test_clean_text_basic(self):
        """Test basic text cleaning"""
        text = "  This is a test!  "
        cleaned = self.processor.clean_text(text)
        
        assert cleaned == "this is a test!"
        assert cleaned.strip() == cleaned
    
    def test_clean_text_urls(self):
        """Test text cleaning with URLs"""
        text = "Check out https://example.com for more info"
        cleaned = self.processor.clean_text(text)
        
        assert "https://example.com" not in cleaned
        assert "check out" in cleaned
        assert "for more info" in cleaned
    
    def test_clean_text_emails(self):
        """Test text cleaning with email addresses"""
        text = "Contact us at test@example.com for support"
        cleaned = self.processor.clean_text(text)
        
        assert "test@example.com" not in cleaned
        assert "contact us at" in cleaned
        assert "for support" in cleaned
    
    def test_clean_text_mentions(self):
        """Test text cleaning with social media mentions"""
        text = "Thanks @username for the help!"
        cleaned = self.processor.clean_text(text)
        
        assert "@username" not in cleaned
        assert "thanks" in cleaned
        assert "for the help" in cleaned
    
    def test_clean_text_hashtags(self):
        """Test text cleaning with hashtags"""
        text = "This is #awesome and #great!"
        cleaned = self.processor.clean_text(text)
        
        assert "#awesome" not in cleaned
        assert "#great" not in cleaned
        assert "awesome" in cleaned
        assert "great" in cleaned
    
    def test_clean_text_contractions(self):
        """Test text cleaning with contractions"""
        text = "I can't believe it's so good!"
        cleaned = self.processor.clean_text(text)
        
        assert "can't" not in cleaned
        assert "it's" not in cleaned
        assert "cannot" in cleaned
        assert "it is" in cleaned
    
    def test_clean_text_preserve_case(self):
        """Test text cleaning while preserving case"""
        text = "This Is A Test!"
        cleaned = self.processor.clean_text(text, preserve_case=True)
        
        assert cleaned == "This Is A Test!"
        assert cleaned != cleaned.lower()
    
    def test_clean_text_special_characters(self):
        """Test text cleaning with special characters"""
        text = "Hello!@#$%^&*()_+ world"
        cleaned = self.processor.clean_text(text)
        
        assert "!@#$%^&*()_+" not in cleaned
        assert "hello" in cleaned
        assert "world" in cleaned
    
    def test_clean_text_extra_whitespace(self):
        """Test text cleaning with extra whitespace"""
        text = "This   has    too     much    whitespace"
        cleaned = self.processor.clean_text(text)
        
        assert "   " not in cleaned
        assert cleaned.count(' ') == 5  # Single spaces only
    
    def test_clean_text_empty(self):
        """Test text cleaning with empty input"""
        assert self.processor.clean_text("") == ""
        assert self.processor.clean_text("   ") == ""
        assert self.processor.clean_text(None) == ""
    
    def test_expand_contractions_basic(self):
        """Test basic contraction expansion"""
        text = "I can't do it"
        expanded = self.processor._expand_contractions(text)
        
        assert "can't" not in expanded
        assert "cannot" in expanded
    
    def test_expand_contractions_multiple(self):
        """Test multiple contraction expansion"""
        text = "I can't believe you're here and it's great!"
        expanded = self.processor._expand_contractions(text)
        
        assert "can't" not in expanded
        assert "you're" not in expanded
        assert "it's" not in expanded
        assert "cannot" in expanded
        assert "you are" in expanded
        assert "it is" in expanded
    
    def test_expand_contractions_case_insensitive(self):
        """Test case-insensitive contraction expansion"""
        text = "I CAN'T believe it"
        expanded = self.processor._expand_contractions(text)
        
        assert "CAN'T" not in expanded
        assert "cannot" in expanded.lower()
    
    def test_expand_contractions_no_contractions(self):
        """Test contraction expansion with no contractions"""
        text = "This text has no contractions"
        expanded = self.processor._expand_contractions(text)
        
        assert expanded == text
    
    def test_preprocess_for_sentiment_basic(self):
        """Test sentiment preprocessing"""
        text = "I can't believe it's not good!"
        processed = self.processor.preprocess_for_sentiment(text)
        
        assert "cannot" in processed
        assert "it is" in processed
        assert processed == processed.lower()
    
    def test_preprocess_for_sentiment_negations(self):
        """Test sentiment preprocessing with negation emphasis"""
        text = "This is not good"
        processed = self.processor.preprocess_for_sentiment(text)
        
        # Should emphasize negation
        assert processed.count("not") > 1
    
    def test_preprocess_for_sentiment_intensifiers(self):
        """Test sentiment preprocessing with intensifier emphasis"""
        text = "This is very good"
        processed = self.processor.preprocess_for_sentiment(text)
        
        # Should emphasize intensifier
        assert processed.count("very") > 1
    
    def test_preprocess_for_stance_basic(self):
        """Test stance preprocessing"""
        text = "Apple makes great products"
        target = "Apple"
        processed_text, target_variations = self.processor.preprocess_for_stance(text, target)
        
        assert processed_text == text.lower()
        assert isinstance(target_variations, list)
        assert len(target_variations) > 1
        assert "apple" in target_variations
    
    def test_preprocess_for_stance_target_variations(self):
        """Test stance preprocessing target variations"""
        text = "Test text"
        target = "Apple"
        processed_text, target_variations = self.processor.preprocess_for_stance(text, target)
        
        assert "apple" in target_variations
        assert "APPLE" in target_variations
        assert "Apple" in target_variations
        assert "@apple" in target_variations
        assert "#apple" in target_variations
        assert "apple's" in target_variations
        assert "apples" in target_variations
    
    def test_generate_target_variations_basic(self):
        """Test target variation generation"""
        target = "Apple"
        variations = self.processor._generate_target_variations(target)
        
        assert "apple" in variations
        assert "APPLE" in variations
        assert "Apple" in variations
        assert len(variations) > 3
    
    def test_generate_target_variations_duplicates(self):
        """Test that target variations don't contain duplicates"""
        target = "test"
        variations = self.processor._generate_target_variations(target)
        
        assert len(variations) == len(set(variations))  # No duplicates
    
    def test_generate_target_variations_social_media(self):
        """Test target variations include social media formats"""
        target = "Apple"
        variations = self.processor._generate_target_variations(target)
        
        assert "@apple" in variations
        assert "#apple" in variations
    
    def test_generate_target_variations_possessive(self):
        """Test target variations include possessive forms"""
        target = "Apple"
        variations = self.processor._generate_target_variations(target)
        
        assert "apple's" in variations
        assert "apples" in variations
    
    def test_extract_sentences_basic(self):
        """Test basic sentence extraction"""
        text = "This is sentence one. This is sentence two! Is this sentence three?"
        sentences = self.processor.extract_sentences(text)
        
        assert len(sentences) == 3
        assert "This is sentence one" in sentences
        assert "This is sentence two" in sentences
        assert "Is this sentence three" in sentences
    
    def test_extract_sentences_multiple_punctuation(self):
        """Test sentence extraction with multiple punctuation"""
        text = "Wow!!! This is amazing... Really?"
        sentences = self.processor.extract_sentences(text)
        
        assert len(sentences) >= 2
        assert "Wow" in sentences[0]
        assert "Really" in sentences[-1]
    
    def test_extract_sentences_no_punctuation(self):
        """Test sentence extraction with no punctuation"""
        text = "This is one long sentence without punctuation"
        sentences = self.processor.extract_sentences(text)
        
        assert len(sentences) == 1
        assert sentences[0] == text
    
    def test_extract_sentences_empty(self):
        """Test sentence extraction with empty text"""
        sentences = self.processor.extract_sentences("")
        assert sentences == []
    
    def test_remove_noise_for_detection_urls(self):
        """Test noise removal for language detection with URLs"""
        text = "This is English text with https://example.com URL"
        cleaned = self.processor._remove_noise_for_detection(text)
        
        assert "https://example.com" not in cleaned
        assert "This is English text" in cleaned
    
    def test_remove_noise_for_detection_numbers(self):
        """Test noise removal for language detection with numbers"""
        text = "This text has 123 numbers and 456 more"
        cleaned = self.processor._remove_noise_for_detection(text)
        
        assert "123" not in cleaned
        assert "456" not in cleaned
        assert "This text has" in cleaned
    
    def test_remove_noise_for_detection_punctuation(self):
        """Test noise removal for language detection with punctuation"""
        text = "This! has@ lots# of$ punctuation%"
        cleaned = self.processor._remove_noise_for_detection(text)
        
        assert "!" not in cleaned
        assert "@" not in cleaned
        assert "#" not in cleaned
        assert "$" not in cleaned
        assert "%" not in cleaned
        assert "This has lots of punctuation" in cleaned
    
    def test_remove_noise_for_detection_mentions_hashtags(self):
        """Test noise removal for language detection with mentions and hashtags"""
        text = "Check @username and #hashtag for more info"
        cleaned = self.processor._remove_noise_for_detection(text)
        
        assert "@username" not in cleaned
        assert "#hashtag" not in cleaned
        assert "Check" in cleaned
        assert "for more info" in cleaned
    
    def test_contractions_dictionary_completeness(self):
        """Test that contractions dictionary contains common contractions"""
        contractions = self.processor.contractions
        
        # Test some common contractions
        assert "can't" in contractions
        assert "won't" in contractions
        assert "it's" in contractions
        assert "you're" in contractions
        assert "don't" in contractions
        assert "isn't" in contractions
        
        # Test that expansions are correct
        assert contractions["can't"] == "cannot"
        assert contractions["won't"] == "will not"
        assert contractions["it's"] == "it is"
        assert contractions["you're"] == "you are"
    
    def test_regex_patterns_compilation(self):
        """Test that regex patterns are properly compiled"""
        # Test that patterns are compiled regex objects
        assert hasattr(self.processor.url_pattern, 'search')
        assert hasattr(self.processor.email_pattern, 'search')
        assert hasattr(self.processor.mention_pattern, 'search')
        assert hasattr(self.processor.hashtag_pattern, 'search')
        assert hasattr(self.processor.extra_whitespace_pattern, 'search')
    
    def test_url_pattern_matching(self):
        """Test URL pattern matching"""
        urls = [
            "http://example.com",
            "https://example.com",
            "https://www.example.com/path?param=value",
            "http://subdomain.example.com:8080/path"
        ]
        
        for url in urls:
            match = self.processor.url_pattern.search(url)
            assert match is not None, f"URL pattern should match {url}"
    
    def test_email_pattern_matching(self):
        """Test email pattern matching"""
        emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@test.com"
        ]
        
        for email in emails:
            match = self.processor.email_pattern.search(email)
            assert match is not None, f"Email pattern should match {email}"
    
    def test_mention_pattern_matching(self):
        """Test mention pattern matching"""
        mentions = ["@username", "@user123", "@test_user"]
        
        for mention in mentions:
            match = self.processor.mention_pattern.search(mention)
            assert match is not None, f"Mention pattern should match {mention}"
    
    def test_hashtag_pattern_matching(self):
        """Test hashtag pattern matching"""
        hashtags = ["#hashtag", "#test123", "#hash_tag"]
        
        for hashtag in hashtags:
            match = self.processor.hashtag_pattern.search(hashtag)
            assert match is not None, f"Hashtag pattern should match {hashtag}"