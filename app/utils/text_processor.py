"""
Text processing utilities for sentiment and stance analysis.
"""

import re
import string
from typing import Optional, List
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException


# Set seed for consistent language detection results
DetectorFactory.seed = 0


class TextProcessor:
    """
    Text processor for cleaning and preprocessing text for sentiment and stance analysis.
    """
    
    def __init__(self):
        """Initialize the TextProcessor."""
        # Common English contractions mapping
        self.contractions = {
            "ain't": "am not",
            "aren't": "are not", 
            "can't": "cannot",
            "couldn't": "could not",
            "didn't": "did not",
            "doesn't": "does not",
            "don't": "do not",
            "hadn't": "had not",
            "hasn't": "has not",
            "haven't": "have not",
            "he'd": "he would",
            "he'll": "he will",
            "he's": "he is",
            "i'd": "i would",
            "i'll": "i will",
            "i'm": "i am",
            "i've": "i have",
            "isn't": "is not",
            "it'd": "it would",
            "it'll": "it will",
            "it's": "it is",
            "let's": "let us",
            "shouldn't": "should not",
            "that's": "that is",
            "there's": "there is",
            "they'd": "they would",
            "they'll": "they will",
            "they're": "they are",
            "they've": "they have",
            "we'd": "we would",
            "we're": "we are",
            "we've": "we have",
            "weren't": "were not",
            "what's": "what is",
            "where's": "where is",
            "who's": "who is",
            "won't": "will not",
            "wouldn't": "would not",
            "you'd": "you would",
            "you'll": "you will",
            "you're": "you are",
            "you've": "you have"
        }
        
        # Patterns for cleaning
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.mention_pattern = re.compile(r'@\w+')
        self.hashtag_pattern = re.compile(r'#\w+')
        self.extra_whitespace_pattern = re.compile(r'\s+')
        
    def is_english_text(self, text: str, confidence_threshold: float = 0.7) -> bool:
        """
        Check if the text is in English.
        
        Args:
            text: Text to check
            confidence_threshold: Minimum confidence for English detection
            
        Returns:
            True if text is detected as English, False otherwise
        """
        if not text or not text.strip():
            return False
            
        # Remove URLs, mentions, hashtags for better language detection
        cleaned_text = self._remove_noise_for_detection(text)
        
        # If text is too short or mostly non-alphabetic, use simple heuristics
        if len(cleaned_text.strip()) < 10:
            return self._is_likely_english_short_text(cleaned_text)
            
        try:
            detected_lang = detect(cleaned_text)
            return detected_lang == 'en'
        except LangDetectException:
            # Fallback to simple heuristics if detection fails
            return self._is_likely_english_short_text(cleaned_text)
    
    def clean_text(self, text: str, preserve_case: bool = False) -> str:
        """
        Clean and normalize text for analysis.
        
        Args:
            text: Raw text to clean
            preserve_case: Whether to preserve original case
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
            
        # Remove URLs
        text = self.url_pattern.sub(' ', text)
        
        # Remove email addresses
        text = self.email_pattern.sub(' ', text)
        
        # Remove mentions and hashtags (but keep the text part of hashtags)
        text = self.mention_pattern.sub(' ', text)
        text = self.hashtag_pattern.sub(lambda m: m.group(0)[1:], text)  # Remove # but keep text
        
        # Expand contractions
        text = self._expand_contractions(text)
        
        # Remove extra punctuation (keep basic punctuation)
        text = re.sub(r'[^\w\s.,!?;:\-\'"()]', ' ', text)
        
        # Normalize whitespace
        text = self.extra_whitespace_pattern.sub(' ', text)
        
        # Convert to lowercase if not preserving case
        if not preserve_case:
            text = text.lower()
            
        return text.strip()
    
    def preprocess_for_sentiment(self, text: str) -> str:
        """
        Preprocess text specifically for sentiment analysis.
        
        Args:
            text: Text to preprocess
            
        Returns:
            Preprocessed text optimized for sentiment analysis
        """
        # Clean the text
        cleaned = self.clean_text(text, preserve_case=False)
        
        # Handle negations - add emphasis to negation words
        negation_words = ['not', 'no', 'never', 'nothing', 'nowhere', 'nobody', 'none', 'neither', 'nor']
        for neg_word in negation_words:
            pattern = r'\b' + re.escape(neg_word) + r'\b'
            cleaned = re.sub(pattern, f'{neg_word} {neg_word}', cleaned, flags=re.IGNORECASE)
        
        # Handle intensifiers
        intensifiers = ['very', 'really', 'extremely', 'incredibly', 'absolutely', 'totally']
        for intensifier in intensifiers:
            pattern = r'\b' + re.escape(intensifier) + r'\b'
            cleaned = re.sub(pattern, f'{intensifier} {intensifier}', cleaned, flags=re.IGNORECASE)
            
        return cleaned
    
    def preprocess_for_stance(self, text: str, target: str) -> tuple[str, List[str]]:
        """
        Preprocess text specifically for stance analysis.
        
        Args:
            text: Text to preprocess
            target: Target entity for stance analysis
            
        Returns:
            Tuple of (preprocessed_text, target_variations)
        """
        # Clean the text while preserving some case for entity recognition
        cleaned = self.clean_text(text, preserve_case=True)
        
        # Generate target variations for better matching
        target_variations = self._generate_target_variations(target)
        
        # Convert to lowercase for analysis
        cleaned_lower = cleaned.lower()
        
        return cleaned_lower, target_variations
    
    def extract_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting on common punctuation
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _remove_noise_for_detection(self, text: str) -> str:
        """Remove noise that might interfere with language detection."""
        # Remove URLs, mentions, hashtags, numbers
        text = self.url_pattern.sub(' ', text)
        text = self.email_pattern.sub(' ', text)
        text = self.mention_pattern.sub(' ', text)
        text = self.hashtag_pattern.sub(' ', text)
        text = re.sub(r'\d+', ' ', text)  # Remove numbers
        text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
        return self.extra_whitespace_pattern.sub(' ', text).strip()
    
    def _is_likely_english_short_text(self, text: str) -> bool:
        """Simple heuristics for short text English detection."""
        if not text:
            return False
            
        # Check for common English words
        common_english_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
            'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you',
            'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they',
            'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my',
            'one', 'all', 'would', 'there', 'their', 'what', 'so',
            'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me'
        }
        
        words = text.lower().split()
        if not words:
            return False
            
        english_word_count = sum(1 for word in words if word in common_english_words)
        return english_word_count / len(words) >= 0.3  # At least 30% common English words
    
    def _expand_contractions(self, text: str) -> str:
        """Expand contractions in text."""
        # Sort by length (longest first) to avoid partial replacements
        sorted_contractions = sorted(self.contractions.items(), key=lambda x: len(x[0]), reverse=True)
        
        for contraction, expansion in sorted_contractions:
            # Case-insensitive replacement
            pattern = re.compile(re.escape(contraction), re.IGNORECASE)
            text = pattern.sub(expansion, text)
            
        return text
    
    def _generate_target_variations(self, target: str) -> List[str]:
        """Generate variations of the target for better matching."""
        variations = [target.lower()]
        
        # Add variations with different cases
        variations.extend([
            target.upper(),
            target.title(),
            target.capitalize()
        ])
        
        # Add variations with common prefixes/suffixes
        base_target = target.lower()
        variations.extend([
            f"@{base_target}",  # Social media mention
            f"#{base_target}",  # Hashtag
            f"{base_target}'s",  # Possessive
            f"{base_target}s",   # Plural
        ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variations = []
        for var in variations:
            if var not in seen:
                seen.add(var)
                unique_variations.append(var)
                
        return unique_variations