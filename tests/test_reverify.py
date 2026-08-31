import datetime

import yaml

from src import reverify


def test_it_lists_every_unconfirmed_fact(repo, today):
    rows = reverify.call_list(root=repo, older_than=90, today=today)
    assert rows, "the seed content is desk checked, so everything should be listed"
    assert all(row["ask"] for row in rows)


def test_agency_rows_carry_a_number_to_dial(repo, today):
    rows = reverify.call_list(root=repo, older_than=90, today=today)
    agency_rows = [r for r in rows if r["where"].startswith("agencies.yaml")]
    assert agency_rows
    assert all(r["phones"] for r in agency_rows)


def test_confirmed_and_fresh_facts_drop_off_the_list(copied_repo, today):
    """Mark everything confirmed and dated today, and the list should empty out."""
    for path in list((copied_repo / "content").rglob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        text = text.replace("confidence: desk", "confidence: confirmed")
        text = text.replace("verified_on: 2026-08-30", f"verified_on: {today}")
        path.write_text(text, encoding="utf-8")

    rows = reverify.call_list(root=copied_repo, older_than=90, today=today)
    assert rows == []


def test_an_old_fact_comes_back_even_when_confirmed(copied_repo, today):
    path = copied_repo / "content" / "steps" / "state-id.yaml"
    step = yaml.safe_load(path.read_text(encoding="utf-8"))
    step["provenance"]["confidence"] = "confirmed"
    step["provenance"]["verified_on"] = today - datetime.timedelta(days=120)
    path.write_text(yaml.safe_dump(step, sort_keys=False), encoding="utf-8")

    rows = reverify.call_list(root=copied_repo, older_than=90, today=today)
    hit = [r for r in rows if r["where"].endswith("state-id.yaml")]
    assert hit and "120 days old" in hit[0]["reason"]
