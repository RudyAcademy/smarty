from smarty.journal import (
    new_operation,
    parse_journal_text,
    reduce_field_states,
    union_ops,
)


def _op(content_id, field, value, base=(), device_label="pc-a"):
    return new_operation(
        device_id=device_label,
        device_label=device_label,
        content_id=content_id,
        field=field,
        base_op_ids=base,
        value=value,
    )


def test_single_edit_is_not_conflicted():
    op = _op("idea-1", "status", "kept")
    states = reduce_field_states([op])
    state = states[("idea-1", "status")]
    assert not state.conflicted
    assert state.value == "kept"


def test_second_edit_based_on_first_supersedes_it():
    op1 = _op("idea-1", "notes", "first note")
    op2 = _op("idea-1", "notes", "second note", base=(op1.op_id,))
    states = reduce_field_states([op1, op2])
    state = states[("idea-1", "notes")]
    assert not state.conflicted
    assert state.value == "second note"


def test_divergent_edits_from_same_base_conflict_and_both_survive():
    base = _op("idea-1", "status", "unreviewed")
    a = _op("idea-1", "status", "kept", base=(base.op_id,), device_label="pc-a")
    b = _op("idea-1", "status", "rejected", base=(base.op_id,), device_label="pc-b")
    states = reduce_field_states([base, a, b])
    state = states[("idea-1", "status")]
    assert state.conflicted
    assert state.value is None
    values = {h.value for h in state.heads}
    assert values == {"kept", "rejected"}


def test_resolving_op_based_on_both_heads_clears_conflict():
    base = _op("idea-1", "status", "unreviewed")
    a = _op("idea-1", "status", "kept", base=(base.op_id,), device_label="pc-a")
    b = _op("idea-1", "status", "rejected", base=(base.op_id,), device_label="pc-b")
    resolve = _op("idea-1", "status", "kept", base=(a.op_id, b.op_id), device_label="pc-a")
    states = reduce_field_states([base, a, b, resolve])
    state = states[("idea-1", "status")]
    assert not state.conflicted
    assert state.value == "kept"


def test_notes_and_status_are_independent_fields():
    status_op = _op("idea-1", "status", "kept", device_label="pc-a")
    notes_op = _op("idea-1", "notes", "check with Lumi", device_label="pc-b")
    states = reduce_field_states([status_op, notes_op])
    assert not states[("idea-1", "status")].conflicted
    assert not states[("idea-1", "notes")].conflicted
    assert states[("idea-1", "status")].value == "kept"
    assert states[("idea-1", "notes")].value == "check with Lumi"


def test_same_op_id_twice_is_a_no_op_in_union():
    op = _op("idea-1", "status", "kept")
    merged = union_ops([op], [op])
    assert len(merged) == 1


def test_parse_journal_text_preserves_damaged_lines():
    op = _op("idea-1", "status", "kept")
    text = op.to_json_line() + "\n" + "{not valid json" + "\n"
    ops, damaged = parse_journal_text(text)
    assert len(ops) == 1
    assert damaged == ["{not valid json"]
