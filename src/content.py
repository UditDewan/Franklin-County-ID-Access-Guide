"""Loading the YAML content. Shared by validate, build and reverify."""

from __future__ import annotations

import datetime
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

# How old a fact may get before it is called out, and before the build stops.
STALE_WARN_DAYS = 90
STALE_FAIL_DAYS = 180

# Only facts at "confirmed" may be published. See CONTRIBUTING.md.
CONFIDENCE_LEVELS = ("desk", "phone", "confirmed")

PROVENANCE_FIELDS = ("source_url", "verified_on", "verified_by", "confidence")


def _strip(value):
    """YAML folded blocks end in a newline, which renders as a stray space."""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return [_strip(v) for v in value]
    if isinstance(value, dict):
        return {k: _strip(v) for k, v in value.items()}
    return value


def _read(path: pathlib.Path):
    with path.open(encoding="utf-8") as handle:
        return _strip(yaml.safe_load(handle))


def _by_id(entries) -> dict:
    """Index a list on its id, tolerating entries that have not got one yet."""
    out = {}
    for position, entry in enumerate(entries or []):
        if isinstance(entry, dict):
            out[entry.get("id") or f"<entry {position + 1} with no id>"] = entry
    return out


def load(root: pathlib.Path | str = ROOT) -> dict:
    """Read every content file under `root` into one dictionary."""
    root = pathlib.Path(root)
    content_dir = root / "content"

    # Nothing here assumes the files are well formed. A half-finished YAML file
    # should produce a validation error naming the file, never a traceback.
    steps = {}
    for path in sorted((content_dir / "steps").glob("*.yaml")):
        relative = str(path.relative_to(root)).replace("\\", "/")
        step = _read(path) or {}
        if not isinstance(step, dict):
            step = {}
        step["_file"] = relative
        steps[step.get("id") or relative] = step

    documents = _read(content_dir / "documents.yaml") or {}
    states = _read(content_dir / "states.yaml") or {}
    agencies = _read(content_dir / "agencies.yaml") or {}

    return {
        "agencies": _by_id(agencies.get("agencies")),
        "documents": _by_id(documents.get("documents")),
        "not_accepted": documents.get("not_accepted") or [],
        "states": states,
        "steps": steps,
        "tree": _read(content_dir / "tree.yaml") or {},
    }


def provenance_nodes(content: dict):
    """Yield (where, node) for everything that must carry provenance."""
    for agency_id, agency in content["agencies"].items():
        yield f"agencies.yaml:{agency_id}", agency
    for doc_id, doc in content["documents"].items():
        yield f"documents.yaml:{doc_id}", doc
    for position, entry in enumerate(content["not_accepted"]):
        name = entry.get("id", position + 1) if isinstance(entry, dict) else position + 1
        yield f"documents.yaml:not_accepted:{name}", entry if isinstance(entry, dict) else {}
    for step_id, step in content["steps"].items():
        yield f"{step['_file']}", step
        if "cost" in step:
            yield f"{step['_file']}:cost", step["cost"]
    states = content["states"] or {}
    if isinstance(states.get("directory"), dict):
        yield "states.yaml:directory", states["directory"]
    for position, state in enumerate(states.get("states") or []):
        if isinstance(state, dict):
            yield f"states.yaml:{state.get('id', position + 1)}", state


def age_in_days(verified_on, today: datetime.date | None = None) -> int:
    today = today or datetime.date.today()
    if isinstance(verified_on, datetime.datetime):
        verified_on = verified_on.date()
    return (today - verified_on).days


def all_answer_sets(tree: dict):
    """Every combination a person could click through. There are not many."""
    questions = tree.get("questions") or []

    def walk(index, answers):
        if index == len(questions):
            yield dict(answers)
            return
        question = questions[index]
        for option in question["options"]:
            answers[question["id"]] = option["value"]
            yield from walk(index + 1, answers)

    yield from walk(0, {})


def plan_for(tree: dict, answers: dict) -> list:
    """The ordered list of step ids for one set of answers."""
    chosen = []
    for entry in tree.get("plan") or []:
        conditions = entry.get("when") or {}
        if all(answers.get(key) in values for key, values in conditions.items()):
            chosen.append(entry["step"])
            if entry.get("stop_after"):
                break
    return chosen
