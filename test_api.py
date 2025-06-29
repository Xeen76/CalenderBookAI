#!/usr/bin/env python3
"""
Test the Calendar Booking Agent API
"""
import requests
import json

def test_chat_api():
    """Test the chat endpoint"""
    url = "http://localhost:8000/chat"
    
    # Test the example conversations from requirements
    test_messages = [
        "Hey, I want to schedule a call for tomorrow afternoon.",
        "Do you have any free time this Friday?",
        "Book a meeting between 3-5 PM next week."
    ]

    for i, message in enumerate(test_messages):
        payload = {
            "message": message,
            "session_id": f"test{i+1}"
        }

        print(f"\n🧪 Test {i+1}: {message}")
        test_single_message(payload)

def test_single_message(payload):
    """Test a single message"""
    url = "http://localhost:8000/chat"
    
    print("🧪 Testing Calendar Booking Agent API...")
    print(f"📡 Sending request to: {url}")
    print(f"📝 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response:")
            print(f"🤖 Agent: {data.get('response', 'No response')}")
            print(f"📅 Available Slots: {len(data.get('available_slots', []))} slots")
            print(f"🎯 Intent: {data.get('intent', 'Unknown')}")
            print(f"📋 Extracted Info: {data.get('extracted_info', {})}")
            
            if data.get('available_slots'):
                print("\n⏰ Available Time Slots:")
                for i, slot in enumerate(data['available_slots'], 1):
                    print(f"  {i}. {slot.get('display', 'Time slot')}")
            
            print("\n🎉 API is working perfectly!")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint"""
    url = "http://localhost:8000/health"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy!")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except:
        print("❌ Backend is not responding")
        return False

if __name__ == "__main__":
    print("🚀 Calendar Booking Agent API Test")
    print("=" * 50)
    
    # Test health first
    if test_health_endpoint():
        # Test chat functionality
        test_chat_api()
    else:
        print("❌ Cannot test chat - backend is not running")
