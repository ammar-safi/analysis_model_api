"""
Validation utilities for the Sentiment and Stance Analysis API.
"""

import re
from typing import Optional, Tuple, List
from pydantic import ValidationError


class ValidationResult:
    """Result of a validation operation."""
    
    def __init__(self, is_valid: bool, error_message: Optional[str] = None, error_code: Optional[str] = None):
        self.is_valid = is_valid
        self.error_message = error_message
        self.error_code = error_code


class InputValidator:
    """Validator for API input data."""
    
    def __init__(self):
        """Initialize the InputValidator."""
        # Text length constraints
        self.MIN_TEXT_LENGTH = 1
        self.MAX_TEXT_LENGTH = 5000
        self.MIN_TARGET_LENGTH = 1
        self.MAX_TARGET_LENGTH = 200
        
        # Patterns for validation
        self.excessive_whitespace_pattern = re.compile(r'\s{10,}')  # 10+ consecutive spaces
        self.only_special_chars_pattern = re.compile(r'^[^\w\s]*$')  # Only special characters
        self.only_numbers_pattern = re.compile(r'^\d+$')  # Only numbers
        
    def validate_text_input(self, text: str, field_name: str = "text") -> ValidationResult:
        """
        Validate text input for sentiment or stance analysis.
        
        Args:
            text: Text to validate
            field_name: Name of the field being validated
            
        Returns:
            ValidationResult indicating if text is valid
        """
        if not text:
            return ValidationResult(
                is_valid=False,
                error_message=f"{field_name} cannot be empty",
                error_code="EMPTY_TEXT"
            )
        
        # Check length constraints
        if len(text) < self.MIN_TEXT_LENGTH:
            return ValidationResult(
                is_valid=False,
                error_message=f"{field_name} must be at least {self.MIN_TEXT_LENGTH} character long",
                error_code="TEXT_TOO_SHORT"
            )
            
        if len(text) > self.MAX_TEXT_LENGTH:
            return ValidationResult(
                is_valid=False,
                error_message=f"{field_name} must not exceed {self.MAX_TEXT_LENGTH} characters",
                error_code="TEXT_TOO_LONG"
            )
        
        # Check for excessive whitespace
        if self.excessive_whitespace_pattern.search(text):
            return ValidationResult(
                is_valid=False,
                error_message=f"{field_name} contains excessive whitespace",
                error_code="EXCESSIVE_WHITESPACE"
            )
        
        # Check if text is only special characters
        stripped_text = text.strip()
        if self.only_special_chars_pattern.match(stripped_text):
            return ValidationResult(
                is_valid=False,
                error_message=f"{field_name} cannot contain only special characters",
                error_code="ONLY_SPECIAL_CHARS"
            )
        
        # Check if text is only numbers
        if self.only_numbers_pattern.match(stripped_text):
            return ValidationResult(
                is_valid=False,
                error_message=f"{field_name} cannot contain only numbers",
                error_code="ONLY_NUMBERS"
            )
        
        # Check for meaningful content (at least some alphabetic characters)
        if not re.search(r'[a-zA-Z]', text):
            return ValidationResult(
                is_valid=False,
                error_message=f"{field_name} must contain some alphabetic characters",
                error_code="NO_ALPHABETIC_CHARS"
            )
        
        return ValidationResult(is_valid=True)
    
    def validate_target_input(self, target: str) -> ValidationResult:
        """
        Validate target input for stance analysis.
        
        Args:
            target: Target entity to validate
            
        Returns:
            ValidationResult indicating if target is valid
        """
        if not target:
            return ValidationResult(
                is_valid=False,
                error_message="Target cannot be empty",
                error_code="EMPTY_TARGET"
            )
        
        # Check length constraints
        if len(target) < self.MIN_TARGET_LENGTH:
            return ValidationResult(
                is_valid=False,
                error_message=f"Target must be at least {self.MIN_TARGET_LENGTH} character long",
                error_code="TARGET_TOO_SHORT"
            )
            
        if len(target) > self.MAX_TARGET_LENGTH:
            return ValidationResult(
                is_valid=False,
                error_message=f"Target must not exceed {self.MAX_TARGET_LENGTH} characters",
                error_code="TARGET_TOO_LONG"
            )
        
        # Check for excessive whitespace
        if self.excessive_whitespace_pattern.search(target):
            return ValidationResult(
                is_valid=False,
                error_message="Target contains excessive whitespace",
                error_code="EXCESSIVE_WHITESPACE"
            )
        
        # Check if target is only special characters
        stripped_target = target.strip()
        if self.only_special_chars_pattern.match(stripped_target):
            return ValidationResult(
                is_valid=False,
                error_message="Target cannot contain only special characters",
                error_code="ONLY_SPECIAL_CHARS"
            )
        
        return ValidationResult(is_valid=True)
    
    def validate_confidence_score(self, confidence: float) -> ValidationResult:
        """
        Validate confidence score.
        
        Args:
            confidence: Confidence score to validate
            
        Returns:
            ValidationResult indicating if confidence is valid
        """
        if not isinstance(confidence, (int, float)):
            return ValidationResult(
                is_valid=False,
                error_message="Confidence must be a number",
                error_code="INVALID_CONFIDENCE_TYPE"
            )
        
        if confidence < 0.0 or confidence > 1.0:
            return ValidationResult(
                is_valid=False,
                error_message="Confidence must be between 0.0 and 1.0",
                error_code="CONFIDENCE_OUT_OF_RANGE"
            )
        
        return ValidationResult(is_valid=True)
    
    def validate_sentiment_label(self, sentiment: str) -> ValidationResult:
        """
        Validate sentiment label.
        
        Args:
            sentiment: Sentiment label to validate
            
        Returns:
            ValidationResult indicating if sentiment is valid
        """
        valid_sentiments = {"positive", "negative", "normal"}
        
        if sentiment not in valid_sentiments:
            return ValidationResult(
                is_valid=False,
                error_message=f"Sentiment must be one of: {', '.join(valid_sentiments)}",
                error_code="INVALID_SENTIMENT_LABEL"
            )
        
        return ValidationResult(is_valid=True)
    
    def validate_stance_label(self, stance: str) -> ValidationResult:
        """
        Validate stance label.
        
        Args:
            stance: Stance label to validate
            
        Returns:
            ValidationResult indicating if stance is valid
        """
        valid_stances = {"مؤيد", "معارض", "محايد"}
        
        if stance not in valid_stances:
            return ValidationResult(
                is_valid=False,
                error_message=f"Stance must be one of: {', '.join(valid_stances)}",
                error_code="INVALID_STANCE_LABEL"
            )
        
        return ValidationResult(is_valid=True)


