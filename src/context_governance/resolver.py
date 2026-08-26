from __future__ import annotations

from dataclasses import dataclass

from .models import Manifest
from .patterns import matches


@dataclass(frozen=True, slots=True)
class ResolvedContext:
    path: str
    scopes: tuple[str, ...]
    instructions: tuple[str, ...]
    canonical_documents: tuple[tuple[str, str], ...]


def resolve_context(manifest: Manifest, path: str) -> ResolvedContext:
    normalized = path.replace("\\", "/").lstrip("./")
    direct = {
        name
        for name, scope in manifest.scopes.items()
        if matches(normalized, scope.paths)
    }
    selected = set(direct)

    def include_parents(name: str) -> None:
        for parent in manifest.scopes[name].extends:
            if parent not in selected:
                selected.add(parent)
                include_parents(parent)

    for name in tuple(direct):
        include_parents(name)

    ordered: list[str] = []
    visiting: set[str] = set()

    def visit(name: str) -> None:
        if name in ordered:
            return
        if name in visiting:
            raise ValueError(f"Scope inheritance cycle at {name}")
        visiting.add(name)
        for parent in manifest.scopes[name].extends:
            visit(parent)
        visiting.remove(name)
        if name in selected:
            ordered.append(name)

    for name in sorted(selected):
        visit(name)

    instructions: list[str] = []
    canonical_names: list[str] = []
    for name in ordered:
        for instruction in manifest.scopes[name].instructions:
            if instruction not in instructions:
                instructions.append(instruction)
        for canonical_name in manifest.scopes[name].canonical:
            if canonical_name not in canonical_names:
                canonical_names.append(canonical_name)

    return ResolvedContext(
        path=normalized,
        scopes=tuple(ordered),
        instructions=tuple(instructions),
        canonical_documents=tuple(
            (name, manifest.canonical[name].path) for name in canonical_names
        ),
    )
