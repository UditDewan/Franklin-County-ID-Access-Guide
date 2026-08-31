"""The validator has to catch every planted error, or it is not worth having.

Each case below breaks the real content in one specific way and checks that the
error comes back naming that problem.
"""

import datetime
import pathlib

import pytest
import yaml

from src import validate


def read(path):
    return yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8"))


def write(path, data):
    pathlib.Path(path).write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def errors(root, today):
    return [p for p in validate.run(root=root, today=today) if p.level == "error"]


def test_the_real_content_is_clean(repo, today):
    problems = validate.run(root=repo, today=today)
    assert [str(p) for p in problems if p.level == "error"] == []


# Each entry: a name, a function that breaks the copy, and text the error must contain.

def drop_provenance(root):
    path = root / "content" / "steps" / "state-id.yaml"
    step = read(path)
    del step["provenance"]
    write(path, step)


def drop_one_provenance_field(root):
    path = root / "content" / "agencies.yaml"
    data = read(path)
    del data["agencies"][0]["provenance"]["verified_by"]
    write(path, data)


def age_a_fact_past_the_limit(root):
    path = root / "content" / "steps" / "birth-cert-ohio.yaml"
    step = read(path)
    step["provenance"]["verified_on"] = datetime.date(2025, 1, 1)
    write(path, step)


def date_in_the_future(root):
    path = root / "content" / "steps" / "birth-cert-ohio.yaml"
    step = read(path)
    step["provenance"]["verified_on"] = datetime.date(2030, 1, 1)
    write(path, step)


def unknown_confidence(root):
    path = root / "content" / "agencies.yaml"
    data = read(path)
    data["agencies"][0]["provenance"]["confidence"] = "pretty sure"
    write(path, data)


def insecure_source_url(root):
    path = root / "content" / "agencies.yaml"
    data = read(path)
    data["agencies"][0]["provenance"]["source_url"] = "http://example.org/"
    write(path, data)


def unknown_agency_id(root):
    path = root / "content" / "steps" / "state-id.yaml"
    step = read(path)
    step["where"] = ["a-place-that-does-not-exist"]
    write(path, step)


def unknown_document_id(root):
    path = root / "content" / "steps" / "state-id.yaml"
    step = read(path)
    step["bring"][0]["id"] = "golden-ticket"
    write(path, step)


def next_step_missing(root):
    path = root / "content" / "steps" / "address-proof.yaml"
    step = read(path)
    step["next_steps"] = ["nowhere"]
    write(path, step)


def make_a_loop(root):
    path = root / "content" / "steps" / "state-id.yaml"
    step = read(path)
    step["next_steps"] = ["address-proof"]
    step.pop("terminal", None)
    write(path, step)


def dead_end_not_marked(root):
    path = root / "content" / "steps" / "state-id.yaml"
    step = read(path)
    del step["terminal"]
    write(path, step)


def plan_names_missing_step(root):
    path = root / "content" / "tree.yaml"
    tree = read(path)
    tree["plan"].append({"step": "buy-a-yacht"})
    write(path, tree)


def condition_on_unknown_question(root):
    path = root / "content" / "tree.yaml"
    tree = read(path)
    tree["plan"][2]["when"] = {"favourite_colour": ["blue"]}
    write(path, tree)


def condition_on_impossible_answer(root):
    path = root / "content" / "tree.yaml"
    tree = read(path)
    tree["plan"][2]["when"] = {"mail": ["maybe"]}
    write(path, tree)


def path_that_never_finishes(root):
    """Cut the last two steps, so some answers end on a step that is not a leaf."""
    path = root / "content" / "tree.yaml"
    tree = read(path)
    tree["plan"] = [e for e in tree["plan"] if e["step"] not in ("state-id", "address-proof")]
    write(path, tree)


def reading_level_too_high(root):
    path = root / "content" / "steps" / "fee-help.yaml"
    step = read(path)
    step["plain_summary"] = (
        "Subsequent to the aforementioned determination, applicants experiencing "
        "documented indigence may pursue administrative remediation of statutory "
        "fee obligations."
    )
    write(path, step)


