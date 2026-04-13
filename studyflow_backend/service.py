from __future__ import annotations

import csv
from datetime import date, datetime, timedelta
from io import StringIO
from pathlib import Path
from typing import Any
from uuid import uuid4

from PySide6.QtCore import Property, QObject, Signal, Slot

from nlp import NLPService, load_training_examples, train_model

from .defaults import SUBJECTS, build_default_notifications
from .models import SubjectMeta
from .presenters import difficulty_color, task_payload
from .storage import load_state, save_state

# Constants
PROGRESS_MASTERED = 80
CONFIDENCE_MAX = 5
SUBJECT_DISPLAY_NAMES = {"Mathematics": "Maths"}
RATING_LABELS = {1: "Again", 2: "Hard", 3: "Good", 4: "Easy"}
RATING_PROGRESS_BOOST = {1: -6, 2: 2, 3: 6, 4: 10}
RATING_CONFIDENCE = {1: 1, 2: 2, 3: 4, 4: 5}


class StudyFlowBackend(QObject):
    stateChanged = Signal()

    def __init__(self, store_path: Path | None = None) -> None:
        super().__init__()
        self._store_path = store_path or Path(__file__).resolve().parent.parent / "studyflow_data.json"
        self._today = date.today()
        self._selected_date = self._today
        self._task_filter = "all"
        self._curriculum_filter = "All"
        self._curriculum_search = ""
        self._nlp_service = NLPService()
        self._bootstrap_nlp_model()

        try:
            state = load_state(self._store_path, self._today)
            self._user = state.get("user", {"name": "User", "plan": "Free"})
            self._settings = state.get("settings", {"notifications": True, "reminders": True, "auto_schedule": True})
            self._alert_settings = state.get("alert_settings", {"study_reminder": True, "break_reminder": True})
            self._suggestion_dismissed = state.get("suggestion_dismissed", False)
            self._study_minutes = state.get("study_minutes", [])
            self._topics = [self._normalize_topic(topic) for topic in state.get("topics", [])]
            self._tasks = state.get("tasks", [])
            self._notifications = state.get("notifications", build_default_notifications())
        except Exception:
            # Fallback defaults if loading fails
            self._user = {"name": "User", "plan": "Free"}
            self._settings = {"notifications": True, "reminders": True, "auto_schedule": True}
            self._alert_settings = {"study_reminder": True, "break_reminder": True}
            self._suggestion_dismissed = False
            self._study_minutes = []
            self._topics = []
            self._tasks = []
            self._notifications = build_default_notifications()

        self._topics = [self._normalize_topic(topic) for topic in self._topics]
        self._rebuild_missing_tasks()

    def _save(self) -> None:
        save_state(
            self._store_path,
            {
                "user": self._user,
                "settings": self._settings,
                "alert_settings": self._alert_settings,
                "suggestion_dismissed": self._suggestion_dismissed,
                "study_minutes": self._study_minutes,
                "topics": self._topics,
                "tasks": self._tasks,
                "notifications": self._notifications,
            },
        )

    def _emit(self) -> None:
        self.stateChanged.emit()

    def _subject_meta(self, subject: str) -> SubjectMeta:
        return SUBJECTS.get(subject, SubjectMeta("?", "#64748B"))

    def _bootstrap_nlp_model(self) -> None:
        if self._nlp_service.model_path.exists():
            return
        dataset_path = Path(__file__).resolve().parent.parent / "nlp" / "data" / "training.csv"
        if dataset_path.exists():
            examples = load_training_examples(dataset_path)
            train_model(examples, service=self._nlp_service)

    def _normalize_topic(self, topic: dict[str, Any]) -> dict[str, Any]:
        item = dict(topic)
        item.setdefault("id", f"topic-{uuid4().hex[:8]}")
        item.setdefault("subject", "General")
        item.setdefault("difficulty", "Medium")
        item.setdefault("progress", 0)
        item.setdefault("confidence", 3)
        item.setdefault("notes", "")
        item.setdefault("parent_topic_id", None)
        item.setdefault("exam_date", "")
        item.setdefault("completion_date", "")
        item.setdefault("is_completed", False)
        return item

    def _rebuild_missing_tasks(self) -> None:
        task_topics = {task["topic"] for task in self._tasks}
        for topic in self._topics:
            if topic["name"] not in task_topics and not topic.get("is_completed"):
                self._tasks.append(self._build_task_for_topic(topic))

    def _build_task_for_topic(self, topic: dict[str, Any]) -> dict[str, Any]:
        difficulty = topic["difficulty"]
        delay_days = {"Easy": 1, "Medium": 0, "Hard": 0}.get(difficulty, 1)
        review_hour = {"Easy": 15, "Medium": 11, "Hard": 9}.get(difficulty, 11)
        return {
            "id": f"task-{uuid4().hex[:8]}",
            "topic": topic["name"],
            "subject": topic["subject"],
            "difficulty": difficulty,
            "scheduled_at": datetime.combine(self._today + timedelta(days=delay_days), datetime.min.time()).replace(hour=review_hour),
            "confidence": topic["confidence"],
            "status": "pending",
            "duration_minutes": {"Easy": 15, "Medium": 25, "Hard": 35}[difficulty],
            "completed_at": None,
            "completed": False,
        }

    def _task_payload(self, task: dict[str, Any]) -> dict[str, Any]:
        return task_payload(self._today, self._subject_meta(task["subject"]), task)

    def _find_task(self, task_id: str) -> dict[str, Any] | None:
        return next((task for task in self._tasks if task["id"] == task_id), None)

    def _find_topic(self, topic_name: str) -> dict[str, Any] | None:
        return next((topic for topic in self._topics if topic["name"] == topic_name), None)

    def _find_topic_by_id(self, topic_id: str) -> dict[str, Any] | None:
        return next((topic for topic in self._topics if topic["id"] == topic_id), None)

    def _subjects_from_topics(self) -> list[str]:
        return sorted(set(SUBJECTS.keys()) | {topic["subject"] for topic in self._topics})

    def _subject_groups(self) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for topic in self._topics:
            grouped.setdefault(topic["subject"], []).append(topic)
        return grouped

    def _average_progress(self, topics: list[dict[str, Any]] | None = None) -> float:
        items = topics if topics is not None else self._topics
        return round(sum(topic["progress"] for topic in items) / len(items), 1) if items else 0.0

    def _average_confidence_pct(self, topics: list[dict[str, Any]] | None = None) -> int:
        items = topics if topics is not None else self._topics
        if not items:
            return 0
        return round(sum(topic["confidence"] for topic in items) / (len(items) * CONFIDENCE_MAX) * 100)

    def _completed_tasks(self) -> list[dict[str, Any]]:
        return [task for task in self._tasks if self._is_task_completed(task)]

    def _weekly_study_minutes(self) -> int:
        return sum(self._study_minutes[-7:])

    def _study_trend_values(self, days: int = 14) -> list[int]:
        values = self._study_minutes[-days:]
        return [0] * (days - len(values)) + values

    def _filtered_topics(self) -> list[dict[str, Any]]:
        topics = self._topics
        if self._curriculum_filter != "All":
            topics = [topic for topic in topics if topic["difficulty"] == self._curriculum_filter]
        if self._curriculum_search:
            needle = self._curriculum_search.lower()
            topics = [
                topic for topic in topics
                if needle in topic["name"].lower() or needle in topic["subject"].lower()
            ]
        return topics

    def _topic_tree_node(self, topic: dict[str, Any], topic_lookup: dict[str, dict[str, Any]]) -> dict[str, Any]:
        children = [
            self._topic_tree_node(candidate, topic_lookup)
            for candidate in topic_lookup.values()
            if candidate.get("parent_topic_id") == topic["id"]
        ]
        children.sort(key=lambda item: item["name"])
        return {
            "id": topic["id"],
            "name": topic["name"],
            "subject": topic["subject"],
            "difficulty": topic["difficulty"],
            "difficultyColor": difficulty_color(topic["difficulty"]),
            "progress": topic["progress"],
            "confidence": topic["confidence"],
            "notes": topic.get("notes", ""),
            "examDate": topic.get("exam_date", ""),
            "completionDate": topic.get("completion_date", ""),
            "isCompleted": topic.get("is_completed", False),
            "children": children,
        }

    def _is_task_completed(self, task: dict[str, Any]) -> bool:
        return bool(task.get("completed_at")) or bool(task.get("completed"))

    def _compute_urgency_score(self, task: dict[str, Any]) -> int:
        days_delta = (task["scheduled_at"].date() - self._today).days
        difficulty_weight = {"Easy": 8, "Medium": 16, "Hard": 24}.get(task["difficulty"], 10)
        confidence_penalty = max(0, 6 - int(task["confidence"])) * 5
        overdue_bonus = 0 if days_delta >= 0 else abs(days_delta) * 30
        due_today_bonus = 18 if days_delta == 0 else 0
        upcoming_decay = max(0, 12 - max(days_delta, 0) * 3)
        return difficulty_weight + confidence_penalty + overdue_bonus + due_today_bonus + upcoming_decay

    def _dashboard_task_payload(self, task: dict[str, Any]) -> dict[str, Any]:
        payload = self._task_payload(task)
        payload["urgencyScore"] = self._compute_urgency_score(task)
        payload["isCompleted"] = self._is_task_completed(task)
        payload["bucket"] = self._task_bucket(task)
        payload["confidenceLabel"] = f"Confidence {task['confidence']}/{CONFIDENCE_MAX}"
        return payload

    def _task_bucket(self, task: dict[str, Any]) -> str:
        if self._is_task_completed(task):
            return "completed"
        scheduled_day = task["scheduled_at"].date()
        if scheduled_day < self._today:
            return "overdue"
        if scheduled_day == self._today:
            return "due_today"
        return "upcoming"

    def _tasks_for_bucket(self, bucket: str) -> list[dict[str, Any]]:
        items = [task for task in self._tasks if self._task_bucket(task) == bucket]
        items.sort(key=lambda task: (-self._compute_urgency_score(task), task["scheduled_at"]))
        return [self._dashboard_task_payload(task) for task in items]

    def _add_notification(self, title: str, body: str, icon: str, color: str) -> None:
        id = f"notif-{len(self._notifications) + 1}"
        self._notifications.append({
            "id": id,
            "title": title,
            "body": body,
            "icon": icon,
            "color": color,
            "timestamp": datetime.now().isoformat(),
        })
        self._emit()

    @Property("QVariantMap", notify=stateChanged)
    def userProfile(self) -> dict[str, Any]:
        return self._user

    @Property("QVariantList", notify=stateChanged)
    def dashboardStats(self) -> list[dict[str, Any]]:
        completed_today = len(
            [task for task in self._tasks if self._is_task_completed(task) and task["scheduled_at"].date() == self._today]
        )
        total_today = len([task for task in self._tasks if task["scheduled_at"].date() == self._today])
        avg_conf = round(sum(topic["confidence"] for topic in self._topics) / len(self._topics), 1) if self._topics else 0.0
        overdue_count = len(self._tasks_for_bucket("overdue"))
        completion_rate = round((completed_today / total_today) * 100) if total_today else 0
        return [
            {
                "title": "OVERDUE",
                "value": str(overdue_count),
                "subtitle": "Need attention",
                "trend": "High" if overdue_count else "Clear",
                "trendUp": overdue_count == 0,
                "valueColor": "#EF4444" if overdue_count else "#1A2332",
                "accentColor": "#EF4444",
            },
            {
                "title": "DUE TODAY",
                "value": str(total_today),
                "subtitle": "Scheduled reviews",
                "trend": f"{completed_today} done",
                "trendUp": True,
                "valueColor": "#1A2332",
                "accentColor": "#3B82F6",
            },
            {
                "title": "COMPLETION",
                "value": f"{completion_rate}%",
                "subtitle": "Today's pace",
                "trend": "On track" if completion_rate >= 50 else "Warm up",
                "trendUp": completion_rate >= 50,
                "valueColor": "#1A2332",
                "accentColor": "#10B981",
            },
            {
                "title": "AVG CONFIDENCE",
                "value": f"{avg_conf:.1f}/5",
                "subtitle": "Across topics",
                "trend": "Steady recall",
                "trendUp": avg_conf >= 3.5,
                "valueColor": "#1A2332",
                "accentColor": "#8B5CF6",
            },
        ]

    @Property("QVariantMap", notify=stateChanged)
    def dashboardBanner(self) -> dict[str, Any]:
        overdue = len(self._tasks_for_bucket("overdue"))
        due_today = len(self._tasks_for_bucket("due_today"))
        if overdue:
            return {
                "emoji": "!",
                "headline": f"{overdue} overdue review{'s' if overdue != 1 else ''} need attention first",
                "detail": "Clear the oldest cards before starting new material.",
            }
        return {
            "emoji": "•",
            "headline": f"{due_today} review{'s' if due_today != 1 else ''} queued for today",
            "detail": "Stay in rhythm with short, consistent revision sessions.",
        }

    @Property("QVariantMap", notify=stateChanged)
    def dashboardFocus(self) -> dict[str, Any]:
        due_items = self._tasks_for_bucket("due_today")
        top_item = due_items[0] if due_items else None
        avg_conf = round(sum(topic["confidence"] for topic in self._topics) / len(self._topics) * 20) if self._topics else 0
        return {
            "score": avg_conf,
            "nextRevision": top_item["name"] if top_item else "No due topics",
        }

    @Property("QVariantList", notify=stateChanged)
    def dashboardColumns(self) -> list[dict[str, Any]]:
        return [
            {
                "key": "overdue",
                "title": "Overdue",
                "subtitle": "Start here first",
                "accentColor": "#EF4444",
                "count": len(self._tasks_for_bucket("overdue")),
                "items": self._tasks_for_bucket("overdue"),
            },
            {
                "key": "due_today",
                "title": "Due Today",
                "subtitle": "Today's core revision flow",
                "accentColor": "#3B82F6",
                "count": len(self._tasks_for_bucket("due_today")),
                "items": self._tasks_for_bucket("due_today"),
            },
            {
                "key": "upcoming",
                "title": "Upcoming",
                "subtitle": "Planned next reviews",
                "accentColor": "#64748B",
                "count": len(self._tasks_for_bucket("upcoming")),
                "items": self._tasks_for_bucket("upcoming"),
            },
        ]

    @Property("QVariantList", notify=stateChanged)
    def todayTasks(self) -> list[dict[str, Any]]:
        tasks = [task for task in self._tasks if task["scheduled_at"].date() == self._selected_date]
        if self._task_filter != "all":
            tasks = [task for task in tasks if self._task_bucket(task) == self._task_filter]
        return [self._task_payload(task) for task in tasks]

    @Property("QVariantList", notify=stateChanged)
    def curriculumSubjects(self) -> list[dict[str, Any]]:
        subjects: dict[str, dict[str, Any]] = {}
        filtered_topics = self._filtered_topics()
        topic_lookup = {topic["id"]: topic for topic in filtered_topics}
        for topic in filtered_topics:
            subject = topic["subject"]
            if subject not in subjects:
                meta = self._subject_meta(subject)
                subjects[subject] = {
                    "subjectName": subject,
                    "iconText": meta.icon,
                    "accentColor": meta.color,
                    "topicCount": 0,
                    "topics": [],
                }
            subjects[subject]["topicCount"] += 1

        for topic in filtered_topics:
            if topic.get("parent_topic_id") is None:
                subjects[topic["subject"]]["topics"].append(self._topic_tree_node(topic, topic_lookup))

        return list(subjects.values())

    @Property("QVariantMap", notify=stateChanged)
    def curriculumSummary(self) -> dict[str, Any]:
        filtered_topics = self._filtered_topics()
        total = len(filtered_topics)
        avg = round(sum(topic["progress"] for topic in filtered_topics) / total, 1) if total > 0 else 0.0
        completed = len([topic for topic in filtered_topics if topic.get("is_completed")])
        subject_count = len({topic["subject"] for topic in filtered_topics})
        return {
            "total_topics": total,
            "avg_progress": avg,
            "stats": [
                {"label": "Subjects", "value": str(subject_count), "color": "#3B82F6"},
                {"label": "Topics", "value": str(total), "color": "#10B981"},
                {"label": "Completed", "value": str(completed), "color": "#F59E0B"},
                {"label": "Avg Progress", "value": f"{avg:.0f}%", "color": "#8B5CF6"},
            ],
        }

    @Property("QVariantList", notify=stateChanged)
    def weekCompletion(self) -> list[dict[str, Any]]:
        today = self._today
        start_of_week = today - timedelta(days=today.weekday())
        current_week = [start_of_week + timedelta(days=i) for i in range(7)]
        completed = sum(
            1 for task in self._tasks if self._is_task_completed(task) and task["scheduled_at"].date() in current_week
        )
        score = round((completed / len(current_week)) * 100) if current_week else 0
        return [{"day": day.strftime("%a"), "completed": completed, "score": score} for day in current_week]

    @Property("QVariantList", notify=stateChanged)
    def dashboardWeekBars(self) -> list[int]:
        base = self._study_minutes[-7:] if len(self._study_minutes) >= 7 else self._study_minutes + [0] * (7 - len(self._study_minutes))
        peak = max(base) if base and max(base) > 0 else 1
        return [round((value / peak) * 100) for value in base]

    @Property(str, notify=stateChanged)
    def selectedDate(self) -> str:
        return self._selected_date.isoformat()

    @Property("QVariantList", notify=stateChanged)
    def selectedDaySessions(self) -> list[dict[str, Any]]:
        tasks = [task for task in self._tasks if task["scheduled_at"].date() == self._selected_date]
        return [
            {
                "subject": SUBJECT_DISPLAY_NAMES.get(task["subject"], task["subject"]),
                "duration": task["duration_minutes"],
                "completed": self._is_task_completed(task),
            }
            for task in tasks
        ]

    @Property("QVariantList", notify=stateChanged)
    def subjectConfidence(self) -> list[dict[str, Any]]:
        rows = []
        for subject, topics in self._subject_groups().items():
            meta = self._subject_meta(subject)
            rows.append(
                {
                    "subject": subject,
                    "pct": self._average_confidence_pct(topics),
                    "progress": self._average_progress(topics),
                    "topicCount": len(topics),
                    "color": meta.color,
                }
            )
        rows.sort(key=lambda row: (-row["pct"], row["subject"]))
        return rows

    @Property(str, notify=stateChanged)
    def taskFilter(self) -> str:
        return self._task_filter

    @Property("QVariantList", notify=stateChanged)
    def topicBalance(self) -> list[float]:
        grouped = {}
        for topic in self._topics:
            subject = topic["subject"]
            grouped.setdefault(subject, []).append(topic["progress"])
        ordered = ["Biology", "Mathematics", "Physics", "Chemistry", "History"]
        return [round(sum(grouped.get(name, [])) / (len(grouped.get(name, [])) * 100), 2) if grouped.get(name, []) else 0.0 for name in ordered]

    @Property(str, notify=stateChanged)
    def curriculumFilter(self) -> str:
        return self._curriculum_filter

    @Property(str, notify=stateChanged)
    def curriculumDifficulty(self) -> str:
        return self._curriculum_filter

    @Property(str, notify=stateChanged)
    def curriculumSearch(self) -> str:
        return self._curriculum_search

    @Property("QVariantList", notify=stateChanged)
    def curriculumSubjectOptions(self) -> list[str]:
        return self._subjects_from_topics()

    @Property("QVariantList", notify=stateChanged)
    def intelligenceStats(self) -> list[dict[str, Any]]:
        completed = len(self._completed_tasks())
        total_tasks = len(self._tasks)
        completion_rate = round((completed / total_tasks) * 100) if total_tasks else 0
        avg_progress = self._average_progress()
        confidence = self._average_confidence_pct()
        hard_topics = len([topic for topic in self._topics if topic["difficulty"] == "Hard" and topic["progress"] < 60])
        return [
            {
                "title": "WEEKLY FOCUS",
                "value": f"{self._weekly_study_minutes()}m",
                "subtitle": "last 7 sessions",
                "trend": "Active" if self._weekly_study_minutes() >= 180 else "Build",
                "trendUp": self._weekly_study_minutes() >= 180,
                "accentColor": "#3B82F6",
                "valueColor": "#1A2332",
            },
            {
                "title": "COMPLETION",
                "value": f"{completion_rate}%",
                "subtitle": f"{completed}/{total_tasks} tasks",
                "trend": "Healthy" if completion_rate >= 60 else "Low",
                "trendUp": completion_rate >= 60,
                "accentColor": "#10B981",
                "valueColor": "#1A2332",
            },
            {
                "title": "MASTERY",
                "value": f"{avg_progress:.0f}%",
                "subtitle": "avg topic progress",
                "trend": "Rising" if avg_progress >= 65 else "Needs reps",
                "trendUp": avg_progress >= 65,
                "accentColor": "#F59E0B",
                "valueColor": "#1A2332",
            },
            {
                "title": "RECALL",
                "value": f"{confidence}%",
                "subtitle": f"{hard_topics} hard weak spots",
                "trend": "Strong" if confidence >= 70 else "Review",
                "trendUp": confidence >= 70,
                "accentColor": "#8B5CF6",
                "valueColor": "#1A2332",
            },
        ]

    @Property("QVariantList", notify=stateChanged)
    def studyTrend(self) -> list[int]:
        return self._study_trend_values()

    @Property("QVariantList", notify=stateChanged)
    def studyTrendLabels(self) -> list[str]:
        start = self._today - timedelta(days=13)
        return [(start + timedelta(days=index)).strftime("%d %b") for index in range(14)]

    @Property("QVariantList", notify=stateChanged)
    def activityHeatmap(self) -> list[int]:
        trend = self._study_trend_values(14)
        cells = []
        for index in range(56):
            day = self._today - timedelta(days=55 - index)
            completed_for_day = len(
                [
                    task
                    for task in self._tasks
                    if self._is_task_completed(task) and task["scheduled_at"].date() == day
                ]
            )
            recent_minutes = trend[index - 42] if index >= 42 else 0
            cells.append(min(100, completed_for_day * 35 + recent_minutes))
        return cells

    @Property("QVariantList", notify=stateChanged)
    def analyticsSubjectRows(self) -> list[dict[str, Any]]:
        rows = []
        for row in self.subjectConfidence:
            weak_topics = [
                topic
                for topic in self._subject_groups().get(row["subject"], [])
                if topic["progress"] < 60 or topic["confidence"] <= 2
            ]
            rows.append(
                {
                    **row,
                    "risk": "High" if len(weak_topics) >= 2 else ("Medium" if weak_topics else "Low"),
                    "nextAction": "Revise weak topics" if weak_topics else "Maintain cadence",
                }
            )
        return rows

    @Property("QVariantList", notify=stateChanged)
    def intelligenceInsights(self) -> list[dict[str, Any]]:
        if not self._topics:
            return [
                {
                    "title": "Add Topics",
                    "body": "Import or create topics so StudyFlow can build personalized analytics.",
                    "color": "#3B82F6",
                    "severity": "Info",
                }
            ]

        weakest = min(self._topics, key=lambda topic: (topic["confidence"], topic["progress"]))
        strongest = max(self._topics, key=lambda topic: (topic["progress"], topic["confidence"]))
        overdue = len(self._tasks_for_bucket("overdue"))
        study_minutes = self._weekly_study_minutes()
        return [
            {
                "title": f"Prioritize {weakest['name']}",
                "body": f"{weakest['subject']} has low recall confidence. Schedule a short active-recall pass before adding new material.",
                "color": "#EF4444" if weakest["confidence"] <= 2 else "#F59E0B",
                "severity": "Focus",
            },
            {
                "title": "Clear Overdue Load",
                "body": f"{overdue} overdue review{'s' if overdue != 1 else ''} are influencing the recall score.",
                "color": "#EF4444" if overdue else "#10B981",
                "severity": "Schedule",
            },
            {
                "title": f"Keep {strongest['subject']} Warm",
                "body": f"{strongest['name']} is your strongest topic. Use lighter reviews to preserve retention without over-spending time.",
                "color": "#10B981",
                "severity": "Maintain",
            },
            {
                "title": "Weekly Study Rhythm",
                "body": f"You logged {study_minutes} minutes across the latest sessions. Aim for steady 25-minute blocks instead of one large catch-up.",
                "color": "#3B82F6",
                "severity": "Habit",
            },
        ]

    @Property("QVariantList", notify=stateChanged)
    def flashcardStats(self) -> list[dict[str, Any]]:
        due_today = len(
            [
                task
                for task in self._tasks
                if not self._is_task_completed(task) and task["scheduled_at"].date() == self._today
            ]
        )
        mastered = len([topic for topic in self._topics if topic["progress"] >= PROGRESS_MASTERED])
        total = len(self._topics)
        return [
            {"label": "Due Today", "value": due_today * 4, "color": "#3B82F6"},
            {"label": "Mastered", "value": mastered * 6, "color": "#10B981"},
            {"label": "Total", "value": total * 2, "color": "#F59E0B"},
        ]

    @Property(str, notify=stateChanged)
    def settingsColumns(self) -> str:
        return "Plan,Notifications,Reminders,Auto Schedule"

    @Property("QVariantList", notify=stateChanged)
    def settingsRows(self) -> list[dict[str, Any]]:
        return [
            {
                "Plan": self._user["plan"],
                "Notifications": self._settings["notifications"],
                "Reminders": self._settings["reminders"],
                "Auto Schedule": self._settings["auto_schedule"],
            }
        ]

    @Property("QVariantList", notify=stateChanged)
    def alertSettingsRows(self) -> list[dict[str, Any]]:
        return [
            {
                "Study Reminder": self._alert_settings["study_reminder"],
                "Break Reminder": self._alert_settings["break_reminder"],
            }
        ]

    @Property("QVariantList", notify=stateChanged)
    def notifications(self) -> list[dict[str, Any]]:
        return self._notifications

    @Property("QVariantMap", notify=stateChanged)
    def userSettings(self) -> dict[str, Any]:
        return self._settings

    @Property("QVariantMap", notify=stateChanged)
    def alertSettings(self) -> dict[str, Any]:
        return self._alert_settings

    @Slot(str)
    def markTaskDone(self, task_id: str) -> None:
        task = self._find_task(task_id)
        if task:
            task["completed"] = True
            task["status"] = "completed"
            task["completed_at"] = datetime.now()
            self._study_minutes.append(task["duration_minutes"])
            self._study_minutes = self._study_minutes[-14:]
            self._save()
            self._emit()

    @Slot()
    def startSession(self) -> None:
        self._add_notification(
            "Session Started",
            "Dashboard quick-start launched. Pick a due topic and rate it when you finish.",
            "play_arrow",
            "#3B82F6",
        )

    @Slot(str, int)
    def completeRevision(self, task_id: str, rating: int) -> None:
        task = self._find_task(task_id)
        if task is None:
            return

        safe_rating = min(max(int(rating), 1), 4)
        task["completed"] = True
        task["status"] = "completed"
        task["completed_at"] = datetime.now()
        task["confidence"] = safe_rating + 1 if safe_rating < 4 else 5
        self._study_minutes.append(task["duration_minutes"])
        self._study_minutes = self._study_minutes[-14:]

        topic = self._find_topic(task["topic"])
        if topic is not None:
            topic["confidence"] = RATING_CONFIDENCE[safe_rating]
            topic["progress"] = min(100, max(0, topic["progress"] + RATING_PROGRESS_BOOST[safe_rating]))

        self._save()
        self._emit()
        self._add_notification(
            "Revision Logged",
            f"{task['topic']} marked complete with rating {RATING_LABELS[safe_rating]}.",
            "check_circle",
            "#10B981",
        )

    @Slot(str, str)
    def addSubject(self, name: str, color_tag: str) -> None:
        clean_name = name.strip()
        if not clean_name or clean_name in self._subjects_from_topics():
            return
        SUBJECTS[clean_name] = SubjectMeta(clean_name[:1].upper(), color_tag or "#3B82F6")
        self._save()
        self._emit()

    @Slot(str, str, str, str, str, str)
    def upsertTopic(
        self,
        topic_id: str,
        name: str,
        subject: str,
        difficulty: str,
        parent_topic_id: str,
        notes: str,
    ) -> None:
        clean_name = name.strip()
        clean_subject = subject.strip()
        if not clean_name or not clean_subject:
            return

        topic = self._find_topic_by_id(topic_id) if topic_id else None
        if topic is None:
            topic = self._normalize_topic(
                {
                    "id": f"topic-{uuid4().hex[:8]}",
                    "name": clean_name,
                    "subject": clean_subject,
                    "difficulty": difficulty or "Medium",
                    "notes": notes.strip(),
                    "parent_topic_id": parent_topic_id or None,
                }
            )
            self._topics.append(topic)
            self._tasks.append(self._build_task_for_topic(topic))
        else:
            previous_name = topic["name"]
            topic["name"] = clean_name
            topic["subject"] = clean_subject
            topic["difficulty"] = difficulty or "Medium"
            topic["notes"] = notes.strip()
            topic["parent_topic_id"] = parent_topic_id or None
            related_task = next((task for task in self._tasks if task["topic"] == previous_name), None)
            if related_task is not None:
                related_task["topic"] = clean_name
                related_task["subject"] = clean_subject
                related_task["difficulty"] = topic["difficulty"]
                related_task["duration_minutes"] = {"Easy": 15, "Medium": 25, "Hard": 35}[topic["difficulty"]]

        self._save()
        self._emit()

    @Slot(str)
    def deleteTopic(self, topic_id: str) -> None:
        topic = self._find_topic_by_id(topic_id)
        if topic is None:
            return
        removed_ids = {topic_id}
        changed = True
        while changed:
            changed = False
            for candidate in self._topics:
                if candidate.get("parent_topic_id") in removed_ids and candidate["id"] not in removed_ids:
                    removed_ids.add(candidate["id"])
                    changed = True
        removed_names = {item["name"] for item in self._topics if item["id"] in removed_ids}
        self._topics = [item for item in self._topics if item["id"] not in removed_ids]
        self._tasks = [task for task in self._tasks if task["topic"] not in removed_names]
        self._save()
        self._emit()

    @Slot(str)
    def markTopicComplete(self, topic_id: str) -> None:
        topic = self._find_topic_by_id(topic_id)
        if topic is None:
            return
        topic["is_completed"] = True
        topic["completion_date"] = self._today.isoformat()
        related_task = next((task for task in self._tasks if task["topic"] == topic["name"]), None)
        if related_task is not None:
            related_task["completed"] = True
            related_task["completed_at"] = datetime.now()
            related_task["status"] = "completed"
        self._save()
        self._emit()

    @Slot(str, result="QVariantMap")
    def suggestTopicDifficulty(self, topic_name: str) -> dict[str, Any]:
        clean_name = topic_name.strip()
        if not clean_name:
            return {"difficulty": "", "confidence": 0.0, "source": "empty"}
        prediction = self._nlp_service.predict_difficulty(clean_name)
        if prediction.difficulty is None:
            return {"difficulty": "", "confidence": round(prediction.confidence, 2), "source": prediction.source}
        return {
            "difficulty": prediction.difficulty.value.capitalize(),
            "confidence": round(prediction.confidence, 2),
            "source": prediction.source,
        }

    @Slot(str, str, bool)
    def importTopics(self, raw_text: str, subject: str, csv_mode: bool) -> None:
        clean_subject = subject.strip()
        if not raw_text.strip() or not clean_subject:
            return

        entries: list[str] = []
        if csv_mode:
            reader = csv.reader(StringIO(raw_text))
            for row in reader:
                if row and row[0].strip():
                    entries.append(row[0].strip())
        else:
            entries = [line.strip() for line in raw_text.splitlines() if line.strip()]

        for entry in entries:
            suggestion = self.suggestTopicDifficulty(entry)
            topic = self._normalize_topic(
                {
                    "id": f"topic-{uuid4().hex[:8]}",
                    "name": entry,
                    "subject": clean_subject,
                    "difficulty": suggestion["difficulty"] or "Medium",
                    "notes": "",
                }
            )
            self._topics.append(topic)
            self._tasks.append(self._build_task_for_topic(topic))

        self._save()
        self._emit()

    @Slot(str)
    def setTaskFilter(self, filter: str) -> None:
        self._task_filter = filter
        self._emit()

    @Slot(str)
    def setCurriculumFilter(self, filter: str) -> None:
        self._curriculum_filter = filter
        self._emit()

    @Slot(str)
    def setCurriculumDifficulty(self, difficulty: str) -> None:
        self._curriculum_filter = difficulty
        self._emit()

    @Slot(str)
    def setCurriculumSearch(self, query: str) -> None:
        self._curriculum_search = query.strip()
        self._emit()

    @Slot()
    def acceptSuggestion(self) -> None:
        # Find the "Calculus" task instead of hardcoded ID
        task = next((t for t in self._tasks if t.get("topic") == "Calculus"), None)
        if task:
            task["completed"] = True
            task["status"] = "completed"
            task["completed_at"] = datetime.now()
            self._study_minutes.append(task["duration_minutes"])
            self._study_minutes = self._study_minutes[-14:]
            self._save()
            self._emit()
            self._add_notification("Suggestion Accepted", "Calculus task completed!", "check_circle", "green")

    @Slot()
    def dismissSuggestion(self) -> None:
        self._suggestion_dismissed = True
        self._save()
        self._emit()

    @Slot(int)
    def toggleSetting(self, index: int) -> None:
        keys = ["notifications", "reminders", "auto_schedule"]
        if 0 <= index < len(keys):
            key = keys[index]
            self._settings[key] = not self._settings[key]
            self._save()
            self._emit()

    @Slot(int)
    def toggleAlertSetting(self, index: int) -> None:
        keys = ["study_reminder", "break_reminder"]
        if 0 <= index < len(keys):
            key = keys[index]
            self._alert_settings[key] = not self._alert_settings[key]
            self._save()
            self._emit()

    @Slot()
    def selectToday(self) -> None:
        self._selected_date = self._today
        self._emit()

    @Slot()
    def selectTomorrow(self) -> None:
        self._selected_date = self._today + timedelta(days=1)
        self._emit()

    @Slot(str)
    def selectCalendarDay(self, date_str: str) -> None:
        try:
            self._selected_date = date.fromisoformat(date_str)
            self._emit()
        except ValueError:
            pass  # Ignore invalid dates

    @Slot(str)
    def updateUserName(self, name: str) -> None:
        self._user["name"] = name
        self._save()
        self._emit()

    @Slot()
    def clearNotifications(self) -> None:
        self._notifications.clear()
        self._save()
        self._emit()

    @Slot(result=str)
    def exportLearningReport(self) -> str:
        export_dir = Path(__file__).resolve().parent.parent / "data"
        export_dir.mkdir(parents=True, exist_ok=True)
        report_path = export_dir / "learning_report.txt"
        stats = {item["title"]: item["value"] for item in self.intelligenceStats}
        insights = "\n".join(f"- {item['title']}: {item['body']}" for item in self.intelligenceInsights)
        subjects = "\n".join(
            f"- {row['subject']}: confidence {row['pct']}%, progress {row['progress']}%, risk {row['risk']}"
            for row in self.analyticsSubjectRows
        )
        report_path.write_text(
            "\n".join(
                [
                    "StudyFlow Learning Report",
                    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    "",
                    "Summary",
                    f"- Weekly focus: {stats.get('WEEKLY FOCUS', '0m')}",
                    f"- Completion: {stats.get('COMPLETION', '0%')}",
                    f"- Mastery: {stats.get('MASTERY', '0%')}",
                    f"- Recall: {stats.get('RECALL', '0%')}",
                    "",
                    "Subject Health",
                    subjects or "- No subjects yet",
                    "",
                    "Insights",
                    insights or "- No insights yet",
                ]
            ),
            encoding="utf-8",
        )
        self._add_notification(
            "Learning Report Exported",
            f"Saved analytics report to {report_path.name}.",
            "R",
            "#8B5CF6",
        )
        return str(report_path)
