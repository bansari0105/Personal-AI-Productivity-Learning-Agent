## Agentic AI Productivity Assistant - Quick Start Guide

### Project Status
✅ **Phase 1 Complete** - All core features working and tested
- NLP task extraction
- RL-based intensity/reward prediction
- Task scheduling with time allocation
- SQLite persistence
- REST API backend
- Streamlit web UI
- **NEW:** Task categorization with confidence scores

### Quick Start (Development)

#### 1. Activate Virtual Environment
```bash
# Windows (Git Bash / PowerShell)
./env/Scripts/activate

# OR use the venv Python directly
./env/Scripts/python
```

#### 2. Configure Environment
The project uses `.env` for configuration. Default values are in `.env`:
```bash
# Backend
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
API_BASE_URL=http://127.0.0.1:8000

# Database
DB_PATH=./backend/schedules.db
USER_DB_PATH=./backend/user_data.db

# Model
MODEL_PATH=./models/productivity_agent

# CORS (for frontend)
CORS_ORIGINS=http://localhost:3000,http://localhost:8501,http://127.0.0.1:3000,http://127.0.0.1:8501
```

#### 3. Start the Application

**Option A: Start everything at once**
```bash
python run_all.py
# Starts: Backend (http://127.0.0.1:8000) + Streamlit UI (http://127.0.0.1:8501)
```

**Option B: Start just the backend**
```bash
python start_backend.py
# Or: uvicorn backend.myapi:app --host 127.0.0.1 --port 8000 --reload
```

**Option C: Start Streamlit UI only** (backend must be running)
```bash
streamlit run streamlit_app.py
# Opens: http://127.0.0.1:8501
```

#### 4. Test the API
```bash
# Run comprehensive API tests
python test_api.py

# Or manually test an endpoint
curl -X POST http://127.0.0.1:8000/run-agent \
  -H "Content-Type: application/json" \
  -d '{"text":"Go to the gym and eat lunch"}'
```

#### 5. Train a New Model (optional)
```bash
# Train single agent
python rl/train_agent.py
# Saves to: models/productivity_agent.zip

# Train multiple agents
python rl/multi_agent_train.py
# Saves to: models/{work,learn,health}_agent.zip
```

### API Endpoints

#### POST /run-agent
Extract tasks from free-form text and evaluate with RL agent.

**Request:**
```json
{
  "text": "Study machine learning and go to the gym"
}
```

**Response:**
```json
[
  {
    "task": "Study machine learning and go to the gym",
    "action": 0.81,
    "reward": 1.63,
    "category": "study",
    "category_confidence": 0.67
  }
]
```

#### GET /run-agent?text=...
Browser-friendly version of above (GET with query parameter).

#### POST /schedule-tasks
Parse tasks and allocate time slots.

**Request:**
```json
{
  "text": "Review code, attend meeting, take break",
  "start_time": "09:00",
  "end_time": "12:00"
}
```

**Response:**
```json
[
  {
    "task": "Review code",
    "start": "09:00",
    "end": "10:00",
    "duration_minutes": 60,
    "category": "work",
    "action": 0.81,
    "reward": 1.63,
    "id": 1
  }
]
```

#### GET /scheduled-tasks
List all persisted tasks.

#### DELETE /scheduled-tasks/{id}
Remove a scheduled task.

#### GET /test-run
Simple HTML form for testing (no JSON/curl needed).

### Project Structure

```
agentic_ai/
├── backend/                 # FastAPI backend
│   ├── myapi.py            # Main API server
│   └── schedules.db        # SQLite database
├── frontend/               # Next.js app (optional)
├── nlp/                    # NLP processing
│   ├── task_extractor.py   # Task extraction (spaCy)
│   └── task_classifier.py  # NEW: Task categorization
├── prod_env/               # RL environment
│   └── productivity_env.py  # Gym environment
├── rl/                     # RL training
│   ├── train_agent.py      # Single agent training
│   └── multi_agent_train.py # Multi-agent training
├── models/                 # Trained models
│   └── productivity_agent.zip
├── config.py               # Configuration loader
├── .env                    # Environment variables
├── run_all.py              # Start backend + Streamlit
├── start_backend.py        # Start backend only
└── test_api.py             # API test suite
```

### Task Categories (NEW)

Tasks are automatically classified into:
- **exercise** - gym, workout, run, yoga, etc. (default: 60 min)
- **meal** - breakfast, lunch, dinner, eat (default: 45 min)
- **meeting** - meetings, calls, standups (default: 60 min)
- **commute** - travel, drive, transport (default: 30 min)
- **study** - learn, read, research, course (default: 120 min)
- **work** - code, develop, review, debug (default: 90 min)
- **break** - rest, pause, coffee, stretch (default: 15 min)
- **personal** - shower, hygiene, grooming (default: 20 min)
- **other** - unclassified tasks (default: 60 min)

Each classification includes a confidence score (0.0 - 1.0).

### Common Issues & Solutions

**Port 8000 already in use:**
```bash
# Either use a different port
uvicorn backend.myapi:app --port 8001

# Or kill the process (Linux/Mac)
lsof -ti:8000 | xargs kill -9
```

**Model not found:**
- Ensure `models/productivity_agent.zip` exists
- Or train a new one: `python rl/train_agent.py`
- Check `MODEL_PATH` in `.env`

**NLP spaCy model missing:**
- Runs fine without it (fallback regex splitter)
- To install: `python -m spacy download en_core_web_sm`

**Backend can't connect to from Streamlit:**
- Verify `API_BASE_URL` in `.env`
- Check backend is running: `curl http://127.0.0.1:8000/`
- Check CORS origins include your UI host

### Next Steps (Roadmap)

**Phase 2 (Medium-term):**
- [ ] Train supervised duration/priority predictors from user edits
- [ ] Multi-user support with auth
- [ ] User preferences (timezone, work hours)
- [ ] Analytics dashboard

**Phase 3 (Long-term):**
- [ ] Recurring tasks & habits
- [ ] Task dependencies
- [ ] Calendar integration
- [ ] Mobile app

### For Contributors

All code is modular and testable:
- `config.py` - Load environment settings
- `nlp/*.py` - NLP/classification logic
- `backend/myapi.py` - API endpoints
- `prod_env/*.py` - RL environment
- `rl/*.py` - Training scripts

Tests: `python test_api.py`

---

**Last Updated:** April 2026
**Status:** Phase 1 Complete, Production Ready for Single User
