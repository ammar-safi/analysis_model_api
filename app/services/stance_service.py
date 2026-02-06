"""
Stance Analysis Service for detecting stance towards specific targets
"""
import re
from typing import Dict, Any, Optional, List, Tuple
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
import uuid
from app.utils.cache_manager import get_cache_manager


class StanceResult:
    """Result object for stance analysis"""
    def __init__(self, stance: str, confidence: float, target: str, 
                 target_mentions: int = 0, context_sentiment: float = 0.0,
                 keyword_score: float = 0.0, combined_score: float = 0.0,
                 consistency: float = 1.0, fallback_used: bool = False, 
                 warning: Optional[str] = None):
        self.stance = stance
        self.confidence = confidence
        self.target = target
        self.target_mentions = target_mentions
        self.context_sentiment = context_sentiment
        self.keyword_score = keyword_score
        self.combined_score = combined_score
        self.consistency = consistency
        self.fallback_used = fallback_used
        self.warning = warning


class StanceService:
    """Service for analyzing stance towards specific targets in English text"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.cache_manager = get_cache_manager()
        
        # Configuration for stance analysis
        self.MIN_TEXT_LENGTH = 3
        self.MAX_TEXT_LENGTH = 5000
        self.CONTEXT_WINDOW = 50  # Characters around target mention to analyze
        self.MIN_CONFIDENCE_THRESHOLD = 0.1
        self.NEUTRAL_THRESHOLD = 0.12  # Threshold for neutral stance
        
        # Keywords that might indicate stance
        self.POSITIVE_INDICATORS = [
            'love', 'like', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'good', 'best', 'awesome', 'perfect', 'brilliant', 'outstanding', 'superb',
            'support', 'endorse', 'recommend', 'praise', 'admire', 'appreciate',
            'trust', 'respect', 'favor', 'champion', 'defend', 'celebrate', 'embrace'
        ]
        
        self.NEGATIVE_INDICATORS = [
            'hate', 'dislike', 'terrible', 'awful', 'horrible', 'bad', 'worst',
            'disgusting', 'pathetic', 'useless', 'garbage', 'trash', 'sucks',
            'oppose', 'against', 'criticize', 'condemn', 'reject', 'disapprove',
            'distrust', 'despise', 'attack', 'blame', 'fault', 'boycott', 'avoid',
            'overpriced', 'worthless', 'disappointing', 'frustrated'
        ]
        
        # Modifiers that can change stance intensity
        self.INTENSIFIERS = ['very', 'extremely', 'really', 'totally', 'completely', 'absolutely']
        self.DIMINISHERS = ['somewhat', 'slightly', 'kind of', 'sort of', 'a bit', 'rather']
        
        # Negation words that can flip stance
        self.NEGATION_WORDS = ['not', 'no', 'never', 'nothing', 'nobody', 'nowhere', 
                              'neither', 'nor', 'none', "don't", "doesn't", "didn't", 
                              "won't", "wouldn't", "can't", "couldn't", "shouldn't"]
    
    def analyze_stance(self, text: str, target: str) -> StanceResult:
        """
        Analyze stance towards a specific target in the given text
        
        Args:
            text: Input text to analyze
            target: Target entity to analyze stance towards
            
        Returns:
            StanceResult with stance classification and confidence
        """
        # Handle empty or None inputs
        if not text or not text.strip():
            return StanceResult(
                stance='neutral',
                confidence=0.1,
                target=target,
                fallback_used=True,
                warning="Empty or whitespace-only text provided"
            )
        
        if not target or not target.strip():
            return StanceResult(
                stance='neutral',
                confidence=0.1,
                target=target or "",
                fallback_used=True,
                warning="Empty or whitespace-only target provided"
            )
        
        # Check cache first
        cache_key = self.cache_manager.generate_stance_key(text, target)
        cached_result = self.cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Check text length constraints
        text_length_check = self._check_text_length(text, target)
        if text_length_check:
            # Cache the result before returning
            self.cache_manager.set(cache_key, text_length_check)
            return text_length_check
        
        # Preprocess text and target
        processed_text = self._preprocess_text(text)
        processed_target = self._preprocess_target(target)
        
        # Find target mentions in the text
        target_positions = self._find_target_mentions(processed_text, processed_target)
        
        if not target_positions:
            # Target not found in text - return neutral with low confidence
            result = StanceResult(
                stance='neutral',
                confidence=0.1,
                target=target,
                target_mentions=0,
                fallback_used=True,
                warning=f"Target '{target}' not found in the provided text"
            )
            # Cache the result before returning
            self.cache_manager.set(cache_key, result)
            return result
        
        # Analyze context around target mentions
        context_sentiment = self._analyze_context_sentiment(processed_text, target_positions)
        
        # Perform keyword-based stance detection
        keyword_stance_score = self._analyze_keyword_based_stance(processed_text, target_positions)
        
        # Combine sentiment and keyword analysis
        combined_score = self._combine_stance_signals(context_sentiment, keyword_stance_score)
        
        # Handle conflicting stances in the same text
        stance_consistency = self._check_stance_consistency(processed_text, target_positions)
        
        # Determine final stance
        stance = self._classify_stance(combined_score)
        
        # Calculate confidence with consistency adjustment
        confidence = self._calculate_confidence(
            combined_score, len(target_positions), processed_text, processed_target, stance_consistency
        )
        
        result = StanceResult(
            stance=stance,
            confidence=confidence,
            target=target,
            target_mentions=len(target_positions),
            context_sentiment=context_sentiment,
            keyword_score=keyword_stance_score,
            combined_score=combined_score,
            consistency=stance_consistency
        )
        
        # Cache the result
        self.cache_manager.set(cache_key, result)
        
        return result
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for stance analysis
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned and preprocessed text
        """
        if not text or not text.strip():
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Convert to lowercase for analysis (but preserve original case for display)
        return text
    
    def _preprocess_target(self, target: str) -> str:
        """
        Preprocess target for better matching
        
        Args:
            target: Raw target string
            
        Returns:
            Cleaned target string
        """
        if not target or not target.strip():
            return ""
        
        # Remove extra whitespace and normalize
        target = re.sub(r'\s+', ' ', target.strip())
        return target
    
    def _check_text_length(self, text: str, target: str) -> Optional[StanceResult]:
        """
        Check if text length is within acceptable bounds
        
        Args:
            text: Input text to check
            target: Target entity
            
        Returns:
            StanceResult if text is too short/long, None otherwise
        """
        text_length = len(text.strip())
        
        # Handle very short text
        if text_length < self.MIN_TEXT_LENGTH:
            return StanceResult(
                stance='neutral',
                confidence=0.1,
                target=target,
                fallback_used=True,
                warning=f"Text too short ({text_length} chars). Minimum {self.MIN_TEXT_LENGTH} characters required for reliable analysis."
            )
        
        # Handle very long text - truncate but continue
        if text_length > self.MAX_TEXT_LENGTH:
            truncated_text = text[:self.MAX_TEXT_LENGTH]
            # Continue with analysis but mark as fallback
            processed_text = self._preprocess_text(truncated_text)
            processed_target = self._preprocess_target(target)
            target_positions = self._find_target_mentions(processed_text, processed_target)
            
            if not target_positions:
                return StanceResult(
                    stance='neutral',
                    confidence=0.1,
                    target=target,
                    fallback_used=True,
                    warning=f"Text truncated from {text_length} to {self.MAX_TEXT_LENGTH} characters. Target not found in truncated text."
                )
            
            context_sentiment = self._analyze_context_sentiment(processed_text, target_positions)
            keyword_stance_score = self._analyze_keyword_based_stance(processed_text, target_positions)
            combined_score = self._combine_stance_signals(context_sentiment, keyword_stance_score)
            stance_consistency = self._check_stance_consistency(processed_text, target_positions)
            stance = self._classify_stance(combined_score)
            confidence = self._calculate_confidence(
                combined_score, len(target_positions), processed_text, processed_target, stance_consistency
            )
            
            return StanceResult(
                stance=stance,
                confidence=max(0.1, confidence - 0.2),  # Reduce confidence for truncated text
                target=target,
                target_mentions=len(target_positions),
                context_sentiment=context_sentiment,
                keyword_score=keyword_stance_score,
                combined_score=combined_score,
                consistency=stance_consistency,
                fallback_used=True,
                warning=f"Text truncated from {text_length} to {self.MAX_TEXT_LENGTH} characters for analysis."
            )
        
        return None
    
    def _find_target_mentions(self, text: str, target: str) -> List[int]:
        """
        Find all mentions of the target in the text
        
        Args:
            text: Preprocessed text to search in
            target: Target entity to find
            
        Returns:
            List of character positions where target is mentioned
        """
        if not text or not target:
            return []
        
        positions = []
        text_lower = text.lower()
        target_lower = target.lower()
        
        # Find exact matches
        start = 0
        while True:
            pos = text_lower.find(target_lower, start)
            if pos == -1:
                break
            
            # Check if it's a word boundary match (not part of another word)
            if self._is_word_boundary_match(text_lower, target_lower, pos):
                positions.append(pos)
            
            start = pos + 1
        
        # Also try to find partial matches or variations
        # Split target into words and look for individual words
        target_words = target_lower.split()
        if len(target_words) > 1:
            for word in target_words:
                if len(word) > 2:  # Only consider meaningful words
                    start = 0
                    while True:
                        pos = text_lower.find(word, start)
                        if pos == -1:
                            break
                        
                        if self._is_word_boundary_match(text_lower, word, pos):
                            # Only add if not already covered by exact match
                            if not any(abs(pos - existing_pos) < len(target_lower) for existing_pos in positions):
                                positions.append(pos)
                        
                        start = pos + 1
        
        return sorted(list(set(positions)))  # Remove duplicates and sort
    
    def _analyze_keyword_based_stance(self, text: str, positions: List[int]) -> float:
        """
        Analyze stance using keyword-based detection around target mentions
        
        Args:
            text: Preprocessed text
            positions: List of target mention positions
            
        Returns:
            Keyword-based stance score (-1 to 1)
        """
        if not positions:
            return 0.0
        
        keyword_scores = []
        text_lower = text.lower()
        
        for pos in positions:
            # Extract extended context for keyword analysis
            start = max(0, pos - self.CONTEXT_WINDOW * 2)
            end = min(len(text), pos + self.CONTEXT_WINDOW * 2)
            context = text_lower[start:end]
            context_words = context.split()
            
            # Find target position within context words
            target_word_pos = self._find_target_word_position(context_words, pos - start, text_lower)
            
            # Analyze keywords around target
            score = self._calculate_keyword_score(context_words, target_word_pos)
            keyword_scores.append(score)
        
        return sum(keyword_scores) / len(keyword_scores) if keyword_scores else 0.0
    
    def _find_target_word_position(self, context_words: List[str], char_offset: int, full_text: str) -> int:
        """
        Find the approximate word position of target within context words
        
        Args:
            context_words: List of words in the context
            char_offset: Character offset of target within context
            full_text: Full text for reference
            
        Returns:
            Approximate word position of target
        """
        # Simple approximation - find middle of context
        return len(context_words) // 2
    
    def _calculate_keyword_score(self, words: List[str], target_pos: int) -> float:
        """
        Calculate stance score based on keywords around target position
        
        Args:
            words: List of words in context
            target_pos: Position of target within words
            
        Returns:
            Keyword-based stance score
        """
        score = 0.0
        window_size = 10  # Words to consider around target
        
        start_idx = max(0, target_pos - window_size)
        end_idx = min(len(words), target_pos + window_size)
        
        for i in range(start_idx, end_idx):
            word = words[i].strip('.,!?;:"()[]{}')
            distance_weight = 1.0 / (abs(i - target_pos) + 1)  # Closer words have more weight
            
            # Check for positive indicators
            if word in self.POSITIVE_INDICATORS:
                word_score = 1.0 * distance_weight
                
                # Check for intensifiers/diminishers nearby
                word_score = self._apply_modifiers(words, i, word_score)
                
                # Check for negation
                word_score = self._apply_negation(words, i, word_score)
                
                score += word_score
            
            # Check for negative indicators
            elif word in self.NEGATIVE_INDICATORS:
                word_score = -1.0 * distance_weight
                
                # Check for intensifiers/diminishers nearby
                word_score = self._apply_modifiers(words, i, word_score)
                
                # Check for negation
                word_score = self._apply_negation(words, i, word_score)
                
                score += word_score
        
        # Normalize score
        max_possible_score = window_size * 2  # Maximum possible absolute score
        return max(-1.0, min(1.0, score / max_possible_score)) if max_possible_score > 0 else 0.0
    
    def _apply_modifiers(self, words: List[str], word_idx: int, base_score: float) -> float:
        """
        Apply intensifiers or diminishers to the base score
        
        Args:
            words: List of words
            word_idx: Index of the current word
            base_score: Base stance score
            
        Returns:
            Modified score
        """
        # Check 2 words before and after for modifiers
        for i in range(max(0, word_idx - 2), min(len(words), word_idx + 3)):
            if i == word_idx:
                continue
            
            word = words[i].strip('.,!?;:"()[]{}')
            
            if word in self.INTENSIFIERS:
                return base_score * 1.5  # Increase intensity
            elif word in self.DIMINISHERS:
                return base_score * 0.7  # Decrease intensity
        
        return base_score
    
    def _apply_negation(self, words: List[str], word_idx: int, base_score: float) -> float:
        """
        Apply negation to flip the stance if negation words are nearby
        
        Args:
            words: List of words
            word_idx: Index of the current word
            base_score: Base stance score
            
        Returns:
            Potentially negated score
        """
        # Check 3 words before for negation (common English pattern)
        for i in range(max(0, word_idx - 3), word_idx):
            word = words[i].strip('.,!?;:"()[]{}')
            
            if word in self.NEGATION_WORDS:
                return -base_score  # Flip the stance
        
        # Also check for contractions like "don't" directly
        if word_idx > 0:
            prev_word = words[word_idx - 1].strip('.,!?;:"()[]{}')
            if prev_word in self.NEGATION_WORDS:
                return -base_score
        
        return base_score
    
    def _combine_stance_signals(self, sentiment_score: float, keyword_score: float) -> float:
        """
        Combine sentiment-based and keyword-based stance signals
        
        Args:
            sentiment_score: Sentiment analysis score
            keyword_score: Keyword-based stance score
            
        Returns:
            Combined stance score
        """
        # Weight keyword analysis more heavily as it's more specific to stance
        combined = (sentiment_score * 0.4) + (keyword_score * 0.6)
        
        # If both signals agree strongly, boost the confidence
        if abs(sentiment_score) > 0.3 and abs(keyword_score) > 0.3:
            if (sentiment_score > 0 and keyword_score > 0) or (sentiment_score < 0 and keyword_score < 0):
                combined *= 1.2  # Boost when both agree
        
        return max(-1.0, min(1.0, combined))
    
    def _check_stance_consistency(self, text: str, positions: List[int]) -> float:
        """
        Check for conflicting stances within the same text
        
        Args:
            text: Preprocessed text
            positions: List of target mention positions
            
        Returns:
            Consistency score (0.0 = very inconsistent, 1.0 = very consistent)
        """
        if len(positions) <= 1:
            return 1.0  # Single mention is always consistent
        
        stance_scores = []
        
        for pos in positions:
            # Analyze each mention independently
            start = max(0, pos - self.CONTEXT_WINDOW)
            end = min(len(text), pos + self.CONTEXT_WINDOW)
            context = text[start:end]
            
            # Get sentiment for this specific context
            scores = self.sentiment_analyzer.polarity_scores(context)
            stance_scores.append(scores['compound'])
        
        if not stance_scores:
            return 1.0
        
        # Calculate variance in stance scores
        mean_score = sum(stance_scores) / len(stance_scores)
        variance = sum((score - mean_score) ** 2 for score in stance_scores) / len(stance_scores)
        
        # Convert variance to consistency score (lower variance = higher consistency)
        consistency = max(0.0, 1.0 - (variance * 2))  # Scale variance to 0-1 range
        
        return consistency
    
    def _is_word_boundary_match(self, text: str, target: str, position: int) -> bool:
        """
        Check if the target match at position is at word boundaries
        
        Args:
            text: Text being searched
            target: Target being matched
            position: Position of the match
            
        Returns:
            True if match is at word boundaries
        """
        # Check character before
        if position > 0:
            char_before = text[position - 1]
            if char_before.isalnum():
                return False
        
        # Check character after
        end_pos = position + len(target)
        if end_pos < len(text):
            char_after = text[end_pos]
            if char_after.isalnum():
                return False
        
        return True
    
    def _analyze_context_sentiment(self, text: str, positions: List[int]) -> float:
        """
        Analyze sentiment in the context around target mentions
        
        Args:
            text: Preprocessed text
            positions: List of target mention positions
            
        Returns:
            Average sentiment score for all contexts
        """
        if not positions:
            return 0.0
        
        context_sentiments = []
        
        for pos in positions:
            # Extract context window around the target
            start = max(0, pos - self.CONTEXT_WINDOW)
            end = min(len(text), pos + self.CONTEXT_WINDOW)
            context = text[start:end]
            
            # Analyze sentiment of the context
            scores = self.sentiment_analyzer.polarity_scores(context)
            context_sentiments.append(scores['compound'])
        
        # Return average sentiment across all contexts
        return sum(context_sentiments) / len(context_sentiments) if context_sentiments else 0.0
    
    def _classify_stance(self, combined_score: float) -> str:
        """
        Classify stance based on combined sentiment and keyword analysis
        
        Args:
            combined_score: Combined stance score from sentiment and keyword analysis
            
        Returns:
            Stance classification: 'supportive', 'opposing', or 'neutral'
        """
        if combined_score > self.NEUTRAL_THRESHOLD:
            return 'supportive'  # Supportive
        elif combined_score < -self.NEUTRAL_THRESHOLD:
            return 'opposing'  # Opposing
        else:
            return 'neutral'  # Neutral
    
    def _calculate_confidence(self, combined_score: float, mention_count: int, 
                             text: str, target: str, consistency: float = 1.0) -> float:
        """
        Calculate confidence score for stance classification
        
        Args:
            combined_score: Combined stance score from sentiment and keyword analysis
            mention_count: Number of target mentions found
            text: Preprocessed text
            target: Target entity
            consistency: Stance consistency score across multiple mentions
            
        Returns:
            Confidence score between 0.1 and 1.0
        """
        # Base confidence on absolute combined score strength
        base_confidence = abs(combined_score)
        
        # Adjust based on number of mentions
        if mention_count > 1:
            base_confidence = min(1.0, base_confidence + 0.1)  # More mentions = higher confidence
        elif mention_count == 0:
            return 0.1  # No mentions = very low confidence
        
        # Adjust based on stance consistency
        base_confidence *= consistency  # Inconsistent stances reduce confidence
        
        # Adjust based on text length
        word_count = len(text.split())
        if word_count < 5:
            base_confidence = max(0.1, base_confidence - 0.2)
        elif word_count > 50:
            base_confidence = min(1.0, base_confidence + 0.1)
        
        # Adjust based on target specificity
        target_word_count = len(target.split())
        if target_word_count > 1:
            base_confidence = min(1.0, base_confidence + 0.05)  # More specific targets
        
        # Bonus for very clear stances
        if abs(combined_score) > 0.7:
            base_confidence = min(1.0, base_confidence + 0.1)
        
        # Ensure confidence is within bounds
        return max(self.MIN_CONFIDENCE_THRESHOLD, min(1.0, base_confidence))