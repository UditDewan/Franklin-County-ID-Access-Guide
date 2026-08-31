"""Checks that run before anything is built.

An error stops the build. A warning is printed and the build carries on.
Wrong information here sends a person across town for nothing, so the
checks are deliberately strict and there is no flag to skip them.

    python -m src.validate                  normal run
    python -m src.validate --check-links    also ask every source URL if it is alive
    python -m src.validate --publish        also refuse anything not confirmed twice
"""

from __future__ import annotations

import argparse
import datetime
import pathlib
import re
import sys
import urllib.error
import urllib.request

import textstat

from . import content as content_mod
from .content import (
    CONFIDENCE_LEVELS,
    PROVENANCE_FIELDS,
    STALE_FAIL_DAYS,
    STALE_WARN_DAYS,
)

MAX_READING_GRADE = 8.0
MAX_WORDS_PER_SENTENCE = 20

# Fields written for the person using the guide, so these get read-level checks.
PLAIN_FIELDS = ("plain_summary", "what_to_say")


class Problem:
    def __init__(self, level: str, where: str, message: str):
        self.level = level
        self.where = where
        self.message = message

    def __str__(self) -> str:
        return f"{self.level.upper():7} {self.where}: {self.message}"


def error(where, message):
    return Problem("error", where, message)


def warn(where, message):
    return Problem("warn", where, message)


def sentences(text: str) -> list[str]:
    text = " ".join(str(text).split())
    return [s for s in re.split(r"(?<=[.!?])\s+", text) if s]


# A phone number has to survive being turned into a tel: link on the page.
PHONE = re.compile(r"^\d{3}-\d{3}-\d{4}$")

REQUIRED_STEP_FIELDS = ("id", "title", "plain_summary", "time_estimate")
REQUIRED_AGENCY_FIELDS = ("id", "name", "what_they_do", "address", "phone", "hours")


def check_shape(content):
    """Runs before everything else, so the later checks can assume well formed data.

    Every message here names the file and says what to type, because the people
    editing this content are volunteers with a YAML file open, not programmers.
    """
    problems = []

    for step_id, step in content["steps"].items():
        where = step.get("_file", step_id)
        if not step or set(step) == {"_file"}:
            problems.append(error(where, "this file is empty, or is not a YAML mapping"))
            continue
        for field in REQUIRED_STEP_FIELDS:
            if not step.get(field):
                problems.append(error(where, f"no {field}: field"))
        for field in ("bring", "where", "next_steps", "steps_detail"):
            if field in step and not isinstance(step[field], list):
                problems.append(error(where, f"{field}: must be a list"))
        for position, item in enumerate(step.get("bring") or [], start=1):
            if not isinstance(item, dict) or not item.get("id"):
                problems.append(error(where, f"bring item {position} has no id:"))
        cost = step.get("cost")
        if cost is not None:
            if not isinstance(cost, dict):
                problems.append(error(where, "cost: must be a block, not a single value"))
            else:
                amount = cost.get("amount_usd")
                if not isinstance(amount, (int, float)) or isinstance(amount, bool):
                    problems.append(
                        error(f"{where}:cost", f"amount_usd must be a number, not {amount!r}")
                    )
                elif amount < 0:
                    problems.append(error(f"{where}:cost", "amount_usd cannot be negative"))

    for agency_id, agency in content["agencies"].items():
        where = f"agencies.yaml:{agency_id}"
        for field in REQUIRED_AGENCY_FIELDS:
            if not agency.get(field):
                problems.append(error(where, f"no {field}: field"))
        phone = agency.get("phone")
        if phone and not PHONE.match(str(phone)):
            problems.append(
                error(where, f"phone {phone!r} must read like 614-555-0100, since it becomes a dial link")
            )

    for doc_id, doc in content["documents"].items():
        for field in ("id", "name", "plain_name"):
            if not doc.get(field):
                problems.append(error(f"documents.yaml:{doc_id}", f"no {field}: field"))
        # A bare string here would make "address" match by substring.
        if "proves" in doc and not isinstance(doc["proves"], list):
            problems.append(error(f"documents.yaml:{doc_id}", "proves: must be a list"))

    tree = content["tree"]
    if not tree.get("questions"):
        problems.append(error("content/tree.yaml", "no questions:"))
    if not tree.get("plan"):
        problems.append(error("content/tree.yaml", "no plan:"))

    for position, question in enumerate(tree.get("questions") or [], start=1):
        where = "content/tree.yaml"
        if not isinstance(question, dict) or not question.get("id"):
            problems.append(error(where, f"question {position} has no id:"))
            continue
        if not question.get("text"):
            problems.append(error(where, f"question {question['id']!r} has no text:"))
        if not question.get("options"):
            problems.append(error(where, f"question {question['id']!r} has no options"))

    seen = set()
    for position, entry in enumerate(tree.get("plan") or [], start=1):
        where = "content/tree.yaml"
        if not isinstance(entry, dict) or not entry.get("step"):
            problems.append(error(where, f"plan entry {position} has no step:"))
            continue
        step_id = entry["step"]
        if step_id in seen:
            # Two entries would render two cards with the same HTML id.
            problems.append(
                error(where, f"{step_id!r} is in the plan twice. List it once and widen its when: block")
            )
        seen.add(step_id)
        if "when" in entry:
            conditions = entry["when"]
            if not isinstance(conditions, dict):
                problems.append(
                    error(where, f"{step_id!r} has a when: that is not a block of conditions")
                )
            else:
                for key, values in conditions.items():
                    if not isinstance(values, list):
                        problems.append(
                            error(
                                where,
                                f"{step_id!r} has when: {key}: {values!r}. Write it as a list, "
                                "['no'], or it becomes a text search instead of a match",
                            )
                        )
                    elif not all(isinstance(v, str) for v in values):
                        problems.append(
                            error(
                                where,
                                f"{step_id!r} has a when: {key}: value that is not text. "
                                "Quote it, because YAML reads yes and no as booleans",
                            )
                        )

    return problems


