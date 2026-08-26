from __future__ import annotations

from pathlib import Path

from context_governance.audit import audit_repository
from context_governance.manifest import load_manifest
from context_governance.resolver import resolve_context

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_repository_context_audit_passes() -> None:
    report = audit_repository(REPO_ROOT)

    assert report.success, report.to_dict()


def test_context_workflow_runs_for_pull_requests_only() -> None:
    workflow = (REPO_ROOT / ".github/workflows/context-governance.yml").read_text(
        encoding="utf-8"
    )

    assert "\n  pull_request:" in workflow
    assert "\n  schedule:" not in workflow
    assert "\n  push:" not in workflow
    assert "\n  workflow_dispatch:" not in workflow


def test_resolver_returns_root_and_evaluation_context() -> None:
    manifest = load_manifest(REPO_ROOT / "context/MANIFEST.toml")

    resolved = resolve_context(manifest, "evals/cases/contract_buy/case.json")

    assert resolved.scopes == ("root", "evaluation_cases")
    assert resolved.instructions == ("AGENTS.md", "evals/AGENTS.md")
    assert ("evaluation_protocol", "docs/evaluation_protocol.md") in (
        resolved.canonical_documents
    )


def test_missing_canonical_document_fails(tmp_path: Path) -> None:
    _write_minimal_repository(tmp_path)
    (tmp_path / "docs/product.md").unlink()

    report = audit_repository(tmp_path)

    assert not report.success
    assert "CG301" in {issue.code for issue in report.issues}


def test_forbidden_runtime_import_fails(tmp_path: Path) -> None:
    _write_minimal_repository(tmp_path)
    runtime = tmp_path / "src/runtime/agent.py"
    runtime.parent.mkdir(parents=True)
    runtime.write_text("import eval_harness\n", encoding="utf-8")

    report = audit_repository(tmp_path)

    assert not report.success
    assert "CG704" in {issue.code for issue in report.issues}


def test_broken_markdown_link_fails(tmp_path: Path) -> None:
    _write_minimal_repository(tmp_path)
    (tmp_path / "docs/product.md").write_text(
        "# Product\n\n[missing](missing.md)\n", encoding="utf-8"
    )

    report = audit_repository(tmp_path)

    assert not report.success
    assert "CG502" in {issue.code for issue in report.issues}


def test_unregistered_agents_file_fails(tmp_path: Path) -> None:
    _write_minimal_repository(tmp_path)
    orphan = tmp_path / "orphan/AGENTS.md"
    orphan.parent.mkdir()
    orphan.write_text("# Orphan\n", encoding="utf-8")

    report = audit_repository(tmp_path)

    assert not report.success
    assert "CG401" in {issue.code for issue in report.issues}


def _write_minimal_repository(root: Path) -> None:
    (root / "context").mkdir()
    (root / "docs").mkdir()
    (root / "AGENTS.md").write_text("# Root\n", encoding="utf-8")
    (root / "docs/product.md").write_text("# Product\n", encoding="utf-8")
    (root / "context/POLICY.md").write_text("# Policy\n", encoding="utf-8")
    (root / "context/REVIEW_RUBRIC.md").write_text("# Rubric\n", encoding="utf-8")
    (root / "context/MANIFEST.toml").write_text(
        """version = 1
policy = "context/POLICY.md"
review_rubric = "context/REVIEW_RUBRIC.md"
managed_markdown = ["AGENTS.md", "docs/**/*.md", "context/**/*.md"]
required_files = ["AGENTS.md"]

[limits]
root_agents_words = 100
child_agents_words = 50

[canonical.product]
path = "docs/product.md"
description = "Product contract"

[scopes.root]
paths = ["**"]
extends = []
instructions = ["AGENTS.md"]
canonical = ["product"]

[[boundaries]]
id = "runtime-no-evals"
kind = "python_import"
from_paths = ["src/runtime/**/*.py"]
forbid_modules = ["eval_harness"]
forbid_patterns = []
reason = "Keep evaluation independent."
""",
        encoding="utf-8",
    )
