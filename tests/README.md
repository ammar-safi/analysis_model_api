# Test Suite Documentation

This directory contains comprehensive tests for the Sentiment and Stance Analysis API.

## Test Structure

### Unit Tests
- `test_sentiment_service.py` - Tests for SentimentService class
- `test_stance_service.py` - Tests for StanceService class  
- `test_text_processor.py` - Tests for TextProcessor utility class

### Integration Tests
- `test_integration_endpoints.py` - End-to-end tests for API endpoints
  - Note: Currently has TestClient compatibility issues with httpx version

### Error Handling & Edge Cases
- `test_error_handling_edge_cases.py` - Comprehensive edge case and error testing

### Test Configuration
- `conftest.py` - Pytest configuration and fixtures
- `pytest.ini` - Pytest settings and markers
- `requirements-test.txt` - Testing dependencies

## Running Tests

### Run All Unit Tests
```bash
pytest tests/test_sentiment_service.py tests/test_stance_service.py tests/test_text_processor.py -v
```

### Run Service Edge Cases
```bash
pytest tests/test_error_handling_edge_cases.py::TestServiceEdgeCases -v
```

### Run Specific Test
```bash
pytest tests/test_sentiment_service.py::TestSentimentService::test_analyze_sentiment_positive_text -v
```

### Run with Coverage
```bash
pytest --cov=app tests/ --cov-report=html
```

## Test Categories

### Sentiment Service Tests
- ✅ Positive, negative, and neutral text analysis
- ✅ Empty and whitespace-only text handling
- ✅ Very short and very long text handling
- ✅ High symbol ratio text handling
- ✅ Text preprocessing and validation
- ✅ Confidence calculation
- ✅ Special case handling
- ✅ Caching functionality

### Stance Service Tests
- ✅ Supportive, opposing, and neutral stance detection
- ✅ Target not found in text scenarios
- ✅ Multiple target mentions handling
- ✅ Case sensitivity testing
- ✅ Keyword-based analysis
- ✅ Context sentiment analysis
- ✅ Stance consistency checking
- ✅ Confidence calculation with various factors

### Text Processor Tests
- ✅ English language detection
- ✅ Text cleaning and normalization
- ✅ Contraction expansion
- ✅ URL, email, mention, hashtag removal
- ✅ Special character handling
- ✅ Target variation generation
- ✅ Sentence extraction

### Edge Cases & Error Handling
- ✅ None/null input handling
- ✅ Extremely long text processing
- ✅ High symbol ratio text
- ✅ Only symbols/numbers text
- ✅ Mixed content handling
- ✅ Repeated characters
- ✅ Punctuation-heavy text
- ✅ Case sensitivity scenarios
- ✅ Memory and performance testing

### Integration Tests (Note: TestClient compatibility issues)
- 🔄 Sentiment analysis endpoint testing
- 🔄 Stance analysis endpoint testing  
- 🔄 Health check endpoint testing
- 🔄 Error response format validation
- 🔄 Concurrent request handling

## Test Results Summary

### Unit Tests Status
- **Sentiment Service**: 29/32 tests passing (3 minor cache mocking issues)
- **Stance Service**: All core functionality tests passing
- **Text Processor**: All tests passing
- **Edge Cases**: 10/11 service-level tests passing

### Known Issues
1. **TestClient Compatibility**: Integration tests fail due to httpx/starlette version compatibility
2. **Cache Mocking**: Some cache-related tests need mock path adjustments
3. **Warning Messages**: Minor differences in expected vs actual warning text

### Coverage Areas
- ✅ Core functionality (sentiment/stance analysis)
- ✅ Input validation and sanitization
- ✅ Error handling and edge cases
- ✅ Text preprocessing and cleaning
- ✅ Special character and symbol handling
- ✅ Performance with various text lengths
- ✅ Confidence calculation accuracy
- 🔄 API endpoint integration (blocked by TestClient issue)

## Recommendations

1. **Fix TestClient Issue**: Update httpx/starlette versions or use alternative testing approach
2. **Improve Cache Tests**: Adjust mock paths for cache-related tests
3. **Add Performance Tests**: Include load testing and memory usage validation
4. **Expand Language Tests**: Add more non-English text handling tests
5. **Add Regression Tests**: Create tests for specific bug scenarios

## Test Data

The test suite includes comprehensive test data covering:
- Positive/negative/neutral sentiment examples
- Supportive/opposing/neutral stance examples
- Edge case texts (empty, symbols, long, short)
- Special character combinations
- Real-world text scenarios
- Error condition triggers

All tests are designed to validate the requirements specified in the project documentation and ensure robust handling of various input scenarios.