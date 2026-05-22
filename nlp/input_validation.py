"""Input validation for API requests.

Validates task text, time ranges, and other inputs to ensure data integrity.
"""
from datetime import datetime, timedelta
import re

class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


def validate_task_text(text: str, min_length: int = 3, max_length: int = 1000) -> str:
    """Validate and clean task text.

    Args:
        text: The task description
        min_length: Minimum length (default 3)
        max_length: Maximum length (default 1000)

    Returns:
        Cleaned text

    Raises:
        ValidationError: If text is invalid
    """
    if not text:
        raise ValidationError("Task text cannot be empty")

    # Strip whitespace
    text = text.strip()

    if len(text) < min_length:
        raise ValidationError(f"Task text must be at least {min_length} characters")

    if len(text) > max_length:
        raise ValidationError(f"Task text cannot exceed {max_length} characters")

    # Check for suspicious patterns (basic injection prevention)
    if re.match(r'^[\s;\'"`]+$', text):
        raise ValidationError("Task text contains only whitespace or special characters")

    # Warn about common issues (but don't fail)
    # This could be logged in production

    return text


def validate_time_format(time_str: str) -> datetime:
    """Validate time string format (HH:MM).

    Args:
        time_str: Time string like "09:00"

    Returns:
        datetime object (date is today)

    Raises:
        ValidationError: If format is invalid
    """
    if not time_str:
        raise ValidationError("Time cannot be empty")

    time_str = time_str.strip()

    # Validate format
    try:
        time_obj = datetime.strptime(time_str, "%H:%M")
    except ValueError:
        raise ValidationError(f"Invalid time format: '{time_str}'. Use HH:MM (e.g., '09:00')")

    return time_obj


def validate_time_range(start_time: str, end_time: str) -> tuple:
    """Validate that start and end times form a valid range.

    Args:
        start_time: Start time as HH:MM
        end_time: End time as HH:MM

    Returns:
        Tuple of (start_datetime, end_datetime)

    Raises:
        ValidationError: If range is invalid
    """
    start_dt = validate_time_format(start_time)
    end_dt = validate_time_format(end_time)

    if start_dt >= end_dt:
        raise ValidationError(
            f"Start time ({start_time}) must be before end time ({end_time})"
        )

    # Check that range is not too long (e.g., more than 24 hours)
    duration = end_dt - start_dt
    if duration > timedelta(hours=24):
        raise ValidationError(
            f"Time range cannot exceed 24 hours (got {duration.total_seconds() / 3600:.1f} hours)"
        )

    # Check that range is reasonable (at least 15 minutes)
    if duration < timedelta(minutes=15):
        raise ValidationError(
            f"Time range must be at least 15 minutes (got {duration.total_seconds() / 60:.0f} minutes)"
        )

    return start_dt, end_dt


def validate_schedule_request(text: str, start_time: str, end_time: str) -> dict:
    """Validate complete schedule request.

    Args:
        text: Task description
        start_time: Start time (HH:MM)
        end_time: End time (HH:MM)

    Returns:
        Dictionary with validated values

    Raises:
        ValidationError: If any input is invalid
    """
    validated = {}

    # Validate task text
    validated["text"] = validate_task_text(text)

    # Validate time range
    start_dt, end_dt = validate_time_range(start_time, end_time)
    validated["start_time"] = start_time
    validated["end_time"] = end_time
    validated["start_dt"] = start_dt
    validated["end_dt"] = end_dt

    return validated


def validate_run_agent_request(text: str) -> dict:
    """Validate /run-agent request.

    Args:
        text: Task text

    Returns:
        Dictionary with validated values

    Raises:
        ValidationError: If input is invalid
    """
    return {
        "text": validate_task_text(text)
    }


if __name__ == "__main__":
    # Test validation
    print("Input Validation Tests")
    print("=" * 70)

    # Test task text validation
    text_tests = [
        ("Valid task", "Study machine learning for 2 hours", True),
        ("Empty task", "", False),
        ("Too short", "Go", False),
    ]

    print("\nTask Text Validation:")
    for name, text, should_pass in text_tests:
        try:
            result = validate_task_text(text)
            status = "PASS" if should_pass else "FAIL (should have raised)"
            print(f"  {status}: {name}")
        except ValidationError as e:
            status = "PASS" if not should_pass else "FAIL (should have passed)"
            print(f"  {status}: {name} - {e}")

    # Test time range validation
    time_tests = [
        ("Valid range", ("09:00", "12:00"), True),
        ("Invalid format", ("9:00", "12:00"), False),
        ("Start >= End", ("12:00", "09:00"), False),
        ("Range 23 hours", ("00:00", "23:00"), True),
        ("Range too short", ("09:00", "09:05"), False),
    ]

    print("\nTime Range Validation:")
    for name, times, should_pass in time_tests:
        try:
            result = validate_time_range(times[0], times[1])
            status = "PASS" if should_pass else "FAIL (should have raised)"
            print(f"  {status}: {name}")
        except ValidationError as e:
            status = "PASS" if not should_pass else "FAIL (should have passed)"
            print(f"  {status}: {name} - {e}")
