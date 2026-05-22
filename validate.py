#!/usr/bin/env python
"""Comprehensive project validation test.

Runs through all major features to ensure everything is working correctly.
"""
import subprocess
import sys
import time
import requests
import json

def run_test(name, test_func):
    """Run a test and report results."""
    try:
        result = test_func()
        if result:
            print(f"[PASS] {name}")
            return True
        else:
            print(f"[FAIL] {name}")
            return False
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        return False

def test_imports():
    """Test all critical imports."""
    try:
        from config import API_BASE_URL
        from backend.myapi import app
        from nlp.task_extractor import extract_tasks
        from nlp.task_classifier import classify_task
        from prod_env.productivity_env import ProductivityEnv
        return True
    except Exception as e:
        print(f"  Import error: {e}")
        return False

def test_task_extraction():
    """Test NLP task extraction."""
    from nlp.task_extractor import extract_tasks
    tasks = extract_tasks("Study machine learning and go to the gym")
    return len(tasks) > 0

def test_task_classification():
    """Test task categorization."""
    from nlp.task_classifier import classify_task
    result = classify_task("Go to the gym")
    return result.get("category") == "exercise" and result.get("confidence") > 0

def test_environment():
    """Test RL environment."""
    from prod_env.productivity_env import ProductivityEnv
    env = ProductivityEnv()
    obs, _ = env.reset()
    return obs.shape == (3,)

def test_config():
    """Test configuration loading."""
    from config import API_BASE_URL, CORS_ORIGINS
    return API_BASE_URL and len(CORS_ORIGINS) > 0

def test_backend_health():
    """Test backend is running."""
    try:
        resp = requests.get("http://127.0.0.1:8000/", timeout=2)
        return resp.status_code == 200
    except:
        return False

def test_api_run_agent():
    """Test /run-agent endpoint."""
    try:
        resp = requests.post(
            "http://127.0.0.1:8000/run-agent",
            json={"text": "Study and exercise"},
            timeout=10
        )
        data = resp.json()
        # Check that response has category fields
        return (resp.status_code == 200 and
                len(data) > 0 and
                "category" in data[0] and
                "category_confidence" in data[0])
    except:
        return False

def test_api_schedule():
    """Test /schedule-tasks endpoint."""
    try:
        resp = requests.post(
            "http://127.0.0.1:8000/schedule-tasks",
            json={
                "text": "Review code and attend meeting",
                "start_time": "09:00",
                "end_time": "12:00"
            },
            timeout=10
        )
        return resp.status_code == 200 and len(resp.json()) > 0
    except:
        return False

def test_database():
    """Test database persistence."""
    import sqlite3
    import os
    if os.path.exists("./backend/schedules.db"):
        con = sqlite3.connect("./backend/schedules.db")
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM scheduled_tasks")
        count = cur.fetchone()[0]
        con.close()
        return count >= 0  # Just verify we can query it
    return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Agentic AI - Comprehensive Validation Test")
    print("=" * 60)

    tests = [
        ("Configuration Loading", test_config),
        ("NLP Imports", test_imports),
        ("Task Extraction", test_task_extraction),
        ("Task Classification", test_task_classification),
        ("RL Environment", test_environment),
        ("Database Access", test_database),
        ("Backend Health Check", test_backend_health),
        ("API: /run-agent", test_api_run_agent),
        ("API: /schedule-tasks", test_api_schedule),
    ]

    results = {}
    for name, test_func in tests:
        results[name] = run_test(name, test_func)

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")

    print(f"\nTotal: {passed}/{total} passed")

    if passed == total:
        print("\n[SUCCESS] All systems operational!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
