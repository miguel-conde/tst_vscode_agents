"""
Reports module for generating daily/weekly summaries and analytics.
Supports multiple export formats: JSON, Markdown, CSV.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from src.storage import load_sessions


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human-readable string."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
    return f"{minutes}m"


class DailyReport:
    """Represents a daily report with session summary."""

    def __init__(self, date: str, sessions: List[Dict[str, Any]]):
        """
        Initialize daily report.

        Args:
            date: Date string in YYYY-MM-DD format
            sessions: List of session dictionaries for the day
        """
        self.date = date
        self.sessions = sessions
        self.total_duration = sum(s.get("duration", 0) for s in sessions)

    def get_category_breakdown(self) -> Dict[str, Dict[str, int]]:
        """
        Calculate breakdown by category.

        Returns:
            Dict with category names as keys, containing count and duration
        """
        breakdown = {}

        for session in self.sessions:
            category = session.get("category", "unknown")

            if category not in breakdown:
                breakdown[category] = {"count": 0, "duration": 0}

            breakdown[category]["count"] += 1
            breakdown[category]["duration"] += session.get("duration", 0)

        return breakdown

    def get_summary(self) -> str:
        """
        Generate text summary of the day.

        Returns:
            Human-readable summary string
        """
        session_word = "session" if len(self.sessions) == 1 else "sessions"
        duration_str = format_duration(self.total_duration)

        return f"Date: {self.date} | {len(self.sessions)} {session_word} | Total: {duration_str}"


class WeeklyReport:
    """Represents a weekly report with aggregated data."""

    def __init__(self, start_date: str, end_date: str, sessions: List[Dict[str, Any]]):
        """
        Initialize weekly report.

        Args:
            start_date: Start date string in YYYY-MM-DD format
            end_date: End date string in YYYY-MM-DD format
            sessions: List of all sessions in the week
        """
        self.start_date = start_date
        self.end_date = end_date
        self.sessions = sessions
        self.total_duration = sum(s.get("duration", 0) for s in sessions)

    def get_daily_breakdown(self) -> Dict[str, Dict[str, int]]:
        """
        Calculate breakdown by day.

        Returns:
            Dict with dates as keys, containing count and duration
        """
        breakdown = {}

        for session in self.sessions:
            start_time = session.get("start_time", "")
            date = start_time.split("T")[0] if "T" in start_time else start_time[:10]

            if date not in breakdown:
                breakdown[date] = {"count": 0, "duration": 0}

            breakdown[date]["count"] += 1
            breakdown[date]["duration"] += session.get("duration", 0)

        return breakdown

    def get_category_breakdown(self) -> Dict[str, Dict[str, int]]:
        """
        Calculate breakdown by category.

        Returns:
            Dict with category names as keys, containing count and duration
        """
        breakdown = {}

        for session in self.sessions:
            category = session.get("category", "unknown")

            if category not in breakdown:
                breakdown[category] = {"count": 0, "duration": 0}

            breakdown[category]["count"] += 1
            breakdown[category]["duration"] += session.get("duration", 0)

        return breakdown


class ReportExporter:
    """Handles exporting reports to multiple formats."""

    def __init__(self, report):
        """
        Initialize exporter with a report.

        Args:
            report: DailyReport or WeeklyReport instance
        """
        self.report = report

    def to_json(self) -> str:
        """
        Export report to JSON format.

        Returns:
            JSON string representation
        """
        data = {
            "date": getattr(self.report, "date", None),
            "start_date": getattr(self.report, "start_date", None),
            "end_date": getattr(self.report, "end_date", None),
            "total_duration": self.report.total_duration,
            "sessions": self.report.sessions,
        }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        return json.dumps(data, indent=2)

    def to_markdown(self) -> str:
        """
        Export report to Markdown format with ASCII chart.

        Returns:
            Markdown formatted string
        """
        lines = []

        # Header
        if hasattr(self.report, "date"):
            lines.append(f"# Daily Report - {self.report.date}")
        else:
            lines.append(f"# Weekly Report - {self.report.start_date} to {self.report.end_date}")

        lines.append("")
        lines.append(f"**Total Duration:** {format_duration(self.report.total_duration)}")
        lines.append(f"**Sessions:** {len(self.report.sessions)}")
        lines.append("")

        # Category breakdown with ASCII chart
        breakdown = self.report.get_category_breakdown()

        if breakdown:
            lines.append("## Category Breakdown")
            lines.append("")

            # Calculate max for scaling
            max_duration = max(cat["duration"] for cat in breakdown.values()) if breakdown else 1

            for category, data in sorted(breakdown.items()):
                duration = data["duration"]
                count = data["count"]
                bar_length = int((duration / max_duration) * 30) if max_duration > 0 else 0
                bar = "█" * bar_length

                lines.append(f"**{category}** ({count} sessions)")
                lines.append(f"{bar} {format_duration(duration)}")
                lines.append("")

        # Session list
        lines.append("## Sessions")
        lines.append("")

        for session in self.report.sessions:
            task = session.get("task", "Untitled")
            category = session.get("category", "unknown")
            duration = session.get("duration", 0)

            lines.append(f"- **{task}** ({category}) - {format_duration(duration)}")

        return "\n".join(lines)

    def to_csv(self) -> str:
        """
        Export report to CSV format.

        Returns:
            CSV formatted string
        """
        lines = ["task,category,start_time,end_time,duration"]

        for session in self.report.sessions:
            task = session.get("task", "").replace(",", ";")
            category = session.get("category", "")
            start_time = session.get("start_time", "")
            end_time = session.get("end_time", "")
            duration = session.get("duration", 0)

            lines.append(f"{task},{category},{start_time},{end_time},{duration}")

        return "\n".join(lines)


def generate_daily_report(date_str: str) -> DailyReport:
    """
    Generate daily report for a specific date.

    Args:
        date_str: Date string in YYYY-MM-DD format

    Returns:
        DailyReport instance
    """
    # Calculate start and end of day
    date = datetime.strptime(date_str, "%Y-%m-%d")
    start_datetime = date.replace(hour=0, minute=0, second=0)
    end_datetime = date.replace(hour=23, minute=59, second=59)

    # Load sessions for the day
    session_objects = load_sessions(start_date=start_datetime.isoformat(), end_date=end_datetime.isoformat())

    # Convert Session objects to dictionaries
    sessions = [s.to_dict() for s in session_objects]

    return DailyReport(date_str, sessions)


def generate_weekly_report(start_date_str: str, end_date_str: str) -> WeeklyReport:
    """
    Generate weekly report for a date range.

    Args:
        start_date_str: Start date in YYYY-MM-DD format
        end_date_str: End date in YYYY-MM-DD format

    Returns:
        WeeklyReport instance
    """
    # Parse dates
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    # Set to start and end of days
    start_datetime = start_date.replace(hour=0, minute=0, second=0)
    end_datetime = end_date.replace(hour=23, minute=59, second=59)

    # Load sessions for the week
    session_objects = load_sessions(start_date=start_datetime.isoformat(), end_date=end_datetime.isoformat())

    # Convert Session objects to dictionaries
    sessions = [s.to_dict() for s in session_objects]

    return WeeklyReport(start_date_str, end_date_str, sessions)
