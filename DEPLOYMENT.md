# Agentic AI - Deployment & Administration Guide

## Overview

This guide covers deploying the Agentic AI Productivity Assistant from development to production, managing users, and operational procedures.

**Current Version:** Phase 1 Complete (Single & Multi-User Ready)
**Last Updated:** April 2026

---

## System Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (User Interface)                │
│   ┌─────────────────┬──────────────────┬────────────────┐  │
│   │  Streamlit UI   │  Web Browser     │  Mobile (WIP)  │  │
│   │  (Port 8501)    │  (Custom UI)     │                │  │
│   └────────┬────────┴────────┬─────────┴────────────────┘  │
└────────────┼────────────────┼─────────────────────────────┘
             │                │
             └────────┬───────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                    │
│  ┌──────────────────┬──────────────┬──────────────────┐   │
│  │  Task Extraction │ Task Classify│ Agent Evaluation│   │
│  │  (NLP / spaCy)   │ (Heuristics) │ (RL Model)      │   │
│  └──────────────────┴──────────────┴──────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Schedule Optimization & Persistence                  │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────┬────────────────────┘
                     │                │
        ┌────────────┘                └────────────┐
        ▼                                          ▼
┌──────────────────┐                    ┌──────────────────┐
│  Task Database   │                    │  User Database   │
│  (SQLite)        │                    │  (SQLite)        │
│  schedules.db    │                    │  user_data.db    │
└──────────────────┘                    └──────────────────┘
        ▲                                          ▲
        │                                          │
        └──────────────────┬─────────────────────┘
                           │
                   ┌───────┴────────┐
                   │  Disk Storage  │
                   │  (./backend/)  │
                   └────────────────┘
```

### Database Schema

#### `scheduled_tasks` (Task Persistence)
```sql
CREATE TABLE scheduled_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,                      -- Task description
    start TEXT NOT NULL,                     -- HH:MM format
    end TEXT NOT NULL,                       -- HH:MM format
    action REAL,                             -- RL agent intensity (0-1)
    reward REAL,                             -- RL agent reward
    duration INTEGER,                        -- Duration in minutes
    category TEXT,                           -- Task category (exercise, work, etc.)
    category_confidence REAL,                -- Category confidence (0-1)
    user_id INTEGER,                         -- Foreign key to users table
    created_at TEXT NOT NULL                 -- Timestamp
);
```

#### `users` (User Management)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,           -- Unique username
    timezone TEXT,                           -- User's timezone
    prefs TEXT,                              -- JSON preferences (future)
    created_at TEXT NOT NULL                 -- Account creation timestamp
);
```

---

## Deployment Scenarios

### Scenario 1: Local Development

**Target:** Single developer, testing features

```bash
# Setup (one time)
python -m venv env
./env/Scripts/activate
pip install -r requirements.txt
python -c "from backend.myapi import init_db; init_db()"

# Run everything
python run_all.py

# Or run individually
python start_backend.py          # Terminal 1
streamlit run streamlit_app.py   # Terminal 2
```

**Ports:** Backend (8000), Streamlit (8501)  
**Database:** Local SQLite files  
**Users:** Single-user mode (no authentication)

### Scenario 2: Multi-User Server (Linux/Mac)

**Target:** Team sharing a server, multiple users

**Prerequisites:**
- Linux/Mac server
- Python 3.9+
- systemd (for service management)
- Reverse proxy (nginx)

**Setup:**

1. **Clone and install:**
   ```bash
   git clone <repo> /opt/agentic-ai
   cd /opt/agentic-ai
   python3 -m venv env
   ./env/bin/pip install -r requirements.txt
   ```

2. **Create systemd service:**
   ```bash
   sudo tee /etc/systemd/system/agentic-ai-backend.service > /dev/null <<EOF
   [Unit]
   Description=Agentic AI Backend
   After=network.target
   
   [Service]
   Type=simple
   User=agentic
   WorkingDirectory=/opt/agentic-ai
   Environment="PATH=/opt/agentic-ai/env/bin"
   ExecStart=/opt/agentic-ai/env/bin/uvicorn backend.myapi:app \
     --host 0.0.0.0 \
     --port 8000 \
     --workers 4
   Restart=on-failure
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   EOF
   
   sudo systemctl daemon-reload
   sudo systemctl enable agentic-ai-backend
   sudo systemctl start agentic-ai-backend
   ```

3. **Configure nginx:**
   ```nginx
   upstream agentic_backend {
       server 127.0.0.1:8000;
   }
   
   server {
       listen 80;
       server_name agentic.company.com;
       
       location /api/ {
           proxy_pass http://agentic_backend/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Create user:**
   ```bash
   # Via API
   curl -X POST http://localhost:8000/users \
     -H "Content-Type: application/json" \
     -d '{"username":"alice","timezone":"America/New_York"}'
   ```

### Scenario 3: Docker Deployment (Recommended)

**Target:** Cloud platforms (AWS, GCP, Azure), kubernetes, easy scaling

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s \
    CMD curl -f http://localhost:8000/ || exit 1

# Run backend
CMD ["uvicorn", "backend.myapi:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      DB_PATH: /data/schedules.db
      USER_DB_PATH: /data/user_data.db
      MODEL_PATH: /app/models/productivity_agent
    volumes:
      - ./data:/data
      - ./models:/app/models:ro
    restart: unless-stopped

  # Optional: Nginx reverse proxy
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - backend
```

