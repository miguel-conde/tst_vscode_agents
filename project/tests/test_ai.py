"""
Tests for AI insights module - TDD approach for Phase 4.
"""
import unittest
from datetime import datetime, timedelta
from src.ai import (
    analyze_patterns,
    generate_suggestions,
    calculate_productivity_score,
    detect_work_blocks,
    identify_peak_hours,
)


class TestPatternAnalysis(unittest.TestCase):
    """Test pattern detection in work sessions."""

    def test_analyze_patterns_empty_sessions(self):
        """Test pattern analysis with no sessions."""
        patterns = analyze_patterns([])
        
        self.assertIsInstance(patterns, dict)
        self.assertIn("total_sessions", patterns)
        self.assertEqual(patterns["total_sessions"], 0)

    def test_analyze_patterns_calculates_totals(self):
        """Test pattern analysis calculates basic totals."""
        sessions = [
            {
                "task": "Task 1",
                "category": "development",
                "start_time": "2024-01-15T09:00:00",
                "end_time": "2024-01-15T10:00:00",
                "duration": 3600,
            },
            {
                "task": "Task 2",
                "category": "meetings",
                "start_time": "2024-01-15T11:00:00",
                "end_time": "2024-01-15T12:00:00",
                "duration": 3600,
            },
        ]
        
        patterns = analyze_patterns(sessions)
        
        self.assertEqual(patterns["total_sessions"], 2)
        self.assertEqual(patterns["total_duration"], 7200)

    def test_analyze_patterns_category_distribution(self):
        """Test pattern analysis includes category distribution."""
        sessions = [
            {
                "task": "Dev 1",
                "category": "development",
                "duration": 7200,
                "start_time": "2024-01-15T09:00:00",
                "end_time": "2024-01-15T11:00:00",
            },
            {
                "task": "Dev 2",
                "category": "development",
                "duration": 3600,
                "start_time": "2024-01-15T13:00:00",
                "end_time": "2024-01-15T14:00:00",
            },
            {
                "task": "Meeting",
                "category": "meetings",
                "duration": 1800,
                "start_time": "2024-01-15T15:00:00",
                "end_time": "2024-01-15T15:30:00",
            },
        ]
        
        patterns = analyze_patterns(sessions)
        
        self.assertIn("category_distribution", patterns)
        self.assertEqual(patterns["category_distribution"]["development"]["count"], 2)
        self.assertEqual(patterns["category_distribution"]["development"]["duration"], 10800)

    def test_analyze_patterns_identifies_most_common_category(self):
        """Test pattern analysis identifies most common category."""
        sessions = [
            {"task": "Dev", "category": "development", "duration": 3600, "start_time": "2024-01-15T09:00:00"},
            {"task": "Dev", "category": "development", "duration": 3600, "start_time": "2024-01-15T10:00:00"},
            {"task": "Dev", "category": "development", "duration": 3600, "start_time": "2024-01-15T11:00:00"},
            {"task": "Meet", "category": "meetings", "duration": 1800, "start_time": "2024-01-15T14:00:00"},
        ]
        
        patterns = analyze_patterns(sessions)
        
        self.assertEqual(patterns["most_common_category"], "development")


class TestProductivityScore(unittest.TestCase):
    """Test productivity scoring."""

    def test_calculate_productivity_score_no_sessions(self):
        """Test productivity score with no sessions."""
        score = calculate_productivity_score([])
        
        self.assertIsInstance(score, dict)
        self.assertIn("score", score)
        self.assertIn("rating", score)

    def test_calculate_productivity_score_range(self):
        """Test productivity score is in valid range (0-100)."""
        sessions = [
            {"task": "Task", "category": "development", "duration": 7200, "start_time": "2024-01-15T09:00:00"},
        ]
        
        score = calculate_productivity_score(sessions)
        
        self.assertGreaterEqual(score["score"], 0)
        self.assertLessEqual(score["score"], 100)

    def test_calculate_productivity_score_considers_duration(self):
        """Test productivity score considers total work duration."""
        short_sessions = [
            {"task": "Task", "category": "development", "duration": 1800, "start_time": "2024-01-15T09:00:00"},
        ]
        
        long_sessions = [
            {"task": "Task", "category": "development", "duration": 14400, "start_time": "2024-01-15T09:00:00"},
        ]
        
        short_score = calculate_productivity_score(short_sessions)
        long_score = calculate_productivity_score(long_sessions)
        
        self.assertGreater(long_score["score"], short_score["score"])

    def test_calculate_productivity_score_rating(self):
        """Test productivity score includes text rating."""
        sessions = [
            {"task": "Task", "category": "development", "duration": 7200, "start_time": "2024-01-15T09:00:00"},
        ]
        
        score = calculate_productivity_score(sessions)
        
        self.assertIn(score["rating"], ["Excellent", "Good", "Fair", "Low"])


