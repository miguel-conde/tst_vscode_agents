"""Tests for the CLI commands."""

import pytest
from click.testing import CliRunner
from datetime import datetime, timedelta
from src.cli import cli, start, stop, status, list_sessions
from src.storage import (
    get_active_timer,
    clear_active_timer,
    save_session,
    load_sessions,
    get_storage_dir
)
from src.timer import Session, get_valid_categories

# Get default categories for tests
VALID_CATEGORIES = get_valid_categories()


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_storage(monkeypatch, tmp_path):
    """Use temporary storage for tests."""
    monkeypatch.setattr('src.storage.get_storage_dir', lambda: tmp_path)
    monkeypatch.setattr('src.cli.get_storage_dir', lambda: tmp_path)
    return tmp_path


@pytest.fixture(autouse=True)
def clean_state(temp_storage):
    """Ensure clean state before each test."""
    clear_active_timer()
    yield
    clear_active_timer()


class TestStartCommand:
    """Tests for the 'start' command."""

    def test_start_with_valid_task_and_category(self, runner, temp_storage):
        """Test starting a timer with valid parameters."""
        result = runner.invoke(cli, ['start', '--task', 'Test task', '--category', 'feature'])
        
        assert result.exit_code == 0
        assert 'Started timer' in result.output
        assert 'Test task' in result.output
        
        # Verify timer was saved
        timer = get_active_timer()
        assert timer is not None
        assert timer.task == 'Test task'
        assert timer.category == 'feature'

    def test_start_with_all_valid_categories(self, runner, temp_storage):
        """Test that start works with all valid categories."""
        for category in get_valid_categories():
            # Clear any existing timer
            clear_active_timer()
            
            result = runner.invoke(cli, ['start', '--task', f'Task for {category}', '--category', category])
            
            assert result.exit_code == 0
            assert category in result.output

    def test_start_with_invalid_category(self, runner, temp_storage):
        """Test that invalid category produces error."""
        result = runner.invoke(cli, ['start', '--task', 'Test', '--category', 'invalid'])
        
        assert result.exit_code != 0
        assert 'Invalid value' in result.output or 'invalid' in result.output.lower()

    def test_start_without_task_fails(self, runner, temp_storage):
        """Test that start command requires --task option."""
        result = runner.invoke(cli, ['start', '--category', 'feature'])
        
        assert result.exit_code != 0
        assert 'Missing option' in result.output or 'task' in result.output.lower()

    def test_start_without_category_fails(self, runner, temp_storage):
        """Test that start command requires --category option."""
        result = runner.invoke(cli, ['start', '--task', 'Test'])
        
        assert result.exit_code != 0
        assert 'Missing option' in result.output or 'category' in result.output.lower()

    def test_start_when_timer_already_running(self, runner, temp_storage):
        """Test that starting a second timer shows error."""
        # Start first timer
        runner.invoke(cli, ['start', '--task', 'First task', '--category', 'feature'])
        
        # Try to start second timer
        result = runner.invoke(cli, ['start', '--task', 'Second task', '--category', 'bug'])
        
        assert result.exit_code != 0
        assert 'already running' in result.output.lower()

    def test_start_with_empty_task_name(self, runner, temp_storage):
        """Test that empty task name produces error."""
        result = runner.invoke(cli, ['start', '--task', '', '--category', 'feature'])
        
        assert result.exit_code != 0
        assert 'empty' in result.output.lower()


class TestStopCommand:
    """Tests for the 'stop' command."""

    def test_stop_running_timer(self, runner, temp_storage):
        """Test stopping an active timer."""
        # Start a timer
        runner.invoke(cli, ['start', '--task', 'Test task', '--category', 'feature'])
        
        # Stop it
        result = runner.invoke(cli, ['stop'])
        
        assert result.exit_code == 0
        assert 'Stopped timer' in result.output or 'saved' in result.output.lower()
        assert 'Test task' in result.output
        
        # Verify session was saved
        sessions = load_sessions()
        assert len(sessions) == 1
        assert sessions[0].task == 'Test task'
        
        # Verify timer state was cleared
        assert get_active_timer() is None

    def test_stop_when_no_timer_running(self, runner, temp_storage):
        """Test stopping when no timer is active."""
        result = runner.invoke(cli, ['stop'])
        
        assert result.exit_code != 0
        assert 'No timer' in result.output or 'not running' in result.output.lower()

    def test_stop_shows_duration(self, runner, temp_storage):
        """Test that stop command shows duration."""
        runner.invoke(cli, ['start', '--task', 'Timed task', '--category', 'bug'])
        
        import time
        time.sleep(0.1)
        
        result = runner.invoke(cli, ['stop'])
        
        assert result.exit_code == 0
        # Should show some time indication
        assert any(word in result.output.lower() for word in ['duration', 'time', 'second', 'minute'])


