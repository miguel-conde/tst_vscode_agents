"""Tests for the Storage module."""

import pytest
import json
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta
from src.storage import (
    save_session,
    load_sessions,
    get_active_timer,
    save_active_timer,
    clear_active_timer,
    get_storage_dir,
    load_sessions_by_category,
    get_category_stats,
    get_sessions_count,
    SESSIONS_FILE,
    STATE_FILE
)
from src.timer import Timer, Session


class TestStorageDirectory:
    """Tests for storage directory management."""

    def test_get_storage_dir_returns_path(self):
        """Test that get_storage_dir returns a Path object."""
        storage_dir = get_storage_dir()
        
        assert isinstance(storage_dir, Path)

    def test_get_storage_dir_creates_directory(self):
        """Test that storage directory is created if it doesn't exist."""
        storage_dir = get_storage_dir()
        
        assert storage_dir.exists()
        assert storage_dir.is_dir()

    def test_storage_dir_is_in_home_directory(self):
        """Test that storage directory is in user's home directory."""
        storage_dir = get_storage_dir()
        home = Path.home()
        
        assert str(storage_dir).startswith(str(home))


class TestSaveSession:
    """Tests for saving sessions."""

    @pytest.fixture
    def temp_storage_dir(self, monkeypatch, tmp_path):
        """Create a temporary storage directory for testing."""
        monkeypatch.setattr('src.storage.get_storage_dir', lambda: tmp_path)
        return tmp_path

    def test_save_session_creates_file(self, temp_storage_dir):
        """Test that saving a session creates the sessions file."""
        session = Session(
            task="Test task",
            category="feature",
            start_time=datetime(2025, 12, 3, 10, 0, 0),
            end_time=datetime(2025, 12, 3, 11, 0, 0)
        )
        
        save_session(session)
        
        sessions_file = temp_storage_dir / SESSIONS_FILE
        assert sessions_file.exists()

    def test_save_session_writes_valid_json(self, temp_storage_dir):
        """Test that saved session is valid JSON."""
        session = Session(
            task="Test task",
            category="bug",
            start_time=datetime(2025, 12, 3, 10, 0, 0),
            end_time=datetime(2025, 12, 3, 11, 0, 0)
        )
        
        save_session(session)
        
        sessions_file = temp_storage_dir / SESSIONS_FILE
        with open(sessions_file, 'r') as f:
            data = json.load(f)
        
        assert "sessions" in data
        assert isinstance(data["sessions"], list)

    def test_save_session_appends_to_existing_sessions(self, temp_storage_dir):
        """Test that saving multiple sessions appends to the file."""
        session1 = Session(
            task="Task 1",
            category="feature",
            start_time=datetime(2025, 12, 3, 10, 0, 0),
            end_time=datetime(2025, 12, 3, 11, 0, 0)
        )
        session2 = Session(
            task="Task 2",
            category="bug",
            start_time=datetime(2025, 12, 3, 12, 0, 0),
            end_time=datetime(2025, 12, 3, 13, 0, 0)
        )
        
        save_session(session1)
        save_session(session2)
        
        sessions = load_sessions()
        assert len(sessions) == 2
        assert sessions[0].task == "Task 1"
        assert sessions[1].task == "Task 2"

    def test_save_session_preserves_all_fields(self, temp_storage_dir):
        """Test that all session fields are correctly saved."""
        start = datetime(2025, 12, 3, 10, 30, 0)
        end = datetime(2025, 12, 3, 11, 45, 0)
        session = Session(
            task="Important task",
            category="refactor",
            start_time=start,
            end_time=end
        )
        
        save_session(session)
        sessions = load_sessions()
        
        assert len(sessions) == 1
        saved = sessions[0]
        assert saved.task == "Important task"
        assert saved.category == "refactor"
        assert saved.start_time == start
        assert saved.end_time == end
        assert saved.duration == timedelta(hours=1, minutes=15)


