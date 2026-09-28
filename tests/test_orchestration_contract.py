"""Role handoff regressions with native evidence; no LLM, dispatcher or network."""
from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import orchestration_contract as routing
import verify
import verify_receipt


class HandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.seed.cleanup)
        cls.seed_root = Path(cls.seed.name).resolve() / "repo"
        cls.seed_root.mkdir()
        (cls.seed_root / "plan.md").write_text("# PLAN-1\nFixed synthetic plan.\n", encoding="utf-8")
        (cls.seed_root / "acceptance.md").write_text("# AC-1\nExpected success.\n# AC-2\nExpected rejection.\n", encoding="utf-8")
        (cls.seed_root / "notes.md").write_text("# NOTE-1\nSynthetic handoff observations.\n", encoding="utf-8")
        cls.data = {
            "schema_version": 1, "docs_paths": ["*.md"], "risk_paths": ["manifest.json"],
            "checks": {name: {"argv": ["{python}", "-c", "pass"], "timeout_seconds": 10}
                       for name in ("smoke", "feature-check")},
            "profiles": {"docs": ["smoke"], "focused": ["smoke"], "full": ["smoke", "feature-check"]},
            "features": [{"id": "pilot", "paths": ["src/*"], "checks": ["feature-check"],
                          "symptoms": ["wrong output"], "entrypoints": ["notes.md"],
                          "journey": ["run fixed probe"], "failure_probe": "reject missing data"}]}
        (cls.seed_root / "manifest.json").write_text(json.dumps(cls.data), encoding="utf-8")
        for args in [("init", "-q"), ("config", "user.name", "Handoff Fixture"),
                     ("config", "user.email", "fixture@example.invalid"),
                     ("add", "."), ("-c", "commit.gpgsign=false", "commit", "-qm", "synthetic inputs")]:
            subprocess.run(["git", "-C", str(cls.seed_root), *args], check=True, capture_output=True)
        cls.head = verify.git(cls.seed_root, "rev-parse", "HEAD").decode().strip()
        state = verify.snapshot(cls.seed_root, cls.head)
        plan = verify.select(cls.data, state["changed_paths"], feature_ids=("pilot",))
        cls.seed_output = cls.seed_root.parent / "evidence"
        cls.receipt = verify.execute(cls.seed_root, cls.data, plan, state, cls.seed_output, "fixture-v1", "run-1")
        cls.seed_context = {
            "version": 1, "task_id": "task-1", "active_role": "planner",
            "plan": {"ref": "plan.md#PLAN-1", "sha256": hashlib.sha256((cls.seed_root / "plan.md").read_bytes()).hexdigest()},
            "source_state": state, "acceptance_refs": ["acceptance.md#AC-1", "acceptance.md#AC-2"],
            "verification": {"manifest": "manifest.json", "profile": "auto", "features": ["pilot"],
                             "run_id": "run-1", "context": "fixture-v1"},
            "review": {"implementation_session": "builder-session", "separate_session_required": True},
            "budget": {"used": 0, "limit": 2}}

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / "repo"
        self.output = self.root.parent / "evidence"
        shutil.copytree(self.seed_root, self.root)
        shutil.copytree(self.seed_output, self.output)
        self.context = copy.deepcopy(self.seed_context)
        self.packet = self.packet_for("planner")

    def packet_for(self, role, event="ready", deviation="none"):
        self.context["active_role"] = role
        if event != "ready":
            outputs = {"finding": "notes.md#NOTE-1"}
            target = routing.FAILURES[event][1] or role
        else:
            target = routing.NEXT[role]
            if role in ("planner", "implementer"):
                keys = routing.PLAN_OUTPUTS if role == "planner" else routing.IMPLEMENT_OUTPUTS
                outputs = {key: "plan.md#PLAN-1" for key in keys.split()}
            elif role == "verifier":
                outputs = {"receipt": str(self.output / "receipt.json"), "observations": "notes.md#NOTE-1"}
            else:
                finding = {"status": "pass", "evidence_ref": "notes.md#NOTE-1"}
                outputs = {"receipt": str(self.output / "receipt.json"),
                           "acceptance": [{"ref": ref, **finding} for ref in self.context["acceptance_refs"]],
                           **{key: finding.copy() for key in ("plan_fidelity", "integration", "structure")}}
        state = self.context["source_state"]
        return {"version": 1, "task_id": "task-1", "role": role, "event": event, "next_role": target,
                "plan_sha256": self.context["plan"]["sha256"], "source_sha": state["head_sha"],
                "workspace_sha256": state["workspace_sha256"], "session_id": role + "-session",
                "adapter_ref": "synthetic-adapter", "model_ref": None if role == "verifier" else "synthetic-model",
                "summary": "Synthetic observations, not actual model quality evidence.",
                "gaps": [] if event == "ready" else ["documented problem"],
                "plan_deviation": deviation, "outputs": outputs}

    def check(self):
        return routing.validate_handoff(self.context, self.packet, self.root)

    def update_receipt(self, mutate):
        path = self.output / "receipt.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        mutate(data)
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_ready_transitions_reuse_native_evidence(self):
        for role, target in routing.NEXT.items():
            with self.subTest(role=role):
                self.packet = self.packet_for(role)
                result = self.check()
                self.assertEqual(result["next_role"], target)
                self.assertEqual(result["evidence_checked"], role in ("verifier", "reviewer"))
                self.assertFalse(result["dispatch_authorized"])
                self.assertFalse(result["merge_authorized"])
                self.assertFalse(result["execution_attested"])
                self.assertFalse(result["state_updated"])

    def test_failure_routes_are_explicit(self):
        for event, (roles, target) in routing.FAILURES.items():
            for role in roles:
                with self.subTest(event=event, role=role):
                    self.packet = self.packet_for(role, event)
                    self.assertEqual(self.check()["next_role"], target or role)

    def test_missing_required_plan_and_implementation_outputs(self):
        for role in ("planner", "implementer"):
            self.packet = self.packet_for(role)
            for key in list(self.packet["outputs"]):
                original = self.packet["outputs"].pop(key)
                with self.subTest(role=role, key=key), self.assertRaisesRegex(routing.HandoffError, "missing_or_unknown_fields"):
                    self.check()
                self.packet["outputs"][key] = original

    def test_plan_file_changed_even_when_packet_hash_matches_context(self):
        (self.root / "plan.md").write_text("# PLAN-1\nChanged meaning\n")
        with self.assertRaisesRegex(routing.HandoffError, "plan_bytes_changed"):
            self.check()

    def test_source_changed_after_context_snapshot(self):
        (self.root / "notes.md").write_text("# NOTE-1\nnew input\n")
        with self.assertRaisesRegex(routing.HandoffError, "source_state_changed"):
            self.check()

    def test_ready_cannot_hide_open_gaps(self):
        self.packet["gaps"] = ["acceptance not implemented"]
        with self.assertRaisesRegex(routing.HandoffError, "unresolved_gaps"):
            self.check()

    def test_material_deviation_routes_to_plan_not_verification(self):
        self.packet = self.packet_for("implementer", deviation="material")
        with self.assertRaisesRegex(routing.HandoffError, "material_change_requires_replan"):
            self.check()
        self.packet = self.packet_for("implementer", "plan_gap", "material")
        self.assertEqual(self.check()["next_role"], "planner")

    def test_plan_alignment_cannot_substitute_for_requirement_coverage(self):
        self.packet = self.packet_for("reviewer")
        self.packet["outputs"]["acceptance"].pop()
        with self.assertRaisesRegex(routing.HandoffError, "review_ac_coverage_incomplete"):
            self.check()

    def test_not_run_requirement_is_not_review_pass(self):
        self.packet = self.packet_for("reviewer")
        self.packet["outputs"]["acceptance"][0]["status"] = "not_run"
        with self.assertRaisesRegex(routing.HandoffError, "review_not_passed"):
            self.check()

    def test_independent_context_not_just_another_model_label(self):
        self.packet = self.packet_for("reviewer")
        self.packet["session_id"] = self.context["review"]["implementation_session"]
        self.packet["model_ref"] = "a-different-model-label"
        with self.assertRaisesRegex(routing.HandoffError, "separate_review_session_required"):
            self.check()
        self.context["review"]["separate_session_required"] = False
        self.assertFalse(self.check()["semantic_review_attested"])

    def test_missing_receipt_blocks_ready(self):
        self.packet = self.packet_for("verifier")
        (self.output / "receipt.json").unlink()
        with self.assertRaises((OSError, ValueError)):
            self.check()

    def test_no_changes_is_not_feature_verification(self):
        self.context["verification"]["features"] = []
        state = self.context["source_state"]
        plan = verify.select(self.data, [], feature_ids=())
        self.output = self.root.parent / "no-changes"
        verify.execute(self.root, self.data, plan, state, self.output, "fixture-v1", "run-1")
        self.packet = self.packet_for("verifier")
        with self.assertRaisesRegex(routing.HandoffError, "no_changes_is_not_feature_verification"):
            self.check()

    def test_missing_or_not_run_native_checks_cannot_advance(self):
        self.packet = self.packet_for("verifier")
        for status in ("NOT_RUN", "FAIL", "TIMEOUT", "ERROR"):
            self.update_receipt(lambda r: r["checks"][0].update(status=status))
            with self.subTest(status=status), self.assertRaises(verify_receipt.EvidenceError):
                self.check()
        self.update_receipt(lambda r: r["checks"].pop())
        with self.assertRaises(verify_receipt.EvidenceError):
            self.check()

    def test_altered_log_even_with_claimed_pass(self):
        self.packet = self.packet_for("reviewer")
        (self.output / "smoke.log").write_text("forged")
        with self.assertRaises(verify_receipt.EvidenceError):
            self.check()

    def test_wrong_native_run_id(self):
        self.packet = self.packet_for("verifier")
        self.context["verification"]["run_id"] = "another-run"
        with self.assertRaisesRegex(verify_receipt.EvidenceError, "run_mismatch"):
            self.check()

    def test_gate_does_not_execute_checks_or_mutate_source(self):
        self.packet = self.packet_for("verifier")
        before = {p.name: p.read_bytes() for p in self.output.iterdir()}
        with patch.object(verify, "execute", side_effect=AssertionError("no second runner")):
            self.check()
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.output.iterdir()})
        self.assertEqual(verify.snapshot(self.root, self.head), self.context["source_state"])

    def test_cli_real_inputs_and_nonzero_blocking(self):
        context = self.root.parent / "context.json"
        packet = self.root.parent / "handoff.json"
        context.write_text(json.dumps(self.context), encoding="utf-8")
        packet.write_text(json.dumps(self.packet), encoding="utf-8")
        command = [sys.executable, "-B", str(ROOT / "tools/orchestration_contract.py"),
                   "--root", str(self.root), "--context", str(context), "--handoff", str(packet)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["next_role"], "implementer")
        packet.write_text('{"version": 1, "version": 1}', encoding="utf-8")
        result = subprocess.run(command, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "BLOCKED")
        self.assertFalse(json.loads(result.stdout)["merge_authorized"])

    def test_gate_imports_no_provider_or_network(self):
        tree = ast.parse((ROOT / "tools/orchestration_contract.py").read_text(encoding="utf-8"))
        allowed = {"__future__", "argparse", "hashlib", "json", "pathlib", "re", "subprocess",
                   "feature_map", "verify", "verify_receipt"}
        imports = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        imports |= {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertLessEqual(imports, allowed)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, {"exec", "eval", "__import__"})


