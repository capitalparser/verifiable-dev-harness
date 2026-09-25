"""CLI for CMP-900. JSON commands are data and are never executed."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from verification_contract import (ContractError, digest, load_json, local_file,
                                   require, sha256, validate_map, validate_receipt)


def git(root: Path, *args: str) -> str:
    # Ignore inherited Git redirection; never run a shell or a manifest command.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                            text=True, timeout=15, check=False, env=env)
    require(result.returncode == 0, "git_check_failed")
    return result.stdout.strip()


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description=__doc__)
    subs = cli.add_subparsers(dest="mode", required=True)
    for name in ("lint", "receipt"):
        sub = subs.add_parser(name)
        sub.add_argument("--root", type=Path, default=Path.cwd())
        sub.add_argument("--map", default="verification/feature-map.json")
        if name == "receipt":
            sub.add_argument("--receipt", required=True)
            sub.add_argument("--feature", required=True)
            sub.add_argument("--run-id", required=True)
            sub.add_argument("--commit-sha", required=True)
    return cli


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    output = {"merge_authorized": False, "execution_attested": False}
    try:
        root = args.root.resolve(strict=True)
        map_path = local_file(root, args.map)
        features = validate_map(load_json(map_path), root)
        output.update(map_sha256=sha256(map_path))
        if args.mode == "lint":
            output.update(status="map_valid", scope="registered_features_only", features=list(features))
        else:
            digest(args.commit_sha, (40, 64))
            require(Path(git(root, "rev-parse", "--show-toplevel")).resolve() == root, "repository_root_required")
            require(git(root, "rev-parse", "HEAD") == args.commit_sha, "workspace_commit_mismatch")
            git(root, "ls-files", "--error-unmatch", "--", ":(literal)" + args.map)
            require(not git(root, "status", "--porcelain", "--untracked-files=all"), "dirty_workspace")
            require(args.feature in features, "unknown_feature")
            receipt = load_json(local_file(root, args.receipt))
            validate_receipt(receipt, features[args.feature], root,
                             expected_commit=args.commit_sha, expected_run=args.run_id,
                             map_hash=output["map_sha256"])
            output.update(status="evidence_valid", scope="one_feature_evidence_consistency",
                          feature=args.feature, run_id=args.run_id, commit_sha=args.commit_sha)
        print(json.dumps(output, ensure_ascii=True, sort_keys=True))
        return 0
    except (ContractError, OSError, ValueError, RecursionError, subprocess.SubprocessError) as error:
        # Do not echo arbitrary file contents, subprocess stderr, or secrets.
        output.update(status="blocked", reason=str(error) if isinstance(error, ContractError)
                      else type(error).__name__)
        print(json.dumps(output, ensure_ascii=True, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
