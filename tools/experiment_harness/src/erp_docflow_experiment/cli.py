"""Command-line interface for the offline experiment harness."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from erp_docflow_experiment.bundle import verify_bundle
from erp_docflow_experiment.errors import HarnessError
from erp_docflow_experiment.repository import (
    find_repo_root,
    resolve_existing_bundle,
)
from erp_docflow_experiment.runner import run_experiment, validate_experiment


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="erp-docflow-experiment",
        description="Run and verify offline ERP DocFlow experiments.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-manifest", help="validate static inputs")
    validate.add_argument("--manifest", type=Path, required=True)

    run = subparsers.add_parser("run", help="execute a registered candidate")
    run.add_argument("--manifest", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)

    verify = subparsers.add_parser("verify-artifact", help="verify an evidence bundle")
    verify.add_argument("--bundle", type=Path, required=True)
    return parser


def _path_from_cwd(value: Path) -> Path:
    return value.resolve() if value.is_absolute() else (Path.cwd() / value).resolve()


def main(argv: Sequence[str] | None = None) -> int:
    """Execute the CLI and emit one machine-readable JSON result."""

    args = _parser().parse_args(argv)
    try:
        repo_root = find_repo_root(Path.cwd())
        if args.command == "validate-manifest":
            result = validate_experiment(repo_root, _path_from_cwd(args.manifest))
        elif args.command == "run":
            result = run_experiment(repo_root, _path_from_cwd(args.manifest), args.output)
        elif args.command == "verify-artifact":
            result = verify_bundle(resolve_existing_bundle(repo_root, args.bundle))
        else:
            raise HarnessError("COMMAND_INVALID", "unsupported command")
    except HarnessError as exc:
        print(
            json.dumps(
                {"status": "FAILED", "reason_code": exc.reason_code, "message": exc.message},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0
