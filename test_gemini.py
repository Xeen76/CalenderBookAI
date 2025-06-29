#!/usr/bin/env python3
"""
Test Gemini API directly
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini():
    """Test Gemini API"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        print(f"🔑 API Key: {api_key[:10]}..." if api_key else "❌ No API key found")
        print(f"🔑 Full Key: {api_key}" if api_key else "❌ No API key found")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("✅ Gemini configured successfully")
        
        # Test a simple prompt
        prompt = """
        Analyze this user message and determine their intent: "I want to schedule a call for tomorrow afternoon"
        
        Possible intents:
        - book_appointment: wants to schedule something
        - check_availability: wants to see free times
        - general_conversation: just chatting or unclear
        
        Respond with just the intent name.
        """
        
        print("🧪 Testing Gemini with intent classification...")
        response = model.generate_content(prompt)
        print(f"📝 Response: {response.text}")
        
        # Test extraction
        extract_prompt = """
        Extract booking information from: "I want to schedule a call for tomorrow afternoon"
        
        Look for:
        - Date/day (today, tomorrow, Monday, etc.)
        - Time (2 PM, afternoon, morning, etc.)
        - Duration (1 hour, 30 minutes, etc.)
        - Meeting type (call, meeting, appointment, etc.)
        
        Return JSON with extracted info or {"has_time_info": false} if unclear.
        """
        
        print("\n🧪 Testing Gemini with information extraction...")
        response2 = model.generate_content(extract_prompt)
        print(f"📝 Response: {response2.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Gemini API Integration")
    print("=" * 50)
    test_gemini()
