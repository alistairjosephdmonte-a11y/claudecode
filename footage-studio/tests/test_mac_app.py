"""The Mac app bundle. Its launcher is a shell script, so it can be exercised
here; this is NOT a substitute for launching it on a real Mac."""

import importlib.util
import os
import plistlib
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
import urllib.request
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_mac_app", PROJECT / "scripts" / "build_mac_app.py")
build_mac_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_mac_app)


@unittest.skipIf(os.name == "nt", "needs a POSIX shell")
class MacApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="fs-app-"))
        cls.app, cls.archive = build_mac_app.build(cls.tmp / "dist")
        cls.launcher = cls.app / "Contents" / "MacOS" / "footage-studio"

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_bundle_layout(self):
        with open(self.app / "Contents" / "Info.plist", "rb") as f:
            info = plistlib.load(f)
        self.assertEqual(info["CFBundleExecutable"], self.launcher.name)
        self.assertEqual(info["CFBundlePackageType"], "APPL")
        self.assertTrue(os.access(self.launcher, os.X_OK))
        self.assertTrue((self.app / "Contents" / "Resources" / "footage_studio" / "web" / "app.html").is_file())
        self.assertEqual(subprocess.run(["bash", "-n", str(self.launcher)]).returncode, 0)

    def test_launcher_starts_the_app_from_any_directory(self):
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        env = dict(os.environ, FOOTAGE_STUDIO_HOME=str(self.tmp / "home"))
        env.pop("PYTHONPATH", None)
        process = subprocess.Popen(
            [str(self.launcher), "app", "--no-browser", "--port", str(port)],
            cwd="/", env=env, stdout=subprocess.PIPE, text=True)
        try:
            line = process.stdout.readline()
            self.assertIn(f"127.0.0.1:{port}", line)
            opener = urllib.request.build_opener(
                urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor())
            with opener.open(line.split()[-1], timeout=10) as response:
                self.assertIn("Footage Studio", response.read().decode())
        finally:
            process.terminate()
            process.wait(timeout=10)
            process.stdout.close()
        self.assertFalse(list(self.app.rglob("__pycache__")))  # the bundle is not modified by running

    def test_launcher_explains_missing_ffmpeg(self):
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir(exist_ok=True)
        if not (bin_dir / "python3").exists():
            (bin_dir / "python3").symlink_to(sys.executable)
        result = subprocess.run(["/bin/bash", str(self.launcher)], env={"PATH": str(bin_dir)},
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 1)
        self.assertIn("brew install ffmpeg", result.stderr)

    def test_zip_keeps_the_launcher_executable(self):
        import zipfile
        with zipfile.ZipFile(self.archive) as z:
            info = z.getinfo("Footage Studio.app/Contents/MacOS/footage-studio")
            self.assertTrue((info.external_attr >> 16) & 0o111)


if __name__ == "__main__":
    unittest.main()
