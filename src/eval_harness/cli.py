from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .runner import HarnessRunner, render_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="eval-harness",
        description="Run the independent Investment Research Agent evaluator.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="Run an evaluation suite")
    run_parser.add_argument("--suite", type=Path, required=True)
    run_parser.add_argument(
        "--output",
        type=Path,
        default=Path(".eval-runs"),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command != "run":
        return 2

    repo_root = Path.cwd()
    suite = args.suite
    if not suite.is_absolute():
        suite = repo_root / suite
    output = args.output
    if not output.is_absolute():
        output = repo_root / output

    try:
        summary = HarnessRunner(repo_root, output).run_suite(suite)
    except Exception as error:
        print(f"Harness error: {error}", file=sys.stderr)
        return 2

    print(render_summary(summary))
    return 0 if summary["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

