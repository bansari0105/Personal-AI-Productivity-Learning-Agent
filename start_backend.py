#!/usr/bin/env python
"""Start the FastAPI backend server.

Usage:
    python start_backend.py

The server will start on the configured host/port (default 127.0.0.1:8000)
"""
import subprocess
import sys
import os
from pathlib import Path

# Change to project root
project_root = Path(__file__).parent
os.chdir(project_root)

# Import config to show startup info
from config import BACKEND_HOST, BACKEND_PORT, API_BASE_URL, DEBUG

print("=" * 60)
print("🚀 Agentic AI Backend Server")
print("=" * 60)
print(f"Host: {BACKEND_HOST}")
print(f"Port: {BACKEND_PORT}")
print(f"API URL: {API_BASE_URL}")
print(f"Debug: {DEBUG}")
print("=" * 60)
print("Starting server (press Ctrl+C to stop)...\n")

# Build command
cmd = [
    sys.executable,
    "-m",
    "uvicorn",
    "backend.myapi:app",
    "--host",
    BACKEND_HOST,
    "--port",
    str(BACKEND_PORT),
]

# Only add reload flag if DEBUG is True
if DEBUG:
    cmd.append("--reload")

# Start uvicorn
try:
    subprocess.run(cmd, cwd=project_root)
except KeyboardInterrupt:
    print("\n\nServer stopped.")
    sys.exit(0)

