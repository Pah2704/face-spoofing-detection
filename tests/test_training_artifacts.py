from __future__ import annotations

from pathlib import Path
import tarfile
import tempfile
import unittest

from face_spoofing.training.artifacts import (
    source_tree_sha256,
    write_source_tree_snapshot,
)


class SourceSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "src" / "package").mkdir(parents=True)
        (self.root / "configs" / "models").mkdir(parents=True)
        (self.root / "src" / "package" / "module.py").write_text(
            "VALUE = 1\n", encoding="utf-8"
        )
        (self.root / "configs" / "models" / "model.yaml").write_text(
            "name: test\n", encoding="utf-8"
        )
        (self.root / "pyproject.toml").write_text(
            "[project]\nname = 'test'\n", encoding="utf-8"
        )

    def test_snapshot_contains_exact_hashed_scope(self) -> None:
        run_dir = self.root / "run"
        expected = source_tree_sha256(self.root)

        metadata = write_source_tree_snapshot(
            run_dir,
            self.root,
            expected_sha256=expected,
        )

        self.assertEqual(metadata["source_tree_sha256"], expected)
        self.assertEqual(metadata["files"], 3)
        snapshot = run_dir / "source" / "source_tree.tar"
        with tarfile.open(snapshot, mode="r") as archive:
            self.assertEqual(
                archive.getnames(),
                [
                    "configs/models/model.yaml",
                    "pyproject.toml",
                    "src/package/module.py",
                ],
            )
            self.assertTrue(all(item.mtime == 0 for item in archive.getmembers()))

    def test_expected_hash_mismatch_is_rejected(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "before snapshot"):
            write_source_tree_snapshot(
                self.root / "run",
                self.root,
                expected_sha256="0" * 64,
            )


if __name__ == "__main__":
    unittest.main()
