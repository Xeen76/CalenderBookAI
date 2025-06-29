"""
Google Calendar Service for booking appointments
"""
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

# Mock mode for development/testing
MOCK_MODE = os.getenv("CALENDAR_MOCK_MODE", "false").lower() == "true"

if not MOCK_MODE:
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        GOOGLE_AVAILABLE = True
    except ImportError:
        print("⚠️  Google Calendar libraries not available, using mock mode")
        GOOGLE_AVAILABLE = False
        MOCK_MODE = True
else:
    GOOGLE_AVAILABLE = False

class GoogleCalendarService:
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        self.mock_mode = MOCK_MODE or not GOOGLE_AVAILABLE
        
        if not self.mock_mode:
            try:
                self.credentials = self._authenticate()
                self.service = build('calendar', 'v3', credentials=self.credentials)
                print("✅ Google Calendar API connected (REAL MODE)")
            except Exception as e:
                print(f"⚠️  Google Calendar setup failed: {e}")
                print("🔄 Falling back to mock mode")
                self.mock_mode = True
        else:
            if MOCK_MODE:
                print("🎭 Using mock calendar mode for development (CALENDAR_MOCK_MODE=true)")
            else:
                print("🎭 Using mock calendar mode for development (Google libraries unavailable)")
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        token_path = 'token.json'
        
        # Load existing token
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                credentials_path = os.getenv('GOOGLE_CALENDAR_CREDENTIALS_PATH')
                if not credentials_path or not os.path.exists(credentials_path):
                    raise Exception("Google Calendar credentials file not found")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        return creds
    
    def get_available_slots(self, 
                          date: datetime, 
                          duration_minutes: int = 60,
                          working_hours: tuple = (9, 17)) -> List[Dict[str, Any]]:
        """Get available time slots for a given date"""
        
        if self.mock_mode:
            return self._get_mock_available_slots(date, duration_minutes, working_hours)
        
        try:
            return self._get_real_available_slots(date, duration_minutes, working_hours)
        except Exception as e:
            print(f"Error getting real calendar data: {e}")
            return self._get_mock_available_slots(date, duration_minutes, working_hours)
    
    def _get_mock_available_slots(self, 
                                date: datetime, 
                                duration_minutes: int = 60,
                                working_hours: tuple = (9, 17)) -> List[Dict[str, Any]]:
        """Generate mock available slots for development"""
        available_slots = []
        start_hour, end_hour = working_hours
        
        # Generate slots every 2 hours within working hours
        current_time = date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        end_time = date.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        
        slot_times = [9, 11, 14, 16]  # 9 AM, 11 AM, 2 PM, 4 PM
        
        for hour in slot_times:
            if hour < end_hour:
                slot_start = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                slot_end = slot_start + timedelta(minutes=duration_minutes)
                
                # Skip if slot is in the past
                if slot_start > datetime.now():
                    available_slots.append({
                        "start_time": slot_start,
                        "end_time": slot_end,
                        "available": True,
                        "title": f"Available {duration_minutes}min slot"
                    })
        
        return available_slots[:3]  # Return max 3 slots
    
    def _get_real_available_slots(self, 
                                date: datetime, 
                                duration_minutes: int = 60,
                                working_hours: tuple = (9, 17)) -> List[Dict[str, Any]]:
        """Get real available slots from Google Calendar"""
        available_slots = []
        start_hour, end_hour = working_hours
        
        # Define the time range for the day
        day_start = date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        day_end = date.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        
        # Get existing events for the day
        events_result = self.service.events().list(
            calendarId=self.calendar_id,
            timeMin=day_start.isoformat() + 'Z',
            timeMax=day_end.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Generate potential slots every 30 minutes
        current_time = day_start
        while current_time + timedelta(minutes=duration_minutes) <= day_end:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            
            # Check if this slot conflicts with any existing event
            is_available = True
            for event in events:
                event_start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')).replace('Z', '+00:00'))
                event_end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')).replace('Z', '+00:00'))
                
                # Check for overlap
                if (current_time < event_end and slot_end > event_start):
                    is_available = False
                    break
            
            if is_available and current_time > datetime.now():
                available_slots.append({
                    "start_time": current_time,
                    "end_time": slot_end,
                    "available": True,
                    "title": f"Available {duration_minutes}min slot"
                })
            
            current_time += timedelta(minutes=30)  # Check every 30 minutes
        
        return available_slots[:5]  # Return max 5 slots
    
    def create_event(self, 
                    title: str, 
                    start_time: datetime, 
                    end_time: datetime,
                    description: str = "",
                    attendees: List[str] = []) -> Dict[str, Any]:
        """Create a calendar event"""
        
        if self.mock_mode:
            return self._create_mock_event(title, start_time, end_time, description, attendees)
        
        try:
            return self._create_real_event(title, start_time, end_time, description, attendees)
        except Exception as e:
            print(f"Error creating real calendar event: {e}")
            return self._create_mock_event(title, start_time, end_time, description, attendees)
    
    def _create_mock_event(self, 
                          title: str, 
                          start_time: datetime, 
                          end_time: datetime,
                          description: str = "",
                          attendees: List[str] = []) -> Dict[str, Any]:
        """Create a mock calendar event for development"""
        event_id = f"mock_event_{int(start_time.timestamp())}"
        
        return {
            'success': True,
            'event_id': event_id,
            'event_link': f"https://calendar.google.com/calendar/event?eid={event_id}",
            'message': f"✅ Mock event '{title}' created for {start_time.strftime('%B %d, %Y at %I:%M %p')}",
            'event_details': {
                'id': event_id,
                'summary': title,
                'start': {'dateTime': start_time.isoformat()},
                'end': {'dateTime': end_time.isoformat()},
                'description': description,
                'attendees': [{'email': email} for email in attendees]
            }
        }
    
    def _create_real_event(self, 
                          title: str, 
                          start_time: datetime, 
                          end_time: datetime,
                          description: str = "",
                          attendees: List[str] = []) -> Dict[str, Any]:
        """Create a real calendar event via Google Calendar API"""
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
            'attendees': [{'email': email} for email in attendees],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        
        created_event = self.service.events().insert(
            calendarId=self.calendar_id, 
            body=event
        ).execute()
        
        return {
            'success': True,
            'event_id': created_event['id'],
            'event_link': created_event.get('htmlLink'),
            'message': f"✅ Event '{title}' created for {start_time.strftime('%B %d, %Y at %I:%M %p')}",
            'event_details': created_event
        }
