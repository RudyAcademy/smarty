"""Pure (no Qt) view-model logic for the category/list/detail panes.

Kept separate from main_window.py so the sorting, filtering and status-view
rules can be unit tested without starting a Qt application.
"""

from __future__ import annotations

from dataclasses import dataclass

from smarty.models import UserState
from smarty.seed import Catalog
from smarty.store import Store
from smarty.version import CATEGORIES_ORDER, STATUS_VIEWS_ORDER

STATUS_VIEW_LABELS = {
    "rudys_collection": "Rudy's collection",
    "park_it_for_later": "Park it for later",
    "rejected_recoverable": "Rejected (recoverable)",
}
STATUS_VIEW_TO_STATUS = {
    "rudys_collection": "kept",
    "park_it_for_later": "parked",
    "rejected_recoverable": "rejected",
}


@dataclass(frozen=True)
class RecordRow:
    content_id: str
    title: str
    kind: str  # "idea" | "performance"
    bot: str | None
    period_sort_key: tuple
    status: str
    transferred_at: str
    record: object


def _all_rows(catalog: Catalog, store: Store) -> list[RecordRow]:
    rows: list[RecordRow] = []
    for idea in catalog.ideas:
        us = store.user_state(idea.id)
        rows.append(
            RecordRow(
                content_id=idea.id,
                title=idea.title,
                kind="idea",
                bot=(idea.originating_bots[0] if idea.originating_bots else None),
                period_sort_key=idea.received_period.sort_key(),
                status=us.status,
                transferred_at=us.transferred_at,
                record=idea,
            )
        )
    for rec in catalog.performance_records:
        us = store.user_state(rec.id)
        rows.append(
            RecordRow(
                content_id=rec.id,
                title=rec.title or rec.bot,
                kind="performance",
                bot=rec.bot,
                period_sort_key=rec.received_period.sort_key(),
                status=us.status,
                transferred_at=us.transferred_at,
                record=rec,
            )
        )
    return rows


def rows_for_category(
    catalog: Catalog,
    store: Store,
    category_label: str,
    *,
    include_rejected: bool = True,
) -> list[RecordRow]:
    """category_label is the category's exact label text (e.g. "Growth and
    enrolment"), matched against each record's own .categories -- both
    ideas and performance records carry that list, so this is uniform."""
    rows = [r for r in _all_rows(catalog, store) if category_label in getattr(r.record, "categories", ())]
    if not include_rejected:
        rows = [r for r in rows if r.status != "rejected"]
    return rows


def rows_for_status_view(catalog: Catalog, store: Store, view_key: str) -> list[RecordRow]:
    status = STATUS_VIEW_TO_STATUS[view_key]
    return [r for r in _all_rows(catalog, store) if r.status == status]


def rows_for_buffer(catalog: Catalog, store: Store) -> list[RecordRow]:
    """Kept, not yet pulled/archived by Grok-bot -- "actionable" in Rudy's
    terms. Parked and rejected never appear here, by design."""
    return [r for r in _all_rows(catalog, store) if r.status == "kept" and not r.transferred_at]


def rows_for_archive(catalog: Catalog, store: Store) -> list[RecordRow]:
    """Kept, already pulled/archived by Grok-bot."""
    return [r for r in _all_rows(catalog, store) if r.status == "kept" and r.transferred_at]


def filter_rows(rows: list[RecordRow], *, search: str = "", bot: str | None = None, status: str | None = None,
                 store: Store | None = None) -> list[RecordRow]:
    out = rows
    if bot:
        out = [r for r in out if (r.bot or "").lower() == bot.lower()]
    if status:
        out = [r for r in out if r.status == status]
    if search:
        needle = search.lower()

        def matches(r: RecordRow) -> bool:
            rec = r.record
            haystacks = [r.title, r.content_id, getattr(rec, "summary", ""), r.bot or ""]
            if store is not None:
                haystacks.append(store.user_state(r.content_id).notes)
            return any(needle in (h or "").lower() for h in haystacks)

        out = [r for r in out if matches(r)]
    return out


def sort_rows(rows: list[RecordRow], *, newest_first: bool = True) -> list[RecordRow]:
    """Sort by received period (newest or oldest first per the toggle).
    Ties within the same period always break by title then id, ascending --
    the original order inside a period is unknown, so this is a documented,
    stable tie-break, not a claim about discovery order."""
    by_tie_break = sorted(rows, key=lambda r: (r.title, r.content_id))
    return sorted(by_tie_break, key=lambda r: r.period_sort_key, reverse=newest_first)
