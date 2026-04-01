from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Property, Signal, Slot


@dataclass(frozen=True)
class SubjectMeta:
    icon: str
    color: str


class StudyFlowBackend(QObject):
    stateChanged = Signal()

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

    def __init__(self, store_path: Path | None = None) -> None:
        super().__init__()
        self._store_path = store_path or Path(__file__).with_name("studyflow_data.json")
        self._today = date.today()
        self._selected_date = self._today
        self._task_filter = "all"
        self._curriculum_filter = "All"
        self._suggestion_dismissed = False
        self._load_state()

    def _load_state(self) -> None:
        self._user = {
            "name": "Alex Johnson",
            "email": "alex@studyflow.app",
            "plan": "Premium",
            "title": "Premium Student",
        }
        self._settings = {
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
        self._alert_settings = {
            "due_today": True,
            "overdue": True,
            "ai_suggestions": True,
            "weekly_reports": True,
            "session_reminders": False,
            "streak_reminders": False,
        }
        self._study_minutes = [25, 48, 30, 62, 40, 55, 38, 72, 46, 58, 34, 66, 41, 60]
        self._topics = deepcopy(self.TOPIC_LIBRARY)
        self._tasks = self._build_default_tasks()
        self._notifications = self._build_default_notifications()

        if self._store_path.exists():
            try:
                payload = json.loads(self._store_path.read_text(encoding="utf-8"))
                self._user.update(payload.get("user", {}))
                self._settings = self._merge_nested(self._settings, payload.get("settings", {}))
                self._alert_settings.update(payload.get("alert_settings", {}))
                self._suggestion_dismissed = payload.get("suggestion_dismissed", False)
                self._study_minutes = payload.get("study_minutes", self._study_minutes)
                self._topics = payload.get("topics", self._topics)
                self._tasks = payload.get("tasks", self._serialize_tasks(self._build_default_tasks()))
                self._notifications = payload.get(
                    "notifications", self._serialize_notifications(self._build_default_notifications())
                )
            except (json.JSONDecodeError, OSError):
                pass

        self._tasks = self._deserialize_tasks(self._tasks)
        self._notifications = self._deserialize_notifications(self._notifications)

    def _save_state(self) -> None:
        payload = {
            "user": self._user,
            "settings": self._settings,
            "alert_settings": self._alert_settings,
            "suggestion_dismissed": self._suggestion_dismissed,
            "study_minutes": self._study_minutes,
            "topics": self._topics,
            "tasks": self._serialize_tasks(self._tasks),
            "notifications": self._serialize_notifications(self._notifications),
        }
        self._store_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _merge_nested(self, base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
        merged = deepcopy(base)
        for key, value in update.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = self._merge_nested(merged[key], value)
            else:
                merged[key] = value
        return merged

    def _build_default_tasks(self) -> list[dict[str, Any]]:
        start = self._today
        rows = [
            ("task-1", "Photosynthesis", "Biology", "Medium", start, time(9, 0), 4),
            ("task-2", "Newton's Laws", "Physics", "Medium", start, time(11, 0), 3),
            ("task-3", "Organic Chemistry", "Chemistry", "Hard", start, time(14, 0), 2),
            ("task-4", "French Revolution", "History", "Hard", start - timedelta(days=2), time(16, 0), 2),
            ("task-5", "Quadratic Equations", "Mathematics", "Easy", start + timedelta(days=1), time(10, 0), 5),
            ("task-6", "Cell Division", "Biology", "Easy", start + timedelta(days=1), time(15, 30), 4),
            ("task-7", "Electromagnetism", "Physics", "Hard", start + timedelta(days=2), time(10, 0), 2),
            ("task-8", "Calculus", "Mathematics", "Hard", start + timedelta(days=2), time(16, 0), 2),
            ("task-9", "Statistics", "Mathematics", "Medium", start + timedelta(days=3), time(12, 0), 4),
            ("task-10", "World War II", "History", "Medium", start + timedelta(days=4), time(17, 0), 4),
            ("task-11", "Respiration", "Biology", "Medium", start + timedelta(days=5), time(8, 0), 3),
            ("task-12", "Periodic Table", "Chemistry", "Easy", start + timedelta(days=6), time(9, 30), 5),
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

    def _build_default_notifications(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "notif-1",
                "icon": "!",
                "title": "Overdue: French Revolution",
                "body": "This topic slipped by two days. Review it before starting something new.",
                "time": "2h ago",
                "read": False,
                "color": "#EF4444",
            },
            {
                "id": "notif-2",
                "icon": "T",
                "title": "Reminder: Photosynthesis",
                "body": "Your next revision starts in 30 minutes.",
                "time": "30m ago",
                "read": False,
                "color": "#F59E0B",
            },
            {
                "id": "notif-3",
                "icon": "AI",
                "title": "AI Suggestion",
                "body": "Move Calculus earlier for better recall based on recent sessions.",
                "time": "1h ago",
                "read": False,
                "color": "#3B82F6",
            },
            {
                "id": "notif-4",
                "icon": "OK",
                "title": "Session Complete",
                "body": "You finished Newton's Laws and rated the session 4 out of 5.",
                "time": "3h ago",
                "read": True,
                "color": "#10B981",
            },
            {
                "id": "notif-5",
                "icon": "R",
                "title": "Weekly Report Ready",
                "body": "Your study report is ready to review.",
                "time": "Yesterday",
                "read": True,
                "color": "#8B5CF6",
            },
        ]

    def _serialize_tasks(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        payload = []
        for task in tasks:
            item = dict(task)
            item["scheduled_at"] = item["scheduled_at"].isoformat()
            item["completed_at"] = item["completed_at"].isoformat() if item["completed_at"] else None
            payload.append(item)
        return payload

    def _deserialize_tasks(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        payload = []
        for task in tasks:
            item = dict(task)
            if isinstance(item["scheduled_at"], str):
                item["scheduled_at"] = datetime.fromisoformat(item["scheduled_at"])
            if item.get("completed_at") and isinstance(item["completed_at"], str):
                item["completed_at"] = datetime.fromisoformat(item["completed_at"])
            payload.append(item)
        return payload

    def _serialize_notifications(self, notifications: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [dict(notification) for notification in notifications]

    def _deserialize_notifications(self, notifications: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [dict(notification) for notification in notifications]

    def _emit(self) -> None:
        self._save_state()
        self.stateChanged.emit()

    def _subject_meta(self, subject: str) -> SubjectMeta:
        return self.SUBJECTS.get(subject, SubjectMeta("?", "#64748B"))

    def _difficulty_color(self, difficulty: str) -> str:
        return {"Easy": "#10B981", "Medium": "#F59E0B", "Hard": "#EF4444"}.get(difficulty, "#64748B")

    def _status_payload(self, task: dict[str, Any]) -> dict[str, Any]:
        if task["completed_at"]:
            status = "Done"
            color = "#10B981"
        elif task["scheduled_at"].date() < self._today:
            status = "Overdue"
            color = "#EF4444"
        elif task["scheduled_at"].date() == self._today:
            status = "Pending"
            color = "#F59E0B"
        else:
            status = "Upcoming"
            color = "#3B82F6"

        meta = self._subject_meta(task["subject"])
        return {
            "id": task["id"],
            "topic": task["topic"],
            "name": task["topic"],
            "subject": task["subject"],
            "subjectShort": "Maths" if task["subject"] == "Mathematics" else task["subject"],
            "difficulty": task["difficulty"],
            "time": f"{task['duration_minutes']}m",
            "status": status,
            "scheduledText": self._format_schedule_text(task["scheduled_at"]),
            "subjectColor": meta.color,
            "difficultyColor": self._difficulty_color(task["difficulty"]),
            "statusColor": color,
            "confidence": task["confidence"],
            "scheduledDate": task["scheduled_at"].date().isoformat(),
            "durationMinutes": task["duration_minutes"],
        }

    def _format_schedule_text(self, scheduled_at: datetime) -> str:
        scheduled_day = scheduled_at.date()
        if scheduled_day < self._today:
            days = (self._today - scheduled_day).days
            return "Overdue" if days == 1 else f"Overdue by {days}d"
        if scheduled_day == self._today:
            return f"Today {scheduled_at.strftime('%H:%M')}"
        if scheduled_day == self._today + timedelta(days=1):
            return f"Tomorrow {scheduled_at.strftime('%H:%M')}"
        return scheduled_at.strftime("%a %H:%M")

    def _find_task(self, task_id: str) -> dict[str, Any] | None:
        return next((task for task in self._tasks if task["id"] == task_id), None)

    def _find_topic(self, topic_name: str) -> dict[str, Any] | None:
        return next((topic for topic in self._topics if topic["name"] == topic_name), None)

    def _add_notification(self, title: str, body: str, icon: str, color: str) -> None:
        self._notifications.insert(
            0,
            {
                "id": f"notif-{len(self._notifications) + 1}",
                "icon": icon,
                "title": title,
                "body": body,
                "time": "Just now",
                "read": False,
                "color": color,
            },
        )

    @Property("QVariantMap", notify=stateChanged)
    def userProfile(self) -> dict[str, Any]:
        initials = "".join(part[0] for part in self._user["name"].split()[:2]).upper()
        return {
            "name": self._user["name"],
            "email": self._user["email"],
            "plan": self._user["plan"],
            "title": self._user["title"],
            "initials": initials,
        }

    @Property("QVariantMap", notify=stateChanged)
    def dashboardBanner(self) -> dict[str, Any]:
        return {
            "emoji": "*",
            "headline": f"12-day study streak! Keep it up, {self._user['name'].split()[0]}!",
            "detail": "Personal best: 21 days",
        }

    @Property("QVariantList", notify=stateChanged)
    def dashboardStats(self) -> list[dict[str, Any]]:
        tasks = [self._status_payload(task) for task in self._tasks]
        due_today = [task for task in tasks if task["scheduledDate"] == self._today.isoformat() and task["status"] != "Done"]
        overdue = [task for task in tasks if task["status"] == "Overdue"]
        mastered = len([topic for topic in self._topics if topic["progress"] >= 80])
        avg_conf = round(sum(topic["confidence"] for topic in self._topics) / len(self._topics), 1)
        completed = len([task for task in self._tasks if task["completed_at"]])
        completion = round((completed / len(self._tasks)) * 100, 1) if self._tasks else 0.0
        return [
            {"title": "DUE TODAY", "value": str(len(due_today)), "subtitle": f"{len(overdue)} overdue", "trend": f"↑ {len(overdue)}", "trendUp": False, "valueColor": "#EF4444", "accentColor": "#EF4444"},
            {"title": "STUDY STREAK", "value": "12 days", "subtitle": "Best: 21 days", "trend": "↑ Active", "trendUp": True, "valueColor": "", "accentColor": "#F59E0B"},
            {"title": "MASTERED", "value": str(mastered), "subtitle": "topics total", "trend": "↑ 2 this week", "trendUp": True, "valueColor": "#10B981", "accentColor": "#10B981"},
            {"title": "AVG CONFIDENCE", "value": f"{avg_conf} / 5", "subtitle": "across all topics", "trend": "", "trendUp": True, "valueColor": "", "accentColor": "#8B5CF6"},
            {"title": "COMPLETION", "value": f"{completion}%", "subtitle": "current queue", "trend": "↑ Consistent", "trendUp": True, "valueColor": "", "accentColor": "#3B82F6"},
        ]

    @Property("QVariantList", notify=stateChanged)
    def todayTasks(self) -> list[dict[str, Any]]:
        tasks = [self._status_payload(task) for task in self._tasks]
        filtered = [task for task in tasks if task["scheduledDate"] == self._today.isoformat() and task["status"] != "Done"]
        filtered.sort(key=lambda item: item["scheduledText"])
        return filtered

    @Property("QVariantMap", notify=stateChanged)
    def dashboardFocus(self) -> dict[str, Any]:
        pending = self.todayTasks
        next_task = pending[0] if pending else None
        return {
            "score": 84,
            "nextRevision": f"Next revision: {next_task['topic']} ({next_task['scheduledText'].lower()})" if next_task else "You are clear for today.",
        }

    @Property("QVariantList", notify=stateChanged)
    def dashboardWeekBars(self) -> list[int]:
        base = self._study_minutes[-7:]
        peak = max(base) if base else 1
        return [round((value / peak) * 100) for value in base]

    @Property("QVariantList", notify=stateChanged)
    def taskFilters(self) -> list[dict[str, Any]]:
        payloads = [self._status_payload(task) for task in self._tasks]
        counts = {
            "all": len([task for task in payloads if task["status"] != "Done"]),
            "today": len([task for task in payloads if task["scheduledDate"] == self._today.isoformat() and task["status"] != "Done"]),
            "overdue": len([task for task in payloads if task["status"] == "Overdue"]),
            "upcoming": len([task for task in payloads if task["status"] == "Upcoming"]),
        }
        labels = {"all": "All", "today": "Due Today", "overdue": "Overdue", "upcoming": "Upcoming"}
        return [{"key": key, "label": f"{labels[key]} ({counts[key]})", "active": key == self._task_filter} for key in ["all", "today", "overdue", "upcoming"]]

    @Property(str, notify=stateChanged)
    def activeTaskFilter(self) -> str:
        return self._task_filter

    @Property("QVariantList", notify=stateChanged)
    def inboxTasks(self) -> list[dict[str, Any]]:
        tasks = [self._status_payload(task) for task in self._tasks if not task["completed_at"]]
        mapping = {
            "all": tasks,
            "today": [task for task in tasks if task["scheduledDate"] == self._today.isoformat()],
            "overdue": [task for task in tasks if task["status"] == "Overdue"],
            "upcoming": [task for task in tasks if task["status"] == "Upcoming"],
        }
        return sorted(mapping[self._task_filter], key=lambda item: (item["scheduledDate"], item["topic"]))

    @Property("QVariantMap", notify=stateChanged)
    def curriculumSummary(self) -> dict[str, Any]:
        total = len(self._topics)
        mastered = len([topic for topic in self._topics if topic["progress"] >= 80])
        not_started = len([topic for topic in self._topics if topic["progress"] < 35])
        in_progress = total - mastered - not_started
        avg = round(sum(topic["progress"] for topic in self._topics) / total)
        return {
            "stats": [
                {"label": "Total Topics", "value": str(total), "color": "#3B82F6"},
                {"label": "Mastered", "value": str(mastered), "color": "#10B981"},
                {"label": "In Progress", "value": str(in_progress), "color": "#F59E0B"},
                {"label": "Not Started", "value": str(not_started), "color": "#EF4444"},
                {"label": "Avg Progress", "value": f"{avg}%", "color": "#8B5CF6"},
            ]
        }

    @Property(str, notify=stateChanged)
    def curriculumDifficulty(self) -> str:
        return self._curriculum_filter

    @Property("QVariantList", notify=stateChanged)
    def curriculumSubjects(self) -> list[dict[str, Any]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for topic in self._topics:
            if self._curriculum_filter != "All" and topic["difficulty"] != self._curriculum_filter:
                continue
            grouped.setdefault(topic["subject"], []).append(topic)

        payload = []
        for subject_name, topics in grouped.items():
            meta = self._subject_meta(subject_name)
            payload.append(
                {
                    "subjectName": subject_name,
                    "iconText": meta.icon,
                    "accentColor": meta.color,
                    "topicCount": len(topics),
                    "topics": [{"name": topic["name"], "difficulty": topic["difficulty"], "difficultyColor": self._difficulty_color(topic["difficulty"]), "progress": topic["progress"], "confidence": topic["confidence"]} for topic in topics],
                }
            )
        return payload

    @Property(str, notify=stateChanged)
    def scheduleTitle(self) -> str:
        week_start = self._today - timedelta(days=self._today.weekday())
        week_end = week_start + timedelta(days=6)
        return f"This Week - {week_start.strftime('%d %b')} to {week_end.strftime('%d %b %Y')}"

    @Property("QVariantList", notify=stateChanged)
    def scheduleDays(self) -> list[dict[str, Any]]:
        week_start = self._today - timedelta(days=self._today.weekday())
        days = []
        for offset in range(7):
            current = week_start + timedelta(days=offset)
            tasks = [self._status_payload(task)["topic"] for task in self._tasks if task["scheduled_at"].date() == current and not task["completed_at"]]
            days.append({"day": current.strftime("%a").upper(), "date": current.strftime("%d"), "isCurrent": current == self._today, "tasks": tasks})
        return days

    @Property("QVariantList", notify=stateChanged)
    def nextDueTasks(self) -> list[dict[str, Any]]:
        tasks = [self._status_payload(task) for task in self._tasks if not task["completed_at"]]
        tasks.sort(key=lambda item: (item["scheduledDate"], item["topic"]))
        return [{"name": task["topic"], "when": task["scheduledText"], "color": task["statusColor"]} for task in tasks[:4]]

    @Property("QVariantMap", notify=stateChanged)
    def aiSuggestion(self) -> dict[str, Any]:
        enabled = self._settings["ai"]["suggestions"] and not self._suggestion_dismissed
        return {"visible": enabled, "text": "Move Calculus earlier. Your retention is strongest before 3 PM based on recent sessions."}

    @Property("QVariantMap", notify=stateChanged)
    def weekCompletion(self) -> dict[str, Any]:
        week_start = self._today - timedelta(days=self._today.weekday())
        week_end = week_start + timedelta(days=6)
        current_week = [task for task in self._tasks if week_start <= task["scheduled_at"].date() <= week_end]
        completed = len([task for task in current_week if task["completed_at"]])
        missed = len([task for task in current_week if task["scheduled_at"].date() < self._today and not task["completed_at"]])
        remaining = len(current_week) - completed - missed
        score = round((completed / len(current_week)) * 100) if current_week else 0
        return {"score": score, "completed": completed, "remaining": remaining, "missed": missed}

    @Property(str, notify=stateChanged)
    def calendarMonthLabel(self) -> str:
        return self._selected_date.strftime("%B %Y")

    @Property("QVariantList", notify=stateChanged)
    def calendarCells(self) -> list[dict[str, Any]]:
        first_day = self._selected_date.replace(day=1)
        start = first_day - timedelta(days=first_day.weekday())
        cells = []
        for offset in range(42):
            current = start + timedelta(days=offset)
            day_tasks = [task for task in self._tasks if task["scheduled_at"].date() == current and not task["completed_at"]]
            cells.append({"dayNum": current.day, "isValid": current.month == first_day.month, "isToday": current == self._today, "isSelected": current == self._selected_date, "taskCount": len(day_tasks)})
        return cells

    @Property("QVariantList", notify=stateChanged)
    def calendarLegend(self) -> list[dict[str, Any]]:
        return [
            {"label": "Biology", "color": self.SUBJECTS["Biology"].color},
            {"label": "Maths", "color": self.SUBJECTS["Mathematics"].color},
            {"label": "Physics", "color": self.SUBJECTS["Physics"].color},
            {"label": "Chemistry", "color": self.SUBJECTS["Chemistry"].color},
            {"label": "History", "color": self.SUBJECTS["History"].color},
        ]

    @Property(str, notify=stateChanged)
    def selectedDayLabel(self) -> str:
        return self._selected_date.strftime("%B %d")

    @Property("QVariantList", notify=stateChanged)
    def selectedDaySessions(self) -> list[dict[str, Any]]:
        sessions = []
        for task in self._tasks:
            if task["scheduled_at"].date() != self._selected_date or task["completed_at"]:
                continue
            meta = self._subject_meta(task["subject"])
            sessions.append({"id": task["id"], "time": task["scheduled_at"].strftime("%H:%M"), "topic": task["topic"], "subject": "Maths" if task["subject"] == "Mathematics" else task["subject"], "duration": f"{task['duration_minutes']}m", "color": meta.color})
        sessions.sort(key=lambda item: item["time"])
        return sessions

    @Property(str, notify=stateChanged)
    def selectedDayTotalText(self) -> str:
        total = sum(int(session["duration"].replace("m", "")) for session in self.selectedDaySessions)
        hours, minutes = divmod(total, 60)
        return f"{hours}h {minutes:02d}m" if hours else f"{minutes}m"

    @Property("QVariantList", notify=stateChanged)
    def intelligenceStats(self) -> list[dict[str, Any]]:
        strongest = max(self._topics, key=lambda item: item["progress"])
        weakest = min(self._topics, key=lambda item: item["progress"])
        return [
            {"title": "STUDY TIME", "value": "142.5h", "subtitle": "last 30 days", "trend": "↑ 12%", "trendUp": True, "accentColor": "#3B82F6", "valueColor": ""},
            {"title": "RETENTION", "value": "84%", "subtitle": "average confidence", "trend": "↑ 6%", "trendUp": True, "accentColor": "#10B981", "valueColor": "#10B981"},
            {"title": "MASTERED TOPICS", "value": strongest["name"], "subtitle": "strongest area", "trend": "", "trendUp": True, "accentColor": "#8B5CF6", "valueColor": ""},
            {"title": "NEEDS WORK", "value": weakest["name"], "subtitle": "lowest retention", "trend": "", "trendUp": True, "accentColor": "#EF4444", "valueColor": "#EF4444"},
        ]

    @Property("QVariantList", notify=stateChanged)
    def studyTrend(self) -> list[int]:
        return self._study_minutes

    @Property("QVariantList", notify=stateChanged)
    def subjectConfidence(self) -> list[dict[str, Any]]:
        payload = []
        grouped: dict[str, list[int]] = {}
        for topic in self._topics:
            grouped.setdefault(topic["subject"], []).append(topic["confidence"])
        for subject, confidences in grouped.items():
            meta = self._subject_meta(subject)
            payload.append({"subject": "Maths" if subject == "Mathematics" else subject, "pct": round(sum(confidences) / (len(confidences) * 5) * 100), "color": meta.color})
        return payload

    @Property("QVariantList", notify=stateChanged)
    def activityHeatmap(self) -> list[int]:
        return [(index * 37 + 13) % 100 for index in range(56)]

    @Property("QVariantList", notify=stateChanged)
    def topicBalance(self) -> list[float]:
        grouped: dict[str, list[int]] = {}
        for topic in self._topics:
            grouped.setdefault(topic["subject"], []).append(topic["progress"])
        ordered = ["Biology", "Mathematics", "Physics", "Chemistry", "History"]
        return [round(sum(grouped[name]) / (len(grouped[name]) * 100), 2) for name in ordered]

    @Property("QVariantList", notify=stateChanged)
    def flashcardStats(self) -> list[dict[str, Any]]:
        due_today = len([task for task in self._tasks if task["scheduled_at"].date() == self._today and not task["completed_at"]])
        mastered = len([topic for topic in self._topics if topic["progress"] >= 80])
        return [
            {"label": "Total Cards", "value": "248", "color": "#3B82F6"},
            {"label": "Due Today", "value": str(due_today * 4), "color": "#F59E0B"},
            {"label": "Mastered", "value": str(mastered * 6), "color": "#10B981"},
            {"label": "Needs Review", "value": str(max(0, 248 - mastered * 6 - due_today * 4)), "color": "#EF4444"},
        ]

    @Property("QVariantList", notify=stateChanged)
    def notifications(self) -> list[dict[str, Any]]:
        return [dict(notification) for notification in self._notifications]

    @Property("QVariantList", notify=stateChanged)
    def alertSettings(self) -> list[dict[str, Any]]:
        labels = [
            ("due_today", "Due Today Alerts"),
            ("overdue", "Overdue Warnings"),
            ("ai_suggestions", "AI Suggestions"),
            ("weekly_reports", "Weekly Reports"),
            ("session_reminders", "Session Reminders"),
            ("streak_reminders", "Streak Reminders"),
        ]
        return [{"key": key, "label": label, "on": self._alert_settings[key]} for key, label in labels]

    @Property("QVariantMap", notify=stateChanged)
    def todayDigest(self) -> dict[str, Any]:
        overdue = len([task for task in self._tasks if self._status_payload(task)["status"] == "Overdue"])
        today = len([task for task in self._tasks if task["scheduled_at"].date() == self._today and not task["completed_at"]])
        next_session = self.todayTasks[0] if self.todayTasks else None
        return {
            "summary": f"{today} tasks due • {overdue} overdue • {0 if self._suggestion_dismissed else 1} AI tip",
            "nextSession": f"Next session: {next_session['topic']} at {next_session['scheduledText'].split()[-1]}" if next_session else "No remaining sessions today.",
        }

    @Property("QVariantList", notify=stateChanged)
    def settingsColumns(self) -> list[list[dict[str, Any]]]:
        left = [
            {"title": "Account", "rows": [{"label": "Name", "value": self._user["name"], "kind": "value", "valueColor": "#374151"}, {"label": "Email", "value": self._user["email"], "kind": "value", "valueColor": "#374151"}, {"label": "Plan", "value": self._user["plan"], "kind": "value", "valueColor": "#10B981"}]},
            {"title": "Scheduling", "rows": [{"label": "Algorithm", "value": self._settings["scheduling"]["algorithm"], "kind": "value", "valueColor": "#374151"}, {"label": "Daily study goal", "value": self._settings["scheduling"]["daily_goal"], "kind": "value", "valueColor": "#374151"}, {"label": "Session length", "value": self._settings["scheduling"]["session_length"], "kind": "value", "valueColor": "#374151"}, {"label": "Weekend sessions", "key": "scheduling.weekend_sessions", "kind": "toggle", "toggleOn": self._settings["scheduling"]["weekend_sessions"]}]},
            {"title": "AI Assistant", "rows": [{"label": "Model", "value": self._settings["ai"]["model"], "kind": "value", "valueColor": "#374151"}, {"label": "AI Suggestions", "key": "ai.suggestions", "kind": "toggle", "toggleOn": self._settings["ai"]["suggestions"]}, {"label": "Auto-reschedule", "key": "ai.auto_reschedule", "kind": "toggle", "toggleOn": self._settings["ai"]["auto_reschedule"]}]},
        ]
        right = [
            {"title": "Appearance", "rows": [{"label": "Theme", "value": self._settings["appearance"]["theme"], "kind": "value", "valueColor": "#374151"}, {"label": "Font size", "value": self._settings["appearance"]["font_size"], "kind": "value", "valueColor": "#374151"}, {"label": "Compact UI", "key": "appearance.compact_ui", "kind": "toggle", "toggleOn": self._settings["appearance"]["compact_ui"]}]},
            {"title": "Notifications", "rows": [{"label": "Push alerts", "key": "notifications.push_alerts", "kind": "toggle", "toggleOn": self._settings["notifications"]["push_alerts"]}, {"label": "Email digest", "key": "notifications.email_digest", "kind": "toggle", "toggleOn": self._settings["notifications"]["email_digest"]}, {"label": "Reminder before", "value": self._settings["notifications"]["reminder_before"], "kind": "value", "valueColor": "#374151"}]},
            {"title": "Data and Privacy", "rows": [{"label": "Export data", "value": self._settings["data"]["export"], "kind": "value", "valueColor": "#374151"}, {"label": "Backup", "value": self._settings["data"]["backup"], "kind": "value", "valueColor": "#374151"}, {"label": "Clear history", "kind": "danger", "dangerLabel": "Clear All Data"}]},
        ]
        return [left, right]

    @Slot()
    def startSession(self) -> None:
        pending = self.todayTasks
        if pending:
            self._add_notification("Session started", f"Focus on {pending[0]['topic']} for the next block.", ">", "#3B82F6")
            self._emit()

    @Slot(str)
    def setTaskFilter(self, filter_key: str) -> None:
        self._task_filter = filter_key
        self.stateChanged.emit()

    @Slot(str)
    def markTaskDone(self, task_id: str) -> None:
        task = self._find_task(task_id)
        if not task or task["completed_at"]:
            return
        task["completed_at"] = datetime.now()
        task["status"] = "done"
        topic = self._find_topic(task["topic"])
        if topic:
            topic["progress"] = min(100, topic["progress"] + 8)
            topic["confidence"] = min(5, topic["confidence"] + 1)
        self._study_minutes.append(task["duration_minutes"])
        self._study_minutes = self._study_minutes[-14:]
        self._add_notification("Session complete", f"{task['topic']} was marked done.", "OK", "#10B981")
        self._emit()

    @Slot()
    def markAllTasksDone(self) -> None:
        changed = False
        for task in self._tasks:
            payload = self._status_payload(task)
            if payload["status"] in {"Pending", "Overdue"} and not task["completed_at"]:
                task["completed_at"] = datetime.now()
                changed = True
        if changed:
            self._add_notification("Inbox cleared", "All due study sessions were marked complete.", "OK", "#10B981")
            self._emit()

    @Slot(str)
    def skipTask(self, task_id: str) -> None:
        task = self._find_task(task_id)
        if not task or task["completed_at"]:
            return
        task["scheduled_at"] = task["scheduled_at"] + timedelta(days=1)
        self._add_notification("Task rescheduled", f"{task['topic']} moved to {self._format_schedule_text(task['scheduled_at'])}.", ">>", "#F59E0B")
        self._emit()

    @Slot(str)
    def setCurriculumDifficulty(self, difficulty: str) -> None:
        self._curriculum_filter = difficulty
        self.stateChanged.emit()

    @Slot()
    def acceptSuggestion(self) -> None:
        task = self._find_task("task-8")
        if task:
            task["scheduled_at"] = datetime.combine(self._today, time(13, 0))
        self._suggestion_dismissed = True
        self._add_notification("Suggestion applied", "Calculus was moved to an earlier slot.", "AI", "#3B82F6")
        self._emit()

    @Slot()
    def dismissSuggestion(self) -> None:
        self._suggestion_dismissed = True
        self._emit()

    @Slot(int)
    def changeCalendarMonth(self, offset: int) -> None:
        month = self._selected_date.month + offset
        year = self._selected_date.year
        while month < 1:
            month += 12
            year -= 1
        while month > 12:
            month -= 12
            year += 1
        self._selected_date = date(year, month, 1)
        self.stateChanged.emit()

    @Slot(int)
    def selectCalendarDay(self, day: int) -> None:
        try:
            self._selected_date = date(self._selected_date.year, self._selected_date.month, day)
        except ValueError:
            return
        self.stateChanged.emit()

    @Slot()
    def goToToday(self) -> None:
        self._selected_date = self._today
        self.stateChanged.emit()

    @Slot()
    def markAllNotificationsRead(self) -> None:
        for notification in self._notifications:
            notification["read"] = True
        self._emit()

    @Slot(str)
    def toggleAlertSetting(self, key: str) -> None:
        if key not in self._alert_settings:
            return
        self._alert_settings[key] = not self._alert_settings[key]
        self._emit()

    @Slot(str)
    def toggleSetting(self, key: str) -> None:
        section, item = key.split(".", 1)
        current = self._settings[section][item]
        if isinstance(current, bool):
            self._settings[section][item] = not current
            self._emit()

    @Slot()
    def saveSettings(self) -> None:
        self._add_notification("Settings saved", "Your app preferences were saved locally.", "S", "#3B82F6")
        self._emit()

    @Slot()
    def clearHistory(self) -> None:
        for task in self._tasks:
            task["completed_at"] = None
        self._suggestion_dismissed = False
        self._notifications = self._build_default_notifications()
        self._emit()