def validate_request_data(data: dict, required_fields: List[str]) -> ValidationResult:
    """
    Validate that required fields are present in request data.
    
    Args:
        data: Request data dictionary
        required_fields: List of required field names
        
    Returns:
        ValidationResult indicating if all required fields are present
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        return ValidationResult(
            is_valid=False,
            error_message=f"Missing required fields: {', '.join(missing_fields)}",
            error_code="MISSING_REQUIRED_FIELDS"
        )
    
    return ValidationResult(is_valid=True)


def sanitize_text_input(text: str) -> str:
    """
    Sanitize text input by removing potentially harmful content.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove null bytes and control characters (except common whitespace)
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Normalize whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    return sanitized


def extract_text_statistics(text: str) -> dict:
    """
    Extract basic statistics from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary containing text statistics
    """
    if not text:
        return {
            "character_count": 0,
            "word_count": 0,
            "sentence_count": 0,
            "avg_word_length": 0.0,
            "has_punctuation": False,
            "has_numbers": False,
            "has_special_chars": False
        }
    
    # Basic counts
    character_count = len(text)
    words = text.split()
    word_count = len(words)
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])
    
    # Average word length
    avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0.0
    
    # Content analysis
    has_punctuation = bool(re.search(r'[.!?,:;]', text))
    has_numbers = bool(re.search(r'\d', text))
    has_special_chars = bool(re.search(r'[^\w\s]', text))
    
    return {
        "character_count": character_count,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_word_length": round(avg_word_length, 2),
        "has_punctuation": has_punctuation,
        "has_numbers": has_numbers,
        "has_special_chars": has_special_chars
    }


def is_text_processable(text: str, min_words: int = 1, max_words: int = 1000) -> Tuple[bool, str]:
    """
    Check if text is processable for analysis.
    
    Args:
        text: Text to check
        min_words: Minimum number of words required
        max_words: Maximum number of words allowed
        
    Returns:
        Tuple of (is_processable, reason_if_not)
    """
    if not text or not text.strip():
        return False, "Text is empty"
    
    words = text.split()
    word_count = len(words)
    
    if word_count < min_words:
        return False, f"Text has too few words (minimum: {min_words})"
    
    if word_count > max_words:
        return False, f"Text has too many words (maximum: {max_words})"
    
    # Check for meaningful content
    alphabetic_chars = sum(1 for char in text if char.isalpha())
    if alphabetic_chars < 3:  # At least 3 alphabetic characters
        return False, "Text lacks sufficient alphabetic content"
    
    return True, ""


def normalize_confidence_score(raw_score: float, min_confidence: float = 0.1) -> float:
    """
    Normalize and bound confidence score.
    
    Args:
        raw_score: Raw confidence score
        min_confidence: Minimum confidence to return
        
    Returns:
        Normalized confidence score between min_confidence and 1.0
    """
    # Ensure score is between 0 and 1
    normalized = max(0.0, min(1.0, abs(raw_score)))
    
    # Apply minimum confidence threshold
    return max(min_confidence, normalized)


def create_validation_error_response(validation_result: ValidationResult, request_id: str) -> dict:
    """
    Create a standardized validation error response.
    
    Args:
        validation_result: ValidationResult with error details
        request_id: Request ID for tracking
        
    Returns:
        Dictionary containing validation error response
    """
    from .helpers import get_current_timestamp
    
    return {
        "error": "Validation Error",
        "message": validation_result.error_message,
        "error_code": validation_result.error_code,
        "request_id": request_id,
        "timestamp": get_current_timestamp()
    }