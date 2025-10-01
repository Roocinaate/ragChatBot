import requests
import json

def test_server():
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/",
        "/health", 
        "/test",
        "/docs"
    ]
    
    print("🧪 Testing backend server endpoints...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"✅ {endpoint}: {response.status_code}")
            if response.status_code != 200:
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ {endpoint}: ERROR - {e}")
    
    # Test chat endpoint
    print("\n🤖 Testing chat endpoint...")
    try:
        chat_data = {
            "message": "Hello, are you working?",
            "chat_history": []
        }
        response = requests.post(f"{base_url}/chat", json=chat_data, timeout=10)
        print(f"✅ /chat: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Response: {result['response']}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ /chat: ERROR - {e}")

if __name__ == "__main__":
    test_server()