def check_provenance(content, today):
    problems = []
    for where, node in content_mod.provenance_nodes(content):
        prov = node.get("provenance")
        if not prov:
            problems.append(error(where, "no provenance block"))
            continue

        for field in PROVENANCE_FIELDS:
            if not prov.get(field):
                problems.append(error(where, f"provenance is missing {field}"))

        confidence = prov.get("confidence")
        if confidence and confidence not in CONFIDENCE_LEVELS:
            problems.append(
                error(where, f"confidence {confidence!r} is not one of {CONFIDENCE_LEVELS}")
            )

        url = prov.get("source_url")
        if url and not str(url).startswith("https://"):
            problems.append(error(where, "source_url must be an https link"))

        verified_on = prov.get("verified_on")
        if not isinstance(verified_on, (datetime.date, datetime.datetime)):
            if verified_on:
                problems.append(error(where, "verified_on must be a date, as 2026-08-30"))
            continue

        age = content_mod.age_in_days(verified_on, today)
        if age < 0:
            problems.append(error(where, "verified_on is in the future"))
        elif age > STALE_FAIL_DAYS:
            problems.append(error(where, f"last checked {age} days ago, limit is {STALE_FAIL_DAYS}"))
        elif age > STALE_WARN_DAYS:
            problems.append(warn(where, f"last checked {age} days ago, worth another call"))
    return problems


def check_references(content):
    problems = []
    for step_id, step in content["steps"].items():
        where = step["_file"]
        for agency_id in step.get("where") or []:
            if agency_id not in content["agencies"]:
                problems.append(error(where, f"unknown agency_id {agency_id!r}"))
        for item in step.get("bring") or []:
            if item["id"] not in content["documents"]:
                problems.append(error(where, f"unknown document id {item['id']!r}"))
        for target in step.get("next_steps") or []:
            if target not in content["steps"]:
                problems.append(error(where, f"next_steps points at missing step {target!r}"))
        if step["id"] != step_id:
            problems.append(error(where, "the id inside the file does not match"))
    return problems


def check_graph(content):
    """No loops, and every path ends somewhere real."""
    problems = []
    steps = content["steps"]

    colour = {}

    def visit(step_id, trail):
        state = colour.get(step_id)
        if state == "done":
            return
        if state == "open":
            loop = " -> ".join(trail + [step_id])
            problems.append(error("content/steps", f"the steps loop: {loop}"))
            return
        colour[step_id] = "open"
        for target in steps[step_id].get("next_steps") or []:
            if target in steps:
                visit(target, trail + [step_id])
        colour[step_id] = "done"

    for step_id in steps:
        visit(step_id, [])

    for step_id, step in steps.items():
        ends_here = not (step.get("next_steps") or [])
        if ends_here and not (step.get("terminal") or step.get("referral")):
            problems.append(
                error(step["_file"], "this step ends the path but is not marked terminal or referral")
            )
    return problems


