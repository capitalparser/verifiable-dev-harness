"""DF-900: read-only structural evidence validation, not execution attestation."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

MAX_JSON_BYTES = 2 * 1024 * 1024
EVIDENCE_TYPES = {"log", "report", "trace", "screenshot", "snapshot"}
CHECK_KINDS = {"positive", "negative", "regression", "architecture", "eval", "e2e"}


class ContractError(ValueError):
    """A fail-closed contract violation with a stable diagnostic code."""


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ContractError(code)


def fields(value: Any, required: str, optional: str = "") -> dict:
    require(type(value) is dict, "object_required")
    keys, allowed = set(required.split()), set((required + " " + optional).split())
    require(keys <= value.keys() <= allowed, "missing_or_unknown_fields")
    return value


def text(value: Any) -> str:
    require(type(value) is str and bool(value.strip()), "nonempty_text_required")
    return value


def items(value: Any) -> list:
    require(type(value) is list and bool(value), "nonempty_array_required")
    return value


def strings(value: Any) -> list[str]:
    return [text(item) for item in items(value)]


def identifier(value: Any) -> str:
    require(bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", text(value))), "invalid_id")
    require(value not in {".", ".."}, "invalid_id")
    return value


def digest(value: Any, lengths: tuple[int, ...] = (64,)) -> str:
    require(bool(re.fullmatch(r"[0-9a-f]+", text(value))) and len(value) in lengths, "invalid_digest")
    return value


def local_file(root: Path, value: Any) -> Path:
    value = text(value)
    parts = PurePosixPath(value)
    require(not parts.is_absolute() and parts.as_posix() == value, "unsafe_path")
    require(not any(p in {".", ".."} for p in parts.parts), "unsafe_path")
    require(not any(c in value for c in ("\\", ":", "\0")), "unsafe_path")
    root = root.resolve(strict=True)
    candidate = root.joinpath(*parts.parts)
    for parent in (candidate, *candidate.parents):
        if parent == root:
            break
        require(not parent.is_symlink(), "symlink_forbidden")
    resolved = candidate.resolve(strict=True)
    require(resolved.is_relative_to(root) and resolved.is_file(), "file_outside_root_or_not_regular")
    return resolved


def sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate_json_key")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise ContractError("nonfinite_json_number")


def load_json(path: Path) -> Any:
    require(path.stat().st_size <= MAX_JSON_BYTES, "json_too_large")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs,
                      parse_constant=_invalid_constant)


def version(value: Any) -> None:
    require(type(value) is int and value == 1, "unsupported_version")


def validate_map(data: Any, root: Path) -> dict[str, dict]:
    fields(data, "version features")
    version(data["version"])
    features = {}
    for feature in items(data["features"]):
        fields(feature, "id owner symptoms entrypoints refs checks", "catalog_ref")
        fid = identifier(feature["id"])
        require(fid not in features, "duplicate_feature")
        text(feature["owner"])
        strings(feature["symptoms"])
        if "catalog_ref" in feature:
            local_file(root, feature["catalog_ref"])
        for entry in items(feature["entrypoints"]):
            fields(entry, "path navigate")
            local_file(root, entry["path"])
            text(entry["navigate"])
        refs = strings(feature["refs"])
        require(len(refs) == len(set(refs)), "duplicate_reference")
        ref_ids = set()
        for ref in refs:
            path, separator, rid = ref.partition("#")
            require(bool(separator) and bool(re.fullmatch(r"(?:BR|WF|CMP|DF|AC)-[0-9]+", rid)), "invalid_reference")
            require(rid not in ref_ids, "duplicate_reference_id")
            source = local_file(root, path).read_text(encoding="utf-8")
            require(bool(re.search(r"^#{1,6}\s+" + re.escape(rid) + r"(?=[\s:]|$)", source, re.M)), "undefined_reference")
            ref_ids.add(rid)
        require({"BR", "WF", "CMP", "DF", "AC"} <= {v.split("-")[0] for v in ref_ids}, "missing_traceability")
        acceptance = {v for v in ref_ids if v.startswith("AC-")}
        checks, kinds, covered = set(), set(), set()
        for check in items(feature["checks"]):
            fields(check, "id kind argv expected covers evidence_types")
            cid = identifier(check["id"])
            require(cid not in checks, "duplicate_check")
            checks.add(cid)
            kind = text(check["kind"])
            require(kind in CHECK_KINDS, "unknown_check_kind")
            kinds.add(kind)
            strings(check["argv"])
            text(check["expected"])
            coverage = strings(check["covers"])
            require(set(coverage) <= acceptance and len(coverage) == len(set(coverage)), "invalid_acceptance_coverage")
            covered.update(coverage)
            types = strings(check["evidence_types"])
            require(set(types) <= EVIDENCE_TYPES and len(types) == len(set(types)), "invalid_evidence_types")
        require({"positive", "negative"} <= kinds, "positive_and_negative_required")
        require(covered == acceptance, "uncovered_acceptance")
        features[fid] = feature
    return features


def timestamp(value: Any) -> datetime:
    try:
        parsed = datetime.fromisoformat(text(value).replace("Z", "+00:00"))
    except ValueError as error:
        raise ContractError("invalid_timestamp") from error
    require(parsed.utcoffset() is not None, "timezone_required")
    return parsed


def validate_receipt(data: Any, feature: dict, root: Path, *, expected_commit: str,
                     expected_run: str, map_hash: str, now: datetime | None = None) -> None:
    fields(data, "version feature_id run_id commit_sha map_sha256 producer environment started_at finished_at results")
    version(data["version"])
    require(identifier(data["feature_id"]) == feature["id"], "feature_mismatch")
    require(identifier(data["run_id"]) == identifier(expected_run), "run_mismatch")
    require(digest(data["commit_sha"], (40, 64)) == digest(expected_commit, (40, 64)), "commit_mismatch")
    require(digest(data["map_sha256"]) == digest(map_hash), "map_mismatch")
    fields(data["producer"], "agent_id adapter")
    identifier(data["producer"]["agent_id"])
    text(data["producer"]["adapter"])
    fields(data["environment"], "os runtime")
    text(data["environment"]["os"])
    text(data["environment"]["runtime"])
    start, finish = timestamp(data["started_at"]), timestamp(data["finished_at"])
    clock = now or datetime.now(timezone.utc)
    require(start <= finish <= clock, "invalid_time_order_or_future")
    expected = {check["id"]: check for check in feature["checks"]}
    seen = set()
    for result in items(data["results"]):
        fields(result, "check_id argv status exit_code artifacts")
        cid = identifier(result["check_id"])
        require(cid in expected and cid not in seen, "unexpected_or_duplicate_result")
        seen.add(cid)
        check = expected[cid]
        require(strings(result["argv"]) == check["argv"], "command_mismatch")
        require(type(result["status"]) is str and result["status"] == "passed", "check_not_passed")
        require(type(result["exit_code"]) is int and result["exit_code"] == 0, "nonzero_or_invalid_exit")
        paths, types = set(), set()
        for artifact in items(result["artifacts"]):
            fields(artifact, "path sha256 type")
            artifact_type = text(artifact["type"])
            require(artifact_type in EVIDENCE_TYPES, "unknown_artifact_type")
            types.add(artifact_type)
            path = text(artifact["path"])
            require(path.startswith(f"artifacts/verification/{expected_run}/"), "artifact_run_mismatch")
            require(path not in paths, "duplicate_artifact")
            paths.add(path)
            file = local_file(root, path)
            require(file.stat().st_size > 0, "empty_artifact")
            require(sha256(file) == digest(artifact["sha256"]), "artifact_digest_mismatch")
        require(set(check["evidence_types"]) <= types, "missing_evidence_type")
    require(seen == set(expected), "incomplete_check_coverage")
