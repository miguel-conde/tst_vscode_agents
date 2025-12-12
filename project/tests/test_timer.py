"""Tests for the Timer class."""

import pytest
from datetime import datetime, timedelta
from src.timer import Timer, Session, get_valid_categories, DEFAULT_CATEGORIES

# Get default categories for tests  
VALID_CATEGORIES = get_valid_categories()


class TestSession:
    """Tests for the Session data class."""

    def test_session_creation_with_all_fields(self):
        """Test creating a session with all required fields."""
        start = datetime(2025, 12, 3, 10, 0, 0)
        end = datetime(2025, 12, 3, 11, 30, 0)
        
        session = Session(
            task="Fix login bug",
            category="bug",
            start_time=start,
            end_time=end
        )
        
        assert session.task == "Fix login bug"
        assert session.category == "bug"
        assert session.start_time == start
        assert session.end_time == end
        assert session.duration == timedelta(hours=1, minutes=30)

    def test_session_duration_calculation(self):
        """Test that session correctly calculates duration."""
        start = datetime(2025, 12, 3, 9, 0, 0)
        end = datetime(2025, 12, 3, 9, 45, 0)
        
        session = Session(
            task="Write tests",
            category="feature",
            start_time=start,
            end_time=end
        )
        
        assert session.duration == timedelta(minutes=45)

    def test_session_with_zero_duration(self):
        """Test session with same start and end time."""
        time = datetime(2025, 12, 3, 10, 0, 0)
        
        session = Session(
            task="Quick task",
            category="docs",
            start_time=time,
            end_time=time
        )
        
        assert session.duration == timedelta(0)

    def test_session_to_dict(self):
        """Test converting session to dictionary."""
        start = datetime(2025, 12, 3, 10, 0, 0)
        end = datetime(2025, 12, 3, 10, 30, 0)
        
        session = Session(
            task="Test task",
            category="feature",
            start_time=start,
            end_time=end
        )
        
        session_dict = session.to_dict()
        
        assert session_dict["task"] == "Test task"
        assert session_dict["category"] == "feature"
        assert session_dict["start_time"] == "2025-12-03T10:00:00"
        assert session_dict["end_time"] == "2025-12-03T10:30:00"
        assert session_dict["duration_seconds"] == 1800
        assert "id" in session_dict

    def test_session_from_dict(self):
        """Test creating session from dictionary."""
        data = {
            "id": "test-id-123",
            "task": "Test task",
            "category": "bug",
            "start_time": "2025-12-03T10:00:00",
            "end_time": "2025-12-03T11:00:00",
            "duration_seconds": 3600
        }
        
        session = Session.from_dict(data)
        
        assert session.id == "test-id-123"
        assert session.task == "Test task"
        assert session.category == "bug"
        assert session.start_time == datetime(2025, 12, 3, 10, 0, 0)
        assert session.end_time == datetime(2025, 12, 3, 11, 0, 0)
        assert session.duration == timedelta(hours=1)


class TestTimer:
    """Tests for the Timer class."""

    def test_timer_initialization(self):
        """Test that timer initializes in stopped state."""
        timer = Timer()
        
        assert not timer.is_running()
        assert timer.task is None
        assert timer.category is None
        assert timer.start_time is None

    def test_start_timer_with_valid_category(self):
        """Test starting timer with valid task and category."""
        timer = Timer()
        
        timer.start(task="Implement feature", category="feature")
        
        assert timer.is_running()
        assert timer.task == "Implement feature"
        assert timer.category == "feature"
        assert timer.start_time is not None
        assert isinstance(timer.start_time, datetime)

    def test_start_timer_with_all_valid_categories(self):
        """Test that all defined categories work."""
        for category in get_valid_categories():
            timer = Timer()
            timer.start(task=f"Task for {category}", category=category)
            
            assert timer.is_running()
            assert timer.category == category

    def test_start_timer_with_invalid_category_raises_error(self):
        """Test that invalid category raises ValueError."""
        timer = Timer()
        
        with pytest.raises(ValueError, match="Invalid category"):
            timer.start(task="Task", category="invalid_category")

    def test_start_timer_twice_raises_error(self):
        """Test that starting an already running timer raises error."""
        timer = Timer()
        timer.start(task="First task", category="feature")
        
        with pytest.raises(RuntimeError, match="Timer is already running"):
            timer.start(task="Second task", category="bug")

    def test_stop_timer_returns_session(self):
        """Test that stopping timer returns a Session object."""
        timer = Timer()
        timer.start(task="Test task", category="feature")
        
        session = timer.stop()
        
        assert isinstance(session, Session)
        assert session.task == "Test task"
        assert session.category == "feature"
        assert session.start_time is not None
        assert session.end_time is not None
        assert session.duration > timedelta(0)

    def test_stop_timer_when_not_running_raises_error(self):
        """Test that stopping a non-running timer raises error."""
        timer = Timer()
        
        with pytest.raises(RuntimeError, match="Timer is not running"):
            timer.stop()

    def test_timer_state_after_stop(self):
        """Test that timer is properly reset after stop."""
        timer = Timer()
        timer.start(task="Task", category="bug")
        session = timer.stop()
        
        assert not timer.is_running()
        assert timer.task is None
        assert timer.category is None
        assert timer.start_time is None

    def test_current_duration_while_running(self):
        """Test getting current duration while timer is running."""
        timer = Timer()
        timer.start(task="Task", category="feature")
        
        import time
        time.sleep(0.1)  # Sleep for a bit to get non-zero duration
        
        duration = timer.current_duration()
        
        assert isinstance(duration, timedelta)
        assert duration > timedelta(0)

    def test_current_duration_when_not_running(self):
        """Test that current_duration returns None when timer not running."""
        timer = Timer()
        
        duration = timer.current_duration()
        
        assert duration is None

    def test_empty_task_name_raises_error(self):
        """Test that empty task name raises ValueError."""
        timer = Timer()
        
        with pytest.raises(ValueError, match="Task name cannot be empty"):
            timer.start(task="", category="feature")

    def test_whitespace_only_task_name_raises_error(self):
        """Test that whitespace-only task name raises ValueError."""
        timer = Timer()
        
        with pytest.raises(ValueError, match="Task name cannot be empty"):
            timer.start(task="   ", category="feature")

    def test_none_task_name_raises_error(self):
        """Test that None task name raises ValueError."""
        timer = Timer()
        
        with pytest.raises(ValueError, match="Task name cannot be empty"):
            timer.start(task=None, category="feature")

    def test_session_duration_accuracy(self):
        """Test that session duration is accurately calculated."""
        timer = Timer()
        timer.start(task="Timed task", category="feature")
        
        import time
        time.sleep(0.2)  # Sleep for 200ms
        
        session = timer.stop()
        
        # Duration should be at least 200ms but less than 300ms
        assert session.duration >= timedelta(milliseconds=200)
        assert session.duration < timedelta(milliseconds=300)


class TestDefaultCategories:
    """Tests for default category constants."""

    def test_default_categories_constant_exists(self):
        """Test that DEFAULT_CATEGORIES is defined."""
        assert DEFAULT_CATEGORIES is not None
        assert isinstance(DEFAULT_CATEGORIES, (list, tuple))

    def test_default_categories_contains_expected_values(self):
        """Test that all expected categories are present."""
        expected = ['feature', 'bug', 'refactor', 'docs', 'meeting']
        
        for category in expected:
            assert category in DEFAULT_CATEGORIES

    def test_default_categories_is_not_empty(self):
        """Test that there is at least one default category."""
        assert len(DEFAULT_CATEGORIES) > 0
