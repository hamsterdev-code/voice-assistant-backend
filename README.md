# Voice Assistant Backend

AI-powered voice assistant for cargo drivers using BotHub API (Whisper-1 + GPT-4).

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Install and run Redis

```bash
# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis

# Docker
docker run -d -p 6379:6379 redis:alpine
```

### 3. Configure environment

Edit `.env` file with your BotHub API key (already configured).

### 4. Run the server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will start on `http://localhost:8000`

## 📋 API Endpoints

### POST /api/voice/transcribe
Transcribe audio to text using Whisper-1.

**Request:**
- `user_id`: string (form data)
- `audio`: file (multipart/form-data)

**Response:**
```json
{
  "text": "найди груз из москвы в казань"
}
```

### POST /api/voice/process
Process text message through AI.

**Request:**
```json
{
  "user_id": "telegram_123",
  "message": "найди груз из москвы в казань",
  "context": {}
}
```

**Response:**
```json
{
  "response": "Ищу грузы из Москвы в Казань. Какая дата нужна?",
  "action": {
    "type": "search_cargo",
    "cargo_search_params": {
      "source": "Москва",
      "target": "Казань"
    }
  },
  "requests_remaining": 4
}
```

### GET /api/voice/usage/{user_id}
Get user usage statistics.

### POST /api/voice/payment
Process payment for paid access (mock implementation).

### DELETE /api/voice/conversation/{user_id}
Clear conversation history.

## 🔧 Configuration

Edit `.env` file:

```env
BOTHUB_API_KEY=your_api_key_here
FREE_REQUESTS_LIMIT=5
PAID_ACCESS_PRICE=1000
CONVERSATION_TTL=7200
```

## 📊 Features

- ✅ Speech-to-text (Whisper-1)
- ✅ AI conversation (GPT-4)
- ✅ Request limits (5 free requests)
- ✅ Conversation history (Redis)
- ✅ Service recommendations
- ✅ Cargo search automation
- ✅ Results analysis

## 🎯 Usage Limits

- Free: 5 requests per user
- Paid: Unlimited for 30 days (1000₽)

## 🧪 Testing

```bash
# Test transcription
curl -X POST http://localhost:8000/api/voice/transcribe \
  -F "user_id=test_user" \
  -F "audio=@test.webm"

# Test AI processing
curl -X POST http://localhost:8000/api/voice/process \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "найди груз из москвы в казань"
  }'
```

## 📝 Architecture

```
Backend (FastAPI)
├── config/          # Settings
├── services/        # Business logic
│   ├── voice_service.py    # Whisper-1 API
│   ├── ai_service.py       # GPT-4 API
│   └── usage_tracker.py    # Redis + limits
├── models/          # Pydantic schemas
│   ├── schemas.py
│   └── prompts.py   # AI prompts
├── api/             # API routes
└── main.py          # Entry point
```

## 🔒 Security

- API key stored in `.env` (not in git)
- CORS configured for frontend origins
- Request limits per user
- Input validation (Pydantic)

## 📞 Support

For issues or questions, contact the development team.
