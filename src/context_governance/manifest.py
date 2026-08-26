from __future__ import annotations

import tomllib
from pathlib import Path, PurePosixPath
from typing import Any

from .models import (
    Boundary,
    CanonicalDocument,
    Manifest,
    Scope,
    SecurityBoundary,
)


class ManifestError(ValueError):
    pass


def _strings(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item for item in value
    ):
        raise ManifestError(f"{field} must be a list of non-empty strings")
    return tuple(value)


def _relative(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ManifestError(f"{field} must be a non-empty string")
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    if path.is_absolute() or ".." in path.parts:
        raise ManifestError(f"{field} must stay inside the repository")
    return normalized


def load_manifest(path: Path) -> Manifest:
    path = path.resolve()
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ManifestError(str(error)) from error

    if data.get("version") != 1:
        raise ManifestError("Only context manifest version 1 is supported")

    canonical: dict[str, CanonicalDocument] = {}
    for name, value in _table(data, "canonical").items():
        canonical[name] = CanonicalDocument(
            name=name,
            path=_relative(value.get("path"), f"canonical.{name}.path"),
            description=_text(
                value.get("description"), f"canonical.{name}.description"
            ),
        )

    scopes: dict[str, Scope] = {}
    for name, value in _table(data, "scopes").items():
        scopes[name] = Scope(
            name=name,
            paths=_strings(value.get("paths"), f"scopes.{name}.paths"),
            extends=_strings(value.get("extends"), f"scopes.{name}.extends"),
            instructions=_strings(
                value.get("instructions"), f"scopes.{name}.instructions"
            ),
            canonical=_strings(value.get("canonical"), f"scopes.{name}.canonical"),
        )

    boundaries = tuple(
        Boundary(
            boundary_id=_text(value.get("id"), "boundaries.id"),
            kind=_text(value.get("kind"), "boundaries.kind"),
            from_paths=_strings(value.get("from_paths"), "boundaries.from_paths"),
            forbid_modules=_strings(
                value.get("forbid_modules", []), "boundaries.forbid_modules"
            ),
            forbid_patterns=_strings(
                value.get("forbid_patterns", []), "boundaries.forbid_patterns"
            ),
            reason=_text(value.get("reason"), "boundaries.reason"),
        )
        for value in data.get("boundaries", [])
    )
    security_boundaries = tuple(
        SecurityBoundary(
            boundary_id=_text(value.get("id"), "security_boundaries.id"),
            consumer=_text(value.get("consumer"), "security_boundaries.consumer"),
            deny_paths=_strings(
                value.get("deny_paths"), "security_boundaries.deny_paths"
            ),
            activation_paths=_strings(
                value.get("activation_paths", []),
                "security_boundaries.activation_paths",
            ),
            enforcement=_text(
                value.get("enforcement"), "security_boundaries.enforcement"
            ),
            implementation_status=_text(
                value.get("implementation_status"),
                "security_boundaries.implementation_status",
            ),
            required_before=_text(
                value.get("required_before"), "security_boundaries.required_before"
            ),
            reason=_text(value.get("reason"), "security_boundaries.reason"),
        )
        for value in data.get("security_boundaries", [])
    )
    limits = _table(data, "limits")
    return Manifest(
        path=path,
        version=1,
        policy=_relative(data.get("policy"), "policy"),
        review_rubric=_relative(data.get("review_rubric"), "review_rubric"),
        managed_markdown=_strings(data.get("managed_markdown"), "managed_markdown"),
        required_files=_strings(data.get("required_files"), "required_files"),
        root_agents_words=_positive_int(
            limits.get("root_agents_words"), "limits.root_agents_words"
        ),
        child_agents_words=_positive_int(
            limits.get("child_agents_words"), "limits.child_agents_words"
        ),
        canonical=canonical,
        scopes=scopes,
        boundaries=boundaries,
        security_boundaries=security_boundaries,
    )


def _table(data: dict[str, Any], field: str) -> dict[str, Any]:
    value = data.get(field)
    if not isinstance(value, dict):
        raise ManifestError(f"{field} must be a table")
    return value


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ManifestError(f"{field} must be a non-empty string")
    return value


def _positive_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ManifestError(f"{field} must be a positive integer")
    return value
