"""Prints the call list.

    python -m src.reverify --older-than 90

Turns "the guide needs checking again" into a list of phone numbers and the
exact question to ask at each one. The point is to make the recurring work a
two hour job rather than a research project someone keeps putting off.
"""

from __future__ import annotations

import argparse
import datetime
import pathlib
import sys

from . import content as content_mod

# What to actually ask when the phone is answered, per kind of fact.
QUESTIONS = {
    "agency": "Confirm the address, the public hours, and the phone number.",
    "cost": "Confirm the fee, and which kinds of payment are taken.",
    "step": "Confirm the requirements, and what happens if the person has no photo ID.",
    "document": "Confirm this is still on the accepted list.",
    "state": "Confirm this is still the right office for that state.",
}


def kind_of(where: str) -> str:
    if where.startswith("agencies.yaml"):
        return "agency"
    if where.startswith("documents.yaml"):
        return "document"
    if where.startswith("states.yaml"):
        return "state"
    if where.endswith(":cost"):
        return "cost"
    return "step"


def phones_for(where: str, content: dict) -> list[str]:
    """The numbers to dial for this fact."""
    if where.startswith("agencies.yaml:"):
        agency = content["agencies"].get(where.split(":", 1)[1])
        return [f"{agency['name']}: {agency['phone']}"] if agency else []

    for step in content["steps"].values():
        if where.startswith(step["_file"]):
            return [
                f"{content['agencies'][a]['name']}: {content['agencies'][a]['phone']}"
                for a in step.get("where") or []
                if a in content["agencies"]
            ]
    return []


def call_list(root=content_mod.ROOT, older_than=content_mod.STALE_WARN_DAYS, today=None):
    today = today or datetime.date.today()
    content = content_mod.load(root)

    rows = []
    for where, node in content_mod.provenance_nodes(content):
        prov = node["provenance"]
        age = content_mod.age_in_days(prov["verified_on"], today)
        confirmed = prov.get("confidence") == "confirmed"
        if age < older_than and confirmed:
            continue
        rows.append(
            {
                "where": where,
                "age": age,
                "confidence": prov.get("confidence"),
                "source_url": prov.get("source_url"),
                "ask": QUESTIONS[kind_of(where)],
                "phones": phones_for(where, content),
                "reason": "not confirmed twice" if not confirmed else f"{age} days old",
            }
        )
    rows.sort(key=lambda r: (-r["age"], r["where"]))
    return rows


def render(rows, older_than) -> str:
    if not rows:
        return f"Nothing is older than {older_than} days and everything is confirmed. Nothing to do."

    lines = [
        f"{len(rows)} facts need a call.",
        "",
        "Log every call in research/verification-log.md, then raise the confidence",
        "in the YAML. Two independent contacts move a fact to confirmed.",
        "",
    ]
    for row in rows:
        lines.append(f"[ ] {row['where']}")
        lines.append(f"      why: {row['reason']} (confidence: {row['confidence']})")
        lines.append(f"      ask: {row['ask']}")
        for phone in row["phones"]:
            lines.append(f"      call: {phone}")
        lines.append(f"      page: {row['source_url']}")
        lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="List the facts that need a phone call.")
    parser.add_argument("--older-than", type=int, default=content_mod.STALE_WARN_DAYS)
    parser.add_argument("--root", default=str(content_mod.ROOT))
    args = parser.parse_args(argv)

    rows = call_list(root=pathlib.Path(args.root), older_than=args.older_than)
    print(render(rows, args.older_than))
    return 0


if __name__ == "__main__":
    sys.exit(main())
