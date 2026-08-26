from __future__ import annotations

import ast
import os
import re
from pathlib import Path
from urllib.parse import unquote

from .manifest import ManifestError, load_manifest
from .models import AuditReport, Issue, Manifest, Severity
from .patterns import matches
from .resolver import resolve_context


CHECKS = (
    "manifest",
    "required_files",
    "hierarchy",
    "canonical_documents",
    "agents_instructions",
    "markdown_links",
    "scope_overlap",
    "boundaries",
    "security_boundaries",
)
IGNORED_DIRECTORIES = {".git", ".venv", ".pytest_cache", "__pycache__"}
LINK_PATTERN = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")


def audit_repository(
    repo_root: Path, manifest_path: Path | None = None
) -> AuditReport:
    root = repo_root.resolve()
    report = AuditReport(CHECKS)
    target = manifest_path or root / "context/MANIFEST.toml"
    try:
        manifest = load_manifest(target)
    except ManifestError as error:
        _add(report, "manifest", "CG001", Severity.ERROR, str(error), str(target))
        return report

    files = tuple(_iter_files(root))
    relative_files = {
        path.relative_to(root).as_posix(): path for path in files
    }
    _check_required_files(root, manifest, report)
    _check_hierarchy(root, manifest, report)
    _check_canonical(root, manifest, report)
    _check_agents(root, manifest, relative_files, report)
    _check_links(root, manifest, relative_files, report)
    _check_scope_overlap(manifest, relative_files, report)
    _check_boundaries(manifest, relative_files, report)
    _check_security_boundaries(manifest, relative_files, report)
    return report


def render_report(report: AuditReport) -> str:
    lines = ["Context audit"]
    for check in report.checks:
        issues = report.issues_for(check)
        severities = {issue.severity for issue in issues}
        status = (
            "FAIL"
            if Severity.ERROR in severities
            else "WARN"
            if Severity.WARNING in severities
            else "PASS"
        )
        lines.append(f"{status} {check}")
        for issue in issues:
            location = f" ({issue.path})" if issue.path else ""
            lines.append(
                f"  [{issue.severity.value} {issue.code}] "
                f"{issue.message}{location}"
            )
    lines.append("SUCCESS" if report.success else "FAILED")
    return "\n".join(lines)


def _iter_files(root: Path):
    for directory, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            name
            for name in dirnames
            if name not in IGNORED_DIRECTORIES
            and not name.startswith(".eval-runs")
        ]
        for filename in filenames:
            yield Path(directory) / filename


def _check_required_files(
    root: Path, manifest: Manifest, report: AuditReport
) -> None:
    for relative in manifest.required_files:
        if not (root / relative).is_file():
            _add(
                report,
                "required_files",
                "CG101",
                Severity.ERROR,
                "Required governance file is missing",
                relative,
            )


def _check_hierarchy(root: Path, manifest: Manifest, report: AuditReport) -> None:
    for scope in manifest.scopes.values():
        for parent in scope.extends:
            if parent not in manifest.scopes:
                _add(
                    report,
                    "hierarchy",
                    "CG201",
                    Severity.ERROR,
                    f"Scope {scope.name} extends unknown scope {parent}",
                    manifest.path.name,
                )
        for name in scope.canonical:
            if name not in manifest.canonical:
                _add(
                    report,
                    "hierarchy",
                    "CG202",
                    Severity.ERROR,
                    f"Scope {scope.name} references unknown canonical topic {name}",
                    manifest.path.name,
                )
        for instruction in scope.instructions:
            if not (root / instruction).is_file():
                _add(
                    report,
                    "hierarchy",
                    "CG203",
                    Severity.ERROR,
                    f"Instruction for scope {scope.name} does not exist",
                    instruction,
                )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(name: str) -> None:
        if name in visiting:
            _add(
                report,
                "hierarchy",
                "CG204",
                Severity.ERROR,
                f"Scope inheritance contains a cycle at {name}",
                manifest.path.name,
            )
            return
        if name in visited:
            return
        visiting.add(name)
        for parent in manifest.scopes[name].extends:
            if parent in manifest.scopes:
                visit(parent)
        visiting.remove(name)
        visited.add(name)

    for name in manifest.scopes:
        visit(name)


def _check_canonical(root: Path, manifest: Manifest, report: AuditReport) -> None:
    seen: dict[str, str] = {}
    for name, document in manifest.canonical.items():
        if not (root / document.path).is_file():
            _add(
                report,
                "canonical_documents",
                "CG301",
                Severity.ERROR,
                f"Canonical topic {name} points to a missing file",
                document.path,
            )
        previous = seen.get(document.path.casefold())
        if previous:
            _add(
                report,
                "canonical_documents",
                "CG302",
                Severity.ERROR,
                f"Canonical topics {previous} and {name} share one path",
                document.path,
            )
        seen[document.path.casefold()] = name


