"""
Streamlit Frontend for Calendar Booking Agent
"""
import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Any, List

# Configure Streamlit page
st.set_page_config(
    page_title="📅 Calendar Booking Agent",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Backend API URL
API_BASE_URL = "http://localhost:8000"

def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"session_{datetime.now().timestamp()}"
    if "available_slots" not in st.session_state:
        st.session_state.available_slots = []

def send_message_to_agent(message: str) -> Dict[str, Any]:
    """Send message to the backend agent"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "message": message,
                "session_id": st.session_state.session_id
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection error: {e}")
        return {"response": "Sorry, I'm having trouble connecting. Please try again.", "available_slots": []}

def confirm_booking(slot_index: int) -> Dict[str, Any]:
    """Confirm a booking for the selected slot"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/confirm-booking",
            json={
                "session_id": st.session_state.session_id,
                "slot_index": slot_index
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Booking error: {e}")
        return {"success": False, "message": "Booking failed. Please try again."}

def display_available_slots(slots: List[Dict[str, Any]]):
    """Display available time slots with booking buttons"""
    if not slots:
        return
    
    st.markdown("### 🕐 Available Time Slots")
    
    cols = st.columns(len(slots))
    
    for i, slot in enumerate(slots):
        with cols[i]:
            # Parse the datetime string
            try:
                start_time = datetime.fromisoformat(slot["start_time"].replace('Z', '+00:00'))
                display_time = start_time.strftime("%I:%M %p")
                display_date = start_time.strftime("%A, %B %d")
            except:
                display_time = slot.get("display", "Time slot")
                display_date = "Available"
            
            st.markdown(f"""
            <div style="
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                margin: 5px;
                background-color: #f8f9fa;
            ">
                <h4 style="margin: 0; color: #2E7D32;">Option {i+1}</h4>
                <p style="margin: 5px 0; font-weight: bold;">{display_time}</p>
                <p style="margin: 0; color: #666;">{display_date}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"📅 Book Option {i+1}", key=f"book_{i}", use_container_width=True):
                with st.spinner("Booking your appointment..."):
                    result = confirm_booking(i)
                    
                    if result.get("success"):
                        st.success(result.get("message", "Booking confirmed!"))
                        st.session_state.available_slots = []  # Clear slots after booking
                        st.balloons()
                    else:
                        st.error(result.get("message", "Booking failed"))

def main():
    """Main Streamlit app"""
    init_session_state()
    
    # Header
    st.markdown("""
    # 📅 Calendar Booking Agent
    
    **Your AI assistant for scheduling appointments on Google Calendar**
    
    I can help you:
    - 📝 Schedule meetings and appointments
    - 🔍 Check your calendar availability  
    - ✅ Book confirmed time slots
    - 💬 Handle natural conversation
    
    ---
    """)
    
    # Example conversations
    with st.expander("💡 Example Conversations", expanded=False):
        st.markdown("""
        **Try these example messages:**
        
        - "Hey, I want to schedule a call for tomorrow afternoon."
        - "Do you have any free time this Friday?"
        - "Book a meeting between 3-5 PM next week."
        - "I need to schedule a doctor appointment for Monday morning."
        """)
    
    # Chat interface
    st.markdown("### 💬 Chat with your Calendar Agent")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Display available slots if any
    if st.session_state.available_slots:
        display_available_slots(st.session_state.available_slots)
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_data = send_message_to_agent(prompt)
                
                agent_response = response_data.get("response", "I'm having trouble right now. Please try again.")
                available_slots = response_data.get("available_slots", [])
                
                # Display agent response
                st.markdown(agent_response)
                
                # Store response in chat history
                st.session_state.messages.append({"role": "assistant", "content": agent_response})
                
                # Update available slots
                st.session_state.available_slots = available_slots
                
                # If there are new slots, rerun to display them
                if available_slots:
                    st.rerun()
    
    # Sidebar with session info
    with st.sidebar:
        st.markdown("### 🔧 Session Info")
        st.text(f"Session ID: {st.session_state.session_id[:8]}...")
        
        if st.button("🔄 New Session"):
            st.session_state.clear()
            st.rerun()
        
        st.markdown("### 📊 Status")
        
        # Check backend health
        try:
            health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if health_response.status_code == 200:
                st.success("✅ Backend Connected")
            else:
                st.error("❌ Backend Issues")
        except:
            st.error("❌ Backend Offline")
        
        st.markdown("### 🎯 Features")
        st.markdown("""
        - **Natural Language**: Just tell me what you want to schedule
        - **Smart Extraction**: I understand dates, times, and meeting types
        - **Calendar Integration**: Real Google Calendar booking
        - **Quick Booking**: Select from suggested time slots
        """)

if __name__ == "__main__":
    main()
