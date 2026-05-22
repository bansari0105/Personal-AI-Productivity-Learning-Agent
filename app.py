from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from stable_baselines3 import PPO
from prod_env.productivity_env import ProductivityEnv
from nlp.task_extractor import extract_tasks
import os


class RunRequest(BaseModel):
    text: str


class TaskResult(BaseModel):
    task: str
    action: float
    reward: float


app = FastAPI(title="Agentic AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model once at startup (if available)
MODEL_PATH = os.path.join("models", "productivity_agent")
try:
    model = PPO.load(MODEL_PATH)
except Exception:
    model = None


@app.post("/run-agent", response_model=List[TaskResult])
def run_agent(req: RunRequest):
    """Run the trained agent for every extracted task and return results.

    For each task we reset the environment so each task is evaluated independently.
    """
    if model is None:
        raise HTTPException(status_code=500, detail=f"Model not found at {MODEL_PATH}")

    tasks = extract_tasks(req.text)
    if not tasks:
        return []

    results: List[TaskResult] = []

    for t in tasks:
        # Reset environment for each task to evaluate independently
        env = ProductivityEnv()
        obs, _ = env.reset()

        # Predict action from current observation
        action, _ = model.predict(obs, deterministic=True)

        # Apply action once and observe reward
        _, reward, terminated, truncated, _ = env.step(action)

        # Action intensity: ensure scalar between 0 and 1
        try:
            intensity = float(action[0])
        except Exception:
            # fallback if action is scalar
            intensity = float(action)

        if intensity < 0.0:
            intensity = 0.0
        if intensity > 1.0:
            intensity = 1.0

        results.append(TaskResult(task=t.get("task", str(t)), action=round(intensity, 2), reward=round(float(reward), 2)))

    return results


if __name__ == "__main__":
    # simple runner for local debugging (not for production)
    sample = "Study reinforcement learning and go to gym"
    print("Running agent locally for:", sample)
    from uvicorn import run

    run("app:app", host="127.0.0.1", port=8000, reload=False)