class TestLoadSessions:
    """Tests for loading sessions."""

    @pytest.fixture
    def temp_storage_dir(self, monkeypatch, tmp_path):
        """Create a temporary storage directory for testing."""
        monkeypatch.setattr('src.storage.get_storage_dir', lambda: tmp_path)
        return tmp_path

    def test_load_sessions_returns_empty_list_when_no_file(self, temp_storage_dir):
        """Test that loading sessions returns empty list when file doesn't exist."""
        sessions = load_sessions()
        
        assert isinstance(sessions, list)
        assert len(sessions) == 0

    def test_load_sessions_returns_all_saved_sessions(self, temp_storage_dir):
        """Test that all saved sessions are loaded."""
        # Save multiple sessions
        for i in range(3):
            session = Session(
                task=f"Task {i}",
                category="feature",
                start_time=datetime(2025, 12, 3, 10 + i, 0, 0),
                end_time=datetime(2025, 12, 3, 11 + i, 0, 0)
            )
            save_session(session)
        
        sessions = load_sessions()
        
        assert len(sessions) == 3
        assert sessions[0].task == "Task 0"
        assert sessions[1].task == "Task 1"
        assert sessions[2].task == "Task 2"

    def test_load_sessions_with_date_filter(self, temp_storage_dir):
        """Test loading sessions filtered by date range."""
        # Save sessions on different dates
        session1 = Session(
            task="Old task",
            category="feature",
            start_time=datetime(2025, 12, 1, 10, 0, 0),
            end_time=datetime(2025, 12, 1, 11, 0, 0)
        )
        session2 = Session(
            task="Recent task",
            category="bug",
            start_time=datetime(2025, 12, 3, 10, 0, 0),
            end_time=datetime(2025, 12, 3, 11, 0, 0)
        )
        
        save_session(session1)
        save_session(session2)
        
        # Load only recent sessions
        sessions = load_sessions(
            start_date=datetime(2025, 12, 3, 0, 0, 0)
        )
        
        assert len(sessions) == 1
        assert sessions[0].task == "Recent task"

    def test_load_sessions_with_end_date_filter(self, temp_storage_dir):
        """Test loading sessions with end date filter."""
        session1 = Session(
            task="Task 1",
            category="feature",
            start_time=datetime(2025, 12, 1, 10, 0, 0),
            end_time=datetime(2025, 12, 1, 11, 0, 0)
        )
        session2 = Session(
            task="Task 2",
            category="bug",
            start_time=datetime(2025, 12, 5, 10, 0, 0),
            end_time=datetime(2025, 12, 5, 11, 0, 0)
        )
        
        save_session(session1)
        save_session(session2)
        
        sessions = load_sessions(
            end_date=datetime(2025, 12, 2, 0, 0, 0)
        )
        
        assert len(sessions) == 1
        assert sessions[0].task == "Task 1"

    def test_load_sessions_with_date_range(self, temp_storage_dir):
        """Test loading sessions within a date range."""
        sessions_data = [
            ("Task 1", datetime(2025, 12, 1, 10, 0, 0)),
            ("Task 2", datetime(2025, 12, 3, 10, 0, 0)),
            ("Task 3", datetime(2025, 12, 5, 10, 0, 0)),
        ]
        
        for task, start in sessions_data:
            session = Session(
                task=task,
                category="feature",
                start_time=start,
                end_time=start + timedelta(hours=1)
            )
            save_session(session)
        
        sessions = load_sessions(
            start_date=datetime(2025, 12, 2, 0, 0, 0),
            end_date=datetime(2025, 12, 4, 0, 0, 0)
        )
        
        assert len(sessions) == 1
        assert sessions[0].task == "Task 2"