class TestStatusCommand:
    """Tests for the 'status' command."""

    def test_status_when_timer_running(self, runner, temp_storage):
        """Test status shows current timer info."""
        runner.invoke(cli, ['start', '--task', 'Active task', '--category', 'refactor'])
        
        result = runner.invoke(cli, ['status'])
        
        assert result.exit_code == 0
        assert 'Active task' in result.output
        assert 'refactor' in result.output
        assert 'running' in result.output.lower() or 'active' in result.output.lower()

    def test_status_when_no_timer_running(self, runner, temp_storage):
        """Test status when no timer is active."""
        result = runner.invoke(cli, ['status'])
        
        assert result.exit_code == 0
        assert 'No timer' in result.output or 'not running' in result.output.lower()

    def test_status_shows_elapsed_time(self, runner, temp_storage):
        """Test that status shows elapsed time."""
        runner.invoke(cli, ['start', '--task', 'Long task', '--category', 'feature'])
        
        import time
        time.sleep(0.1)
        
        result = runner.invoke(cli, ['status'])
        
        assert result.exit_code == 0
        # Should show elapsed time
        assert any(word in result.output.lower() for word in ['elapsed', 'running', 'duration'])

    def test_status_shows_start_time(self, runner, temp_storage):
        """Test that status shows when timer was started."""
        runner.invoke(cli, ['start', '--task', 'Task', '--category', 'docs'])
        
        result = runner.invoke(cli, ['status'])
        
        assert result.exit_code == 0
        assert 'started' in result.output.lower() or 'since' in result.output.lower()


class TestCLIIntegration:
    """Integration tests for CLI workflow."""

    def test_complete_workflow(self, runner, temp_storage):
        """Test complete start-stop-status workflow."""
        # Check status initially
        result = runner.invoke(cli, ['status'])
        assert 'No timer' in result.output or 'not running' in result.output.lower()
        
        # Start timer
        result = runner.invoke(cli, ['start', '--task', 'Full workflow', '--category', 'feature'])
        assert result.exit_code == 0
        
        # Check status while running
        result = runner.invoke(cli, ['status'])
        assert 'Full workflow' in result.output
        
        # Stop timer
        result = runner.invoke(cli, ['stop'])
        assert result.exit_code == 0
        
        # Check status after stop
        result = runner.invoke(cli, ['status'])
        assert 'No timer' in result.output or 'not running' in result.output.lower()
        
        # Verify session was saved
        sessions = load_sessions()
        assert len(sessions) == 1
        assert sessions[0].task == 'Full workflow'

    def test_multiple_sessions(self, runner, temp_storage):
        """Test creating multiple sessions."""
        tasks = [
            ('Task 1', 'feature'),
            ('Task 2', 'bug'),
            ('Task 3', 'refactor')
        ]
        
        for task, category in tasks:
            runner.invoke(cli, ['start', '--task', task, '--category', category])
            import time
            time.sleep(0.05)
            runner.invoke(cli, ['stop'])
        
        # Verify all sessions were saved
        sessions = load_sessions()
        assert len(sessions) == 3
        assert sessions[0].task == 'Task 1'
        assert sessions[1].task == 'Task 2'
        assert sessions[2].task == 'Task 3'

    def test_cli_help_command(self, runner, temp_storage):
        """Test that help command works."""
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert 'start' in result.output.lower()
        assert 'stop' in result.output.lower()
        assert 'status' in result.output.lower()

    def test_start_help(self, runner, temp_storage):
        """Test help for start command."""
        result = runner.invoke(cli, ['start', '--help'])
        
        assert result.exit_code == 0
        assert 'task' in result.output.lower()
        assert 'category' in result.output.lower()