def check_tree(content):
    problems = []
    tree = content["tree"]
    where = "content/tree.yaml"

    questions = {}
    for question in tree["questions"]:
        if question["id"] in questions:
            problems.append(error(where, f"two questions share the id {question['id']!r}"))
        # Unquoted Yes and No are booleans to YAML, which then reach the page as
        # "true" and "false". Caught once already, so it is checked here now.
        for option in question["options"]:
            for key in ("value", "label"):
                if not isinstance(option.get(key), str):
                    problems.append(
                        error(
                            where,
                            f"question {question['id']!r} has an option {key} that is not text: "
                            f"{option.get(key)!r}. Put quotes round it in the YAML.",
                        )
                    )

        values = [o["value"] for o in question["options"]]
        if len(values) != len(set(values)):
            problems.append(error(where, f"question {question['id']!r} repeats an answer value"))
        questions[question["id"]] = set(values)

    planned = set()
    for entry in tree["plan"]:
        step_id = entry["step"]
        planned.add(step_id)
        if step_id not in content["steps"]:
            problems.append(error(where, f"the plan names a missing step {step_id!r}"))
        for key, values in (entry.get("when") or {}).items():
            if key not in questions:
                problems.append(error(where, f"{step_id!r} asks about unknown question {key!r}"))
                continue
            for value in values:
                if value not in questions[key]:
                    problems.append(
                        error(where, f"{step_id!r} expects {key}={value!r}, which is not an option")
                    )

    for step_id in content["steps"]:
        if step_id not in planned:
            problems.append(warn(step_id, "no set of answers ever reaches this step"))

    # Walking the paths below needs the ids above to resolve, so stop on errors
    # only. A warning here is fine and the walk still runs.
    if any(p.level == "error" for p in problems):
        return problems

    # Walk every combination a person could click. A path that ends nowhere is a
    # person left standing in a hallway, so this one is an error.
    seen_steps = set()
    for answers in content_mod.all_answer_sets(tree):
        plan = content_mod.plan_for(tree, answers)
        seen_steps.update(plan)
        if not plan:
            problems.append(error(where, f"these answers produce no steps at all: {answers}"))
            continue
        last = content["steps"][plan[-1]]
        if not (last.get("terminal") or last.get("referral")):
            problems.append(
                error(where, f"the path ending at {last['id']!r} is neither finished nor handed off")
            )

    for step_id in planned - seen_steps:
        problems.append(warn(where, f"{step_id!r} is in the plan but no answers select it"))
    return problems


def check_plain_language(content):
    problems = []
    for step in content["steps"].values():
        for field in PLAIN_FIELDS:
            text = step.get(field)
            if not text:
                continue
            where = f"{step['_file']}:{field}"
            grade = textstat.flesch_kincaid_grade(str(text))
            if grade > MAX_READING_GRADE:
                problems.append(
                    error(where, f"reads at grade {grade:.1f}, the limit is {MAX_READING_GRADE}")
                )
        for field in PLAIN_FIELDS + ("steps_detail",):
            value = step.get(field)
            if not value:
                continue
            lines = value if isinstance(value, list) else [value]
            for line in lines:
                for sentence in sentences(line):
                    words = len(sentence.split())
                    if words > MAX_WORDS_PER_SENTENCE:
                        problems.append(
                            Problem(
                                "error",
                                f"{step['_file']}:{field}",
                                f"{words} words in one sentence, the limit is "
                                f"{MAX_WORDS_PER_SENTENCE}: {sentence[:60]}...",
                            )
                        )
    return problems


def check_publishable(content):
    """The gate that stops a draft being mistaken for a finished guide."""
    problems = []
    for where, node in content_mod.provenance_nodes(content):
        confidence = (node.get("provenance") or {}).get("confidence")
        if confidence != "confirmed":
            problems.append(
                error(where, f"confidence is {confidence!r}, publishing needs a second contact")
            )
    return problems


def check_links(content):
    """Advisory only. Agency sites go down, and several block robots outright."""
    problems = []
    checked = {}
    for where, node in content_mod.provenance_nodes(content):
        url = (node.get("provenance") or {}).get("source_url")
        if not url or url in checked:
            continue
        request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "id-guide-linkcheck"})
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                checked[url] = response.status
        except urllib.error.HTTPError as exc:
            checked[url] = exc.code
        except Exception as exc:  # network down, DNS, timeout
            checked[url] = str(exc)
        status = checked[url]
        if status == 200:
            continue
        if status in (401, 403, 405, 429):
            problems.append(warn(where, f"{url} answered {status}, likely blocking robots"))
        else:
            problems.append(warn(where, f"{url} answered {status}, open it by hand"))
    return problems


def run(root=content_mod.ROOT, today=None, check_link_health=False, publish=False):
    today = today or datetime.date.today()
    content = content_mod.load(root)

    # If the files are the wrong shape, every later check is guessing.
    shape_problems = check_shape(content)
    if any(p.level == "error" for p in shape_problems):
        return shape_problems

    problems = list(shape_problems)
    problems += check_provenance(content, today)
    problems += check_references(content)
    problems += check_graph(content)
    problems += check_tree(content)
    problems += check_plain_language(content)
    if publish:
        problems += check_publishable(content)
    if check_link_health:
        problems += check_links(content)
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Check the guide's content.")
    parser.add_argument("--check-links", action="store_true", help="ask every source URL if it is alive")
    parser.add_argument("--publish", action="store_true", help="also require a second confirmation on every fact")
    parser.add_argument("--root", default=str(content_mod.ROOT))
    args = parser.parse_args(argv)

    problems = run(
        root=pathlib.Path(args.root),
        check_link_health=args.check_links,
        publish=args.publish,
    )
    for problem in problems:
        print(problem)

    errors = [p for p in problems if p.level == "error"]
    warnings = [p for p in problems if p.level == "warn"]
    print(f"\n{len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
