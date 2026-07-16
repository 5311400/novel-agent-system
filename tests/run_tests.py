"""
Tests for tools/validate.py

Usage:
    python -m unittest tests.run_tests
    python tests/run_tests.py
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# Add repo root to path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import validate


class TestValidateCrossReferences(unittest.TestCase):

    def setUp(self):
        """Create a temporary project structure for each test."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.tmpdir.name) / "data"
        self.world_dir = self.data_dir / "world"
        self.char_dir = self.data_dir / "characters"
        self.world_dir.mkdir(parents=True, exist_ok=True)
        self.char_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.tmpdir.cleanup()

    def _write_md(self, path, content):
        """Helper to write a .md file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.strip(), encoding="utf-8")

    def test_all_refs_resolve(self):
        """IDs defined in one file should be resolvable from another."""
        self._write_md(self.world_dir / "geography.md", """
# Geography

## [[geo:yunlan]] Yunlan Mountain
A sacred mountain in the east.

## [[geo:qinghai]] Qinghai Lake
The largest lake in the realm.
""")
        self._write_md(self.world_dir / "factions.md", """
# Factions

## [[faction:qingyun]] Qingyun Sect
Located at [[geo:yunlan]].
Allies with [[faction:molian]].
""")
        self._write_md(self.world_dir / "power-system.md", """
## [[faction:molian]] Molian Sect
A demon sect based at [[geo:qinghai]].
""")
        issues = validate.validate_cross_references(self.tmpdir.name)
        self.assertTrue(any("resolve correctly" in i for i in issues),
                        f"Expected OK, got: {issues}")

    def test_broken_ref_detected(self):
        """A [[type:id]] with no matching definition should be flagged."""
        self._write_md(self.world_dir / "factions.md", """
# Factions

## [[faction:qingyun]] Qingyun Sect
Located at [[geo:does-not-exist]].
""")
        issues = validate.validate_cross_references(self.tmpdir.name)
        has_broken = any("BROKEN" in i for i in issues)
        self.assertTrue(has_broken, f"Expected BROKEN, got: {issues}")

    def test_empty_dir_no_error(self):
        """An empty data/ directory should report no broken refs."""
        issues = validate.validate_cross_references(self.tmpdir.name)
        self.assertTrue(any("clean" in i.lower() for i in issues),
                        f"Expected clean message, got: {issues}")

    def test_self_ref_resolves(self):
        """A file that defines [[type:id]] and also references it should pass."""
        self._write_md(self.world_dir / "factions.md", """
## [[faction:qingyun]] Qingyun Sect
Located at [[geo:yunlan]].

## [[geo:yunlan]] Yunlan Mountain
The sacred mountain.
""")
        issues = validate.validate_cross_references(self.tmpdir.name)
        self.assertTrue(any("resolve correctly" in i for i in issues),
                        f"Expected OK, got: {issues}")

    def test_multiple_broken_refs(self):
        """Multiple broken refs should all be reported."""
        self._write_md(self.world_dir / "factions.md", """
## [[faction:qingyun]] Qingyun Sect
Located at [[geo:a]] and [[geo:b]] and [[geo:c]].
""")
        issues = validate.validate_cross_references(self.tmpdir.name)
        # Check header reports 3 broken refs
        header = [i for i in issues if i.startswith("FOUND")]
        self.assertEqual(len(header), 1)
        self.assertIn("FOUND 3", header[0])
        # Check each broken ref is listed
        ref_lines = [i for i in issues if "NOT FOUND" in i]
        self.assertEqual(len(ref_lines), 3)


class TestValidateIndex(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.tmpdir.name) / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.tmpdir.cleanup()

    def _write_index(self, content):
        (self.data_dir / "INDEX.md").write_text(content.strip(), encoding="utf-8")

    def test_valid_index(self):
        self._write_index("""
# INDEX.md
## Current Versions
- GV: 0
- WV: 1
- CV: 2
- CH-V: 3
""")
        issues = validate.validate_index_md(self.tmpdir.name)
        self.assertTrue(any("valid" in i for i in issues),
                        f"Expected valid, got: {issues}")

    def test_missing_version_field(self):
        self._write_index("""
# INDEX.md
- GV: 0
""")
        issues = validate.validate_index_md(self.tmpdir.name)
        has_warning = any("missing" in i.lower() for i in issues)
        self.assertTrue(has_warning, f"Expected missing warnings, got: {issues}")

    def test_no_index_file(self):
        """INDEX.md not existing should not crash."""
        issues = validate.validate_index_md(self.tmpdir.name)
        self.assertTrue(any("not found" in i for i in issues))


if __name__ == "__main__":
    unittest.main()
