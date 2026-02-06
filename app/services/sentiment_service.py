"""
Sentiment Analysis Service using VADER
"""
import re
import time
from typing import Dict, Any, Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
import uuid
from app.utils.cache_manager import get_cache_manager


class SentimentResult:
    """Result object for sentiment analysis"""
    def __init__(self, sentiment: str, confidence: float, scores: Dict[str, float], 
                 fallback_used: bool = False, warning: Optional[str] = None):
        self.sentiment = sentiment
        self.confidence = confidence
        self.scores = scores
        self.fallback_used = fallback_used
        self.warning = warning


class SentimentService:
    """Service for analyzing sentiment in English text using VADER"""
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.cache_manager = get_cache_manager()
        
        # Configuration for special cases
        self.MIN_TEXT_LENGTH = 3
        self.MAX_TEXT_LENGTH = 5000
        self.MIN_WORDS_FOR_RELIABLE_ANALYSIS = 3
        self.MAX_SYMBOL_RATIO = 0.7  # Maximum ratio of symbols to text length
        
    def analyze_sentiment(self, text: str, request_state=None) -> SentimentResult:
        """
        Analyze sentiment of the given text with special case handling
        
        Args:
            text: Input text to analyze
            request_state: Optional request state for tracking cache hits
            
        Returns:
            SentimentResult with sentiment classification and confidence
        """
        start_time = time.time()
        
        # Handle empty or None text
        if not text or not text.strip():
            return SentimentResult(
                sentiment='normal',
                confidence=0.1,
                scores={'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0},
                fallback_used=True,
                warning="Empty or whitespace-only text provided"
            )
        
        # Check cache first
        cache_key = self.cache_manager.generate_sentiment_key(text)
        cached_result = self.cache_manager.get(cache_key)
        if cached_result is not None:
            # Mark cache hit in request state if available
            if request_state:
                request_state.cache_hit = True
            return cached_result
        
        # Mark cache miss in request state if available
        if request_state:
            request_state.cache_hit = False
        
        # Check text length constraints
        text_length_check = self._check_text_length(text)
        if text_length_check:
            # Cache the result before returning
            self.cache_manager.set(cache_key, text_length_check)
            return text_length_check
        
        # Preprocess the text
        processed_text = self._preprocess_text(text)
        
        # Check for special cases that might affect analysis
        special_case_result = self._handle_special_cases(text, processed_text)
        if special_case_result:
            # Cache the result before returning
            self.cache_manager.set(cache_key, special_case_result)
            return special_case_result
        
        # Get VADER scores
        scores = self.analyzer.polarity_scores(processed_text)
        
        # Determine sentiment classification
        sentiment = self._classify_sentiment(scores)
        
        # Calculate confidence with special case adjustments
        confidence = self._calculate_confidence(scores, text, processed_text)
        
        result = SentimentResult(
            sentiment=sentiment,
            confidence=confidence,
            scores=scores
        )
        
        # Cache the result
        self.cache_manager.set(cache_key, result)
        
        return result
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for sentiment analysis
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned and preprocessed text
        """
        if not text or not text.strip():
            return ""
            
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Handle repeated punctuation (preserve for VADER)
        # VADER handles punctuation well, so we keep it mostly intact
        
        # Remove excessive repeated characters (more than 3)
        text = re.sub(r'(.)\1{3,}', r'\1\1\1', text)
        
        return text
    
    def _check_text_length(self, text: str) -> Optional[SentimentResult]:
        """
        Check if text length is within acceptable bounds
        
        Args:
            text: Input text to check
            
        Returns:
            SentimentResult if text is too short/long, None otherwise
        """
        text_length = len(text.strip())
        
        # Handle very short text
        if text_length < self.MIN_TEXT_LENGTH:
            return SentimentResult(
                sentiment='normal',
                confidence=0.1,
                scores={'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0},
                fallback_used=True,
                warning=f"Text too short ({text_length} chars). Minimum {self.MIN_TEXT_LENGTH} characters required for reliable analysis."
            )
        
        # Handle very long text
        if text_length > self.MAX_TEXT_LENGTH:
            # Truncate text but continue with analysis
            truncated_text = text[:self.MAX_TEXT_LENGTH]
            processed_text = self._preprocess_text(truncated_text)
            scores = self.analyzer.polarity_scores(processed_text)
            sentiment = self._classify_sentiment(scores)
            confidence = self._calculate_confidence(scores, truncated_text, processed_text)
            
            return SentimentResult(
                sentiment=sentiment,
                confidence=max(0.1, confidence - 0.2),  # Reduce confidence for truncated text
                scores=scores,
                fallback_used=True,
                warning=f"Text truncated from {text_length} to {self.MAX_TEXT_LENGTH} characters for analysis."
            )
        
        return None
    
    def _handle_special_cases(self, original_text: str, processed_text: str) -> Optional[SentimentResult]:
        """
        Handle special cases that might affect sentiment analysis
        
        Args:
            original_text: Original input text
            processed_text: Preprocessed text
            
        Returns:
            SentimentResult if special handling is needed, None otherwise
        """
        # Check for high symbol/number ratio
        symbol_ratio = self._calculate_symbol_ratio(original_text)
        if symbol_ratio > self.MAX_SYMBOL_RATIO:
            # Try to extract meaningful text
            meaningful_text = re.sub(r'[^\w\s.,!?;:\'"()-]', ' ', original_text)
            meaningful_text = re.sub(r'\s+', ' ', meaningful_text.strip())
            
            if len(meaningful_text.split()) < 2:
                return SentimentResult(
                    sentiment='normal',
                    confidence=0.1,
                    scores={'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0},
                    fallback_used=True,
                    warning=f"Text contains too many symbols ({symbol_ratio:.1%}). Unable to extract meaningful content."
                )
            
            # Analyze the cleaned text with reduced confidence
            scores = self.analyzer.polarity_scores(meaningful_text)
            sentiment = self._classify_sentiment(scores)
            confidence = self._calculate_confidence(scores, meaningful_text, meaningful_text)
            
            return SentimentResult(
                sentiment=sentiment,
                confidence=max(0.1, confidence - 0.3),  # Significantly reduce confidence
                scores=scores,
                fallback_used=True,
                warning=f"High symbol ratio ({symbol_ratio:.1%}) detected. Analysis based on extracted text."
            )
        
        # Check for very few words
        word_count = len(processed_text.split())
        if word_count < self.MIN_WORDS_FOR_RELIABLE_ANALYSIS:
            scores = self.analyzer.polarity_scores(processed_text)
            sentiment = self._classify_sentiment(scores)
            confidence = self._calculate_confidence(scores, original_text, processed_text)
            
            return SentimentResult(
                sentiment=sentiment,
                confidence=max(0.1, confidence - 0.2),  # Reduce confidence for short texts
                scores=scores,
                fallback_used=True,
                warning=f"Very short text ({word_count} words). Analysis may be less reliable."
            )
        
        return None
    
    def _calculate_symbol_ratio(self, text: str) -> float:
        """
        Calculate the ratio of symbols and numbers to total text length
        
        Args:
            text: Input text
            
        Returns:
            Ratio of symbols/numbers to total length (0.0 to 1.0)
        """
        if not text:
            return 0.0
        
        # Count non-alphabetic, non-whitespace characters
        symbol_count = len(re.findall(r'[^\w\s]', text))
        number_count = len(re.findall(r'\d', text))
        total_symbols = symbol_count + number_count
        
        return total_symbols / len(text) if len(text) > 0 else 0.0
    
    def _classify_sentiment(self, scores: Dict[str, float]) -> str:
        """
        Classify sentiment based on VADER compound score
        
        Args:
            scores: VADER polarity scores dictionary
            
        Returns:
            Sentiment classification: 'positive', 'negative', or 'normal'
        """
        compound = scores['compound']
        
        # VADER compound score thresholds
        if compound >= 0.05:
            return 'positive'
        elif compound <= -0.05:
            return 'negative'
        else:
            return 'normal'
    
    def _calculate_confidence(self, scores: Dict[str, float], 
                             original_text: str = "", processed_text: str = "") -> float:
        """
        Calculate confidence score based on VADER scores and text characteristics
        
        Args:
            scores: VADER polarity scores dictionary
            original_text: Original input text (for additional analysis)
            processed_text: Preprocessed text (for additional analysis)
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        compound = abs(scores['compound'])
        
        # Base confidence on absolute compound score
        # VADER compound ranges from -1 to 1, so abs gives us 0 to 1
        base_confidence = compound
        
        # Adjust confidence based on the distribution of pos/neg/neu scores
        pos, neg, neu = scores['pos'], scores['neg'], scores['neu']
        
        # If one sentiment dominates, increase confidence
        max_sentiment = max(pos, neg, neu)
        if max_sentiment > 0.6:  # Strong dominance
            base_confidence = min(1.0, base_confidence + 0.1)
        elif max_sentiment < 0.4:  # Weak dominance, reduce confidence
            base_confidence = max(0.1, base_confidence - 0.1)
        
        # Additional adjustments based on text characteristics
        if original_text and processed_text:
            # Reduce confidence for very short texts
            word_count = len(processed_text.split())
            if word_count < 3:
                base_confidence = max(0.1, base_confidence - 0.2)
            elif word_count < 5:
                base_confidence = max(0.1, base_confidence - 0.1)
            
            # Reduce confidence if there's a big difference between original and processed
            length_ratio = len(processed_text) / len(original_text) if len(original_text) > 0 else 1.0
            if length_ratio < 0.5:  # Significant text was removed during preprocessing
                base_confidence = max(0.1, base_confidence - 0.15)
        
        # Ensure confidence is at least 0.1 and at most 1.0
        return max(0.1, min(1.0, base_confidence))