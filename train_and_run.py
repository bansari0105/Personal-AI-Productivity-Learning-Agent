"""Train a new model then launch the app.

Usage:
    python train_and_run.py

This will call the existing training script (rl/train_agent.py) and then
start the backend + Streamlit UI (run_all.py).
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    cwd = os.path.dirname(os.path.abspath(__file__))
    os.chdir(cwd)

    # train model
    print("Training agent...")
    ret = subprocess.call([sys.executable, "rl/train_agent.py"])
    if ret != 0:
        print("Training script failed, aborting.")
        sys.exit(ret)

    # launch servers
    print("Launching application...")
    subprocess.call([sys.executable, "run_all.py"])