**Deploy:**
```bash
docker-compose up -d
docker-compose logs -f backend

# Create user
docker-compose exec backend python -c "
import requests
requests.post('http://localhost:8000/users', json={'username':'alice'})
"
```

---

## User Management

### Create User

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "timezone": "America/Los_Angeles"
  }'
```

**Response:**
```json
{
  "id": 1,
  "username": "alice",
  "timezone": "America/Los_Angeles",
  "created_at": "2026-04-19T22:30:00.000000"
}
```

### Get User Info

```bash
curl http://localhost:8000/users/1
```

### Get User's Tasks

```bash
curl http://localhost:8000/users/1/scheduled-tasks
```

### List All Tasks (Admin)

```bash
curl http://localhost:8000/scheduled-tasks
```

---

## Monitoring & Logging

### Check Backend Status

```bash
curl http://localhost:8000/
# Returns: {"name": "Agentic AI Backend"}

# Detailed health check
curl http://localhost:8000/test-run
```

### View Logs

```bash
# Systemd service
sudo journalctl -u agentic-ai-backend -f

# Docker
docker-compose logs -f backend

# Local development
# Check /tmp/backend.log or console output
```

### Database Integrity

```bash
# Check scheduled_tasks
sqlite3 backend/schedules.db "SELECT COUNT(*) FROM scheduled_tasks;"

# Check users
sqlite3 backend/user_data.db "SELECT username FROM users;"

# Backup database
cp backend/schedules.db backups/schedules_$(date +%Y%m%d_%H%M%S).db
```

---

## Performance Tuning

### API Optimization

1. **Increase Uvicorn Workers:**
   ```bash
   uvicorn backend.myapi:app --workers 4 --host 0.0.0.0
   ```

2. **Add Caching:** (Future feature)
   - Redis for task extraction results
   - HTTP caching headers

3. **Database Indexing:**
   ```sql
   CREATE INDEX idx_user_id ON scheduled_tasks(user_id);
   CREATE INDEX idx_created_at ON scheduled_tasks(created_at);
   ```

### Model Optimization

1. **GPU Acceleration:** (If available)
   - Uncomment GPU in `rl/train_agent.py`

2. **Batch Processing:**
   - Group multiple requests
   - Process offline for non-interactive tasks

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Mac/Linux
taskkill /F /PID <PID>  # Windows
```

### Database Locked

```bash
# SQLite locks indicate another process is using DB
# Solution: Ensure only one backend instance is running

# Check running processes
ps aux | grep python  # Mac/Linux
tasklist | findstr python  # Windows
```

### Model Not Found

```bash
# Verify model exists
ls -la models/productivity_agent.zip

# If missing, train new model
python rl/train_agent.py

# Check MODEL_PATH in .env
cat .env | grep MODEL_PATH
```

### NLP Errors

```bash
# Install spaCy model (optional, fallback exists)
python -m spacy download en_core_web_sm

# Test extraction without spaCy
from nlp.task_extractor import extract_tasks
tasks = extract_tasks("Go to gym and study")  # Should work
```

---

## Backup & Recovery

### Regular Backups

```bash
# Manual backup
tar -czf backup_$(date +%Y%m%d).tar.gz backend/schedules.db backend/user_data.db

# Automated (Linux cron)
0 2 * * * tar -czf /backups/agentic_$(date +\%Y\%m\%d).tar.gz /opt/agentic-ai/backend/*.db
```

### Recovery

```bash
# Restore from backup
tar -xzf backup_20260419.tar.gz -C backend/

# Verify integrity
sqlite3 backend/schedules.db "PRAGMA integrity_check;"
```

---

## Future Enhancements

**Planned Features (Phase 2+):**

- [ ] Authentication & Authorization (JWT)
- [ ] Task edit history & undo
- [ ] Integration with calendar apps (Google Calendar, Outlook)
- [ ] Mobile app (React Native)
- [ ] Real-time collaboration
- [ ] Analytics dashboard
- [ ] Email notifications
- [ ] Recurring tasks & habits
- [ ] Advanced time zone support
- [ ] Automated backups to cloud storage

---

## Support & Issues

**Issue Template (GitHub/Issue Tracker):**

```
## System Information
- Python version: `python --version`
- OS: Windows/Mac/Linux
- Deployment: Local/Docker/Server

## Steps to Reproduce
1. ...
2. ...

## Expected Behavior
...

## Actual Behavior
...

## Logs
<paste relevant logs>
```

---

**Questions? Open an issue or contact the development team.**

**Last Updated:** 2026-04-19  
**Maintainer:** Agentic AI Team