class TestActiveTimer:
    """Tests for active timer state management."""

    @pytest.fixture
    def temp_storage_dir(self, monkeypatch, tmp_path):
        """Create a temporary storage directory for testing."""
        monkeypatch.setattr('src.storage.get_storage_dir', lambda: tmp_path)
        return tmp_path

    def test_get_active_timer_returns_none_when_no_state(self, temp_storage_dir):
        """Test that get_active_timer returns None when no state file exists."""
        timer = get_active_timer()
        
        assert timer is None

    def test_save_active_timer_creates_state_file(self, temp_storage_dir):
        """Test that saving active timer creates state file."""
        timer = Timer()
        timer.start(task="Active task", category="feature")
        
        save_active_timer(timer)
        
        state_file = temp_storage_dir / STATE_FILE
        assert state_file.exists()

    def test_save_and_load_active_timer(self, temp_storage_dir):
        """Test that active timer can be saved and loaded."""
        timer = Timer()
        timer.start(task="Test task", category="bug")
        
        save_active_timer(timer)
        loaded_timer = get_active_timer()
        
        assert loaded_timer is not None
        assert loaded_timer.task == "Test task"
        assert loaded_timer.category == "bug"
        assert loaded_timer.is_running()

    def test_clear_active_timer_removes_state_file(self, temp_storage_dir):
        """Test that clearing active timer removes state file."""
        timer = Timer()
        timer.start(task="Task", category="feature")
        save_active_timer(timer)
        
        clear_active_timer()
        
        state_file = temp_storage_dir / STATE_FILE
        assert not state_file.exists()

    def test_clear_active_timer_when_no_state_file(self, temp_storage_dir):
        """Test that clearing active timer works even when no state file exists."""
        # Should not raise an error
        clear_active_timer()
        
        state_file = temp_storage_dir / STATE_FILE
        assert not state_file.exists()

    def test_get_active_timer_after_clear(self, temp_storage_dir):
        """Test that get_active_timer returns None after clearing."""
        timer = Timer()
        timer.start(task="Task", category="feature")
        save_active_timer(timer)
        
        clear_active_timer()
        loaded_timer = get_active_timer()
        
        assert loaded_timer is None


class TestStorageIntegration:
    """Integration tests for storage operations."""

    @pytest.fixture
    def temp_storage_dir(self, monkeypatch, tmp_path):
        """Create a temporary storage directory for testing."""
        monkeypatch.setattr('src.storage.get_storage_dir', lambda: tmp_path)
        return tmp_path

    def test_complete_timer_workflow(self, temp_storage_dir):
        """Test complete workflow: start timer, save state, stop, save session."""
        # Start timer and save state
        timer = Timer()
        timer.start(task="Full workflow task", category="feature")
        save_active_timer(timer)
        
        # Verify state is saved
        loaded_timer = get_active_timer()
        assert loaded_timer is not None
        assert loaded_timer.is_running()
        
        # Stop timer and save session
        session = loaded_timer.stop()
        save_session(session)
        clear_active_timer()
        
        # Verify session is saved and state is cleared
        sessions = load_sessions()
        assert len(sessions) == 1
        assert sessions[0].task == "Full workflow task"
        
        assert get_active_timer() is None


