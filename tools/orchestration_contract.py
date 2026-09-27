#!/usr/bin/env python3
"""Validate one role handoff. Never dispatch a model, execute checks, or grant authority."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from feature_map import resolve, source_file
import verify
import verify_receipt

ROLES = ("planner", "implementer", "verifier", "reviewer")
NEXT = dict(zip(ROLES, ("implementer", "verifier", "reviewer", "coordinator")))
FAILURES = {
    "implementation_gap": ({"verifier", "reviewer"}, "implementer"),
    "plan_gap": ({"implementer", "verifier", "reviewer"}, "planner"),
    "environment_blocked": (set(ROLES), "environment_owner"),
    "authority_blocked": (set(ROLES), "human"),
    "invalid_output": (set(ROLES), None),
}
PLAN_OUTPUTS = "scope owner contracts steps consumers verification decisions"
IMPLEMENT_OUTPUTS = "changes wiring tests deviations"
BOUNDARY = {"dispatch_authorized": False, "merge_authorized": False,
            "execution_attested": False, "state_updated": False}


class HandoffError(ValueError):
    """A role, binding or evidence requirement was not satisfied."""


def need(condition: bool, code: str) -> None:
    if not condition:
        raise HandoffError(code)


def fields(value: object, names: str) -> dict:
    need(type(value) is dict and set(value) == set(names.split()), "missing_or_unknown_fields")
    return value


def text(value: object) -> str:
    need(type(value) is str and bool(value.strip()), "nonempty_text_required")
    return value


def digest(value: object, lengths: tuple[int, ...] = (64,)) -> str:
    text(value)
    need(len(value) in lengths and re.fullmatch(r"[0-9a-f]+", value) is not None, "invalid_digest")
    return value


def strings(value: object, *, empty: bool = False) -> list[str]:
    need(type(value) is list and (empty or bool(value)), "array_required")
    return [text(item) for item in value]


def reference(root: Path, value: object) -> None:
    # Reuse the native non-executing resolver; existence is not semantic correctness.
    resolve(root, text(value))


def context_contract(context: dict, root: Path) -> None:
    fields(context, "version task_id active_role plan source_state acceptance_refs verification review budget")
    need(type(context["version"]) is int and context["version"] == 1, "unsupported_context_version")
    text(context["task_id"])
    need(text(context["active_role"]) in ROLES, "unknown_active_role")
    fields(context["plan"], "ref sha256")
    reference(root, context["plan"]["ref"])
    path = context["plan"]["ref"].split("#", 1)[0]
    need(path.endswith(".md"), "markdown_plan_required")
    actual = hashlib.sha256(source_file(root, path).read_bytes()).hexdigest()
    need(digest(context["plan"]["sha256"]) == actual, "plan_bytes_changed")
    state = context["source_state"]
    fields(state, "head_sha base_sha merge_base_sha workspace_sha256 dirty changed_paths")
    for key in ("head_sha", "base_sha", "merge_base_sha"):
        digest(state[key], (40, 64))
    digest(state["workspace_sha256"])
    need(type(state["dirty"]) is bool, "invalid_dirty_flag")
    strings(state["changed_paths"], empty=True)
    acs = strings(context["acceptance_refs"])
    need(len(acs) == len(set(acs)), "duplicate_acceptance")
    for ref in acs:
        need("#AC-" in ref, "acceptance_heading_required")
        reference(root, ref)
    verification = fields(context["verification"], "manifest profile features run_id context")
    source_file(root, text(verification["manifest"]))
    need(text(verification["profile"]) in ("auto", *verify.LEVELS), "unknown_profile")
    strings(verification["features"], empty=True)
    text(verification["run_id"])
    text(verification["context"])
    review = fields(context["review"], "implementation_session separate_session_required")
    text(review["implementation_session"])
    need(type(review["separate_session_required"]) is bool, "invalid_review_policy")
    budget = fields(context["budget"], "used limit")
    need(type(budget["used"]) is int and budget["used"] >= 0
         and type(budget["limit"]) is int and budget["limit"] > 0, "invalid_budget")


def evidence(context: dict, root: Path, receipt_ref: object) -> dict:
    path = Path(text(receipt_ref))
    need(path.is_absolute() and not path.is_symlink(), "absolute_nonsymlink_receipt_required")
    path = path.resolve(strict=True)
    need(root not in path.parents, "receipt_must_be_outside_checkout")
    config = context["verification"]
    data = verify.validate(verify_receipt.load_json(source_file(root, config["manifest"])))
    state = context["source_state"]
    plan = verify.select(data, state["changed_paths"], config["profile"], tuple(config["features"]))
    # Native consumer recomputes commands and checks every actual log, not a claimed PASS.
    result = verify_receipt.validate_receipt(
        verify_receipt.load_json(path), data, plan, state, path.parent,
        expected_head=state["head_sha"], expected_run=config["run_id"],
        expected_context=config["context"])
    need(result["status"] == "VERIFIED_EVIDENCE", "no_changes_is_not_feature_verification")
    return result


def review_finding(root: Path, item: dict) -> None:
    fields(item, "status evidence_ref")
    need(item["status"] == "pass", "review_not_passed")
    reference(root, item["evidence_ref"])


def validate_handoff(context: dict, packet: dict, root: Path) -> dict:
    """Check one transition against an owner-supplied snapshot; no history/authority store."""
    root = root.resolve(strict=True)
    need(Path(verify.git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve() == root,
         "repository_root_required")
    context_contract(context, root)
    fields(packet, "version task_id role event next_role plan_sha256 source_sha workspace_sha256 "
                   "session_id adapter_ref model_ref summary gaps plan_deviation outputs")
    need(type(packet["version"]) is int and packet["version"] == 1, "unsupported_packet_version")
    need(packet["task_id"] == context["task_id"], "task_mismatch")
    role = text(packet["role"])
    need(role == context["active_role"], "active_role_mismatch")
    need(digest(packet["plan_sha256"]) == context["plan"]["sha256"], "plan_revision_mismatch")
    state = context["source_state"]
    need(digest(packet["source_sha"], (40, 64)) == state["head_sha"]
         and digest(packet["workspace_sha256"]) == state["workspace_sha256"], "source_binding_mismatch")
    for key in ("session_id", "adapter_ref", "summary"):
        text(packet[key])
    if role == "verifier":
        need(packet["model_ref"] is None, "verifier_is_native_runner_not_model")
    else:
        text(packet["model_ref"])
    gaps = strings(packet["gaps"], empty=True)
    deviation = text(packet["plan_deviation"])
    need(deviation in ("none", "within_contract", "material"), "unknown_deviation")
    event = text(packet["event"])
    if event == "ready":
        next_role = NEXT[role]
        need(not gaps, "unresolved_gaps_prevent_ready")
        need(deviation != "material", "material_change_requires_replan")
    else:
        need(event in FAILURES and role in FAILURES[event][0], "illegal_role_event")
        next_role = FAILURES[event][1] or role
        need(bool(gaps), "failure_reason_required")
        need(deviation != "material" or event in ("plan_gap", "authority_blocked"),
             "material_change_requires_replan")
    need(packet["next_role"] == next_role, "illegal_transition")
    need(context["budget"]["used"] < context["budget"]["limit"], "budget_exhausted")
    # A stale workspace may not use even a well-formed packet to advance.
    before = verify.snapshot(root, state["base_sha"])
    need(verify_receipt.canonical(before) == verify_receipt.canonical(state), "source_state_changed")
    outputs = packet["outputs"]
    proof = None
    if event != "ready":
        fields(outputs, "finding")
        reference(root, outputs["finding"])
    elif role in ("planner", "implementer"):
        fields(outputs, PLAN_OUTPUTS if role == "planner" else IMPLEMENT_OUTPUTS)
        for value in outputs.values():
            reference(root, value)
    elif role == "verifier":
        fields(outputs, "receipt observations")
        reference(root, outputs["observations"])
        proof = evidence(context, root, outputs["receipt"])
    else:
        fields(outputs, "receipt acceptance plan_fidelity integration structure")
        if context["review"]["separate_session_required"]:
            need(packet["session_id"] != context["review"]["implementation_session"],
                 "separate_review_session_required")
        rows = outputs["acceptance"]
        need(type(rows) is list and bool(rows), "acceptance_review_required")
        seen = set()
        for row in rows:
            fields(row, "ref status evidence_ref")
            ref = text(row["ref"])
            need(ref in context["acceptance_refs"] and ref not in seen, "unknown_or_duplicate_review_ac")
            seen.add(ref)
            review_finding(root, {k: row[k] for k in ("status", "evidence_ref")})
        need(seen == set(context["acceptance_refs"]), "review_ac_coverage_incomplete")
        for key in ("plan_fidelity", "integration", "structure"):
            review_finding(root, outputs[key])
        proof = evidence(context, root, outputs["receipt"])
    need(verify_receipt.canonical(verify.snapshot(root, state["base_sha"]))
         == verify_receipt.canonical(state), "source_changed_during_handoff")
    context_contract(context, root)
    # References can exist and reviews can claim PASS while being semantically wrong.
    return {"status": "HANDOFF_VALID", "scope": "role_contract_and_native_evidence_when_required",
            "task_id": context["task_id"], "event": event, "from_role": role, "next_role": next_role,
            "binding": "workspace" if state["dirty"] else "commit",
            "evidence_checked": proof is not None, "semantic_review_attested": False,
            "model_capability_attested": False, **BOUNDARY}


def main(argv: list[str] | None = None) -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--root", type=Path, default=Path.cwd())
    cli.add_argument("--context", type=Path, required=True, help="trusted existing-coordinator snapshot")
    cli.add_argument("--handoff", type=Path, required=True)
    args = cli.parse_args(argv)
    try:
        result = validate_handoff(verify_receipt.load_json(args.context),
                                  verify_receipt.load_json(args.handoff), args.root)
        print(json.dumps(result, ensure_ascii=True, sort_keys=True))
        return 0
    except (OSError, ValueError, TypeError, KeyError, SyntaxError, RecursionError,
            subprocess.SubprocessError) as exc:
        reason = str(exc) if isinstance(exc, HandoffError) else type(exc).__name__
        print(json.dumps({"status": "BLOCKED", "reason": reason, "next_role": "coordinator", **BOUNDARY}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
