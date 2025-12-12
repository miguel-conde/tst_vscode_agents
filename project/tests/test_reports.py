"""
Tests for reports module - TDD approach for Phase 3.
"""

import unittest
from datetime import datetime, timedelta
from src.reports import (
    DailyReport,
    WeeklyReport,
    ReportExporter,
    generate_daily_report,
    generate_weekly_report,
)


class TestDailyReport(unittest.TestCase):
    """Test daily report generation."""

    def test_daily_report_creation(self):
        """Test creating a daily report with sessions."""
        sessions = [
            {
                "task": "Code review",
                "category": "development",
                "start_time": "2024-01-15T09:00:00",
                "end_time": "2024-01-15T10:30:00",
                "duration": 5400,
            },
            {
                "task": "Meeting",
                "category": "meetings",
                "start_time": "2024-01-15T14:00:00",
                "end_time": "2024-01-15T15:00:00",
                "duration": 3600,
            },
        ]

        report = DailyReport("2024-01-15", sessions)

        self.assertEqual(report.date, "2024-01-15")
        self.assertEqual(len(report.sessions), 2)
        self.assertEqual(report.total_duration, 9000)

    def test_daily_report_empty_sessions(self):
        """Test daily report with no sessions."""
        report = DailyReport("2024-01-15", [])

        self.assertEqual(report.total_duration, 0)
        self.assertEqual(len(report.sessions), 0)

    def test_daily_report_category_breakdown(self):
        """Test daily report calculates category breakdown."""
        sessions = [
            {
                "task": "Coding",
                "category": "development",
                "start_time": "2024-01-15T09:00:00",
                "end_time": "2024-01-15T10:00:00",
                "duration": 3600,
            },
            {
                "task": "More coding",
                "category": "development",
                "start_time": "2024-01-15T11:00:00",
                "end_time": "2024-01-15T12:00:00",
                "duration": 3600,
            },
            {
                "task": "Meeting",
                "category": "meetings",
                "start_time": "2024-01-15T14:00:00",
                "end_time": "2024-01-15T15:00:00",
                "duration": 3600,
            },
        ]

        report = DailyReport("2024-01-15", sessions)
        breakdown = report.get_category_breakdown()

        self.assertEqual(breakdown["development"]["count"], 2)
        self.assertEqual(breakdown["development"]["duration"], 7200)
        self.assertEqual(breakdown["meetings"]["count"], 1)
        self.assertEqual(breakdown["meetings"]["duration"], 3600)

    def test_daily_report_summary_text(self):
        """Test daily report generates summary text."""
        sessions = [
            {
                "task": "Task",
                "category": "development",
                "start_time": "2024-01-15T09:00:00",
                "end_time": "2024-01-15T10:00:00",
                "duration": 3600,
            }
        ]

        report = DailyReport("2024-01-15", sessions)
        summary = report.get_summary()

        self.assertIn("2024-01-15", summary)
        self.assertIn("1 session", summary)
        self.assertIn("1h", summary)


class TestWeeklyReport(unittest.TestCase):
    """Test weekly report generation."""

    def test_weekly_report_creation(self):
        """Test creating a weekly report."""
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
                "start_time": "2024-01-16T09:00:00",
                "end_time": "2024-01-16T10:00:00",
                "duration": 3600,
            },
        ]

        report = WeeklyReport("2024-01-15", "2024-01-21", sessions)

        self.assertEqual(report.start_date, "2024-01-15")
        self.assertEqual(report.end_date, "2024-01-21")
        self.assertEqual(report.total_duration, 7200)

    def test_weekly_report_daily_breakdown(self):
        """Test weekly report shows daily breakdown."""
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
                "start_time": "2024-01-15T11:00:00",
                "end_time": "2024-01-15T12:00:00",
                "duration": 3600,
            },
            {
                "task": "Task 3",
                "category": "meetings",
                "start_time": "2024-01-16T09:00:00",
                "end_time": "2024-01-16T10:00:00",
                "duration": 3600,
            },
        ]

        report = WeeklyReport("2024-01-15", "2024-01-21", sessions)
        daily = report.get_daily_breakdown()

        self.assertEqual(daily["2024-01-15"]["duration"], 7200)
        self.assertEqual(daily["2024-01-15"]["count"], 2)
        self.assertEqual(daily["2024-01-16"]["duration"], 3600)
        self.assertEqual(daily["2024-01-16"]["count"], 1)

    def test_weekly_report_category_totals(self):
        """Test weekly report calculates category totals."""
        sessions = [
            {
                "task": "Task 1",
                "category": "development",
                "start_time": "2024-01-15T09:00:00",
                "end_time": "2024-01-15T12:00:00",
                "duration": 10800,
            },
            {
                "task": "Task 2",
                "category": "meetings",
                "start_time": "2024-01-16T09:00:00",
                "end_time": "2024-01-16T10:00:00",
                "duration": 3600,
            },
        ]

        report = WeeklyReport("2024-01-15", "2024-01-21", sessions)
        breakdown = report.get_category_breakdown()

        self.assertEqual(breakdown["development"]["duration"], 10800)
        self.assertEqual(breakdown["meetings"]["duration"], 3600)


