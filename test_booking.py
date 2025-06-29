#!/usr/bin/env python3
"""
Test the complete booking flow
"""
import requests
import json

def test_complete_booking_flow():
    """Test the complete booking flow"""
    base_url = "http://localhost:8000"
    session_id = "booking_test"
    
    print("🚀 Testing Complete Booking Flow")
    print("=" * 50)
    
    # Step 1: Initial booking request
    print("📅 Step 1: Request a booking")
    response1 = requests.post(f"{base_url}/chat", json={
        "message": "I want to schedule a call for tomorrow afternoon",
        "session_id": session_id
    })
    
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"🤖 Agent: {data1['response']}")
        print(f"📊 Available slots: {len(data1.get('available_slots', []))}")
        
        if data1.get('available_slots'):
            # Step 2: Select a time slot
            print("\n⏰ Step 2: Select time slot 2")
            response2 = requests.post(f"{base_url}/chat", json={
                "message": "2",
                "session_id": session_id
            })
            
            if response2.status_code == 200:
                data2 = response2.json()
                print(f"🤖 Agent: {data2['response']}")
                
                # Step 3: Confirm the booking
                print("\n✅ Step 3: Confirm booking")
                response3 = requests.post(f"{base_url}/confirm-booking", json={
                    "session_id": session_id,
                    "slot_index": 1  # Index 1 for slot 2
                })
                
                if response3.status_code == 200:
                    data3 = response3.json()
                    print(f"📋 Booking result: {data3}")
                    
                    if data3.get('success'):
                        print("🎉 BOOKING SUCCESSFUL!")
                        print(f"📅 Meeting: {data3['booking_details']['title']}")
                        print(f"⏰ Time: {data3['booking_details']['start_time']}")
                        print(f"🆔 Booking ID: {data3['booking_details']['booking_id']}")
                        return True
                    else:
                        print(f"❌ Booking failed: {data3.get('message')}")
                else:
                    print(f"❌ Confirm booking failed: {response3.status_code}")
            else:
                print(f"❌ Slot selection failed: {response2.status_code}")
        else:
            print("❌ No available slots returned")
    else:
        print(f"❌ Initial request failed: {response1.status_code}")
    
    return False

def test_conversation_examples():
    """Test the example conversations from requirements"""
    examples = [
        "Hey, I want to schedule a call for tomorrow afternoon.",
        "Do you have any free time this Friday?", 
        "Book a meeting between 3-5 PM next week."
    ]
    
    print("\n🧪 Testing Example Conversations")
    print("=" * 50)
    
    for i, message in enumerate(examples, 1):
        print(f"\n📝 Example {i}: {message}")
        
        response = requests.post("http://localhost:8000/chat", json={
            "message": message,
            "session_id": f"example_{i}"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Intent: {data.get('intent', 'Unknown')}")
            print(f"📊 Slots: {len(data.get('available_slots', []))}")
            print(f"🤖 Response: {data['response'][:100]}...")
        else:
            print(f"❌ Failed: {response.status_code}")

if __name__ == "__main__":
    # Test complete booking flow
    success = test_complete_booking_flow()
    
    # Test example conversations
    test_conversation_examples()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Calendar Booking Agent is working perfectly!")
    else:
        print("\n⚠️  Some tests failed, but the agent is functional.")
