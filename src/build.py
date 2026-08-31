"""Turns the YAML into the site in public/.

    python -m src.build

Validation runs first. If it finds an error, nothing is written.
"""

from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import re
import shutil
import sys

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from . import content as content_mod
from . import validate
from .validate import sentences

# Users are on phones, often paying for the data. Keep the whole page small.
PAGE_WEIGHT_LIMIT_BYTES = 100 * 1024

SITE_URL = "https://franklin-id-guide.example.org"

# Roughly what fits on one side of US Letter at 10.5pt. A soft warning, because
# only a person holding the paper can really tell.
PRINT_SHEET_WORD_LIMIT = 620

# The steps that carry a line worth printing on the handout.
PRINT_STEPS = {
    "birth-cert-ohio": "Birth certificate",
    "social-security-card": "Social Security card",
    "state-id": "BMV",
    "address-proof": "Address papers",
}

PRINT_PLACES = [
    "columbus-public-health-vitals",
    "odh-vital-statistics",
    "bmv-deputy-registrar",
    "homeless-hotline",
    "star-house",
]


def json_for_script(payload) -> Markup:
    """JSON for a <script> tag.

    Browsers do not decode HTML entities inside a script tag, so this has to
    go in unescaped. Escaping the less-than sign keeps a stray closing tag
    inside the data from ending the script early.
    """
    text = json.dumps(payload, separators=(",", ":"))
    return Markup(text.replace("<", r"\u003c"))


def visible_words(html: str) -> list[str]:
    """The words a reader actually sees. Style and script blocks are not words."""
    for tag in ("style", "script"):
        html = re.sub("<" + tag + "[^>]*>.*?</" + tag + ">", " ", html, flags=re.S | re.I)
    return re.sub("<[^>]+>", " ", html).split()


def decorate(prov: dict, today: datetime.date) -> dict:
    """Add the fields templates need: how old this fact is, and whether to flag it."""
    out = dict(prov)
    age = content_mod.age_in_days(prov["verified_on"], today)
    out["age_days"] = age
    out["stale"] = age > content_mod.STALE_WARN_DAYS
    out["verified_on"] = str(prov["verified_on"])
    return out


def prepare(content: dict, today: datetime.date) -> dict:
    """Resolve every id into the thing it points at, so templates stay dumb."""
    agencies = {}
    for agency_id, agency in content["agencies"].items():
        agency = dict(agency)
        agency["provenance"] = decorate(agency["provenance"], today)
        agencies[agency_id] = agency

    # Plan order first, then anything not yet wired into the plan. A step that is
    # only half wired up still has to render, or the no-JavaScript page silently
    # loses a page the validator only warned about.
    order = [entry["step"] for entry in content["tree"]["plan"]]
    order += [step_id for step_id in content["steps"] if step_id not in order]

    steps = []
    for step_id in order:
        step = dict(content["steps"][step_id])
        step["provenance"] = decorate(step["provenance"], today)
        if "cost" in step:
            cost = dict(step["cost"])
            cost["provenance"] = decorate(cost["provenance"], today)
            step["cost"] = cost
        step["places"] = [agencies[a] for a in step.get("where") or []]
        step["bring"] = [
            dict(item, document=content["documents"][item["id"]])
            for item in step.get("bring") or []
        ]
        steps.append(step)

    address_documents = [
        doc for doc in content["documents"].values() if "address" in (doc.get("proves") or [])
    ]

    provenances = [decorate(node["provenance"], today) for _, node in content_mod.provenance_nodes(content)]
    dates = sorted(p["verified_on"] for p in provenances)
    unconfirmed = [p for p in provenances if p["confidence"] != "confirmed"]

    # The handout names specific steps and offices. If content is renamed and
    # these are not, the sheet would quietly lose half its contents, so say so.
    missing_steps = [s for s in PRINT_STEPS if s not in content["steps"]]
    missing_places = [a for a in PRINT_PLACES if a not in agencies]
    if missing_steps or missing_places:
        raise SystemExit(
            "The printed sheet refers to content that no longer exists: "
            + ", ".join(missing_steps + missing_places)
            + ". Update PRINT_STEPS and PRINT_PLACES in src/build.py."
        )

    # The handout lists the steps most people need, in order. Referral pages are
    # left off: they are for one person at a desk, not for a sheet on a wall.
    sheet_steps = [
        {"title": s["title"], "first_line": sentences(s["plain_summary"])[0]}
        for s in steps
        if not s.get("referral")
    ]

    key_steps = [
        {"short": PRINT_STEPS[s["id"]], "what_to_say": s["what_to_say"]}
        for s in steps
        if s["id"] in PRINT_STEPS and s.get("what_to_say")
    ]

    return {
        "steps": steps,
        "agencies": agencies,
        "documents": list(content["documents"].values()),
        "not_accepted": content["not_accepted"],
        "address_documents": address_documents,
        "states": content["states"],
        "questions": content["tree"]["questions"],
        "tree_json": json_for_script(
            {"questions": content["tree"]["questions"], "plan": content["tree"]["plan"]}
        ),
        "fact_count": len(provenances),
        "unconfirmed": len(unconfirmed),
        "draft": bool(unconfirmed),
        "newest_check": dates[-1],
        "oldest_check": dates[0],
        "key_steps": key_steps,
        "sheet_steps": sheet_steps,
        "places": [agencies[a] for a in PRINT_PLACES],
        "site_url": SITE_URL,
        "build_date": str(today),
    }