def _check_agents(
    root: Path,
    manifest: Manifest,
    relative_files: dict[str, Path],
    report: AuditReport,
) -> None:
    agents = {
        relative: path
        for relative, path in relative_files.items()
        if path.name.casefold() == "agents.md"
    }
    registered = {
        instruction
        for scope in manifest.scopes.values()
        for instruction in scope.instructions
    }
    for relative in agents:
        if relative not in registered:
            _add(
                report,
                "agents_instructions",
                "CG401",
                Severity.ERROR,
                "AGENTS.md is not registered by any manifest scope",
                relative,
            )

    root_path = agents.get("AGENTS.md")
    root_bullets = (
        _normalized_bullets(root_path.read_text(encoding="utf-8"))
        if root_path
        else set()
    )
    for relative, path in agents.items():
        text = path.read_text(encoding="utf-8")
        word_count = len(text.split())
        limit = (
            manifest.root_agents_words
            if relative == "AGENTS.md"
            else manifest.child_agents_words
        )
        if word_count > limit:
            _add(
                report,
                "agents_instructions",
                "CG402",
                Severity.ERROR,
                f"Instruction file has {word_count} words; limit is {limit}",
                relative,
            )
        bullets = _normalized_bullets(text)
        if relative != "AGENTS.md":
            for duplicate in sorted(bullets & root_bullets):
                _add(
                    report,
                    "agents_instructions",
                    "CG403",
                    Severity.ERROR,
                    f"Child instruction duplicates root rule: {duplicate}",
                    relative,
                )


def _check_links(
    root: Path,
    manifest: Manifest,
    relative_files: dict[str, Path],
    report: AuditReport,
) -> None:
    for relative, path in relative_files.items():
        if not matches(relative, manifest.managed_markdown):
            continue
        text = path.read_text(encoding="utf-8")
        for raw_target in LINK_PATTERN.findall(text):
            target = raw_target.strip().strip("<>")
            if " " in target and not target.startswith(("http://", "https://")):
                target = target.split(" ", 1)[0]
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            local = unquote(target.split("#", 1)[0])
            if not local:
                continue
            destination = (path.parent / local).resolve()
            try:
                destination.relative_to(root)
            except ValueError:
                _add(
                    report,
                    "markdown_links",
                    "CG501",
                    Severity.ERROR,
                    "Local Markdown link escapes the repository",
                    f"{relative} -> {target}",
                )
                continue
            if not destination.exists():
                _add(
                    report,
                    "markdown_links",
                    "CG502",
                    Severity.ERROR,
                    "Local Markdown link target does not exist",
                    f"{relative} -> {target}",
                )


def _check_scope_overlap(
    manifest: Manifest,
    relative_files: dict[str, Path],
    report: AuditReport,
) -> None:
    parents = {
        name: _all_parents(name, manifest) for name in manifest.scopes
    }
    for relative in relative_files:
        direct = [
            name
            for name, scope in manifest.scopes.items()
            if matches(relative, scope.paths)
        ]
        for index, left in enumerate(direct):
            for right in direct[index + 1 :]:
                if left in parents[right] or right in parents[left]:
                    continue
                _add(
                    report,
                    "scope_overlap",
                    "CG601",
                    Severity.ERROR,
                    f"Sibling scopes {left} and {right} both match this path",
                    relative,
                )


def _check_boundaries(
    manifest: Manifest,
    relative_files: dict[str, Path],
    report: AuditReport,
) -> None:
    for boundary in manifest.boundaries:
        if boundary.kind not in {"python_import", "text_reference"}:
            _add(
                report,
                "boundaries",
                "CG701",
                Severity.ERROR,
                f"Unknown boundary kind {boundary.kind}",
                boundary.boundary_id,
            )
            continue
        for relative, path in relative_files.items():
            if not matches(relative, boundary.from_paths):
                continue
            if boundary.kind == "python_import":
                _check_python_imports(boundary, relative, path, report)
            else:
                text = path.read_text(encoding="utf-8").casefold()
                for forbidden in boundary.forbid_patterns:
                    if forbidden.casefold() in text:
                        _add(
                            report,
                            "boundaries",
                            "CG702",
                            Severity.ERROR,
                            f"Boundary {boundary.boundary_id} forbids reference "
                            f"to {forbidden}: {boundary.reason}",
                            relative,
                        )


def _check_security_boundaries(
    manifest: Manifest,
    relative_files: dict[str, Path],
    report: AuditReport,
) -> None:
    for boundary in manifest.security_boundaries:
        active = any(
            matches(relative, boundary.activation_paths)
            for relative in relative_files
        )
        if active and boundary.implementation_status != "ENFORCED":
            _add(
                report,
                "security_boundaries",
                "CG801",
                Severity.WARNING,
                f"Security boundary {boundary.boundary_id} is active but "
                f"{boundary.implementation_status}; required before "
                f"{boundary.required_before}: {boundary.reason}",
                manifest.path.name,
            )


def _check_python_imports(boundary, relative: str, path: Path, report: AuditReport) -> None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
    except SyntaxError as error:
        _add(
            report,
            "boundaries",
            "CG703",
            Severity.ERROR,
            f"Cannot inspect imports because Python syntax is invalid: {error.msg}",
            relative,
        )
        return
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    for module in modules:
        for forbidden in boundary.forbid_modules:
            if module == forbidden or module.startswith(forbidden + "."):
                _add(
                    report,
                    "boundaries",
                    "CG704",
                    Severity.ERROR,
                    f"Boundary {boundary.boundary_id} forbids import {module}: "
                    f"{boundary.reason}",
                    relative,
                )


def _all_parents(name: str, manifest: Manifest) -> set[str]:
    result: set[str] = set()
    pending = list(manifest.scopes[name].extends)
    while pending:
        parent = pending.pop()
        if parent in result or parent not in manifest.scopes:
            continue
        result.add(parent)
        pending.extend(manifest.scopes[parent].extends)
    return result


def _normalized_bullets(text: str) -> set[str]:
    result: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("- ", "* ")):
            result.add(" ".join(stripped[2:].casefold().split()))
    return result


def _add(
    report: AuditReport,
    check: str,
    code: str,
    severity: Severity,
    message: str,
    path: str | None = None,
) -> None:
    report.issues.append(Issue(check, code, severity, message, path))