def sentence_too_long(root):
    path = root / "content" / "steps" / "fee-help.yaml"
    step = read(path)
    step["steps_detail"] = [
        "Ask a case worker at the front desk to help you fill out the form and "
        "then wait for a reply that may take a while to come back to you."
    ]
    write(path, step)


def unquoted_yes_becomes_a_boolean(root):
    path = root / "content" / "tree.yaml"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("label: 'Yes'", "label: Yes", 1), encoding="utf-8")


def duplicate_question_id(root):
    path = root / "content" / "tree.yaml"
    tree = read(path)
    tree["questions"].append(dict(tree["questions"][0]))
    write(path, tree)


PLANTED = [
    ("a step with no provenance", drop_provenance, "no provenance block"),
    ("provenance missing a field", drop_one_provenance_field, "missing verified_by"),
    ("a fact older than 180 days", age_a_fact_past_the_limit, "limit is 180"),
    ("a date in the future", date_in_the_future, "in the future"),
    ("an invented confidence level", unknown_confidence, "is not one of"),
    ("a source url that is not https", insecure_source_url, "https"),
    ("a step pointing at no such agency", unknown_agency_id, "unknown agency_id"),
    ("a step pointing at no such document", unknown_document_id, "unknown document id"),
    ("next_steps pointing nowhere", next_step_missing, "missing step"),
    ("steps that loop", make_a_loop, "loop"),
    ("a dead end not marked as one", dead_end_not_marked, "terminal or referral"),
    ("the plan naming a missing step", plan_names_missing_step, "missing step"),
    ("a condition on an unknown question", condition_on_unknown_question, "unknown question"),
    ("a condition on an impossible answer", condition_on_impossible_answer, "not an option"),
    ("a path that never finishes", path_that_never_finishes, "neither finished nor handed off"),
    ("writing that is too hard to read", reading_level_too_high, "reads at grade"),
    ("a sentence over twenty words", sentence_too_long, "words in one sentence"),
    ("an unquoted Yes turning into a boolean", unquoted_yes_becomes_a_boolean, "is not text"),
    ("two questions with the same id", duplicate_question_id, "share the id"),
]


@pytest.mark.parametrize("name,break_it,expected", PLANTED, ids=[c[0] for c in PLANTED])
def test_planted_error_is_caught(copied_repo, today, name, break_it, expected):
    break_it(copied_repo)
    found = errors(copied_repo, today)
    assert found, f"the validator missed: {name}"
    assert any(expected in p.message for p in found), (
        f"{name} was not reported clearly. Got: " + "; ".join(p.message for p in found)
    )


def test_stale_fact_warns_before_it_fails(copied_repo, today):
    path = copied_repo / "content" / "steps" / "birth-cert-ohio.yaml"
    step = read(path)
    step["provenance"]["verified_on"] = today - datetime.timedelta(days=120)
    write(path, step)

    problems = validate.run(root=copied_repo, today=today)
    assert not [p for p in problems if p.level == "error"]
    assert any("worth another call" in p.message for p in problems)


def test_publish_gate_blocks_unconfirmed_facts(repo, today):
    problems = validate.run(root=repo, today=today, publish=True)
    assert any("second contact" in p.message for p in problems), (
        "the seed content is desk checked only, so --publish must refuse it"
    )


# --- shape checks: an ordinary YAML mistake must name the file, never traceback ---

def empty_step_file(root):
    (root / "content" / "steps" / "fee-help.yaml").write_text("", encoding="utf-8")


def step_with_no_id(root):
    path = root / "content" / "steps" / "fee-help.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("id: fee-help\n", "", 1), encoding="utf-8")


def bring_item_with_no_id(root):
    path = root / "content" / "steps" / "state-id.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace("  - id: birth-certificate\n", "  -\n", 1),
        encoding="utf-8",
    )


def cost_written_as_words(root):
    path = root / "content" / "steps" / "birth-cert-ohio.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace("amount_usd: 25.00", 'amount_usd: "twenty five"'),
        encoding="utf-8",
    )


