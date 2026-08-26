from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any


class Severity(StrEnum):
    ERROR = "ERROR"
    WARNING = "WARNING"


@dataclass(frozen=True, slots=True)
class Issue:
    check: str
    code: str
    severity: Severity
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "check": self.check,
            "code": self.code,
            "severity": self.severity.value,
            "message": self.message,
            "path": self.path,
        }


@dataclass(slots=True)
class AuditReport:
    checks: tuple[str, ...]
    issues: list[Issue] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return not any(issue.severity == Severity.ERROR for issue in self.issues)

    def issues_for(self, check: str) -> list[Issue]:
        return [issue for issue in self.issues if issue.check == check]

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "checks": {
                check: {
                    "status": self._status(check),
                    "issues": [issue.to_dict() for issue in self.issues_for(check)],
                }
                for check in self.checks
            },
        }

    def _status(self, check: str) -> str:
        severities = {issue.severity for issue in self.issues_for(check)}
        if Severity.ERROR in severities:
            return "FAIL"
        if Severity.WARNING in severities:
            return "WARN"
        return "PASS"


@dataclass(frozen=True, slots=True)
class CanonicalDocument:
    name: str
    path: str
    description: str


@dataclass(frozen=True, slots=True)
class Scope:
    name: str
    paths: tuple[str, ...]
    extends: tuple[str, ...]
    instructions: tuple[str, ...]
    canonical: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Boundary:
    boundary_id: str
    kind: str
    from_paths: tuple[str, ...]
    forbid_modules: tuple[str, ...]
    forbid_patterns: tuple[str, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class SecurityBoundary:
    boundary_id: str
    consumer: str
    deny_paths: tuple[str, ...]
    activation_paths: tuple[str, ...]
    enforcement: str
    implementation_status: str
    required_before: str
    reason: str


@dataclass(frozen=True, slots=True)
class Manifest:
    path: Path
    version: int
    policy: str
    review_rubric: str
    managed_markdown: tuple[str, ...]
    required_files: tuple[str, ...]
    root_agents_words: int
    child_agents_words: int
    canonical: dict[str, CanonicalDocument]
    scopes: dict[str, Scope]
    boundaries: tuple[Boundary, ...]
    security_boundaries: tuple[SecurityBoundary, ...]
