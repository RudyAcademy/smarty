"""Combines the content catalog with the reduced user-state journal.

This is the main object the UI and CLI talk to: it owns the local journal
file, exposes the current status/notes/practical-steps per record, and
appends new operations when the user edits something.
"""

from __future__ import annotations

from pathlib import Path

from smarty.journal import (
    Operation,
    append_operation,
    new_operation,
    read_journal,
    reduce_field_states,
)
from smarty.models import STATUSES, UserState
from smarty.paths import SmartyPaths
from smarty.seed import Catalog


class Store:
    def __init__(self, paths: SmartyPaths, catalog: Catalog):
        self.paths = paths
        self.catalog = catalog
        self._ops: list[Operation] = []
        self._damaged: list[str] = []
        self._states: dict[tuple[str, str], object] = {}
        self.reload_journal()

    def reload_journal(self) -> None:
        self._ops, self._damaged = read_journal(self.paths.local_journal_path)
        self._states = reduce_field_states(self._ops)

    @property
    def damaged_lines(self) -> list[str]:
        return list(self._damaged)

    @property
    def all_operations(self) -> list[Operation]:
        return list(self._ops)

    def all_content_ids(self) -> list[str]:
        ids = [i.id for i in self.catalog.ideas]
        ids += [p.id for p in self.catalog.performance_records]
        return ids

    def user_state(self, content_id: str) -> UserState:
        us = UserState(content_id=content_id)
        for field_name in ("status", "notes", "practical_steps", "transferred_at"):
            state = self._states.get((content_id, field_name))
            if state is None:
                continue
            if state.conflicted:
                us.conflicts[field_name] = [
                    (h.value, h.device_label, h.event_time) for h in state.heads
                ]
            else:
                value = state.value
                if field_name == "status" and value is not None:
                    us.status = value
                elif field_name == "notes" and value is not None:
                    us.notes = value
                elif field_name == "practical_steps" and value is not None:
                    us.practical_steps = value
                elif field_name == "transferred_at" and value is not None:
                    us.transferred_at = value
        return us

    def current_heads(self, content_id: str, field_name: str) -> tuple[str, ...]:
        state = self._states.get((content_id, field_name))
        if state is None:
            return ()
        return tuple(h.op_id for h in state.heads)

    def _apply(self, content_id: str, field_name: str, value: str) -> Operation:
        base = self.current_heads(content_id, field_name)
        op = new_operation(
            device_id=self.paths.device_id,
            device_label=self.paths.device_label,
            content_id=content_id,
            field=field_name,
            base_op_ids=base,
            value=value,
        )
        append_operation(self.paths.local_journal_path, op)
        self._ops.append(op)
        self._states = reduce_field_states(self._ops)
        return op

    def set_status(self, content_id: str, status: str) -> Operation:
        if status not in STATUSES:
            raise ValueError(f"unknown status: {status!r}")
        op = self._apply(content_id, "status", status)
        if status == "kept":
            # Every (re-)confirmation as kept re-enters the buffer, even if
            # it was already archived before -- a fresh "kept" decision is
            # meaningfully new information for Grok-bot to see again.
            self._apply(content_id, "transferred_at", "")
        return op

    def set_notes(self, content_id: str, notes: str) -> Operation:
        return self._apply(content_id, "notes", notes)

    def set_practical_steps(self, content_id: str, text: str) -> Operation:
        return self._apply(content_id, "practical_steps", text)

    def set_transferred_at(self, content_id: str, timestamp: str) -> Operation:
        return self._apply(content_id, "transferred_at", timestamp)

    def merge_remote_ops(self, remote_ops: list[Operation]) -> None:
        """Merge operations read from the shared journal into the local view."""
        known_ids = {op.op_id for op in self._ops}
        new_ops = [op for op in remote_ops if op.op_id not in known_ids]
        if not new_ops:
            return
        self._ops.extend(new_ops)
        self._states = reduce_field_states(self._ops)
