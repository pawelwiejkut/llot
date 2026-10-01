#!/usr/bin/env bash
# PostToolUse hook: format edited Python files with ruff (no-op if ruff isn't installed).
file="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input", {}).get("file_path", ""))')"
[[ "$file" == *.py ]] || exit 0
ruff="$CLAUDE_PROJECT_DIR/.venv/bin/ruff"
[[ -x "$ruff" ]] || exit 0
"$ruff" format --quiet "$file" && "$ruff" check --fix --quiet "$file" || true
