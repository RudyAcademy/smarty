"""Data model for Smarty's content records and editable user state.

Content records (ideas, performance records, categories) come only from the
seed file or an imported batch -- this module never invents field values.
User state (status / notes / practical steps) is a separate, append-only
concern tracked in the journal (see journal.py). A seed/import file's own
``user_state`` block (present for provenance -- it should always show
unreviewed/blank/null) is never read for actual app state.

Field names here match the real Tower Hill seed schema: ideas key their
received window as ``received_date``, performance records as ``period``;
categories are referenced on records by their exact ``label`` text (e.g.
"Growth and enrolment"), not a slug.
"""

from __future__ import annotations

from dataclasses import dataclass, field

STATUSES = ("unreviewed", "kept", "parked", "rejected")

REQUIRED_IDEA_FIELDS = ("id", "title", "categories", "summary", "implementation_advice")
REQUIRED_PERFORMANCE_FIELDS = ("id", "bot", "summary", "caveats", "verification_status")
REQUIRED_CATEGORY_FIELDS = ("id", "label")


class SeedValidationError(ValueError):
    """Raised when a seed/import file does not match the required shape."""


@dataclass(frozen=True)
class ReceivedPeriod:
    start: str | None = None
    end: str | None = None
    granularity: str = "period"
    timezone: str = "America/Toronto"
    original_discovery_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict | None) -> "ReceivedPeriod":
        if not data:
            return cls()
        return cls(
            start=data.get("start"),
            end=data.get("end"),
            granularity=data.get("granularity", "period"),
            timezone=data.get("timezone", "America/Toronto"),
            original_discovery_at=data.get("original_discovery_at"),
        )

    def sort_key(self) -> tuple:
        # Newest-first sort key; ties broken by caller (title, then id).
        return (self.start or "", self.end or "")

    def to_dict(self) -> dict:
        return {
            "start": self.start,
            "end": self.end,
            "granularity": self.granularity,
            "timezone": self.timezone,
            "original_discovery_at": self.original_discovery_at,
        }


@dataclass(frozen=True)
class Idea:
    id: str
    title: str
    categories: tuple[str, ...]
    summary: str
    implementation_advice: dict
    originating_bots: tuple[str, ...] = field(default_factory=tuple)
    received_period: ReceivedPeriod = field(default_factory=ReceivedPeriod)
    sources: tuple[dict, ...] = field(default_factory=tuple)
    source_records: tuple[dict, ...] = field(default_factory=tuple)
    missing_source_note: str | None = None
    evidence_claim: str | None = None
    verification_status: str | None = None
    cautions: tuple[str, ...] = field(default_factory=tuple)
    content_revision: int = 1

    @classmethod
    def from_dict(cls, data: dict) -> "Idea":
        _require_fields(data, REQUIRED_IDEA_FIELDS, "idea")
        advice = data["implementation_advice"]
        if not isinstance(advice, dict) or "kind" not in advice or "text" not in advice:
            raise SeedValidationError(
                f"idea {data.get('id')!r}: implementation_advice must have 'kind' and 'text'"
            )
        evidence = data.get("evidence") or {}
        return cls(
            id=data["id"],
            title=data["title"],
            categories=tuple(data["categories"]),
            summary=data["summary"],
            implementation_advice=dict(advice),
            originating_bots=tuple(data.get("originating_bots", [])),
            received_period=ReceivedPeriod.from_dict(data.get("received_date")),
            sources=tuple(data.get("sources", [])),
            source_records=tuple(data.get("source_records", [])),
            missing_source_note=evidence.get("missing_source_note"),
            evidence_claim=evidence.get("claim"),
            verification_status=evidence.get("verification_status"),
            cautions=tuple(data.get("cautions", [])),
            content_revision=int(data.get("content_revision", 1)),
        )

    def to_cache_dict(self) -> dict:
        """Inverse of ``from_dict``: the exact shape the catalog cache
        stores and later re-parses. A generic ``dataclasses.asdict`` would
        serialize under this class's Python attribute names instead (e.g.
        ``received_period`` instead of ``received_date``, a flat
        ``missing_source_note`` instead of a nested ``evidence`` object),
        which ``from_dict`` would then fail to find -- silently dropping
        those fields on the next read. Keep this in sync with ``from_dict``.
        """
        return {
            "id": self.id,
            "title": self.title,
            "categories": list(self.categories),
            "summary": self.summary,
            "implementation_advice": dict(self.implementation_advice),
            "originating_bots": list(self.originating_bots),
            "received_date": self.received_period.to_dict(),
            "sources": [dict(s) for s in self.sources],
            "source_records": [dict(s) for s in self.source_records],
            "evidence": {
                "verification_status": self.verification_status,
                "claim": self.evidence_claim,
                "missing_source_note": self.missing_source_note,
            },
            "cautions": list(self.cautions),
            "content_revision": self.content_revision,
        }