def build(root: pathlib.Path = content_mod.ROOT, today: datetime.date | None = None) -> dict:
    today = today or datetime.date.today()
    root = pathlib.Path(root)

    problems = validate.run(root=root, today=today)
    errors = [p for p in problems if p.level == "error"]
    for problem in problems:
        print(problem)
    if errors:
        raise SystemExit(f"\n{len(errors)} errors. Nothing was built.")

    content = content_mod.load(root)
    context = prepare(content, today)
    context["css"] = Markup((root / "static" / "style.css").read_text(encoding="utf-8"))
    context["js"] = Markup((root / "static" / "app.js").read_text(encoding="utf-8"))
    context["plan_js"] = Markup((root / "static" / "plan.js").read_text(encoding="utf-8"))

    env = Environment(
        loader=FileSystemLoader(str(root / "templates")),
        # The templates end in .j2, so name them explicitly or escaping is off.
        autoescape=select_autoescape(enabled_extensions=("html", "j2"), default_for_string=True),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Render everything before deleting anything, so a template error leaves the
    # last good site in place rather than an empty directory.
    pages = {
        name: env.get_template(template).render(**context)
        for name, template in (("index.html", "index.html.j2"), ("print.html", "print.html.j2"))
    }
    pages["sw.js"] = (root / "static" / "sw.js").read_text(encoding="utf-8").replace(
        "__VERSION__", today.strftime("%Y%m%d")
    )

    out = root / "public"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    written = {}
    for name, text in pages.items():
        (out / name).write_text(text, encoding="utf-8")
        written[name] = len(text.encode("utf-8"))

    # GitHub Pages would otherwise run the output through Jekyll.
    (out / ".nojekyll").write_text("", encoding="utf-8")

    print()
    for name, size in written.items():
        print(f"{name:12} {size / 1024:6.1f} KB")

    visible = len(visible_words(pages["print.html"]))
    if visible > PRINT_SHEET_WORD_LIMIT:
        print()
        print(
            f'Warning: the handout is {visible} words. Over about '
            f'{PRINT_SHEET_WORD_LIMIT} it stops fitting on one page. Check it on paper.'
        )

    first_load = written["index.html"]
    print(f"\nfirst load    {first_load / 1024:6.1f} KB of {PAGE_WEIGHT_LIMIT_BYTES / 1024:.0f} KB budget")
    if first_load > PAGE_WEIGHT_LIMIT_BYTES:
        raise SystemExit("The page is over the weight budget. Cut something.")

    if context["draft"]:
        print(
            f"\nDraft build. {context['unconfirmed']} of {context['fact_count']} facts are not "
            "confirmed twice, so the pages carry a draft banner."
        )
    return written


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build the guide.")
    parser.add_argument("--root", default=str(content_mod.ROOT))
    args = parser.parse_args(argv)
    build(root=pathlib.Path(args.root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