class TestSuggestionGeneration(unittest.TestCase):
    """Test AI suggestion generation."""

    def test_generate_suggestions_returns_list(self):
        """Test generate suggestions returns a list."""
        sessions = [
            {"task": "Task", "category": "development", "duration": 3600, "start_time": "2024-01-15T09:00:00"},
        ]
        
        suggestions = generate_suggestions(sessions)
        
        self.assertIsInstance(suggestions, list)

    def test_generate_suggestions_not_empty_with_sessions(self):
        """Test suggestions are generated when sessions exist."""
        sessions = [
            {"task": "Task", "category": "development", "duration": 3600, "start_time": "2024-01-15T09:00:00"},
        ]
        
        suggestions = generate_suggestions(sessions)
        
        self.assertGreater(len(suggestions), 0)

    def test_generate_suggestions_for_long_sessions(self):
        """Test suggestions recommend breaks for long sessions."""
        long_sessions = [
            {"task": "Marathon coding", "category": "development", "duration": 14400, "start_time": "2024-01-15T09:00:00"},
        ]
        
        suggestions = generate_suggestions(long_sessions)
        
        # Should suggest taking breaks
        has_break_suggestion = any("break" in s.lower() for s in suggestions)
        self.assertTrue(has_break_suggestion)

    def test_generate_suggestions_for_category_imbalance(self):
        """Test suggestions identify category imbalance."""
        imbalanced_sessions = [
            {"task": "Dev", "category": "development", "duration": 7200, "start_time": "2024-01-15T09:00:00"},
            {"task": "Dev", "category": "development", "duration": 7200, "start_time": "2024-01-15T13:00:00"},
            {"task": "Dev", "category": "development", "duration": 7200, "start_time": "2024-01-16T09:00:00"},
        ]
        
        suggestions = generate_suggestions(imbalanced_sessions)
        
        # Should suggest diversifying activities
        has_balance_suggestion = any("balance" in s.lower() or "divers" in s.lower() for s in suggestions)
        self.assertTrue(has_balance_suggestion)


class TestWorkBlockDetection(unittest.TestCase):
    """Test work block detection."""

    def test_detect_work_blocks_empty_sessions(self):
        """Test work block detection with no sessions."""
        blocks = detect_work_blocks([])
        
        self.assertIsInstance(blocks, list)
        self.assertEqual(len(blocks), 0)

    def test_detect_work_blocks_single_session(self):
        """Test work block detection with single session."""
        sessions = [
            {
                "task": "Task",
                "category": "development",
                "start_time": "2024-01-15T09:00:00",
                "end_time": "2024-01-15T10:00:00",
                "duration": 3600,
            },
        ]
        
        blocks = detect_work_blocks(sessions)
        
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["session_count"], 1)

    def test_detect_work_blocks_groups_consecutive_sessions(self):
        """Test work blocks group consecutive sessions."""
        sessions = [
            {
                "task": "Task 1",
                "category": "development",
                "start_time": "2024-01-15T09:00:00",
                "end_time": "2024-01-15T10:00:00",
                "duration": 3600,
            },
            {
                "task": "Task 2",
                "category": "development",
                "start_time": "2024-01-15T10:00:00",
                "end_time": "2024-01-15T11:00:00",
                "duration": 3600,
            },
        ]
        
        blocks = detect_work_blocks(sessions)
        
        # Should be grouped into one block
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["session_count"], 2)

    def test_detect_work_blocks_separates_with_gaps(self):
        """Test work blocks separated by time gaps."""
        sessions = [
            {
                "task": "Morning",
                "category": "development",
                "start_time": "2024-01-15T09:00:00",
                "end_time": "2024-01-15T10:00:00",
                "duration": 3600,
            },
            {
                "task": "Afternoon",
                "category": "development",
                "start_time": "2024-01-15T14:00:00",
                "end_time": "2024-01-15T15:00:00",
                "duration": 3600,
            },
        ]
        
        blocks = detect_work_blocks(sessions)
        
        # Should be separated into two blocks
        self.assertEqual(len(blocks), 2)


class TestPeakHoursDetection(unittest.TestCase):
    """Test peak productivity hours identification."""

    def test_identify_peak_hours_empty_sessions(self):
        """Test peak hours with no sessions."""
        peak_hours = identify_peak_hours([])
        
        self.assertIsInstance(peak_hours, dict)

    def test_identify_peak_hours_returns_hours(self):
        """Test peak hours returns hour distribution."""
        sessions = [
            {"task": "Task", "category": "development", "start_time": "2024-01-15T09:00:00", "duration": 3600},
            {"task": "Task", "category": "development", "start_time": "2024-01-15T09:30:00", "duration": 3600},
            {"task": "Task", "category": "development", "start_time": "2024-01-15T14:00:00", "duration": 1800},
        ]
        
        peak_hours = identify_peak_hours(sessions)
        
        self.assertIn("hour_distribution", peak_hours)
        self.assertIn("peak_hour", peak_hours)

    def test_identify_peak_hours_detects_most_productive_hour(self):
        """Test peak hours correctly identifies most productive hour."""
        # Create multiple sessions at 9 AM
        sessions = [
            {"task": "Task", "category": "development", "start_time": "2024-01-15T09:00:00", "duration": 3600},
            {"task": "Task", "category": "development", "start_time": "2024-01-15T09:30:00", "duration": 3600},
            {"task": "Task", "category": "development", "start_time": "2024-01-16T09:00:00", "duration": 3600},
            {"task": "Task", "category": "development", "start_time": "2024-01-16T14:00:00", "duration": 1800},
        ]
        
        peak_hours = identify_peak_hours(sessions)
        
        self.assertEqual(peak_hours["peak_hour"], 9)


if __name__ == "__main__":
    unittest.main()
