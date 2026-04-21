from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import uuid4

SYNCED = "synced"
PENDING = "pending"
CONFLICT = "conflict"


@dataclass(frozen=True)
class SyncConfig:
    enabled: bool = False
    supabase_url: str = ""
    supabase_anon_key: str = ""
    device_id: str = ""
    last_sync_at: str = ""

    @property
    def is_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_anon_key)


@dataclass(frozen=True)
class SyncResult:
    status: str
    pushed: int = 0
    pulled: int = 0
    conflicts: int = 0
    message: str = ""
    synced_at: str = ""


class SyncService:
    """Offline-first sync planner with last-write-wins conflict handling."""

    def __init__(self, config: SyncConfig | None = None) -> None:
        self.config = config or SyncConfig(device_id=f"device-{uuid4().hex[:10]}")

    def status(self, state: dict[str, Any]) -> dict[str, Any]:
        pending = self.count_pending_changes(state)
        return {
            "enabled": self.config.enabled,
            "configured": self.config.is_configured,
            "deviceId": self.config.device_id,
            "lastSyncAt": self.config.last_sync_at,
            "pendingChanges": pending,
            "label": self._status_label(pending),
            "color": self._status_color(pending),
        }

    def count_pending_changes(self, state: dict[str, Any]) -> int:
        return sum(1 for item in self.iter_sync_items(state) if item.get("sync_status", PENDING) != SYNCED)

    def iter_sync_items(self, state: dict[str, Any]) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for key in ("topics", "tasks", "notifications"):
            items.extend(dict(item, _collection=key) for item in state.get(key, []))
        for key in ("settings", "alert_settings", "reminder_preferences"):
            value = state.get(key, {})
            if value:
                items.append({"id": key, "_collection": key, "sync_status": value.get("sync_status", PENDING)})
        return items

    def mark_pending(self, item: dict[str, Any]) -> None:
        item["sync_status"] = PENDING
        item["updated_at"] = datetime.now().isoformat()
        item.setdefault("device_id", self.config.device_id)

    def sync(self, state: dict[str, Any], remote_state: dict[str, Any] | None = None) -> SyncResult:
        if not self.config.enabled:
            return SyncResult(status="disabled", message="Cloud sync is off.")
        if not self.config.is_configured:
            return SyncResult(status="local_only", message="Add Supabase URL and anon key to enable cloud sync.")

        remote_state = remote_state or {}
        pushed = 0
        pulled = 0
        conflicts = 0
        for collection in ("topics", "tasks", "notifications"):
            local_items = {item["id"]: item for item in state.get(collection, []) if item.get("id")}
            remote_items = {item["id"]: item for item in remote_state.get(collection, []) if item.get("id")}
            for item_id, local_item in local_items.items():
                remote_item = remote_items.get(item_id)
                if remote_item is None or self._is_newer(local_item, remote_item):
                    local_item["sync_status"] = SYNCED
                    local_item["last_synced_at"] = datetime.now().isoformat()
                    pushed += 1
                elif self._is_newer(remote_item, local_item):
                    local_item.update(remote_item)
                    local_item["sync_status"] = SYNCED
                    pulled += 1
                else:
                    local_item["sync_status"] = CONFLICT
                    conflicts += 1

        if not conflicts:
            for key in ("settings", "alert_settings", "reminder_preferences"):
                if key in state:
                    state[key]["sync_status"] = SYNCED
                    state[key]["last_synced_at"] = datetime.now().isoformat()

        synced_at = datetime.now().isoformat()
        return SyncResult(
            status=CONFLICT if conflicts else SYNCED,
            pushed=pushed,
            pulled=pulled,
            conflicts=conflicts,
            message=f"Sync complete: pushed {pushed}, pulled {pulled}, conflicts {conflicts}.",
            synced_at=synced_at,
        )

    def _status_label(self, pending: int) -> str:
        if not self.config.enabled:
            return "Offline only"
        if not self.config.is_configured:
            return "Cloud not connected"
        if pending:
            return f"{pending} pending change{'s' if pending != 1 else ''}"
        return "Synced"

    def _status_color(self, pending: int) -> str:
        if not self.config.enabled:
            return "#64748B"
        if not self.config.is_configured:
            return "#F59E0B"
        return "#F59E0B" if pending else "#10B981"

    def _is_newer(self, left: dict[str, Any], right: dict[str, Any]) -> bool:
        return self._timestamp(left) > self._timestamp(right)

    def _timestamp(self, item: dict[str, Any]) -> datetime:
        raw = item.get("updated_at") or item.get("timestamp") or item.get("scheduled_at")
        if isinstance(raw, datetime):
            return raw
        if isinstance(raw, str):
            try:
                return datetime.fromisoformat(raw)
            except ValueError:
                return datetime.min
        return datetime.min
