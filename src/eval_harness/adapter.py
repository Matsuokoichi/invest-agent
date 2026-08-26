from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .io import deep_merge, read_json, resolve_inside, write_json

TRACE_EVENTS = [
    "research_started",
    "source_selected",
    "fact_extracted",
    "initial_thesis_created",
    "counter_evidence_search_started",
    "counter_evidence_recorded",
    "thesis_reconsidered",
    "forecast_completed",
    "valuation_completed",
    "decision_computed",
    "evidence_audit_completed",
    "report_emitted",
]


class FixtureAdapter:
    """Creates deterministic Agent artifacts from versioned contract fixtures."""

    def execute(
        self,
        repo_root: Path,
        case_path: Path,
        case: dict[str, Any],
        run_directory: Path,
    ) -> None:
        fixture = case["fixture"]
        base_path = resolve_inside(repo_root, case_path.parent / fixture["base_report"])
        report = deep_merge(read_json(base_path), fixture.get("report_patch", {}))
        omitted = set(fixture.get("omit_artifacts", []))
        run_directory.mkdir(parents=True, exist_ok=True)

        if "report.json" not in omitted:
            write_json(run_directory / "report.json", report)
        if "report.md" not in omitted:
            (run_directory / "report.md").write_text(
                f"# {report.get('report_id', case['case_id'])}\n",
                encoding="utf-8",
                newline="\n",
            )
        if "sources.json" not in omitted:
            write_json(run_directory / "sources.json", report.get("sources", []))
        if "calculations.json" not in omitted:
            write_json(
                run_directory / "calculations.json",
                {
                    "recommendation": report.get("recommendation"),
                    "scenarios": report.get("scenarios"),
                },
            )
        if "trace.jsonl" not in omitted:
            self._write_trace(run_directory / "trace.jsonl", case, report)
        if "run_manifest.json" not in omitted:
            write_json(
                run_directory / "run_manifest.json",
                {
                    "run_id": run_directory.parent.name,
                    "case_id": case["case_id"],
                    "adapter": "fixture",
                    "agent_version": "fixture-1.0.0",
                    "started_at": datetime.now(UTC).isoformat(),
                    "status": "completed",
                },
            )

    @staticmethod
    def _write_trace(path: Path, case: dict[str, Any], report: dict[str, Any]) -> None:
        source_id = (report.get("sources") or [{"id": None}])[0].get("id")
        claim_id = (report.get("claims") or [{"id": None}])[0].get("id")
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            for index, event in enumerate(TRACE_EVENTS):
                record = {
                    "event": event,
                    "sequence": index + 1,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "run_id": path.parent.parent.name,
                    "case_id": case["case_id"],
                    "source_ids": [source_id] if source_id else [],
                    "claim_ids": [claim_id] if claim_id else [],
                    "status": "completed",
                }
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
