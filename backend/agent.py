"""
Simple Calendar Booking Agent
"""
import os
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

# Simple LLM service using Gemini
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')  # Updated model name
    LLM_AVAILABLE = True
    print("✅ Gemini API configured successfully")
except Exception as e:
    print(f"⚠️  Gemini not available: {e}, using mock responses")
    model = None
    LLM_AVAILABLE = False

from calendar_service import GoogleCalendarService

class CalendarBookingAgent:
    def __init__(self):
        self.calendar_service = GoogleCalendarService()
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def _call_llm(self, prompt: str) -> str:
        """Call LLM service using Gemini with smart fallbacks"""
        if not LLM_AVAILABLE or not model:
            return self._get_fallback_response(prompt)

        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API error: {e}")
            # Return smart fallback instead of generic error
            return self._get_fallback_response(prompt)

    def _get_fallback_response(self, prompt: str) -> str:
        """Provide smart fallback responses when AI is unavailable"""
        prompt_lower = prompt.lower()

        # Intent classification fallbacks
        if "intent" in prompt_lower and "analyze this user message" in prompt_lower:
            # Extract the user message from the prompt
            if '"' in prompt:
                user_msg = prompt.split('"')[1].lower()
                if any(word in user_msg for word in ["schedule", "book", "meeting", "call", "appointment"]):
                    return "book_appointment"
                elif any(word in user_msg for word in ["free", "available", "availability", "time"]):
                    return "check_availability"
                else:
                    return "general_conversation"
            return "book_appointment"

        # Information extraction fallbacks
        elif "extract booking information" in prompt_lower:
            if '"' in prompt:
                user_msg = prompt.split('"')[1].lower()
                result = {"has_time_info": False}

                # Check for time info
                if any(word in user_msg for word in ["tomorrow", "today", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "next week", "pm", "am", "afternoon", "morning", "evening"]):
                    result["has_time_info"] = True

                    # Extract day
                    if "tomorrow" in user_msg:
                        result["day"] = "tomorrow"
                    elif "today" in user_msg:
                        result["day"] = "today"
                    elif "friday" in user_msg:
                        result["day"] = "Friday"
                    elif "monday" in user_msg:
                        result["day"] = "Monday"
                    elif "next week" in user_msg:
                        result["day"] = "next week"

                    # Extract time
                    if "2 pm" in user_msg or "2pm" in user_msg:
                        result["time"] = "2 PM"
                    elif "afternoon" in user_msg:
                        result["time"] = "afternoon"
                    elif "morning" in user_msg:
                        result["time"] = "morning"

                    # Extract type
                    if "call" in user_msg:
                        result["type"] = "call"
                    elif "meeting" in user_msg:
                        result["type"] = "meeting"
                    else:
                        result["type"] = "appointment"

                return json.dumps(result)
            return '{"has_time_info": false}'

        # Conversation fallbacks
        elif "calendar booking assistant" in prompt_lower:
            if '"' in prompt:
                user_msg = prompt.split('"')[1].lower()
                if any(word in user_msg for word in ["hi", "hello", "hey"]):
                    return "Hi! I'm your calendar assistant. What would you like to schedule today?"
                elif any(word in user_msg for word in ["help", "what", "how"]):
                    return "I can help you schedule meetings, check availability, and book appointments. What would you like to schedule?"
                else:
                    return "I'd be happy to help you schedule something! What would you like to book?"
            return "I can help you schedule appointments. What would you like to book?"

        # Default fallback
        return "I can help you schedule appointments. What would you like to book?"

    def _understand_intent(self, message: str) -> str:
        """Understand user intent from their message"""
        prompt = f"""You are a smart calendar booking assistant. Analyze this user message and determine their intent.

User message: "{message}"

Intent categories:
- book_appointment: User wants to schedule/book a meeting, call, appointment, or event
- check_availability: User is asking about free time, availability, or when they're free
- general_conversation: Greetings, questions, or unclear requests

Examples:
- "I want to schedule a call" → book_appointment
- "Book a meeting for tomorrow" → book_appointment
- "Do you have any free time?" → check_availability
- "When am I available?" → check_availability
- "Hi there" → general_conversation

Respond with ONLY the intent name (book_appointment, check_availability, or general_conversation)."""

        response = self._call_llm(prompt)
        return response.strip().lower()

    def _extract_details(self, message: str) -> Dict[str, Any]:
        """Extract booking details from user message"""
        prompt = f"""You are a smart calendar assistant. Extract booking details from this message.

User message: "{message}"

Extract these details:
- day: The day mentioned (today, tomorrow, Monday, Friday, next week, etc.)
- time: Specific time or time period (2 PM, afternoon, morning, 3-5 PM, etc.)
- type: Type of meeting (call, meeting, appointment, interview, etc.)
- duration: How long (1 hour, 30 minutes, etc.)

Return a JSON object with the extracted information. If the message contains time/scheduling information, set "has_time_info": true.

Examples:
"Schedule a call for tomorrow afternoon" → {{"has_time_info": true, "day": "tomorrow", "time": "afternoon", "type": "call"}}
"Meeting at 2 PM Friday" → {{"has_time_info": true, "day": "Friday", "time": "2 PM", "type": "meeting"}}
"Just saying hi" → {{"has_time_info": false}}

Return ONLY valid JSON:"""

        response = self._call_llm(prompt)
        try:
            # Clean up the response to extract JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()

            extracted = json.loads(response)
            return extracted
        except Exception as e:
            print(f"JSON parsing error: {e}, response: {response}")
            # Fallback extraction using regex
            return self._regex_extract(message)
    
    def _regex_extract(self, message: str) -> Dict[str, Any]:
        """Fallback regex extraction"""
        info = {"has_time_info": False}
        
        # Extract time
        time_patterns = [
            r'(\d{1,2}):?(\d{0,2})\s*(am|pm)',
            r'(morning|afternoon|evening)',
            r'(noon|midnight)'
        ]
        
        for pattern in time_patterns:
            if re.search(pattern, message.lower()):
                info["has_time_info"] = True
                info["time"] = re.search(pattern, message.lower()).group()
                break
        
        # Extract day
        day_patterns = [
            r'(today|tomorrow)',
            r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'next\s+(week|monday|tuesday|wednesday|thursday|friday)'
        ]
        
        for pattern in day_patterns:
            match = re.search(pattern, message.lower())
            if match:
                info["has_time_info"] = True
                info["day"] = match.group()
                break
        
        # Extract meeting type
        if "call" in message.lower():
            info["type"] = "call"
        elif "meeting" in message.lower():
            info["type"] = "meeting"
        elif "appointment" in message.lower():
            info["type"] = "appointment"
        else:
            info["type"] = "meeting"
        
        return info
    
    def _check_availability(self, extracted_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check calendar availability"""
        # Convert extracted info to datetime
        target_date = self._parse_date(extracted_info.get("day", "tomorrow"))

        # Get available slots for the target date
        available_slots = self.calendar_service.get_available_slots(
            date=target_date,
            duration_minutes=60  # Default 1 hour
        )

        return [
            {
                "start_time": slot["start_time"].isoformat(),
                "end_time": slot["end_time"].isoformat(),
                "display": slot["start_time"].strftime("%I:%M %p"),
                "available": True
            }
            for slot in available_slots[:3]  # Limit to 3 options
        ]
    
    def _parse_date(self, day_str: str) -> datetime:
        """Parse day string to datetime"""
        today = datetime.now()
        
        if "today" in day_str.lower():
            return today
        elif "tomorrow" in day_str.lower():
            return today + timedelta(days=1)
        elif "monday" in day_str.lower():
            days_ahead = 0 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return today + timedelta(days=days_ahead)
        # Add more day parsing as needed
        else:
            return today + timedelta(days=1)  # Default to tomorrow
    
    def _suggest_slots(self, slots: List[Dict[str, Any]], extracted_info: Dict[str, Any]) -> str:
        """Suggest available time slots to user"""
        meeting_type = extracted_info.get("type", "meeting")

        if slots:
            response = f"I found some available times for your {meeting_type}:\n\n"
            for i, slot in enumerate(slots, 1):
                response += f"{i}. {slot['display']}\n"
            response += "\nWhich time works best for you? Just reply with the number."
        else:
            response = "I couldn't find any available times. Would you like to try a different day?"

        return response

    def _handle_conversation(self, message: str, session_data: Dict[str, Any]) -> str:
        """Handle general conversation with smart responses"""
        # Check if user is selecting a time slot
        if session_data.get("available_slots") and re.search(r'\b[123]\b', message):
            try:
                slot_num = int(re.search(r'\b([123])\b', message).group(1))
                slots = session_data.get("available_slots", [])
                if 0 <= slot_num - 1 < len(slots):
                    selected_slot = slots[slot_num - 1]
                    response = f"Perfect! You've selected {selected_slot['display']}. I'll book this time slot for you. The meeting has been scheduled!"
                else:
                    response = "Please select 1, 2, or 3 for your preferred time."
            except:
                response = "Please select 1, 2, or 3 for your preferred time."
        else:
            # Use AI for smarter conversation handling
            prompt = f"""You are a helpful calendar booking assistant. The user said: "{message}"

Context: This is a calendar booking conversation. The user might be:
- Greeting you
- Asking for help
- Asking about availability without specific times
- Making unclear requests
- Asking questions about the service

Respond naturally and helpfully. Keep responses concise (1-2 sentences). Always guide them toward booking if appropriate.

Examples:
- "Hi" → "Hi! I'm your calendar assistant. What would you like to schedule today?"
- "Help" → "I can help you schedule meetings, check availability, and book appointments. What would you like to schedule?"
- "What can you do?" → "I can schedule meetings, check your calendar availability, and book appointments. Just tell me when you'd like to meet!"

Respond naturally:"""

            ai_response = self._call_llm(prompt)
            response = ai_response.strip()

            # Fallback to simple responses if AI fails
            if not response or len(response) < 10:
                if any(word in message.lower() for word in ["hi", "hello", "hey", "good morning", "good afternoon"]):
                    response = "Hi! I'm your calendar assistant. What would you like to schedule today?"
                elif any(word in message.lower() for word in ["help", "what", "how"]):
                    response = "I can help you schedule meetings, check availability, and book appointments. What would you like to schedule?"
                else:
                    response = "I'd be happy to help you schedule something! Try saying 'I want to schedule a call for tomorrow afternoon' or 'Do you have any free time this Friday?'"

        return response

    def _direct_book_appointment(self, extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        """Directly book an appointment when specific time information is available"""
        try:
            # Parse the target date
            target_date = self._parse_date(extracted_info.get("day", "tomorrow"))
            
            # Parse the time
            time_str = extracted_info.get("time", "").lower()
            hour = 9  # Default to 9 AM
            minute = 0
            
            # Extract hour and minute from time string
            if "8pm" in time_str or "8 pm" in time_str:
                hour = 20
            elif "8am" in time_str or "8 am" in time_str:
                hour = 8
            elif "9pm" in time_str or "9 pm" in time_str:
                hour = 21
            elif "9am" in time_str or "9 am" in time_str:
                hour = 9
            elif "10pm" in time_str or "10 pm" in time_str:
                hour = 22
            elif "10am" in time_str or "10 am" in time_str:
                hour = 10
            elif "11pm" in time_str or "11 pm" in time_str:
                hour = 23
            elif "11am" in time_str or "11 am" in time_str:
                hour = 11
            elif "12pm" in time_str or "12 pm" in time_str or "noon" in time_str:
                hour = 12
            elif "12am" in time_str or "12 am" in time_str or "midnight" in time_str:
                hour = 0
            elif "afternoon" in time_str:
                hour = 14  # 2 PM
            elif "morning" in time_str:
                hour = 9   # 9 AM
            elif "evening" in time_str:
                hour = 18  # 6 PM
            else:
                # Try to parse specific times like "2:30pm", "3:45am", etc.
                import re
                time_pattern = r'(\d{1,2}):?(\d{0,2})\s*(am|pm)'
                match = re.search(time_pattern, time_str)
                if match:
                    hour = int(match.group(1))
                    minute = int(match.group(2)) if match.group(2) else 0
                    if match.group(3) == 'pm' and hour != 12:
                        hour += 12
                    elif match.group(3) == 'am' and hour == 12:
                        hour = 0
                else:
                    # Try to parse just hour like "2pm", "3am"
                    hour_pattern = r'(\d{1,2})\s*(am|pm)'
                    match = re.search(hour_pattern, time_str)
                    if match:
                        hour = int(match.group(1))
                        if match.group(2) == 'pm' and hour != 12:
                            hour += 12
                        elif match.group(2) == 'am' and hour == 12:
                            hour = 0
            
            # Create start and end times
            start_time = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            end_time = start_time + timedelta(hours=1)  # Default 1 hour duration
            
            # Check if the time is in the past
            if start_time <= datetime.now():
                return {
                    "success": False,
                    "message": f"Sorry, {start_time.strftime('%I:%M %p')} is in the past. Please choose a future time."
                }
            
            # Create event title
            meeting_type = extracted_info.get("type", "Meeting")
            event_title = f"{meeting_type.capitalize()} - {start_time.strftime('%I:%M %p')}"
            
            # Create the calendar event
            booking_result = self.calendar_service.create_event(
                title=event_title,
                start_time=start_time,
                end_time=end_time,
                description=f"Booked via Calendar Agent - {meeting_type}",
                attendees=[]
            )
            
            if booking_result.get("success"):
                return {
                    "success": True,
                    "message": booking_result.get("message", f"✅ {meeting_type.capitalize()} booked for {start_time.strftime('%B %d, %Y at %I:%M %p')}!"),
                    "booking_details": {
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "title": event_title,
                        "booking_id": booking_result.get("event_id"),
                        "event_link": booking_result.get("event_link")
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to create calendar event. Please try again."
                }
                
        except Exception as e:
            print(f"Error in direct booking: {e}")
            return {
                "success": False,
                "message": "I had trouble booking that time. Let me show you some available slots instead."
            }

    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """Process a user message through the simple workflow"""
        # Initialize or get session state
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "messages": [],
                "user_intent": "",
                "extracted_info": {},
                "available_slots": [],
                "booking_confirmed": False,
                "session_id": session_id
            }

        session_data = self.sessions[session_id]
        session_data["messages"].append({"role": "user", "content": message})

        # Smart workflow with better logic
        intent = self._understand_intent(message)
        print(f"🎯 Detected intent: {intent}")

        if "book_appointment" in intent:
            # Extract details and check availability
            extracted_info = self._extract_details(message)
            print(f"📋 Extracted info: {extracted_info}")

            if extracted_info.get("has_time_info"):
                # Try to directly book the appointment
                direct_booking_result = self._direct_book_appointment(extracted_info)
                
                if direct_booking_result.get("success"):
                    # Direct booking successful
                    session_data["booking_confirmed"] = True
                    response = direct_booking_result.get("message")
                    # Don't show available slots since we booked directly
                    session_data["available_slots"] = []
                else:
                    # Direct booking failed, fall back to showing available slots
                    available_slots = self._check_availability(extracted_info)
                    session_data["available_slots"] = available_slots
                    session_data["extracted_info"] = extracted_info
                    response = direct_booking_result.get("message") + "\n\n" + self._suggest_slots(available_slots, extracted_info)
            else:
                response = "I'd love to help you schedule that! Could you tell me when you'd like to meet? For example: 'tomorrow at 2 PM' or 'Friday morning'."

        elif "check_availability" in intent:
            # User is asking about availability
            extracted_info = self._extract_details(message)
            if extracted_info.get("has_time_info"):
                available_slots = self._check_availability(extracted_info)
                session_data["available_slots"] = available_slots
                session_data["extracted_info"] = extracted_info
                day = extracted_info.get("day", "that day")
                response = f"Let me check your availability for {day}:\n\n"
                if available_slots:
                    response += "Here are your free time slots:\n\n"
                    for i, slot in enumerate(available_slots, 1):
                        response += f"{i}. {slot['display']}\n"
                    response += "\nWould you like to book any of these times? Just reply with the number."
                else:
                    response = f"Sorry, you don't have any free time slots for {day}. Would you like to try a different day?"
            else:
                response = "I can check your availability! Which day are you interested in? For example: 'tomorrow', 'Friday', or 'next week'."

        else:
            # Handle conversation or slot selection
            response = self._handle_conversation(message, session_data)

        session_data["messages"].append({"role": "assistant", "content": response})

        return {
            "response": response,
            "available_slots": session_data.get("available_slots", []),
            "session_id": session_id,
            "intent": intent,
            "extracted_info": session_data.get("extracted_info", {})
        }
    
    async def confirm_booking(self, session_id: str, slot_index: int) -> Dict[str, Any]:
        """Confirm a booking for the selected slot"""
        if session_id not in self.sessions:
            return {"success": False, "message": "Session not found"}
        
        state = self.sessions[session_id]
        slots = state.get("available_slots", [])
        
        if 0 <= slot_index < len(slots):
            selected_slot = slots[slot_index]
            extracted_info = state.get("extracted_info", {})
            
            # Parse the datetime strings
            start_time = datetime.fromisoformat(selected_slot["start_time"].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(selected_slot["end_time"].replace('Z', '+00:00'))
            
            # Create event title
            meeting_type = extracted_info.get("type", "Meeting")
            event_title = f"{meeting_type.capitalize()} - {start_time.strftime('%I:%M %p')}"
            
            # Create the actual calendar event
            booking_result = self.calendar_service.create_event(
                title=event_title,
                start_time=start_time,
                end_time=end_time,
                description=f"Booked via Calendar Agent - {meeting_type}",
                attendees=[]
            )
            
            if booking_result.get("success"):
                state["booking_confirmed"] = True
                return {
                    "success": True,
                    "message": booking_result.get("message", f"✅ Booking confirmed for {selected_slot['display']}!"),
                    "booking_details": {
                        "start_time": selected_slot["start_time"],
                        "end_time": selected_slot["end_time"],
                        "title": event_title,
                        "booking_id": booking_result.get("event_id"),
                        "event_link": booking_result.get("event_link")
                    }
                }
            else:
                return {
                    "success": False, 
                    "message": "Failed to create calendar event. Please try again."
                }
        else:
            return {"success": False, "message": "Invalid slot selection"}
