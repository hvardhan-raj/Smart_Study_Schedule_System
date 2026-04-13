from __future__ import annotations

import json
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .defaults import (
    build_default_notifications,
    build_default_tasks,
    default_alert_settings,
    default_settings,
    default_study_minutes,
    default_topics,
    default_user,
)


def merge_nested(base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in update.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_nested(merged[key], value)
        else:
            merged[key] = value
    return merged


def serialize_tasks(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    payload = []
    for task in tasks:
        item = dict(task)
        item["scheduled_at"] = item["scheduled_at"].isoformat()
        item["completed_at"] = item["completed_at"].isoformat() if item["completed_at"] else None
        payload.append(item)
    return payload


def deserialize_tasks(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    payload = []
    for task in tasks:
        item = dict(task)
        if isinstance(item["scheduled_at"], str):
            item["scheduled_at"] = datetime.fromisoformat(item["scheduled_at"])
        if item.get("completed_at") and isinstance(item["completed_at"], str):
            item["completed_at"] = datetime.fromisoformat(item["completed_at"])
        payload.append(item)
    return payload


def serialize_notifications(notifications: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [dict(notification) for notification in notifications]


def deserialize_notifications(notifications: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [dict(notification) for notification in notifications]


def load_state(store_path: Path, today: date) -> dict[str, Any]:
    state = {
        "user": default_user(),
        "settings": default_settings(),
        "alert_settings": default_alert_settings(),
        "suggestion_dismissed": False,
        "study_minutes": default_study_minutes(),
        "topics": default_topics(),
        "tasks": build_default_tasks(today),
        "notifications": build_default_notifications(),
    }

    if store_path.exists():
        try:
            payload = json.loads(store_path.read_text(encoding="utf-8"))
            state["user"].update(payload.get("user", {}))
            state["settings"] = merge_nested(state["settings"], payload.get("settings", {}))
            state["alert_settings"].update(payload.get("alert_settings", {}))
            state["suggestion_dismissed"] = payload.get("suggestion_dismissed", False)
            state["study_minutes"] = payload.get("study_minutes", state["study_minutes"])
            state["topics"] = payload.get("topics", state["topics"])
            state["tasks"] = payload.get("tasks", serialize_tasks(build_default_tasks(today)))
            state["notifications"] = payload.get("notifications", serialize_notifications(build_default_notifications()))
        except (json.JSONDecodeError, OSError):
            pass

    state["tasks"] = deserialize_tasks(state["tasks"])
    state["notifications"] = deserialize_notifications(state["notifications"])
    return state


def save_state(store_path: Path, state: dict[str, Any]) -> None:
    payload = {
        "user": state["user"],
        "settings": state["settings"],
        "alert_settings": state["alert_settings"],
        "suggestion_dismissed": state["suggestion_dismissed"],
        "study_minutes": state["study_minutes"],
        "topics": state["topics"],
        "tasks": serialize_tasks(state["tasks"]),
        "notifications": serialize_notifications(state["notifications"]),
    }
    store_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
