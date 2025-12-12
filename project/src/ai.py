"""
AI insights module for pattern analysis and productivity suggestions.
Provides intelligent analysis of work patterns and actionable recommendations.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict


def analyze_patterns(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze work patterns from session data.
    
    Args:
        sessions: List of session dictionaries
    
    Returns:
        Dictionary containing pattern analysis
    """
    if not sessions:
        return {
            "total_sessions": 0,
            "total_duration": 0,
            "category_distribution": {},
            "most_common_category": None,
        }
    
    total_duration = sum(s.get("duration", 0) for s in sessions)
    
    # Calculate category distribution
    category_stats = defaultdict(lambda: {"count": 0, "duration": 0})
    
    for session in sessions:
        category = session.get("category", "unknown")
        category_stats[category]["count"] += 1
        category_stats[category]["duration"] += session.get("duration", 0)
    
    # Find most common category by count
    most_common = None
    if category_stats:
        most_common = max(category_stats.items(), key=lambda x: x[1]["count"])[0]
    
    return {
        "total_sessions": len(sessions),
        "total_duration": total_duration,
        "category_distribution": dict(category_stats),
        "most_common_category": most_common,
    }


def calculate_productivity_score(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate a productivity score based on work patterns.
    
    Args:
        sessions: List of session dictionaries
    
    Returns:
        Dictionary with score (0-100) and rating
    """
    if not sessions:
        return {
            "score": 0,
            "rating": "Low",
            "explanation": "No work sessions recorded",
        }
    
    # Calculate score based on multiple factors
    total_duration = sum(s.get("duration", 0) for s in sessions)
    num_sessions = len(sessions)
    
    # Factor 1: Total work time (target: 6-8 hours per day)
    hours_worked = total_duration / 3600
    time_score = min((hours_worked / 7.0) * 50, 50)  # Max 50 points
    
    # Factor 2: Session frequency (consistent work is good)
    frequency_score = min(num_sessions * 5, 30)  # Max 30 points
    
    # Factor 3: Category diversity (balanced work is good)
    categories = set(s.get("category") for s in sessions)
    diversity_score = min(len(categories) * 10, 20)  # Max 20 points
    
    # Calculate final score
    score = int(time_score + frequency_score + diversity_score)
    
    # Determine rating
    if score >= 80:
        rating = "Excellent"
    elif score >= 60:
        rating = "Good"
    elif score >= 40:
        rating = "Fair"
    else:
        rating = "Low"
    
    return {
        "score": score,
        "rating": rating,
        "explanation": f"Based on {num_sessions} sessions totaling {hours_worked:.1f} hours",
    }


def generate_suggestions(sessions: List[Dict[str, Any]]) -> List[str]:
    """
    Generate AI-powered productivity suggestions.
    
    Args:
        sessions: List of session dictionaries
    
    Returns:
        List of suggestion strings
    """
    suggestions = []
    
    if not sessions:
        suggestions.append("Start tracking your work sessions to get personalized insights!")
        return suggestions
    
    # Analyze patterns
    patterns = analyze_patterns(sessions)
    total_duration = patterns["total_duration"]
    
    # Check for very long sessions (>4 hours)
    long_sessions = [s for s in sessions if s.get("duration", 0) > 14400]
    if long_sessions:
        suggestions.append("Consider taking breaks during long coding sessions to maintain focus and prevent burnout.")
    
    # Check for category imbalance
    category_dist = patterns["category_distribution"]
    if len(category_dist) == 1:
        suggestions.append("Try to balance your work across different categories for a more diverse and sustainable workflow.")
    
    # Check total work duration
    hours_worked = total_duration / 3600
    if hours_worked > 10:
        suggestions.append("You've been working long hours. Remember to take time for rest and recovery.")
    elif hours_worked < 2:
        suggestions.append("Consider increasing your focused work time to boost productivity.")
    
    # Check session frequency
    if len(sessions) > 20:
        suggestions.append("Great consistency! You're maintaining a steady work rhythm.")
    elif len(sessions) < 3:
        suggestions.append("Try to break your work into more focused sessions throughout the day.")
    
    # Category-specific suggestions
    if "development" in category_dist:
        dev_duration = category_dist["development"]["duration"]
        if dev_duration > total_duration * 0.8:
            suggestions.append("Heavy development day! Consider scheduling code reviews or documentation time.")
    
    if "meetings" in category_dist:
        meeting_duration = category_dist["meetings"]["duration"]
        if meeting_duration > total_duration * 0.5:
            suggestions.append("High meeting load today. Try to protect some blocks for deep work.")
    
    # Always provide a positive suggestion
    if not suggestions or len(suggestions) == 0:
        suggestions.append("Keep up the great work! Your productivity patterns look healthy.")
    
    return suggestions


def detect_work_blocks(sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect continuous work blocks from sessions.
    
    A work block is a group of sessions with small gaps between them (< 30 min).
    
    Args:
        sessions: List of session dictionaries
    
    Returns:
        List of work block dictionaries
    """
    if not sessions:
        return []
    
    # Sort sessions by start time
    sorted_sessions = sorted(sessions, key=lambda s: s.get("start_time", ""))
    
    blocks = []
    current_block = None
    
    for session in sorted_sessions:
        start_time_str = session.get("start_time", "")
        end_time_str = session.get("end_time", "")
        
        if not start_time_str or not end_time_str:
            continue
        
        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.fromisoformat(end_time_str)
        
        if current_block is None:
            # Start new block
            current_block = {
                "start_time": start_time,
                "end_time": end_time,
                "session_count": 1,
                "total_duration": session.get("duration", 0),
            }
        else:
            # Check if this session is close to the previous one
            gap = (start_time - current_block["end_time"]).total_seconds()
            
            if gap < 1800:  # Less than 30 minutes gap
                # Extend current block
                current_block["end_time"] = end_time
                current_block["session_count"] += 1
                current_block["total_duration"] += session.get("duration", 0)
            else:
                # Save current block and start new one
                blocks.append(current_block)
                current_block = {
                    "start_time": start_time,
                    "end_time": end_time,
                    "session_count": 1,
                    "total_duration": session.get("duration", 0),
                }
    
    # Don't forget the last block
    if current_block:
        blocks.append(current_block)
    
    # Convert datetime objects to strings for JSON serialization
    for block in blocks:
        block["start_time"] = block["start_time"].isoformat()
        block["end_time"] = block["end_time"].isoformat()
    
    return blocks


def identify_peak_hours(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Identify peak productivity hours from session data.
    
    Args:
        sessions: List of session dictionaries
    
    Returns:
        Dictionary with hour distribution and peak hour
    """
    if not sessions:
        return {
            "hour_distribution": {},
            "peak_hour": None,
        }
    
    # Count sessions by hour of day
    hour_counts = defaultdict(int)
    hour_durations = defaultdict(int)
    
    for session in sessions:
        start_time_str = session.get("start_time", "")
        if not start_time_str:
            continue
        
        start_time = datetime.fromisoformat(start_time_str)
        hour = start_time.hour
        
        hour_counts[hour] += 1
        hour_durations[hour] += session.get("duration", 0)
    
    # Find peak hour (by session count)
    peak_hour = None
    if hour_counts:
        peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
    
    # Build hour distribution
    hour_distribution = {}
    for hour in range(24):
        if hour in hour_counts:
            hour_distribution[hour] = {
                "count": hour_counts[hour],
                "duration": hour_durations[hour],
            }
    
    return {
        "hour_distribution": hour_distribution,
        "peak_hour": peak_hour,
    }
