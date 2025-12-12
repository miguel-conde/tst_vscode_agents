"""Storage module for persisting timer data."""

import json
from pathlib import Path
from typing import List, Optional, Union, Dict
from datetime import datetime, timedelta
from collections import defaultdict

from src.timer import Timer, Session

# Storage file names
SESSIONS_FILE = "sessions.json"
STATE_FILE = ".timer_state.json"


def get_storage_dir() -> Path:
    """
    Get the storage directory path, creating it if it doesn't exist.
    
    Returns:
        Path to the storage directory (~/.task_timer/)
    """
    storage_dir = Path.home() / ".task_timer"
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir


def save_session(session: Session) -> None:
    """
    Save a completed session to persistent storage.
    
    Sessions are stored in a JSON file with all existing sessions.
    New sessions are appended to the existing list.
    
    Args:
        session: The Session object to save
    """
    storage_dir = get_storage_dir()
    sessions_file = storage_dir / SESSIONS_FILE
    
    # Load existing sessions
    if sessions_file.exists():
        with open(sessions_file, 'r') as f:
            data = json.load(f)
    else:
        data = {"sessions": []}
    
    # Append new session
    data["sessions"].append(session.to_dict())
    
    # Save back to file
    with open(sessions_file, 'w') as f:
        json.dump(data, f, indent=2)


def load_sessions(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Session]:
    """
    Load sessions from persistent storage.
    
    Optionally filter sessions by date range. If start_date is provided,
    only sessions starting on or after that date are returned. If end_date
    is provided, only sessions starting before that date are returned.
    
    Args:
        start_date: Optional start date for filtering (inclusive)
        end_date: Optional end date for filtering (exclusive)
    
    Returns:
        List of Session objects, possibly filtered by date
    """
    storage_dir = get_storage_dir()
    sessions_file = storage_dir / SESSIONS_FILE
    
    # Return empty list if file doesn't exist
    if not sessions_file.exists():
        return []
    
    # Load sessions from file
    with open(sessions_file, 'r') as f:
        data = json.load(f)
    
    sessions = []
    for session_data in data.get("sessions", []):
        session = Session.from_dict(session_data)
        
        # Apply date filters
        if start_date and session.start_time < start_date:
            continue
        if end_date and session.start_time >= end_date:
            continue
        
        sessions.append(session)
    
    return sessions


def save_active_timer(timer: Timer) -> None:
    """
    Save the current active timer state.
    
    This allows resuming a timer session after the application is closed.
    Only the task, category, and start time are saved.
    
    Args:
        timer: The active Timer object to save
    
    Raises:
        RuntimeError: If timer is not running
    """
    if not timer.is_running():
        raise RuntimeError("Cannot save inactive timer")
    
    storage_dir = get_storage_dir()
    state_file = storage_dir / STATE_FILE
    
    state = {
        "task": timer.task,
        "category": timer.category,
        "start_time": timer.start_time.isoformat()
    }
    
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)


def get_active_timer() -> Optional[Timer]:
    """
    Load the active timer state if one exists.
    
    Returns:
        Timer object with restored state, or None if no active timer
    """
    storage_dir = get_storage_dir()
    state_file = storage_dir / STATE_FILE
    
    if not state_file.exists():
        return None
    
    with open(state_file, 'r') as f:
        state = json.load(f)
    
    # Restore timer state
    timer = Timer()
    timer.task = state["task"]
    timer.category = state["category"]
    timer.start_time = datetime.fromisoformat(state["start_time"])
    
    return timer


def clear_active_timer() -> None:
    """
    Clear the active timer state.
    
    This removes the state file, indicating no timer is currently running.
    Safe to call even if no state file exists.
    """
    storage_dir = get_storage_dir()
    state_file = storage_dir / STATE_FILE
    
    if state_file.exists():
        state_file.unlink()


def load_sessions_by_category(
    category: Union[str, List[str]],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Session]:
    """
    Load sessions filtered by category.
    
    Args:
        category: Single category string or list of categories to filter by
        start_date: Optional start date for filtering (inclusive)
        end_date: Optional end date for filtering (exclusive)
    
    Returns:
        List of Session objects matching the category filter(s)
    """
    # Convert single category to list for uniform processing
    if isinstance(category, str):
        categories = [category]
    else:
        categories = category
    
    # Load all sessions with date filters
    all_sessions = load_sessions(start_date=start_date, end_date=end_date)
    
    # Filter by category
    filtered_sessions = [
        session for session in all_sessions
        if session.category in categories
    ]
    
    return filtered_sessions


def get_category_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Dict]:
    """
    Get statistics for each category.
    
    Calculates count, total duration, and average duration for each category.
    
    Args:
        start_date: Optional start date for filtering (inclusive)
        end_date: Optional end date for filtering (exclusive)
    
    Returns:
        Dictionary mapping category names to their statistics:
        {
            "category_name": {
                "count": int,
                "total_duration": timedelta,
                "average_duration": timedelta
            }
        }
    """
    sessions = load_sessions(start_date=start_date, end_date=end_date)
    
    if not sessions:
        return {}
    
    # Aggregate by category
    stats = defaultdict(lambda: {"count": 0, "total_duration": timedelta(0)})
    
    for session in sessions:
        category = session.category
        stats[category]["count"] += 1
        stats[category]["total_duration"] += session.duration
    
    # Calculate averages
    for category, data in stats.items():
        count = data["count"]
        total = data["total_duration"]
        data["average_duration"] = total / count if count > 0 else timedelta(0)
    
    return dict(stats)


def get_sessions_count(
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> int:
    """
    Get the count of sessions, optionally filtered.
    
    Args:
        category: Optional category to filter by
        start_date: Optional start date for filtering (inclusive)
        end_date: Optional end date for filtering (exclusive)
    
    Returns:
        Number of sessions matching the filters
    """
    if category:
        sessions = load_sessions_by_category(
            category,
            start_date=start_date,
            end_date=end_date
        )
    else:
        sessions = load_sessions(start_date=start_date, end_date=end_date)
    
    return len(sessions)
