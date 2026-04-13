from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, time, timedelta
from typing import Any

from .models import SubjectMeta

SUBJECTS: dict[str, SubjectMeta] = {
    "Biology": SubjectMeta("B", "#10B981"),
    "Mathematics": SubjectMeta("M", "#3B82F6"),
    "Maths": SubjectMeta("M", "#3B82F6"),
    "Physics": SubjectMeta("P", "#8B5CF6"),
    "Chemistry": SubjectMeta("C", "#F59E0B"),
    "History": SubjectMeta("H", "#EF4444"),
}

TOPIC_LIBRARY: list[dict[str, Any]] = [
    {"subject": "Biology", "name": "Photosynthesis", "difficulty": "Medium", "progress": 72, "confidence": 4},
    {"subject": "Biology", "name": "Cell Division", "difficulty": "Easy", "progress": 88, "confidence": 5},
    {"subject": "Biology", "name": "Respiration", "difficulty": "Medium", "progress": 55, "confidence": 3},
    {"subject": "Biology", "name": "Genetics", "difficulty": "Hard", "progress": 40, "confidence": 2},
    {"subject": "Mathematics", "name": "Quadratic Equations", "difficulty": "Easy", "progress": 90, "confidence": 5},
    {"subject": "Mathematics", "name": "Trigonometry", "difficulty": "Medium", "progress": 65, "confidence": 3},
    {"subject": "Mathematics", "name": "Calculus", "difficulty": "Hard", "progress": 48, "confidence": 2},
    {"subject": "Mathematics", "name": "Statistics", "difficulty": "Medium", "progress": 70, "confidence": 4},
    {"subject": "Physics", "name": "Newton's Laws", "difficulty": "Medium", "progress": 80, "confidence": 4},
    {"subject": "Physics", "name": "Electromagnetism", "difficulty": "Hard", "progress": 35, "confidence": 2},
    {"subject": "Physics", "name": "Waves", "difficulty": "Medium", "progress": 60, "confidence": 3},
    {"subject": "Physics", "name": "Thermodynamics", "difficulty": "Hard", "progress": 28, "confidence": 1},
    {"subject": "Chemistry", "name": "Organic Chemistry", "difficulty": "Hard", "progress": 42, "confidence": 2},
    {"subject": "Chemistry", "name": "Periodic Table", "difficulty": "Easy", "progress": 85, "confidence": 5},
    {"subject": "Chemistry", "name": "Acid-Base", "difficulty": "Medium", "progress": 58, "confidence": 3},
    {"subject": "Chemistry", "name": "Redox Reactions", "difficulty": "Hard", "progress": 30, "confidence": 2},
    {"subject": "History", "name": "French Revolution", "difficulty": "Hard", "progress": 50, "confidence": 2},
    {"subject": "History", "name": "World War II", "difficulty": "Medium", "progress": 75, "confidence": 4},
    {"subject": "History", "name": "Industrial Revolution", "difficulty": "Easy", "progress": 82, "confidence": 4},
    {"subject": "History", "name": "Cold War", "difficulty": "Medium", "progress": 62, "confidence": 3},
]


def default_user() -> dict[str, Any]:
    return {
        "name": "Alex Johnson",
        "email": "alex@studyflow.app",
        "plan": "Premium",
        "title": "Premium Student",
    }


def default_settings() -> dict[str, Any]:
    return {
        "scheduling": {
            "algorithm": "SM-2 (Spaced Repetition)",
            "daily_goal": "2 hours",
            "session_length": "25 min (Pomodoro)",
            "weekend_sessions": False,
        },
        "ai": {
            "model": "Local study assistant",
            "suggestions": True,
            "auto_reschedule": False,
        },
        "appearance": {"theme": "Light", "font_size": "Medium", "compact_ui": False},
        "notifications": {"push_alerts": True, "email_digest": False, "reminder_before": "30 minutes"},
        "data": {"export": "CSV / JSON", "backup": "Local only"},
    }


def default_alert_settings() -> dict[str, bool]:
    return {
        "due_today": True,
        "overdue": True,
        "ai_suggestions": True,
        "weekly_reports": True,
        "session_reminders": False,
        "streak_reminders": False,
    }


def default_study_minutes() -> list[int]:
    return [25, 48, 30, 62, 40, 55, 38, 72, 46, 58, 34, 66, 41, 60]


def default_topics() -> list[dict[str, Any]]:
    return deepcopy(TOPIC_LIBRARY)


def build_default_tasks(today: date) -> list[dict[str, Any]]:
    rows = [
        ("task-1", "Photosynthesis", "Biology", "Medium", today, time(9, 0), 4),
        ("task-2", "Newton's Laws", "Physics", "Medium", today, time(11, 0), 3),
        ("task-3", "Organic Chemistry", "Chemistry", "Hard", today, time(14, 0), 2),
        ("task-4", "French Revolution", "History", "Hard", today - timedelta(days=2), time(16, 0), 2),
        ("task-5", "Quadratic Equations", "Mathematics", "Easy", today + timedelta(days=1), time(10, 0), 5),
        ("task-6", "Cell Division", "Biology", "Easy", today + timedelta(days=1), time(15, 30), 4),
        ("task-7", "Electromagnetism", "Physics", "Hard", today + timedelta(days=2), time(10, 0), 2),
        ("task-8", "Calculus", "Mathematics", "Hard", today + timedelta(days=2), time(16, 0), 2),
        ("task-9", "Statistics", "Mathematics", "Medium", today + timedelta(days=3), time(12, 0), 4),
        ("task-10", "World War II", "History", "Medium", today + timedelta(days=4), time(17, 0), 4),
        ("task-11", "Respiration", "Biology", "Medium", today + timedelta(days=5), time(8, 0), 3),
        ("task-12", "Periodic Table", "Chemistry", "Easy", today + timedelta(days=6), time(9, 30), 5),
    ]
    return [
        {
            "id": task_id,
            "topic": topic,
            "subject": subject,
            "difficulty": difficulty,
            "scheduled_at": datetime.combine(day, slot),
            "confidence": confidence,
            "status": "pending",
            "duration_minutes": {"Easy": 15, "Medium": 25, "Hard": 35}[difficulty],
            "completed_at": None,
        }
        for task_id, topic, subject, difficulty, day, slot, confidence in rows
    ]


def build_default_notifications() -> list[dict[str, Any]]:
    return [
        {"id": "notif-1", "icon": "!", "title": "Overdue: French Revolution", "body": "This topic slipped by two days. Review it before starting something new.", "time": "2h ago", "read": False, "color": "#EF4444"},
        {"id": "notif-2", "icon": "T", "title": "Reminder: Photosynthesis", "body": "Your next revision starts in 30 minutes.", "time": "30m ago", "read": False, "color": "#F59E0B"},
        {"id": "notif-3", "icon": "AI", "title": "AI Suggestion", "body": "Move Calculus earlier for better recall based on recent sessions.", "time": "1h ago", "read": False, "color": "#3B82F6"},
        {"id": "notif-4", "icon": "OK", "title": "Session Complete", "body": "You finished Newton's Laws and rated the session 4 out of 5.", "time": "3h ago", "read": True, "color": "#10B981"},
        {"id": "notif-5", "icon": "R", "title": "Weekly Report Ready", "body": "Your study report is ready to review.", "time": "Yesterday", "read": True, "color": "#8B5CF6"},
    ]
