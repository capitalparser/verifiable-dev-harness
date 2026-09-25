"""Independent synthetic fixtures for AC-900..903; no model/product execution."""
from __future__ import annotations

import ast
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from verification_contract import ContractError, load_json, local_file, validate_map, validate_receipt

NOW = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)
COMMIT = "a" * 40


def fixture(root: Path) -> tuple[dict, dict, str]:
    (root / "src").mkdir()
    (root / "src/main.py").write_text("print('synthetic fixture, not product E2E')\n")
    (root / "contracts.md").write_text("\n".join("## " + v for v in ["BR-1", "WF-1", "CMP-1", "DF-1", "AC-1"]))
    (root / ".gitignore").write_text("artifacts/verification/\n__pycache__/\n")
    artifact = root / "artifacts/verification/run-1/test.log"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(b"Synthetic evidence: expected path asserted.\n")
    checks = [{"id": name, "kind": kind, "argv": ["python", "test.py", name],
               "expected": "fixture behaves as specified", "covers": ["AC-1"], "evidence_types": ["log"]}
              for name, kind in [("positive", "positive"), ("negative", "negative")]]
    feature = {"id": "feature-1", "owner": "maintainer", "symptoms": ["wrong output"],
               "entrypoints": [{"path": "src/main.py", "navigate": "Run the synthetic CLI"}],
               "refs": ["contracts.md#" + v for v in ["BR-1", "WF-1", "CMP-1", "DF-1", "AC-1"]],
               "checks": checks}
    data = {"version": 1, "features": [feature]}
    raw = json.dumps(data).encode()
    (root / "map.json").write_bytes(raw)
    map_hash = hashlib.sha256(raw).hexdigest()
    receipt = {"version": 1, "feature_id": "feature-1", "run_id": "run-1",
               "commit_sha": COMMIT, "map_sha256": map_hash,
               "producer": {"agent_id": "verifier-1", "adapter": "synthetic"},
               "environment": {"os": "synthetic", "runtime": "fixture"},
               "started_at": "2026-09-25T10:00:00Z", "finished_at": "2026-09-25T11:00:00Z",
               "results": [{"check_id": c["id"], "argv": c["argv"], "status": "passed", "exit_code": 0,
                            "artifacts": [{"path": "artifacts/verification/run-1/test.log", "type": "log",
                                           "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest()}]}
                           for c in checks]}
    return data, receipt, map_hash


class Base(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data, self.receipt, self.map_hash = fixture(self.root)

    def verify(self, receipt=None):
        return validate_receipt(self.receipt if receipt is None else receipt,
                                self.data["features"][0], self.root,
                                expected_commit=COMMIT, expected_run="run-1",
                                map_hash=self.map_hash, now=NOW)


class ValidTests(Base):
    def test_map(self):
        self.assertEqual(list(validate_map(self.data, self.root)), ["feature-1"])

    def test_receipt(self):
        self.assertIsNone(self.verify())

    def test_declared_command_is_not_executed(self):
        sentinel = self.root / "MUST_NOT_EXIST"
        command = [sys.executable, "-c", f"open({str(sentinel)!r}, 'w').write('bad')"]
        self.data["features"][0]["checks"][0]["argv"] = command
        self.receipt["results"][0]["argv"] = command
        validate_map(self.data, self.root)
        self.verify()
        self.assertFalse(sentinel.exists())

    def test_shipped_map(self):
        result = validate_map(load_json(ROOT / "verification/feature-map.json"), ROOT)
        self.assertIn("verification-gate", result)


class RejectionTests(Base):
    def test_duplicate_feature(self):
        self.data["features"].append(copy.deepcopy(self.data["features"][0]))
        with self.assertRaisesRegex(ContractError, "duplicate_feature"):
            validate_map(self.data, self.root)

    def test_uncovered_acceptance(self):
        with (self.root / "contracts.md").open("a") as stream:
            stream.write("\n## AC-2\n")
        self.data["features"][0]["refs"].append("contracts.md#AC-2")
        with self.assertRaisesRegex(ContractError, "uncovered_acceptance"):
            validate_map(self.data, self.root)

    def test_duplicate_artifact(self):
        result = self.receipt["results"][0]
        result["artifacts"].append(copy.deepcopy(result["artifacts"][0]))
        with self.assertRaisesRegex(ContractError, "duplicate_artifact"):
            self.verify()

    def test_unknown_map_field(self):
        self.data["silently_skip"] = True
        with self.assertRaisesRegex(ContractError, "missing_or_unknown_fields"):
            validate_map(self.data, self.root)

    def test_missing_result_is_not_pass(self):
        self.receipt["results"].pop()
        with self.assertRaisesRegex(ContractError, "incomplete_check_coverage"):
            self.verify()

    def test_receipt_does_not_change_source(self):
        before = (self.root / "src/main.py").read_bytes()
        self.verify()
        self.assertEqual((self.root / "src/main.py").read_bytes(), before)

    def test_modified_artifact(self):
        (self.root / "artifacts/verification/run-1/test.log").write_text("different")
        with self.assertRaisesRegex(ContractError, "artifact_digest_mismatch"):
            self.verify()

    def test_empty_artifact_even_with_matching_hash(self):
        (self.root / "artifacts/verification/run-1/test.log").write_bytes(b"")
        for result in self.receipt["results"]:
            result["artifacts"][0]["sha256"] = hashlib.sha256(b"").hexdigest()
        with self.assertRaisesRegex(ContractError, "empty_artifact"):
            self.verify()

    def test_missing_artifact(self):
        (self.root / "artifacts/verification/run-1/test.log").unlink()
        with self.assertRaises(OSError):
            self.verify()

    def test_duplicate_json_keys(self):
        path = self.root / "duplicate.json"
        path.write_text('{"version":1,"version":1}')
        with self.assertRaisesRegex(ContractError, "duplicate_json_key"):
            load_json(path)

    def test_nonfinite_json(self):
        path = self.root / "nan.json"
        path.write_text('{"version":NaN}')
        with self.assertRaisesRegex(ContractError, "nonfinite_json_number"):
            load_json(path)

    def test_oversized_json(self):
        path = self.root / "large.json"
        path.write_bytes(b" " * (2 * 1024 * 1024 + 1))
        with self.assertRaisesRegex(ContractError, "json_too_large"):
            load_json(path)

    def test_unsafe_paths(self):
        for path in ["../contracts.md", "/etc/passwd", "C:/secret", "src/../contracts.md", "src\\main.py", "src//main.py"]:
            with self.subTest(path=path), self.assertRaises(ContractError):
                local_file(self.root, path)

    def test_symlink(self):
        link = self.root / "linked.md"
        try:
            link.symlink_to(self.root / "contracts.md")
        except OSError:
            self.skipTest("OS does not permit unprivileged symlinks")
        with self.assertRaisesRegex(ContractError, "symlink_forbidden"):
            local_file(self.root, "linked.md")

    def test_json_root_types(self):
        for value in [None, False, 0, 1.0, "data", [], [None]]:
            with self.subTest(value=value), self.assertRaises(ContractError):
                validate_map(value, self.root)
            with self.subTest(receipt=value), self.assertRaises(ContractError):
                self.verify(value) if value is not None else validate_receipt(
                    None, self.data["features"][0], self.root, expected_commit=COMMIT,
                    expected_run="run-1", map_hash=self.map_hash, now=NOW)


def replace(data, path, value):
    node = data
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = copy.deepcopy(value)


# Each case creates a separately reported unittest, rather than hiding counts in a loop.
MAP_CASES = {
    "boolean_version": (["version"], True),
    "unknown_version": (["version"], 2),
    "no_features": (["features"], []),
    "missing_navigation": (["features", 0, "entrypoints", 0, "navigate"], ""),
    "missing_source": (["features", 0, "entrypoints", 0, "path"], "missing.py"),
    "no_negative": (["features", 0, "checks", 1, "kind"], "regression"),
    "duplicate_check": (["features", 0, "checks", 1, "id"], "positive"),
    "unknown_kind": (["features", 0, "checks", 1, "kind"], "magic"),
    "string_command": (["features", 0, "checks", 0, "argv"], "python test.py"),
    "empty_oracle": (["features", 0, "checks", 0, "expected"], ""),
    "bad_coverage": (["features", 0, "checks", 0, "covers"], ["AC-999"]),
    "undefined_reference": (["features", 0, "refs", 4], "contracts.md#AC-9"),
    "missing_reference_kind": (["features", 0, "refs", 3], "contracts.md#AC-1"),
    "unknown_evidence_type": (["features", 0, "checks", 0, "evidence_types"], ["faith"]),
    "invalid_feature_id": (["features", 0, "id"], "../escape"),
}
RECEIPT_CASES = {
    "wrong_commit": (["commit_sha"], "b" * 40),
    "wrong_map": (["map_sha256"], "b" * 64),
    "wrong_run": (["run_id"], "old-run"),
    "wrong_feature": (["feature_id"], "different"),
    "no_results": (["results"], []),
    "duplicate_result": (["results", 1, "check_id"], "positive"),
    "unexpected_result": (["results", 1, "check_id"], "unknown"),
    "not_run": (["results", 0, "status"], "not_run"),
    "failed": (["results", 0, "status"], "failed"),
    "error": (["results", 0, "status"], "error"),
    "boolean_exit": (["results", 0, "exit_code"], False),
    "nonzero_exit": (["results", 0, "exit_code"], 1),
    "string_exit": (["results", 0, "exit_code"], "0"),
    "command_drift": (["results", 0, "argv"], ["echo", "passed"]),
    "no_artifacts": (["results", 0, "artifacts"], []),
    "missing_log": (["results", 0, "artifacts", 0, "type"], "screenshot"),
    "bad_hash": (["results", 0, "artifacts", 0, "sha256"], "z" * 64),
    "other_run_path": (["results", 0, "artifacts", 0, "path"], "artifacts/verification/old/test.log"),
    "traversal": (["results", 0, "artifacts", 0, "path"], "artifacts/verification/run-1/../../../contracts.md"),
    "naive_timestamp": (["started_at"], "2026-09-25T10:00:00"),
    "reversed_time": (["started_at"], "2026-09-25T11:30:00Z"),
    "future_time": (["finished_at"], "2099-01-01T00:00:00Z"),
    "unknown_field": (["approval_granted"], True),
}


def rejection_test(surface, path, value):
    def test(self):
        data = copy.deepcopy(self.data if surface == "map" else self.receipt)
        replace(data, path, value)
        with self.assertRaises((ContractError, OSError)):
            validate_map(data, self.root) if surface == "map" else self.verify(data)
    return test


for surface, cases in [("map", MAP_CASES), ("receipt", RECEIPT_CASES)]:
    for name, (path, value) in cases.items():
        setattr(RejectionTests, f"test_{surface}_{name}", rejection_test(surface, path, value))


class ArchitectureTests(unittest.TestCase):
    def test_import_boundaries(self):
        # Repository-specific deterministic boundary, not a universal Python rule.
        allowed = {
            "verification_contract.py": {"__future__", "hashlib", "json", "re", "datetime", "pathlib", "typing"},
            "verify_contract.py": {"__future__", "argparse", "json", "os", "pathlib", "subprocess", "sys", "verification_contract"},
        }
        for name, modules in allowed.items():
            tree = ast.parse((ROOT / "tools" / name).read_text(encoding="utf-8"))
            imports = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
            imports |= {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
            self.assertLessEqual(imports, modules)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    self.assertNotIn(node.func.id, {"eval", "exec", "__import__"})


@unittest.skipUnless(shutil.which("git"), "Git is required for receipt CLI tests")
class CliTests(Base):
    def setUp(self):
        super().setUp()
        for args in [("init",), ("config", "user.name", "Contract Tests"),
                     ("config", "user.email", "tests@example.invalid"),
                     ("add", "."), ("commit", "-m", "Synthetic fixture")]:
            subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)
        self.head = subprocess.check_output(["git", "-C", str(self.root), "rev-parse", "HEAD"], text=True).strip()
        self.receipt["commit_sha"] = self.head
        # CLI uses the real clock: make valid timestamps independent of today's date.
        self.receipt["started_at"] = "2000-01-01T00:00:00Z"
        self.receipt["finished_at"] = "2000-01-01T00:00:01Z"
        self.receipt_path = self.root / "artifacts/verification/run-1/receipt.json"
        self.receipt_path.write_text(json.dumps(self.receipt))

    def run_cli(self, mode="receipt", extra=()):
        args = [sys.executable, str(ROOT / "tools/verify_contract.py"), mode,
                "--root", str(self.root), "--map", "map.json"]
        if mode == "receipt":
            args += ["--receipt", "artifacts/verification/run-1/receipt.json", "--feature", "feature-1",
                     "--run-id", "run-1", "--commit-sha", self.head]
        result = subprocess.run(args + list(extra), capture_output=True, text=True, timeout=20)
        return result.returncode, json.loads(result.stdout)

    def test_lint_not_readiness(self):
        code, result = self.run_cli("lint")
        self.assertEqual((code, result["status"]), (0, "map_valid"))
        self.assertFalse(result["merge_authorized"])

    def test_valid_cli_receipt(self):
        code, result = self.run_cli()
        self.assertEqual((code, result["status"]), (0, "evidence_valid"))
        self.assertFalse(result["execution_attested"])
        self.assertFalse(result["merge_authorized"])

    def test_dirty_workspace(self):
        (self.root / "src/main.py").write_text("changed")
        code, result = self.run_cli()
        self.assertEqual((code, result["reason"]), (1, "dirty_workspace"))

    def test_wrong_head(self):
        code, result = self.run_cli(extra=("--commit-sha", "b" * 40))
        self.assertEqual((code, result["reason"]), (1, "workspace_commit_mismatch"))

    def test_untracked_map(self):
        subprocess.run(["git", "-C", str(self.root), "rm", "--cached", "map.json"], check=True, capture_output=True)
        code, result = self.run_cli()
        self.assertEqual((code, result["reason"]), (1, "git_check_failed"))

    def test_partial_receipt(self):
        self.receipt["results"].pop()
        self.receipt_path.write_text(json.dumps(self.receipt))
        code, result = self.run_cli()
        self.assertEqual((code, result["reason"]), (1, "incomplete_check_coverage"))

    def test_malformed_json_blocks_without_traceback(self):
        self.receipt_path.write_text("{")
        code, result = self.run_cli()
        self.assertEqual((code, result["status"]), (1, "blocked"))


if __name__ == "__main__":
    unittest.main()
