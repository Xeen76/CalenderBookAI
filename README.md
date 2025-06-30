![Main Page](https://github.com/user-attachments/assets/7459f061-b197-455e-bf69-998f76527011)


![Booking confirmed in Gmail](https://github.com/user-attachments/assets/f9817b1b-fd7a-4297-98db-331a6f18a5a4)




# 📅 Calendar Booking Agent

A conversational AI agent that assists users in booking appointments on Google Calendar using FastAPI backend, LangGraph agent framework, and Streamlit frontend.

## 🚀 Features

- **Natural Language Processing**: Understands booking requests in plain English
- **Google Calendar Integration**: Real calendar availability checking and booking
- **Conversational Interface**: Guides users through the booking process
- **Smart Time Extraction**: Automatically extracts dates, times, and meeting types
- **Interactive UI**: Clean Streamlit interface with booking buttons

## 🛠️ Technical Stack

- **Backend**: Python with FastAPI
- **Agent Framework**: LangGraph for conversational workflows
- **Frontend**: Streamlit for chat interface
- **Calendar**: Google Calendar API integration
- **LLM**: Gemini Pro (with OpenAI fallback)

## 📋 Requirements

- Python 3.8+
- Google Calendar API credentials
- Gemini API key (or OpenAI API key)

## ⚡ Quick Start

1. **Clone and setup**:
   ```bash
   cd calendar_agent
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   - Copy `.env` and add your API keys
   - Add Google Calendar credentials to `credentials.json`

3. **Run the application**:
   ```bash
   python run.py
   ```

4. **Open your browser**:
   - Frontend: http://localhost:8501
   - API Docs: http://localhost:8000/docs

## 💬 Example Conversations

The agent handles these types of requests:

- **"Hey, I want to schedule a call for tomorrow afternoon."**
- **"Do you have any free time this Friday?"**
- **"Book a meeting between 3-5 PM next week."**

## 🎯 How It Works

1. **User Input**: Natural language booking request
2. **Intent Classification**: LangGraph determines user intent
3. **Information Extraction**: Extracts dates, times, meeting types
4. **Calendar Check**: Queries Google Calendar for availability
5. **Slot Suggestion**: Presents available time options
6. **Booking Confirmation**: Creates calendar event upon confirmation

## 🔧 Configuration

### Environment Variables (.env)
```
GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials.json
GOOGLE_CALENDAR_ID=your-email@gmail.com
GEMINI_API_KEY=your-gemini-api-key
CALENDAR_MOCK_MODE=false
```

### Google Calendar Setup
1. Go to Google Cloud Console
2. Enable Calendar API
3. Create credentials (OAuth 2.0)
4. Download as `credentials.json`

## 📁 Project Structure

```
calendar_agent/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── agent.py             # LangGraph agent
│   └── calendar_service.py  # Google Calendar integration
├── frontend/
│   └── app.py              # Streamlit interface
├── requirements.txt        # Dependencies
├── .env                   # Environment variables
└── run.py                # Startup script
```

## 🧪 Development Mode

The system includes a mock mode for development without Google Calendar setup:
- Set `CALENDAR_MOCK_MODE=true` in `.env`
- Mock calendar service generates sample availability
- Perfect for testing the conversation flow

## 🎉 Demo

Try these example conversations:
1. "I need to schedule a client meeting tomorrow at 2 PM"
2. "Do you have any free time this Friday?"
3. "Book a call for next Monday morning"

The agent will:
- Extract the meeting details
- Check calendar availability
- Suggest specific time slots
- Allow one-click booking

## 📞 Support

For issues or questions, check the console logs or API documentation at `/docs` endpoint.
