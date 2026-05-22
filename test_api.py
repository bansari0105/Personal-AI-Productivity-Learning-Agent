#!/usr/bin/env python
"""Test script to validate all API endpoints.

Usage:
    python test_api.py

Make sure the backend is running first!
"""
import requests
import json
import sys
import time
from pathlib import Path

# Import config
sys.path.insert(0, str(Path(__file__).parent))
from config import API_BASE_URL

BASE_URL = API_BASE_URL

def test_health():
    """Test health endpoint."""
    print("\n[TEST] Health Check")
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=2)
        if resp.status_code == 200:
            print(f"[PASS] Health check passed: {resp.json()}")
            return True
        else:
            print(f"[FAIL] Health check failed: {resp.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")
        print(f"      Make sure backend is running at {BASE_URL}")
        return False

def test_run_agent():
    """Test agent execution endpoint."""
    print("\n[TEST] Run Agent")
    try:
        payload = {"text": "Study machine learning for 2 hours and go to the gym"}
        resp = requests.post(f"{BASE_URL}/run-agent", json=payload, timeout=10)
        if resp.status_code == 200:
            results = resp.json()
            print(f"[PASS] Agent execution passed")
            print(f"       Input: {payload['text']}")
            print(f"       Results ({len(results)} tasks):")
            for r in results:
                print(f"         - {r['task']}: action={r['action']}, reward={r['reward']}")
            return True
        else:
            print(f"[FAIL] Agent execution failed: {resp.status_code}")
            print(f"       Response: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_schedule_tasks():
    """Test task scheduling endpoint."""
    print("\n[TEST] Schedule Tasks")
    try:
        payload = {
            "text": "Review code, attend meeting, take break",
            "start_time": "09:00",
            "end_time": "12:00"
        }
        resp = requests.post(f"{BASE_URL}/schedule-tasks", json=payload, timeout=10)
        if resp.status_code == 200:
            results = resp.json()
            print(f"[PASS] Scheduling passed")
            print(f"       Input: {payload['text']}")
            print(f"       Window: {payload['start_time']} - {payload['end_time']}")
            print(f"       Scheduled {len(results)} tasks:")
            for r in results:
                print(f"         - {r['task']}: {r['start']} - {r['end']} ({r.get('duration_minutes')} min)")
            return True
        else:
            print(f"[FAIL] Scheduling failed: {resp.status_code}")
            print(f"       Response: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_list_scheduled():
    """Test list scheduled tasks endpoint."""
    print("\n[TEST] List Scheduled Tasks")
    try:
        resp = requests.get(f"{BASE_URL}/scheduled-tasks", timeout=5)
        if resp.status_code == 200:
            results = resp.json()
            print(f"[PASS] List passed")
            print(f"       Found {len(results)} scheduled task(s)")
            if results:
                print(f"       (Showing first 3)")
                for r in results[:3]:
                    print(f"         - {r['task']}: {r['start']} - {r['end']}")
            return True
        else:
            print(f"[FAIL] List failed: {resp.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_get_agent():
    """Test GET convenience endpoint."""
    print("\n[TEST] GET /run-agent (Browser-friendly)")
    try:
        params = {"text": "Write documentation"}
        resp = requests.get(f"{BASE_URL}/run-agent", params=params, timeout=10)
        if resp.status_code == 200:
            results = resp.json()
            print(f"[PASS] GET endpoint passed")
            print(f"       Query: {params['text']}")
            print(f"       Results: {len(results)} task(s)")
            return True
        else:
            print(f"[FAIL] GET endpoint failed: {resp.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("API Endpoint Tests")
    print("=" * 60)
    print(f"Testing: {BASE_URL}")

    tests = [
        ("Health Check", test_health),
        ("Run Agent", test_run_agent),
        ("GET Agent", test_get_agent),
        ("Schedule Tasks", test_schedule_tasks),
        ("List Scheduled", test_list_scheduled),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n[FAIL] Test '{name}' crashed: {e}")
            results[name] = False

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    for name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")

    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
