"""
Quick API test script to verify the fix
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_sentiment_analysis():
    """Test sentiment analysis endpoint"""
    print("Testing Sentiment Analysis...")
    
    url = f"{BASE_URL}/sentiment-analysis"
    data = {
        "text": "I love this product! It works great!"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Sentiment Analysis: SUCCESS")
            return True
        else:
            print("❌ Sentiment Analysis: FAILED")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_stance_analysis():
    """Test stance analysis endpoint"""
    print("\nTesting Stance Analysis...")
    
    url = f"{BASE_URL}/stance-analysis"
    data = {
        "text": "Apple makes innovative products that change the industry",
        "target": "Apple"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Stance Analysis: SUCCESS")
            return True
        else:
            print("❌ Stance Analysis: FAILED")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health():
    """Test health endpoint"""
    print("\nTesting Health Check...")
    
    url = f"{BASE_URL}/health"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Health Check: SUCCESS")
            return True
        else:
            print("❌ Health Check: FAILED")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("API Quick Test")
    print("=" * 60)
    
    # Test all endpoints
    health_ok = test_health()
    sentiment_ok = test_sentiment_analysis()
    stance_ok = test_stance_analysis()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Sentiment Analysis: {'✅ PASS' if sentiment_ok else '❌ FAIL'}")
    print(f"Stance Analysis: {'✅ PASS' if stance_ok else '❌ FAIL'}")
    
    if health_ok and sentiment_ok and stance_ok:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