class TestLoadSessionsByCategory:
    """Tests for loading sessions filtered by category."""

    @pytest.fixture
    def temp_storage_dir(self, monkeypatch, tmp_path):
        """Create a temporary storage directory for testing."""
        monkeypatch.setattr('src.storage.get_storage_dir', lambda: tmp_path)
        return tmp_path

    def test_load_sessions_by_single_category(self, temp_storage_dir):
        """Test loading sessions for a single category."""
        # Save sessions with different categories
        categories_data = [
            ("Feature 1", "feature"),
            ("Bug 1", "bug"),
            ("Feature 2", "feature"),
            ("Refactor 1", "refactor"),
            ("Feature 3", "feature"),
        ]
        
        for task, category in categories_data:
            session = Session(
                task=task,
                category=category,
                start_time=datetime(2025, 12, 3, 10, 0, 0),
                end_time=datetime(2025, 12, 3, 11, 0, 0)
            )
            save_session(session)
        
        # Load only feature sessions
        feature_sessions = load_sessions_by_category("feature")
        
        assert len(feature_sessions) == 3
        assert all(s.category == "feature" for s in feature_sessions)
        assert feature_sessions[0].task == "Feature 1"
        assert feature_sessions[1].task == "Feature 2"
        assert feature_sessions[2].task == "Feature 3"

    def test_load_sessions_by_multiple_categories(self, temp_storage_dir):
        """Test loading sessions for multiple categories."""
        categories_data = [
            ("Feature 1", "feature"),
            ("Bug 1", "bug"),
            ("Bug 2", "bug"),
            ("Docs 1", "docs"),
            ("Feature 2", "feature"),
        ]
        
        for task, category in categories_data:
            session = Session(
                task=task,
                category=category,
                start_time=datetime(2025, 12, 3, 10, 0, 0),
                end_time=datetime(2025, 12, 3, 11, 0, 0)
            )
            save_session(session)
        
        # Load feature and bug sessions
        sessions = load_sessions_by_category(["feature", "bug"])
        
        assert len(sessions) == 4
        categories = [s.category for s in sessions]
        assert "feature" in categories
        assert "bug" in categories
        assert "docs" not in categories

    def test_load_sessions_by_category_returns_empty_when_none_match(self, temp_storage_dir):
        """Test that loading by category returns empty list when no matches."""
        session = Session(
            task="Feature task",
            category="feature",
            start_time=datetime(2025, 12, 3, 10, 0, 0),
            end_time=datetime(2025, 12, 3, 11, 0, 0)
        )
        save_session(session)
        
        bug_sessions = load_sessions_by_category("bug")
        
        assert len(bug_sessions) == 0

    def test_load_sessions_by_category_with_date_filter(self, temp_storage_dir):
        """Test combining category and date filters."""
        sessions_data = [
            ("Old feature", "feature", datetime(2025, 12, 1, 10, 0, 0)),
            ("Recent feature", "feature", datetime(2025, 12, 3, 10, 0, 0)),
            ("Recent bug", "bug", datetime(2025, 12, 3, 10, 0, 0)),
        ]
        
        for task, category, start in sessions_data:
            session = Session(
                task=task,
                category=category,
                start_time=start,
                end_time=start + timedelta(hours=1)
            )
            save_session(session)
        
        # Load recent feature sessions only
        sessions = load_sessions_by_category(
            "feature",
            start_date=datetime(2025, 12, 2, 0, 0, 0)
        )
        
        assert len(sessions) == 1
        assert sessions[0].task == "Recent feature"


class TestCategoryStats:
    """Tests for category statistics."""

    @pytest.fixture
    def temp_storage_dir(self, monkeypatch, tmp_path):
        """Create a temporary storage directory for testing."""
        monkeypatch.setattr('src.storage.get_storage_dir', lambda: tmp_path)
        return tmp_path

    def test_get_category_stats_empty_sessions(self, temp_storage_dir):
        """Test category stats with no sessions."""
        stats = get_category_stats()
        
        assert isinstance(stats, dict)
        assert len(stats) == 0

    def test_get_category_stats_single_category(self, temp_storage_dir):
        """Test category stats with single category."""
        for i in range(3):
            session = Session(
                task=f"Task {i}",
                category="feature",
                start_time=datetime(2025, 12, 3, 10 + i, 0, 0),
                end_time=datetime(2025, 12, 3, 11 + i, 0, 0)
            )
            save_session(session)
        
        stats = get_category_stats()
        
        assert "feature" in stats
        assert stats["feature"]["count"] == 3
        assert stats["feature"]["total_duration"] == timedelta(hours=3)

    def test_get_category_stats_multiple_categories(self, temp_storage_dir):
        """Test category stats with multiple categories."""
        sessions_data = [
            ("Task 1", "feature", 2),  # 2 hours
            ("Task 2", "bug", 1),      # 1 hour
            ("Task 3", "feature", 1),  # 1 hour
            ("Task 4", "refactor", 3), # 3 hours
            ("Task 5", "bug", 2),      # 2 hours
        ]
        
        for task, category, hours in sessions_data:
            start = datetime(2025, 12, 3, 10, 0, 0)
            session = Session(
                task=task,
                category=category,
                start_time=start,
                end_time=start + timedelta(hours=hours)
            )
            save_session(session)
        
        stats = get_category_stats()
        
        assert len(stats) == 3
        assert stats["feature"]["count"] == 2
        assert stats["feature"]["total_duration"] == timedelta(hours=3)
        assert stats["bug"]["count"] == 2
        assert stats["bug"]["total_duration"] == timedelta(hours=3)
        assert stats["refactor"]["count"] == 1
        assert stats["refactor"]["total_duration"] == timedelta(hours=3)

    def test_get_category_stats_calculates_average_duration(self, temp_storage_dir):
        """Test that category stats include average duration."""
        for i in range(4):
            session = Session(
                task=f"Task {i}",
                category="feature",
                start_time=datetime(2025, 12, 3, 10, 0, 0),
                end_time=datetime(2025, 12, 3, 11, 0, 0)  # 1 hour each
            )
            save_session(session)
        
        stats = get_category_stats()
        
        assert stats["feature"]["average_duration"] == timedelta(hours=1)

    def test_get_category_stats_with_date_filter(self, temp_storage_dir):
        """Test category stats with date filtering."""
        sessions_data = [
            ("Old task", "feature", datetime(2025, 12, 1, 10, 0, 0)),
            ("Recent task 1", "feature", datetime(2025, 12, 3, 10, 0, 0)),
            ("Recent task 2", "bug", datetime(2025, 12, 3, 12, 0, 0)),
        ]
        
        for task, category, start in sessions_data:
            session = Session(
                task=task,
                category=category,
                start_time=start,
                end_time=start + timedelta(hours=1)
            )
            save_session(session)
        
        # Get stats for recent sessions only
        stats = get_category_stats(start_date=datetime(2025, 12, 2, 0, 0, 0))
        
        assert len(stats) == 2
        assert stats["feature"]["count"] == 1
        assert stats["bug"]["count"] == 1


