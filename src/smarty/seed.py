"""Loads the bundled/local seed catalog (ideas, performance records, categories).

No ideas, scores, dates, URLs, or research are invented here. If no seed
files are present, the catalog is simply empty and the UI must say so
plainly -- never silently show a synthesized catalog.

Each seed file is a wrapped JSON object, not a bare list:
``categories.json`` -> {"categories": [...], ...}; ``ideas.json`` ->
{"metadata": {...}, "ideas": [...]}; ``weekly-performance.json`` ->
{"metadata": {...}, "records": [...]}. Records reference a category by its
exact ``label`` text (e.g. "Growth and enrolment"), not a slug.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from smarty.models import Category, Idea, PerformanceRecord, SeedValidationError


@dataclass
class Catalog:
    ideas: tuple[Idea, ...]
    performance_records: tuple[PerformanceRecord, ...]
    categories: tuple[Category, ...]
    source_note: str = "no seed catalog found"

    @property
    def is_empty(self) -> bool:
        return not self.ideas and not self.performance_records


def empty_catalog(note: str = "no seed catalog found") -> Catalog:
    return Catalog(ideas=(), performance_records=(), categories=(), source_note=note)


def _load_json_object_key(path: Path, key: str) -> list:
    """Read a wrapped seed file and return the list under ``key``."""
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SeedValidationError(f"{path}: invalid JSON ({exc})") from exc
    if not isinstance(data, dict):
        raise SeedValidationError(f"{path}: expected a JSON object at the top level")
    value = data.get(key, [])
    if not isinstance(value, list):
        raise SeedValidationError(f"{path}: expected a list under {key!r}")
    return value


def build_catalog(
    idea_dicts: list[dict],
    performance_dicts: list[dict],
    category_dicts: list[dict],
    *,
    source_note: str = "seed",
) -> Catalog:
    known_category_labels = {c["label"] for c in category_dicts}

    categories = tuple(Category.from_dict(c, order=i) for i, c in enumerate(category_dicts))

    seen_ids: set[str] = set()
    ideas: list[Idea] = []
    for d in idea_dicts:
        idea = Idea.from_dict(d)
        if idea.id in seen_ids:
            raise SeedValidationError(f"duplicate id in seed: {idea.id!r}")
        seen_ids.add(idea.id)
        unknown = [cat for cat in idea.categories if cat not in known_category_labels]
        if unknown:
            raise SeedValidationError(
                f"idea {idea.id!r} references unknown category label(s): {unknown}"
            )
        ideas.append(idea)

    performance_records: list[PerformanceRecord] = []
    for d in performance_dicts:
        rec = PerformanceRecord.from_dict(d)
        if rec.id in seen_ids:
            raise SeedValidationError(f"duplicate id in seed: {rec.id!r}")
        seen_ids.add(rec.id)
        unknown = [cat for cat in rec.categories if cat not in known_category_labels]
        if unknown:
            raise SeedValidationError(
                f"performance record {rec.id!r} references unknown category label(s): {unknown}"
            )
        performance_records.append(rec)

    return Catalog(
        ideas=tuple(ideas),
        performance_records=tuple(performance_records),
        categories=categories,
        source_note=source_note,
    )


def load_seed_from_dir(seed_dir: Path) -> Catalog:
    """Load ideas.json / weekly-performance.json / categories.json from a directory.

    Returns an empty catalog (clearly labeled) if the directory or files are
    missing -- this is the expected state until a real seed is provided.
    """
    ideas_path = seed_dir / "ideas.json"
    performance_path = seed_dir / "weekly-performance.json"
    categories_path = seed_dir / "categories.json"

    if not ideas_path.exists() and not performance_path.exists() and not categories_path.exists():
        return empty_catalog(f"no seed catalog found at {seed_dir}")

    idea_dicts = _load_json_object_key(ideas_path, "ideas")
    performance_dicts = _load_json_object_key(performance_path, "records")
    category_dicts = _load_json_object_key(categories_path, "categories")

    return build_catalog(idea_dicts, performance_dicts, category_dicts, source_note=str(seed_dir))