class TestListCommand:
    """Tests for the 'list' command."""

    def test_list_when_no_sessions(self, runner, temp_storage):
        """Test list command when no sessions exist."""
        result = runner.invoke(cli, ['list'])
        
        assert result.exit_code == 0
        assert 'No sessions' in result.output or '0' in result.output

    def test_list_displays_all_sessions(self, runner, temp_storage):
        """Test that list displays all saved sessions."""
        # Create multiple sessions
        sessions_data = [
            ("Task 1", "feature"),
            ("Task 2", "bug"),
            ("Task 3", "refactor"),
        ]
        
        for task, category in sessions_data:
            session = Session(
                task=task,
                category=category,
                start_time=datetime(2025, 12, 3, 10, 0, 0),
                end_time=datetime(2025, 12, 3, 11, 0, 0)
            )
            save_session(session)
        
        result = runner.invoke(cli, ['list'])
        
        assert result.exit_code == 0
        assert 'Task 1' in result.output
        assert 'Task 2' in result.output
        assert 'Task 3' in result.output

    def test_list_shows_session_details(self, runner, temp_storage):
        """Test that list shows task, category, and duration."""
        session = Session(
            task="Important task",
            category="feature",
            start_time=datetime(2025, 12, 3, 10, 0, 0),
            end_time=datetime(2025, 12, 3, 11, 30, 0)
        )
        save_session(session)
        
        result = runner.invoke(cli, ['list'])
        
        assert result.exit_code == 0
        assert 'Important task' in result.output
        assert 'feature' in result.output
        # Should show duration in some form
        assert any(word in result.output.lower() for word in ['1h', '90m', 'hour', 'minute'])

    def test_list_filter_by_category(self, runner, temp_storage):
        """Test filtering sessions by category."""
        sessions_data = [
            ("Feature 1", "feature"),
            ("Bug 1", "bug"),
            ("Feature 2", "feature"),
            ("Docs 1", "docs"),
        ]
        
        for task, category in sessions_data:
            session = Session(
                task=task,
                category=category,
                start_time=datetime(2025, 12, 3, 10, 0, 0),
                end_time=datetime(2025, 12, 3, 11, 0, 0)
            )
            save_session(session)
        
        result = runner.invoke(cli, ['list', '--category', 'feature'])
        
        assert result.exit_code == 0
        assert 'Feature 1' in result.output
        assert 'Feature 2' in result.output
        assert 'Bug 1' not in result.output
        assert 'Docs 1' not in result.output

    def test_list_filter_by_today(self, runner, temp_storage):
        """Test filtering sessions by today's date."""
        today = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        
        sessions_data = [
            ("Yesterday task", yesterday),
            ("Today task", today),
        ]
        
        for task, start in sessions_data:
            session = Session(
                task=task,
                category="feature",
                start_time=start,
                end_time=start + timedelta(hours=1)
            )
            save_session(session)
        
        result = runner.invoke(cli, ['list', '--today'])
        
        assert result.exit_code == 0
        assert 'Today task' in result.output
        assert 'Yesterday task' not in result.output

    def test_list_filter_by_week(self, runner, temp_storage):
        """Test filtering sessions by current week."""
        now = datetime.now()
        this_week = now.replace(hour=10, minute=0, second=0, microsecond=0)
        last_week = this_week - timedelta(days=8)
        
        sessions_data = [
            ("Last week task", last_week),
            ("This week task", this_week),
        ]
        
        for task, start in sessions_data:
            session = Session(
                task=task,
                category="feature",
                start_time=start,
                end_time=start + timedelta(hours=1)
            )
            save_session(session)
        
        result = runner.invoke(cli, ['list', '--week'])
        
        assert result.exit_code == 0
        assert 'This week task' in result.output
        assert 'Last week task' not in result.output

    def test_list_shows_total_count(self, runner, temp_storage):
        """Test that list shows total session count."""
        for i in range(3):
            session = Session(
                task=f"Task {i}",
                category="feature",
                start_time=datetime(2025, 12, 3, 10, 0, 0),
                end_time=datetime(2025, 12, 3, 11, 0, 0)
            )
            save_session(session)
        
        result = runner.invoke(cli, ['list'])
        
        assert result.exit_code == 0
        assert '3' in result.output

    def test_list_shows_total_duration(self, runner, temp_storage):
        """Test that list shows total time spent."""
        for i in range(2):
            session = Session(
                task=f"Task {i}",
                category="feature",
                start_time=datetime(2025, 12, 3, 10 + i, 0, 0),
                end_time=datetime(2025, 12, 3, 11 + i, 30, 0)  # 1.5 hours each
            )
            save_session(session)
        
        result = runner.invoke(cli, ['list'])
        
        assert result.exit_code == 0
        # Should show total duration (3 hours)
        assert any(word in result.output.lower() for word in ['total', 'duration', 'time'])

    def test_list_with_limit(self, runner, temp_storage):
        """Test limiting number of sessions displayed."""
        for i in range(10):
            session = Session(
                task=f"Task {i}",
                category="feature",
                start_time=datetime(2025, 12, 3, 10, 0, 0),
                end_time=datetime(2025, 12, 3, 11, 0, 0)
            )
            save_session(session)
        
        result = runner.invoke(cli, ['list', '--limit', '5'])
        
        assert result.exit_code == 0
        # Should show indication of limit
        assert '5' in result.output or 'more' in result.output.lower()

    def test_list_combined_filters(self, runner, temp_storage):
        """Test combining category and date filters."""
        today = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        
        sessions_data = [
            ("Yesterday feature", "feature", yesterday),
            ("Today feature", "feature", today),
            ("Today bug", "bug", today),
        ]
        
        for task, category, start in sessions_data:
            session = Session(
                task=task,
                category=category,
                start_time=start,
                end_time=start + timedelta(hours=1)
            )
            save_session(session)
        
        result = runner.invoke(cli, ['list', '--today', '--category', 'feature'])
        
        assert result.exit_code == 0
        assert 'Today feature' in result.output
        assert 'Yesterday feature' not in result.output
        assert 'Today bug' not in result.output