def negative_cost(root):
    path = root / "content" / "steps" / "birth-cert-ohio.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace("amount_usd: 25.00", "amount_usd: -5"),
        encoding="utf-8",
    )


def agency_with_no_phone(root):
    path = root / "content" / "agencies.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace("    phone: 614-645-7331\n", "", 1),
        encoding="utf-8",
    )


def phone_that_cannot_be_dialled(root):
    path = root / "content" / "agencies.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "    phone: 614-645-7331", "    phone: call the main line"
        ),
        encoding="utf-8",
    )


def step_listed_twice_in_the_plan(root):
    path = root / "content" / "tree.yaml"
    path.write_text(path.read_text(encoding="utf-8") + "\n  - step: state-id\n", encoding="utf-8")


def question_with_no_options(root):
    path = root / "content" / "tree.yaml"
    text = path.read_text(encoding="utf-8")
    start = text.index("  - id: name_changed")
    end = text.index("plan:")
    path.write_text(
        text[:start] + "  - id: name_changed\n    text: Has your name changed?\n    options: []\n\n" + text[end:],
        encoding="utf-8",
    )


def where_that_is_not_a_list(root):
    path = root / "content" / "steps" / "state-id.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "where:\n  - bmv-deputy-registrar", "where: bmv-deputy-registrar"
        ),
        encoding="utf-8",
    )


MALFORMED = [
    ("an empty step file", empty_step_file, "empty"),
    ("a step with no id", step_with_no_id, "no id: field"),
    ("a bring item with no id", bring_item_with_no_id, "bring item 1 has no id"),
    ("a cost written as words", cost_written_as_words, "must be a number"),
    ("a negative cost", negative_cost, "cannot be negative"),
    ("an agency with no phone", agency_with_no_phone, "no phone: field"),
    ("a phone nobody can dial", phone_that_cannot_be_dialled, "614-555-0100"),
    ("a step listed twice in the plan", step_listed_twice_in_the_plan, "in the plan twice"),
    ("a question with no options", question_with_no_options, "has no options"),
    ("a where: that is not a list", where_that_is_not_a_list, "must be a list"),
]


@pytest.mark.parametrize("name,break_it,expected", MALFORMED, ids=[c[0] for c in MALFORMED])
def test_malformed_content_is_reported_not_crashed(copied_repo, today, name, break_it, expected):
    break_it(copied_repo)
    found = errors(copied_repo, today)  # must not raise
    assert found, f"the validator missed: {name}"
    assert any(expected in p.message for p in found), (
        f"{name} was not explained clearly. Got: " + "; ".join(p.message for p in found)
    )


def when_written_as_a_bare_string(root):
    """`when: {mail: 'no'}` without brackets becomes a substring test, not a match."""
    path = root / "content" / "tree.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace("when: {mail: ['no']}", "when: {mail: 'no'}"),
        encoding="utf-8",
    )


def when_value_left_unquoted(root):
    path = root / "content" / "tree.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace("when: {mail: ['no']}", "when: {mail: [no]}"),
        encoding="utf-8",
    )


def proves_written_as_a_bare_string(root):
    path = root / "content" / "documents.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace("    proves: [ssn]", "    proves: ssn", 1),
        encoding="utf-8",
    )


MALFORMED_TOO = [
    ("a when: written as a bare string", when_written_as_a_bare_string, "Write it as a list"),
    ("a when: value left unquoted", when_value_left_unquoted, "not text"),
    ("proves: written as a bare string", proves_written_as_a_bare_string, "proves: must be a list"),
]


@pytest.mark.parametrize("name,break_it,expected", MALFORMED_TOO, ids=[c[0] for c in MALFORMED_TOO])
def test_yaml_traps_are_caught(copied_repo, today, name, break_it, expected):
    break_it(copied_repo)
    found = errors(copied_repo, today)
    assert found, f"the validator missed: {name}"
    assert any(expected in p.message for p in found), (
        f"{name} was not explained clearly. Got: " + "; ".join(p.message for p in found)
    )
