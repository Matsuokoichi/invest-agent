from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audit import audit_repository, render_report
from .manifest import ManifestError, load_manifest
from .resolver import resolve_context


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="context-audit",
        description="Audit and resolve repository context governance.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("context/MANIFEST.toml"),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="Run deterministic checks")
    check.add_argument("--json", action="store_true", dest="as_json")
    resolve = subparsers.add_parser(
        "resolve", help="Resolve instructions and canonical docs for one path"
    )
    resolve.add_argument("--path", required=True)
    resolve.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path.cwd().resolve()
    manifest_path = args.manifest
    if not manifest_path.is_absolute():
        manifest_path = root / manifest_path

    if args.command == "check":
        report = audit_repository(root, manifest_path)
        print(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
            if args.as_json
            else render_report(report)
        )
        return 0 if report.success else 1

    try:
        manifest = load_manifest(manifest_path)
        resolved = resolve_context(manifest, args.path)
    except (ManifestError, ValueError) as error:
        print(f"Context resolution failed: {error}")
        return 2
    payload = {
        "path": resolved.path,
        "scopes": list(resolved.scopes),
        "instructions": list(resolved.instructions),
        "canonical_documents": [
            {"topic": topic, "path": path}
            for topic, path in resolved.canonical_documents
        ],
    }
    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Context for {resolved.path}")
        print("Scopes: " + ", ".join(resolved.scopes))
        print("Instructions:")
        for instruction in resolved.instructions:
            print(f"  - {instruction}")
        print("Canonical documents:")
        for topic, path in resolved.canonical_documents:
            print(f"  - {topic}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
