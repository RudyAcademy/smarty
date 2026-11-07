import pytest

from smarty.models import Idea, PerformanceRecord, SeedValidationError


def _idea_dict(**overrides):
    d = {
        "id": "sparky-idea-gauss",
        "title": "Gauss contest preparation",
        "categories": ["growth_and_enrolment"],
        "summary": "A proposal for contest prep sessions.",
        "implementation_advice": {
            "kind": "bot_suggested_not_original_source_evidence",
            "text": "Run a 6-week prep block.",
        },
    }
    d.update(overrides)
    return d


def test_idea_from_dict_round_trips_required_fields():
    idea = Idea.from_dict(_idea_dict())
    assert idea.id == "sparky-idea-gauss"
    assert idea.categories == ("growth_and_enrolment",)
    assert idea.implementation_advice["kind"] == "bot_suggested_not_original_source_evidence"


def test_idea_missing_required_field_rejected():
    bad = _idea_dict()
    del bad["summary"]
    with pytest.raises(SeedValidationError):
        Idea.from_dict(bad)


def test_idea_missing_implementation_advice_kind_rejected():
    bad = _idea_dict(implementation_advice={"text": "no kind here"})
    with pytest.raises(SeedValidationError):
        Idea.from_dict(bad)


def test_performance_record_requires_fields():
    d = {
        "id": "sparky-performance-2026-11-07-professor",
        "bot": "Professor",
        "summary": "v61 published; later geometry work stayed unpublished.",
        "caveats": ["partial recovered review"],
        "verification_status": "documented_partial",
    }
    rec = PerformanceRecord.from_dict(d)
    assert rec.verification_status == "documented_partial"


def test_performance_record_rejects_invented_score():
    d = {
        "id": "x",
        "bot": "Professor",
        "summary": "s",
        "caveats": [],
        "verification_status": "documented_partial",
        "score": 9,
    }
    with pytest.raises(SeedValidationError):
        PerformanceRecord.from_dict(d)
