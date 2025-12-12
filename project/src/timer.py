"""Timer module for tracking task time."""

import uuid
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List

# Default task categories
DEFAULT_CATEGORIES = ['feature', 'bug', 'refactor', 'docs', 'meeting']

# For backward compatibility
VALID_CATEGORIES = DEFAULT_CATEGORIES.copy()


def get_storage_dir() -> Path:
    """
    Get the storage directory path.
    
    Returns:
        Path to the storage directory (~/.task_timer/)
    """
    storage_dir = Path.home() / ".task_timer"
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir


def _load_custom_categories() -> List[str]:
    """
    Load custom categories from configuration file.
    
    Returns:
        List of custom category names
    """
    config_file = get_categories_file()
    
    if not config_file.exists():
        return []
    
    try:
        with open(config_file, 'r') as f:
            data = json.load(f)
            return data.get("custom_categories", [])
    except (json.JSONDecodeError, IOError):
        return []


def _save_custom_categories(custom_categories: List[str]) -> None:
    """
    Save custom categories to configuration file.
    
    Args:
        custom_categories: List of custom category names to save
    """
    config_file = get_categories_file()
    
    data = {"custom_categories": custom_categories}
    
    with open(config_file, 'w') as f:
        json.dump(data, f, indent=2)


# In-memory cache for custom categories
_custom_categories_cache = None


def get_categories_file() -> Path:
    """
    Get the path to the categories configuration file.
    
    Returns:
        Path to categories.json file
    """
    return get_storage_dir() / "categories.json"


def get_valid_categories() -> List[str]:
    """
    Get all valid categories (default + custom).
    
    Returns:
        List of all valid category names
    """
    global _custom_categories_cache
    
    # Load from cache or file
    if _custom_categories_cache is None:
        _custom_categories_cache = _load_custom_categories()
    
    # Combine default and custom categories
    return DEFAULT_CATEGORIES + _custom_categories_cache


def add_category(name: str) -> bool:
    """
    Add a custom category.
    
    Args:
        name: Name of the category to add
        
    Returns:
        True if category was added, False if it already exists
        
    Raises:
        ValueError: If category name is empty or None
    """
    global _custom_categories_cache
    
    # Validate input
    if name is None or not name.strip():
        raise ValueError("Category name cannot be empty")
    
    # Check if already exists
    if name in get_valid_categories():
        return False
    
    # Load current custom categories
    if _custom_categories_cache is None:
        _custom_categories_cache = _load_custom_categories()
    
    # Add new category
    _custom_categories_cache.append(name)
    _save_custom_categories(_custom_categories_cache)
    
    return True


def remove_category(name: str) -> bool:
    """
    Remove a custom category.
    
    Cannot remove default categories.
    
    Args:
        name: Name of the category to remove
        
    Returns:
        True if category was removed, False if it doesn't exist or is default
    """
    global _custom_categories_cache
    
    # Cannot remove default categories
    if name in DEFAULT_CATEGORIES:
        return False
    
    # Load current custom categories
    if _custom_categories_cache is None:
        _custom_categories_cache = _load_custom_categories()
    
    # Check if exists in custom categories
    if name not in _custom_categories_cache:
        return False
    
    # Remove category
    _custom_categories_cache.remove(name)
    _save_custom_categories(_custom_categories_cache)
    
    return True


def reset_categories() -> None:
    """
    Reset categories to defaults by removing all custom categories.
    """
    global _custom_categories_cache
    
    _custom_categories_cache = []
    
    categories_file = get_categories_file()
    if categories_file.exists():
        categories_file.unlink()


class Session:
    """
    Represents a completed timing session.
    
    Attributes:
        id: Unique identifier for the session
        task: Description of the task
        category: Task category (feature, bug, refactor, docs, meeting)
        start_time: When the session started
        end_time: When the session ended
        duration: Total time spent (calculated from start_time and end_time)
    """

    def __init__(
        self,
        task: str,
        category: str,
        start_time: datetime,
        end_time: datetime,
        session_id: Optional[str] = None
    ):
        """
        Initialize a new Session.
        
        Args:
            task: Description of the task
            category: Task category
            start_time: When the session started
            end_time: When the session ended
            session_id: Optional unique identifier (generated if not provided)
        """
        self.id = session_id or str(uuid.uuid4())
        self.task = task
        self.category = category
        self.start_time = start_time
        self.end_time = end_time
        self.duration = end_time - start_time

    def to_dict(self) -> dict:
        """
        Convert session to dictionary for serialization.
        
        Returns:
            Dictionary representation of the session
        """
        return {
            "id": self.id,
            "task": self.task,
            "category": self.category,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": int(self.duration.total_seconds())
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """
        Create a Session from a dictionary.
        
        Args:
            data: Dictionary containing session data
            
        Returns:
            Session instance
        """
        return cls(
            task=data["task"],
            category=data["category"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            session_id=data.get("id")
        )


class Timer:
    """
    Manages individual timing sessions.
    
    The Timer class handles starting and stopping time tracking sessions,
    validating inputs, and creating Session objects when timing is complete.
    """

    def __init__(self):
        """Initialize a new Timer in stopped state."""
        self.task: Optional[str] = None
        self.category: Optional[str] = None
        self.start_time: Optional[datetime] = None

    def is_running(self) -> bool:
        """
        Check if the timer is currently running.
        
        Returns:
            True if timer is running, False otherwise
        """
        return self.start_time is not None

    def start(self, task: str, category: str) -> None:
        """
        Start timing a new task.
        
        Args:
            task: Description of the task
            category: Task category (must be in valid categories)
            
        Raises:
            ValueError: If task is empty or category is invalid
            RuntimeError: If timer is already running
        """
        # Validate timer state
        if self.is_running():
            raise RuntimeError("Timer is already running")

        # Validate task
        if task is None or not task.strip():
            raise ValueError("Task name cannot be empty")

        # Validate category using dynamic category list
        valid_categories = get_valid_categories()
        if category not in valid_categories:
            raise ValueError(
                f"Invalid category: {category}. "
                f"Must be one of {valid_categories}"
            )

        # Start the timer
        self.task = task
        self.category = category
        self.start_time = datetime.now()

    def stop(self) -> Session:
        """
        Stop the timer and create a Session.
        
        Returns:
            Session object containing the timing data
            
        Raises:
            RuntimeError: If timer is not running
        """
        if not self.is_running():
            raise RuntimeError("Timer is not running")

        # Create session
        session = Session(
            task=self.task,
            category=self.category,
            start_time=self.start_time,
            end_time=datetime.now()
        )

        # Reset timer state
        self.task = None
        self.category = None
        self.start_time = None

        return session

    def current_duration(self) -> Optional[timedelta]:
        """
        Get the current duration of the running timer.
        
        Returns:
            Current duration as timedelta if timer is running, None otherwise
        """
        if not self.is_running():
            return None

        return datetime.now() - self.start_time
