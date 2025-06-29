"""
FastAPI Backend for Calendar Booking Agent
"""
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agent import CalendarBookingAgent

app = FastAPI(title="Calendar Booking Agent", version="1.0.0")

# CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"

class BookingConfirmation(BaseModel):
    session_id: str
    slot_index: int

# Initialize the agent
agent = CalendarBookingAgent()

@app.post("/chat")
async def chat(request: ChatMessage) -> Dict[str, Any]:
    """
    Main chat endpoint for conversational booking
    """
    try:
        response = await agent.process_message(
            message=request.message,
            session_id=request.session_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/confirm-booking")
async def confirm_booking(request: BookingConfirmation) -> Dict[str, Any]:
    """
    Confirm a booking for a selected time slot
    """
    try:
        response = await agent.confirm_booking(
            session_id=request.session_id,
            slot_index=request.slot_index
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    print("🚀 Starting Calendar Booking Agent API...")
    print("📅 Google Calendar integration enabled")
    print("🤖 LangGraph agent framework loaded")
    print("🌐 API available at: http://localhost:8000")
    print("📖 API docs: http://localhost:8000/docs")
    
    uvicorn.run(
        app, 
        host=os.getenv("FASTAPI_HOST", "localhost"), 
        port=int(os.getenv("FASTAPI_PORT", 8000))
    )
