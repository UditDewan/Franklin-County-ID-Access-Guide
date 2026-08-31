"""The page and the build must pick the same steps.

The question flow runs in the browser, the printed list is generated in Python.
If the two rule engines ever drift apart, somebody gets handed a list that does
not match what they were told on screen. So both are run over every possible
answer set and compared.

Needs node on PATH. Skipped if it is missing, which is why CI installs it.
"""

import json
import shutil
import subprocess

import pytest

from src import build
from src import content as content_mod

NODE = shutil.which("node")


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_javascript_and_python_agree_on_every_answer_set(repo, tmp_path):
    content = content_mod.load(repo)
    tree = content["tree"]
    answer_sets = list(content_mod.all_answer_sets(tree))
    assert len(answer_sets) > 100, "the tree got smaller, check this test still means anything"

    expected = [content_mod.plan_for(tree, answers) for answers in answer_sets]

    script = (
        "const planFor = require(process.argv[1]);\n"
        "const input = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));\n"
        "console.log(JSON.stringify(input.answer_sets.map(a => planFor(input.plan, a))));\n"
    )

    payload = {"plan": tree["plan"], "answer_sets": answer_sets}
    # Written outside the repository, so an interrupted run leaves nothing behind.
    tmp = tmp_path / "parity_input.json"
    tmp.write_text(json.dumps(payload), encoding="utf-8")
    result = subprocess.run(
        [NODE, "-e", script, "--", str(repo / "static" / "plan.js"), str(tmp)],
        capture_output=True,
        text=True,
        check=True,
    )

    actual = json.loads(result.stdout)
    assert actual == expected


def test_the_built_page_carries_the_same_rules(repo, tmp_path, today):
    """The page embeds its own copy of the plan. It must match the source.

    This builds its own copy. Reading the repository's public/ made the test
    depend on somebody having run the build first, which is true on a laptop
    and false on a clean checkout.
    """
    for name in ("content", "templates", "static"):
        shutil.copytree(repo / name, tmp_path / name)
    build.build(root=tmp_path, today=today)
    built = (tmp_path / "public" / "index.html").read_text(encoding="utf-8")
    start = built.index('id="tree-data">') + len('id="tree-data">')
    end = built.index("</script>", start)
    embedded = json.loads(built[start:end])

    tree = content_mod.load(repo)["tree"]
    assert embedded["plan"] == tree["plan"]
    assert [q["id"] for q in embedded["questions"]] == [q["id"] for q in tree["questions"]]
