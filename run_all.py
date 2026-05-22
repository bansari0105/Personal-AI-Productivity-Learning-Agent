"""Utility script to start backend and UI together.

Run this from the project root after activating the Python environment:

    python run_all.py

Ctrl-C will stop both processes.
"""

import subprocess
import sys
import os

if __name__ == "__main__":
    # ensure we are in the repo root
    cwd = os.path.dirname(os.path.abspath(__file__))
    os.chdir(cwd)

    print("Starting backend (uvicorn) and Streamlit UI...")

    uvicorn_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.myapi:app", "--reload"],
    )
    streamlit_proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "streamlit_app.py"],
    )

    try:
        uvicorn_proc.wait()
        streamlit_proc.wait()
    except KeyboardInterrupt:
        print("Stopping processes...")
        uvicorn_proc.terminate()
        streamlit_proc.terminate()
        uvicorn_proc.wait()
        streamlit_proc.wait()
    print("Done.")
