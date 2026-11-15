import hashlib
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from footage_studio import samples

_SAMPLES = None


def sample_template():
    """Sample footage is slow to make, so it is generated once per test run."""
    global _SAMPLES
    if _SAMPLES is None:
        _SAMPLES = Path(tempfile.mkdtemp(prefix="fs-samples-"))
        samples.make_samples(_SAMPLES / "proj", count=9)
    return _SAMPLES / "proj"


def snapshot(root):
    """Every directory and every file's bytes under root."""
    state = {}
    for path in sorted(Path(root).rglob("*")):
        rel = path.relative_to(root).as_posix()
        state[rel] = "dir" if path.is_dir() else hashlib.sha256(path.read_bytes()).hexdigest()
    return state


class ProjectCase(unittest.TestCase):
    """A fresh copy of the sample project and an isolated app data folder."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fs-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.root = self.tmp / "Sharma x Patel"
        shutil.copytree(sample_template(), self.root)
        self.home = self.tmp / "home"
        previous = os.environ.get("FOOTAGE_STUDIO_HOME")
        os.environ["FOOTAGE_STUDIO_HOME"] = str(self.home)
        self.addCleanup(self._restore_home, previous)

    @staticmethod
    def _restore_home(previous):
        if previous is None:
            os.environ.pop("FOOTAGE_STUDIO_HOME", None)
        else:
            os.environ["FOOTAGE_STUDIO_HOME"] = previous


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self._payload