class TestReportExporter(unittest.TestCase):
    """Test report exporters for multiple formats."""

    def test_export_to_json(self):
        """Test exporting report to JSON."""
        sessions = [
            {
                "task": "Task",
                "category": "development",
                "start_time": "2024-01-15T09:00:00",
                "end_time": "2024-01-15T10:00:00",
                "duration": 3600,
            }
        ]

        report = DailyReport("2024-01-15", sessions)
        exporter = ReportExporter(report)
        json_output = exporter.to_json()

        self.assertIn('"date":', json_output)
        self.assertIn('"total_duration":', json_output)
        self.assertIn('"sessions":', json_output)

    def test_export_to_markdown(self):
        """Test exporting report to Markdown."""
        sessions = [
            {
                "task": "Code review",
                "category": "development",
                "start_time": "2024-01-15T09:00:00",
                "end_time": "2024-01-15T10:00:00",
                "duration": 3600,
            }
        ]

        report = DailyReport("2024-01-15", sessions)
        exporter = ReportExporter(report)
        md_output = exporter.to_markdown()

        self.assertIn("# Daily Report", md_output)
        self.assertIn("2024-01-15", md_output)
        self.assertIn("Code review", md_output)
        self.assertIn("development", md_output)

    def test_export_to_csv(self):
        """Test exporting report to CSV."""
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

        report = DailyReport("2024-01-15", sessions)
        exporter = ReportExporter(report)
        csv_output = exporter.to_csv()

        self.assertIn("task,category,start_time,end_time,duration", csv_output)
        self.assertIn("Task 1,development", csv_output)
        self.assertIn("Task 2,meetings", csv_output)

    def test_export_with_ascii_chart(self):
        """Test markdown export includes ASCII chart."""
        sessions = [
            {
                "task": "Dev",
                "category": "development",
                "start_time": "2024-01-15T09:00:00",
                "end_time": "2024-01-15T12:00:00",
                "duration": 10800,
            },
            {
                "task": "Meet",
                "category": "meetings",
                "start_time": "2024-01-15T13:00:00",
                "end_time": "2024-01-15T14:00:00",
                "duration": 3600,
            },
        ]

        report = DailyReport("2024-01-15", sessions)
        exporter = ReportExporter(report)
        md_output = exporter.to_markdown()

        # Should contain ASCII visualization
        self.assertIn("█", md_output)
        self.assertIn("development", md_output)
        self.assertIn("meetings", md_output)


class TestReportGeneration(unittest.TestCase):
    """Test high-level report generation functions."""

    def test_generate_daily_report_for_date(self):
        """Test generating daily report retrieves correct sessions."""
        # This will integrate with storage module
        date_str = "2024-01-15"
        report = generate_daily_report(date_str)

        self.assertIsInstance(report, DailyReport)
        self.assertEqual(report.date, date_str)

    def test_generate_weekly_report_for_range(self):
        """Test generating weekly report for date range."""
        start = "2024-01-15"
        end = "2024-01-21"
        report = generate_weekly_report(start, end)

        self.assertIsInstance(report, WeeklyReport)
        self.assertEqual(report.start_date, start)
        self.assertEqual(report.end_date, end)


if __name__ == "__main__":
    unittest.main()