class TestSessionsCount:
    """Tests for counting sessions."""

    @pytest.fixture
    def temp_storage_dir(self, monkeypatch, tmp_path):
        """Create a temporary storage directory for testing."""
        monkeypatch.setattr('src.storage.get_storage_dir', lambda: tmp_path)
        return tmp_path

    def test_get_sessions_count_when_empty(self, temp_storage_dir):
        """Test getting count when no sessions exist."""
        count = get_sessions_count()
        
        assert count == 0

    def test_get_sessions_count_returns_total(self, temp_storage_dir):
        """Test that get_sessions_count returns total number of sessions."""
        for i in range(5):
            session = Session(
                task=f"Task {i}",
                category="feature",
                start_time=datetime(2025, 12, 3, 10, 0, 0),
                end_time=datetime(2025, 12, 3, 11, 0, 0)
            )
            save_session(session)
        
        count = get_sessions_count()
        
        assert count == 5

    def test_get_sessions_count_with_category_filter(self, temp_storage_dir):
        """Test counting sessions by category."""
        categories_data = [
            ("Task 1", "feature"),
            ("Task 2", "bug"),
            ("Task 3", "feature"),
            ("Task 4", "refactor"),
            ("Task 5", "feature"),
        ]
        
        for task, category in categories_data:
            session = Session(
                task=task,
                category=category,
                start_time=datetime(2025, 12, 3, 10, 0, 0),
                end_time=datetime(2025, 12, 3, 11, 0, 0)
            )
            save_session(session)
        
        feature_count = get_sessions_count(category="feature")
        bug_count = get_sessions_count(category="bug")
        
        assert feature_count == 3
        assert bug_count == 1

    def test_get_sessions_count_with_date_filter(self, temp_storage_dir):
        """Test counting sessions with date range."""
        sessions_data = [
            ("Task 1", datetime(2025, 12, 1, 10, 0, 0)),
            ("Task 2", datetime(2025, 12, 3, 10, 0, 0)),
            ("Task 3", datetime(2025, 12, 5, 10, 0, 0)),
        ]
        
        for task, start in sessions_data:
            session = Session(
                task=task,
                category="feature",
                start_time=start,
                end_time=start + timedelta(hours=1)
            )
            save_session(session)
        
        count = get_sessions_count(
            start_date=datetime(2025, 12, 2, 0, 0, 0),
            end_date=datetime(2025, 12, 4, 0, 0, 0)
        )
        
        assert count == 1
