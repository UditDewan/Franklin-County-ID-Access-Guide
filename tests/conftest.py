import datetime
import pathlib
import shutil
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# The date the seed content was checked. Tests pin it so they do not start
# failing on their own three months from now.
TODAY = datetime.date(2026, 8, 31)


@pytest.fixture(scope="session")
def repo():
    return REPO


@pytest.fixture(scope="session")
def today():
    return TODAY


@pytest.fixture
def copied_repo(tmp_path):
    """A throwaway copy of the repo, for tests that break the content on purpose."""
    for name in ("content", "templates", "static"):
        shutil.copytree(REPO / name, tmp_path / name)
    return tmp_path