@dataclass(frozen=True)
class PerformanceRecord:
    id: str
    bot: str
    summary: str
    caveats: tuple[str, ...]
    verification_status: str
    title: str | None = None
    categories: tuple[str, ...] = field(default_factory=tuple)
    received_period: ReceivedPeriod = field(default_factory=ReceivedPeriod)
    sources: tuple[dict, ...] = field(default_factory=tuple)
    content_revision: int = 1

    @classmethod
    def from_dict(cls, data: dict) -> "PerformanceRecord":
        _require_fields(data, REQUIRED_PERFORMANCE_FIELDS, "performance record")
        if "score" in data or "grade" in data:
            raise SeedValidationError(
                f"performance record {data.get('id')!r}: must not carry an invented score or grade"
            )
        return cls(
            id=data["id"],
            bot=data["bot"],
            summary=data["summary"],
            caveats=tuple(data["caveats"]),
            verification_status=data["verification_status"],
            title=data.get("title"),
            categories=tuple(data.get("categories", [])),
            received_period=ReceivedPeriod.from_dict(data.get("period")),
            sources=tuple(data.get("sources", [])),
            content_revision=int(data.get("content_revision", 1)),
        )

    def to_cache_dict(self) -> dict:
        """Inverse of ``from_dict`` -- see Idea.to_cache_dict for why this
        can't be a generic ``dataclasses.asdict`` call."""
        return {
            "id": self.id,
            "bot": self.bot,
            "title": self.title,
            "categories": list(self.categories),
            "summary": self.summary,
            "caveats": list(self.caveats),
            "verification_status": self.verification_status,
            "period": self.received_period.to_dict(),
            "sources": [dict(s) for s in self.sources],
            "content_revision": self.content_revision,
        }


@dataclass(frozen=True)
class Category:
    id: str
    label: str
    kind: str = "content_category"
    status_filter: str | None = None
    order: int = 0

    @classmethod
    def from_dict(cls, data: dict, order: int = 0) -> "Category":
        _require_fields(data, REQUIRED_CATEGORY_FIELDS, "category")
        return cls(
            id=data["id"],
            label=data["label"],
            kind=data.get("kind", "content_category"),
            status_filter=data.get("status_filter"),
            order=order,
        )


@dataclass
class UserState:
    """Current reduced user state for one content record (idea or performance record)."""

    content_id: str
    status: str = "unreviewed"
    notes: str = ""
    practical_steps: str = ""
    # Fields with unresolved conflicting values: field_name -> list of (value, device_label, event_time)
    conflicts: dict = field(default_factory=dict)

    def is_conflicted(self, field_name: str) -> bool:
        return field_name in self.conflicts and len(self.conflicts[field_name]) > 1


def _require_fields(data: dict, required: tuple[str, ...], kind: str) -> None:
    missing = [f for f in required if f not in data or data[f] in (None, "")]
    if missing:
        raise SeedValidationError(f"{kind} {data.get('id')!r} missing required field(s): {missing}")