def rejects(surface, path, value):
    def test(self):
        target = self.context if surface == "context" else self.packet
        for part in path[:-1]:
            target = target[part]
        target[path[-1]] = value
        with self.assertRaises((routing.HandoffError, ValueError)):
            self.check()
    return test


CASES = {
    "plan_version": ("packet", ["plan_sha256"], "a" * 64),
    "source_version": ("packet", ["source_sha"], "b" * 40),
    "workspace_version": ("packet", ["workspace_sha256"], "c" * 64),
    "task": ("packet", ["task_id"], "other-task"),
    "bool_version": ("packet", ["version"], True),
    "unknown_version": ("context", ["version"], 2),
    "role_skip": ("packet", ["role"], "reviewer"),
    "transition_skip": ("packet", ["next_role"], "reviewer"),
    "merge_transition": ("packet", ["next_role"], "merge"),
    "planner_cannot_fix_impl": ("packet", ["event"], "implementation_gap"),
    "invented_event": ("packet", ["event"], "auto_approve"),
    "budget_exhausted": ("context", ["budget", "used"], 2),
    "bool_budget": ("context", ["budget", "limit"], True),
    "bool_review_policy": ("context", ["review", "separate_session_required"], "true"),
    "empty_ac": ("context", ["acceptance_refs"], []),
    "unsafe_plan": ("context", ["plan", "ref"], "../plan.md"),
    "missing_output_ref": ("packet", ["outputs", "consumers"], "missing.md"),
    "unknown_field": ("packet", ["approved"], True),
}
for name, args in CASES.items():
    setattr(HandoffTests, "test_reject_" + name, rejects(*args))


if __name__ == "__main__":
    unittest.main()
