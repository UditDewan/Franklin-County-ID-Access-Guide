"""Drives the built page the way a person would, in a real DOM.

Needs node with jsdom available. Skipped when it is not installed, so a plain
`pytest` run still works on a laptop; CI installs it.
"""

import json
import shutil
import subprocess
import textwrap

import pytest

from src import build as build_mod

NODE = shutil.which("node")

DRIVER = textwrap.dedent(
    """
    const fs = require("fs");
    const { JSDOM } = require("jsdom");

    const dom = new JSDOM(fs.readFileSync(process.argv[1], "utf8"), {
      runScripts: "dangerously",
      url: "https://example.org/",
    });
    const d = dom.window.document;
    const picks = JSON.parse(process.argv[2]);

    const out = {
      errors: [],
      toolHidden: d.getElementById("tool").hidden,
      fallbackHidden: d.getElementById("fallback").hidden,
      firstQuestion: d.querySelector("#quiz legend").textContent,
      progress: d.querySelector("#quiz .progress").textContent,
    };
    dom.window.addEventListener("error", (e) => out.errors.push(String(e.error)));

    picks.forEach(function (index) {
      const buttons = d.querySelectorAll("#quiz .choice");
      if (buttons.length) buttons[index].click();
    });

    out.steps = [...d.querySelectorAll("#results .step")].map((n) => n.id.replace("step-", ""));
    out.allVisible = [...d.querySelectorAll("#results .step")].every((n) => !n.hidden);
    out.quizHidden = d.getElementById("quiz").hidden;
    out.summary = d.querySelector("#results .lede").textContent;

    const startOver = [...d.querySelectorAll("#results button")]
      .find((b) => b.textContent === "Start over");
    startOver.click();
    out.afterReset = {
      progress: d.querySelector("#quiz .progress").textContent,
      cardsHome: d.querySelectorAll("#all-steps .step").length,
      resultsEmpty: d.getElementById("results").children.length === 0,
    };

    console.log(JSON.stringify(out));
    """
)


def jsdom_available():
    if NODE is None:
        return False
    probe = subprocess.run(
        [NODE, "-e", "require.resolve('jsdom')"], capture_output=True, text=True
    )
    return probe.returncode == 0


needs_jsdom = pytest.mark.skipif(not jsdom_available(), reason="node with jsdom is not installed")


@pytest.fixture(scope="module")
def built(tmp_path_factory, repo, today):
    root = tmp_path_factory.mktemp("flow")
    for name in ("content", "templates", "static"):
        shutil.copytree(repo / name, root / name)
    build_mod.build(root=root, today=today)
    return root / "public" / "index.html"


def drive(page, picks):
    result = subprocess.run(
        [NODE, "-e", DRIVER, "--", str(page), json.dumps(picks)],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


@needs_jsdom
def test_the_flow_starts_and_swaps_out_the_fallback(built):
    # 18 or over, has ID, born in Ohio, has the certificate, has the card,
    # has an address, no name change.
    out = drive(built, [1, 0, 0, 0, 0, 0, 0])

    assert out["errors"] == []
    assert out["toolHidden"] is False
    assert out["fallbackHidden"] is True, "the no-script list should be hidden once JS runs"
    assert out["progress"] == "Question 1 of 7"
    assert out["firstQuestion"] == "Are you under 18?"


@needs_jsdom
def test_the_easiest_case_is_two_steps(built):
    out = drive(built, [1, 0, 0, 0, 0, 0, 0])
    assert out["steps"] == ["address-proof", "state-id"]
    assert out["allVisible"] is True
    assert out["quizHidden"] is True


@needs_jsdom
def test_the_hardest_case_walks_the_whole_chain(built):
    # 18 or over, no ID, born out of state, no certificate, no number,
    # nowhere to get mail, name changed.
    out = drive(built, [1, 1, 1, 1, 2, 1, 1])
    assert out["steps"] == [
        "mailing-address",
        "birth-cert-other-state",
        "social-security-card",
        "name-change-papers",
        "fee-help",
        "address-proof",
        "state-id",
    ]
    assert "7 things to do" in out["summary"]


@needs_jsdom
def test_answering_under_18_stops_everything_else(built):
    out = drive(built, [0, 0, 0, 0, 0, 0, 0])
    assert out["steps"] == ["under-18"], "an under-18 answer must go straight to a referral"
    assert "One thing to do" in out["summary"]


@needs_jsdom
def test_start_over_puts_the_page_back(built):
    out = drive(built, [1, 1, 1, 1, 2, 1, 1])
    assert out["afterReset"]["progress"] == "Question 1 of 7"
    assert out["afterReset"]["cardsHome"] == 10, "every step card should return to its home"
    assert out["afterReset"]["resultsEmpty"] is True


BREAKER = textwrap.dedent(
    """
    const fs = require("fs");
    const { JSDOM } = require("jsdom");

    let html = fs.readFileSync(process.argv[1], "utf8");
    // Break the flow the way a bad edit would.
    html = html.replace(
      "quiz.appendChild(progress);",
      "quiz.appendChild(progress); throw new Error('broken');"
    );
    const dom = new JSDOM(html, { runScripts: "dangerously", url: "https://example.org/" });
    const d = dom.window.document;
    console.log(JSON.stringify({
      toolHidden: d.getElementById("tool").hidden,
      fallbackVisible: !d.getElementById("fallback").hidden,
      readableCards: [...d.querySelectorAll("#all-steps .step")].filter((n) => !n.hidden).length,
    }));
    """
)


@needs_jsdom
def test_a_broken_script_leaves_a_readable_page(built):
    """If the flow throws, the reader must keep the plain list, not a blank page."""
    result = subprocess.run(
        [NODE, "-e", BREAKER, "--", str(built)], capture_output=True, text=True, check=True
    )
    out = json.loads(result.stdout)
    assert out["toolHidden"] is True
    assert out["fallbackVisible"] is True
    assert out["readableCards"] == 10, "every step must stay readable when the script dies"
