"""Append-only, field-level operation journal.

Each edit (status change, notes edit, practical-steps edit) is one
``Operation``. Notes and status are independent fields, so one device can
edit notes while another edits status without a false conflict. Two
operations on the same field that both list the *same* base heads but
disagree in value are a genuine conflict: both are kept, visible, until a
later operation explicitly bases itself on all current heads (a deliberate
resolution). Nothing is ever deleted from the journal; resolving writes a
new operation, it does not erase the conflicting ones.
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

FIELDS = ("status", "notes", "practical_steps", "transferred_at")


@dataclass(frozen=True)
class Operation:
    op_id: str
    device_id: str
    device_label: str
    content_id: str
    field: str
    base_op_ids: tuple[str, ...]
    value: str
    event_time: str

    def to_dict(self) -> dict:
        d = asdict(self)
        d["base_op_ids"] = list(self.base_op_ids)
        return d

    def to_json_line(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_dict(cls, d: dict) -> "Operation":
        return cls(
            op_id=d["op_id"],
            device_id=d["device_id"],
            device_label=d["device_label"],
            content_id=d["content_id"],
            field=d["field"],
            base_op_ids=tuple(d.get("base_op_ids", [])),
            value=d["value"],
            event_time=d["event_time"],
        )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_operation(
    *,
    device_id: str,
    device_label: str,
    content_id: str,
    field: str,
    base_op_ids: tuple[str, ...],
    value: str,
) -> Operation:
    if field not in FIELDS:
        raise ValueError(f"unknown field: {field!r}")
    return Operation(
        op_id=str(uuid.uuid4()),
        device_id=device_id,
        device_label=device_label,
        content_id=content_id,
        field=field,
        base_op_ids=tuple(base_op_ids),
        value=value,
        event_time=now_iso(),
    )


def parse_journal_text(text: str) -> tuple[list[Operation], list[str]]:
    """Split journal text into parsed operations and raw damaged lines.

    Damaged lines are never discarded by this parser -- callers that
    republish the journal must carry them forward verbatim.
    """
    ops: list[Operation] = []
    damaged: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            op = Operation.from_dict(d)
        except (json.JSONDecodeError, KeyError, TypeError):
            damaged.append(raw_line)
            continue
        ops.append(op)
    return ops, damaged


def read_journal(path: Path) -> tuple[list[Operation], list[str]]:
    if not path.exists():
        return [], []
    return parse_journal_text(path.read_text(encoding="utf-8"))


def append_operation(path: Path, op: Operation) -> None:
    """Append one operation to the local journal, fsynced before returning."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(op.to_json_line() + "\n")
        f.flush()
        os.fsync(f.fileno())


def union_ops(*op_lists: list[Operation]) -> list[Operation]:
    """Union operations by op_id. Same op_id twice is a no-op (first wins)."""
    by_id: dict[str, Operation] = {}
    for ops in op_lists:
        for op in ops:
            by_id.setdefault(op.op_id, op)
    return sorted(by_id.values(), key=lambda o: (o.event_time, o.op_id))


@dataclass
class FieldState:
    heads: tuple[Operation, ...]

    @property
    def conflicted(self) -> bool:
        return len(self.heads) > 1

    @property
    def value(self) -> str | None:
        if not self.heads:
            return None
        return self.heads[0].value if not self.conflicted else None


def reduce_field_states(ops: list[Operation]) -> dict[tuple[str, str], FieldState]:
    """Reduce operations to the current head(s) per (content_id, field)."""
    by_key: dict[tuple[str, str], dict[str, Operation]] = {}
    superseded: dict[tuple[str, str], set[str]] = {}

    for op in ops:
        key = (op.content_id, op.field)
        by_key.setdefault(key, {})[op.op_id] = op
        superseded.setdefault(key, set()).update(op.base_op_ids)

    states: dict[tuple[str, str], FieldState] = {}
    for key, op_map in by_key.items():
        superseded_ids = superseded.get(key, set())
        heads = [op for op_id, op in op_map.items() if op_id not in superseded_ids]
        heads.sort(key=lambda o: (o.device_label, o.event_time, o.op_id))
        states[key] = FieldState(heads=tuple(heads))
    return states
