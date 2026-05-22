from fastapi import FastAPI, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from nlp.task_extractor import extract_tasks
from datetime import datetime, timedelta
import os

app = FastAPI(title="Agentic AI Backend")

# simple SQLite persistence for scheduled tasks
DB_PATH = os.path.join(os.path.dirname(__file__), "schedules.db")
import sqlite3


def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS scheduled_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            start TEXT NOT NULL,
            end TEXT NOT NULL,
            action REAL,
            reward REAL,
            created_at TEXT NOT NULL
        )
        """
    )
    con.commit()
    con.close()


try:
    init_db()
except Exception as e:
    # don't prevent the app from importing; log the error so it's visible in the server output
    import traceback

    print("Warning: init_db() failed during import:")
    traceback.print_exc()

# Helper: find and load RL model (accept folder or .zip)
def _find_and_load_model():
    try:
        from stable_baselines3 import PPO
        base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "productivity_agent")
        candidates = [base, base + ".zip"]
        for p in candidates:
            if os.path.exists(p):
                try:
                    return PPO.load(p)
                except Exception:
                    continue
    except Exception:
        return None
    return None


# optional import of environment class (silent if missing)
try:
    from env.productivity_env import ProductivityEnv
except Exception:
    ProductivityEnv = None


class ScheduleRequest(BaseModel):
    # Provide either `text` (free-form) or `tasks` (list of strings)
    text: Optional[str] = None
    tasks: Optional[List[str]] = None
    # optional schedule window (HH:MM)
    start_time: Optional[str] = "09:00"
    end_time: Optional[str] = "17:00"


class ScheduledTask(BaseModel):
    task: str
    start: str
    end: str
    action: Optional[float] = None
    reward: Optional[float] = None
    id: Optional[int] = None


def parse_time_hhmm(s: str) -> datetime:
    today = datetime.now().date()
    hh, mm = map(int, s.split(":"))
    return datetime.combine(today, datetime.min.time()) + timedelta(hours=hh, minutes=mm)


@app.get("/")
def index():
    return {"name": "Agentic AI Backend"}


@app.post("/schedule-tasks", response_model=List[ScheduledTask])
def schedule_tasks(req: ScheduleRequest):
    # resolve task list
    if req.tasks:
        tasks = [{"task": t} for t in req.tasks]
    elif req.text:
        tasks = extract_tasks(req.text)
    else:
        raise HTTPException(status_code=400, detail="Provide `text` or `tasks` in the request")

    n = len(tasks)
    if n == 0:
        return []

    # parse start/end
    try:
        start_dt = parse_time_hhmm(req.start_time)
        end_dt = parse_time_hhmm(req.end_time)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid time format, expected HH:MM")

    if end_dt <= start_dt:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    total_minutes = int((end_dt - start_dt).total_seconds() // 60)
    per_task = max(1, total_minutes // n)

    model = _find_and_load_model()

    scheduled: List[ScheduledTask] = []
    cursor = start_dt

    for t in tasks:
        # duration in minutes (can be adjusted by text length / priority)
        duration = per_task

        # compute action & reward using model if available
        action_val = None
        reward_val = None
        if model is not None:
            try:
                env = ProductivityEnv()
                obs, _ = env.reset()
                action, _ = model.predict(obs, deterministic=True)
                _, reward, _, _, _ = env.step(action)
                try:
                    action_val = float(action[0])
                except Exception:
                    action_val = float(action)
                reward_val = float(reward)
            except Exception:
                action_val = None
                reward_val = None

        start_str = cursor.strftime("%H:%M")
        end_cursor = cursor + timedelta(minutes=duration)
        end_str = end_cursor.strftime("%H:%M")

        st = ScheduledTask(task=t.get("task", str(t)), start=start_str, end=end_str, action=(round(action_val,2) if action_val is not None else None), reward=(round(reward_val,2) if reward_val is not None else None))

        # persist
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO scheduled_tasks (task, start, end, action, reward, created_at) VALUES (?,?,?,?,?,?)",
            (st.task, st.start, st.end, st.action, st.reward, datetime.utcnow().isoformat()),
        )
        con.commit()
        st.id = cur.lastrowid
        con.close()

        scheduled.append(st)
        cursor = end_cursor

    return scheduled


@app.get("/scheduled-tasks", response_model=List[ScheduledTask])
def list_scheduled_tasks():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT id, task, start, end, action, reward FROM scheduled_tasks ORDER BY id DESC")
    rows = cur.fetchall()
    con.close()

    out: List[ScheduledTask] = []
    for r in rows:
        out.append(ScheduledTask(id=r[0], task=r[1], start=r[2], end=r[3], action=(r[4] if r[4] is not None else None), reward=(r[5] if r[5] is not None else None)))
    return out


@app.delete("/scheduled-tasks/{item_id}")
def delete_scheduled_task(item_id: int):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DELETE FROM scheduled_tasks WHERE id=?", (item_id,))
    con.commit()
    changed = cur.rowcount
    con.close()
    if changed == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"deleted": item_id}


# --- run-agent endpoint (merged from root app.py) ---
class RunRequest(BaseModel):
    text: str


class TaskResult(BaseModel):
    task: str
    action: float
    reward: float


@app.post("/run-agent", response_model=List[TaskResult])
def run_agent(req: RunRequest):
    # Load model if available
    model = None
    model = _find_and_load_model()

    tasks = extract_tasks(req.text)
    if not tasks:
        return []

    results: List[TaskResult] = []
    for t in tasks:
        env = None
        try:
            from env.productivity_env import ProductivityEnv
            env = ProductivityEnv()
            obs, _ = env.reset()
        except Exception:
            env = None

        intensity = 0.0
        reward = 0.0

        if model is not None and env is not None:
            try:
                action, _ = model.predict(obs, deterministic=True)
                _, reward, _, _, _ = env.step(action)
                try:
                    intensity = float(action[0])
                except Exception:
                    intensity = float(action)
            except Exception:
                intensity = 0.0
                reward = 0.0

        results.append(TaskResult(task=t.get("task", str(t)), action=round(intensity, 2), reward=round(float(reward), 2)))

    return results