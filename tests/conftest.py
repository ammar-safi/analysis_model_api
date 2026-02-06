"""
Pytest configuration and fixtures for testing
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock

from main import app


@pytest.fixture
def client():
    """Fixture to provide FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def mock_sentiment_service():
    """Fixture to provide mock sentiment service"""
    mock_service = Mock()
    mock_service.analyze_sentiment.return_value = Mock(
        sentiment='positive',
        confidence=0.8,
        scores={'compound': 0.8, 'pos': 0.7, 'neu': 0.2, 'neg': 0.1},
        fallback_used=False,
        warning=None
    )
    return mock_service


@pytest.fixture
def mock_stance_service():
    """Fixture to provide mock stance service"""
    mock_service = Mock()
    mock_service.analyze_stance.return_value = Mock(
        stance='supportive',
        confidence=0.7,
        target='Apple',
        target_mentions=1,
        context_sentiment=0.5,
        keyword_score=0.6,
        combined_score=0.55,
        consistency=1.0,
        fallback_used=False,
        warning=None
    )
    return mock_service


@pytest.fixture
def sample_sentiment_request():
    """Fixture to provide sample sentiment request data"""
    return {"text": "This is a great product! I love it."}


@pytest.fixture
def sample_stance_request():
    """Fixture to provide sample stance request data"""
    return {"text": "Apple makes amazing phones and computers.", "target": "Apple"}


@pytest.fixture
def sample_error_response():
    """Fixture to provide sample error response structure"""
    return {
        "error": "ValidationError",
        "message": "Sample error message",
        "details": {"field": "text"},
        "request_id": "test_request_id",
        "timestamp": "2024-01-01T00:00:00Z"
    }


# Test data fixtures
@pytest.fixture
def positive_texts():
    """Fixture providing positive sentiment test texts"""
    return [
        "I love this product!",
        "This is amazing and wonderful!",
        "Excellent quality and great service!",
        "Best purchase I've ever made!",
        "Absolutely fantastic experience!"
    ]


@pytest.fixture
def negative_texts():
    """Fixture providing negative sentiment test texts"""
    return [
        "I hate this product!",
        "This is terrible and awful!",
        "Worst quality and bad service!",
        "Terrible purchase, waste of money!",
        "Absolutely horrible experience!"
    ]


@pytest.fixture
def neutral_texts():
    """Fixture providing neutral sentiment test texts"""
    return [
        "This is a product.",
        "The item exists in the store.",
        "It has features and functions.",
        "The company makes products.",
        "This is information about the item."
    ]


@pytest.fixture
def supportive_stance_cases():
    """Fixture providing supportive stance test cases"""
    return [
        {"text": "I love Apple products! They are amazing.", "target": "Apple"},
        {"text": "Microsoft makes excellent software.", "target": "Microsoft"},
        {"text": "Google has the best search engine.", "target": "Google"},
        {"text": "Tesla cars are innovative and eco-friendly.", "target": "Tesla"},
        {"text": "Amazon provides great customer service.", "target": "Amazon"}
    ]


@pytest.fixture
def opposing_stance_cases():
    """Fixture providing opposing stance test cases"""
    return [
        {"text": "I hate Apple products! They are overpriced.", "target": "Apple"},
        {"text": "Microsoft software is buggy and unreliable.", "target": "Microsoft"},
        {"text": "Google violates user privacy constantly.", "target": "Google"},
        {"text": "Tesla cars are dangerous and poorly made.", "target": "Tesla"},
        {"text": "Amazon treats workers terribly.", "target": "Amazon"}
    ]


@pytest.fixture
def neutral_stance_cases():
    """Fixture providing neutral stance test cases"""
    return [
        {"text": "Apple is a technology company.", "target": "Apple"},
        {"text": "Microsoft was founded in 1975.", "target": "Microsoft"},
        {"text": "Google is based in California.", "target": "Google"},
        {"text": "Tesla manufactures electric vehicles.", "target": "Tesla"},
        {"text": "Amazon is an e-commerce platform.", "target": "Amazon"}
    ]


@pytest.fixture
def edge_case_texts():
    """Fixture providing edge case texts for testing"""
    return [
        "",  # Empty
        "   ",  # Whitespace only
        "A",  # Single character
        "OK",  # Very short
        "!@#$%^&*()",  # Only symbols
        "123456789",  # Only numbers
        "😀😃😄😁😆",  # Only emojis
        "A" * 4999,  # Maximum length
        "Mixed 123 !@# content 😀",  # Mixed content
        "Repeated repeated repeated repeated text"  # Repeated words
    ]


@pytest.fixture
def special_character_texts():
    """Fixture providing texts with special characters"""
    return [
        "Price: $99.99 - Great deal!!!",
        "Email: test@example.com Phone: +1-555-0123",
        "Visit https://example.com for more info",
        "Follow @username and check #hashtag",
        "Café naïve résumé jalapeño",  # Accented characters
        "Здравствуй мир",  # Non-Latin script
        "🚀 Launch successful! 🎉 Celebration time! 🎊",  # Emojis
        "Line 1\nLine 2\tTabbed\rCarriage return"  # Control characters
    ]


# Configuration for pytest
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "edge_case: marks tests as edge case tests"
    )


# Pytest collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add markers based on test file names
        if "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "test_edge_cases" in item.nodeid or "test_error_handling" in item.nodeid:
            item.add_marker(pytest.mark.edge_case)
        else:
            item.add_marker(pytest.mark.unit)
        
        # Mark slow tests
        if "test_large_batch" in item.name or "test_concurrent" in item.name:
            item.add_marker(pytest.mark.slow)