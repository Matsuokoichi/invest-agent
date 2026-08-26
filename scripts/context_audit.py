"""Compatibility entry point for `uv run python scripts/context_audit.py`."""

from context_governance.cli import main


raise SystemExit(main())
