"""The build, and the promises the page makes about itself."""

import json
import re
import shutil

import pytest

from src import build as build_mod
from src import content as content_mod


@pytest.fixture(scope="module")
def site(tmp_path_factory, repo, today):
    root = tmp_path_factory.mktemp("site")
    for name in ("content", "templates", "static"):
        shutil.copytree(repo / name, root / name)
    build_mod.build(root=root, today=today)
    return root / "public"


def page(site):
    return (site / "index.html").read_text(encoding="utf-8")


def test_it_writes_the_files(site):
    assert (site / "index.html").exists()
    assert (site / "print.html").exists()
    assert (site / "sw.js").exists()
    assert (site / ".nojekyll").exists()


def test_page_fits_the_weight_budget(site):
    size = (site / "index.html").stat().st_size
    assert size <= build_mod.PAGE_WEIGHT_LIMIT_BYTES, f"{size} bytes is over budget"


def test_nothing_loads_from_anywhere_else(site):
    """The whole privacy promise in one test.

    Links out to agency websites are fine, a person clicks those on purpose.
    What must not exist is anything the page fetches by itself.
    """
    html = page(site)
    banned = [
        (r"<script[^>]+src=", "an external script"),
        (r"<link[^>]+rel=[\"']?stylesheet", "an external stylesheet"),
        (r"<img[^>]+src=[\"']https?:", "an image from another site"),
        (r"<iframe", "an iframe"),
        (r"@import", "a CSS import"),
        (r"url\(\s*[\"']?https?:", "a CSS url pointing off site"),
        (r"\bfetch\s*\(", "a fetch call"),
        (r"XMLHttpRequest", "an XHR call"),
        (r"navigator\.sendBeacon", "a beacon"),
        (r"googletagmanager|google-analytics|gtag\(|plausible|matomo", "analytics"),
        (r"localStorage|sessionStorage|document\.cookie", "storage"),
        (r"fonts\.(googleapis|gstatic)", "a web font"),
    ]
    for pattern, description in banned:
        assert not re.search(pattern, html, re.I), f"the page contains {description}"


def test_the_service_worker_only_caches_this_site(site):
    worker = (site / "sw.js").read_text(encoding="utf-8")
    assert "__VERSION__" not in worker, "the cache name was not stamped"
    assert not re.search(r"https?://", worker), "the worker mentions another site"


def test_it_works_with_javascript_switched_off(site):
    """With no JS the fallback list is visible and holds every step."""
    html = page(site)
    fallback = html.index('id="fallback"')
    assert "hidden" not in html[fallback : fallback + 30], "the fallback starts hidden"
    assert 'id="tool" hidden' in html, "the question flow must start hidden"

    content = content_mod.load(site.parent)
    for step_id in content["steps"]:
        assert f'id="step-{step_id}"' in html, f"{step_id} is missing from the page"


def test_every_step_says_when_it_was_checked(site):
    html = page(site)
    assert html.count("Checked 2026-") == len(content_mod.load(site.parent)["steps"])


def test_draft_banner_appears_while_facts_are_unconfirmed(site):
    assert "Draft. Do not hand this out yet." in page(site)
    assert "Draft." in (site / "print.html").read_text(encoding="utf-8")


def test_the_printed_sheet_has_the_phone_numbers(site):
    sheet = (site / "print.html").read_text(encoding="utf-8")
    for number in ("614-274-7000", "614-645-7331"):
        assert number in sheet


def test_embedded_tree_is_valid_json(site):
    html = page(site)
    blob = re.search(r'id="tree-data">(.*?)</script>', html, re.S).group(1)
    data = json.loads(blob)
    assert all(isinstance(o["label"], str) for q in data["questions"] for o in q["options"])


def test_build_refuses_broken_content(copied_repo, today):
    step = copied_repo / "content" / "steps" / "state-id.yaml"
    step.write_text(step.read_text(encoding="utf-8").replace("terminal: true", ""), encoding="utf-8")
    with pytest.raises(SystemExit):
        build_mod.build(root=copied_repo, today=today)
    assert not (copied_repo / "public").exists(), "a failed build must write nothing"


def test_no_duplicate_element_ids(site):
    """A step listed twice would render two cards sharing one id."""
    ids = re.findall(r'\bid="([^"]+)"', page(site))
    duplicates = {i for i in ids if ids.count(i) > 1}
    assert not duplicates, f"repeated ids in the page: {sorted(duplicates)}"


def test_every_phone_becomes_a_working_dial_link(site):
    html = page(site)
    for link in re.findall(r'href="tel:([^"]*)"', html):
        assert re.fullmatch(r"\d{10}", link), f"tel:{link} is not dialable"


def test_a_failed_render_leaves_the_previous_site_alone(copied_repo, today):
    build_mod.build(root=copied_repo, today=today)
    before = (copied_repo / "public" / "index.html").read_text(encoding="utf-8")

    template = copied_repo / "templates" / "index.html.j2"
    template.write_text(template.read_text(encoding="utf-8") + "\n{% for %}", encoding="utf-8")
    with pytest.raises(Exception):
        build_mod.build(root=copied_repo, today=today)

    assert (copied_repo / "public" / "index.html").read_text(encoding="utf-8") == before


def test_the_handout_word_count_ignores_the_stylesheet(site):
    """The overflow warning once counted the inlined CSS and always fired."""
    html = (site / "print.html").read_text(encoding="utf-8")
    words = build_mod.visible_words(html)
    assert "flex" not in words and "var(--line)" not in words
    assert len(words) < len(html.split()) / 2


def test_the_handout_still_fits_one_page(site):
    words = build_mod.visible_words((site / "print.html").read_text(encoding="utf-8"))
    assert len(words) <= build_mod.PRINT_SHEET_WORD_LIMIT, (
        f"the sheet is {len(words)} words and will spill onto a second page"
    )


def test_the_handout_steps_come_from_the_content(site):
    """The sheet used to carry its own hand-written copy of the steps."""
    sheet = (site / "print.html").read_text(encoding="utf-8")
    content = content_mod.load(site.parent)
    for step_id in ("mailing-address", "address-proof", "state-id"):
        assert content["steps"][step_id]["title"] in sheet
    for referral in ("under-18", "unclear-birthplace"):
        assert content["steps"][referral]["title"] not in sheet
