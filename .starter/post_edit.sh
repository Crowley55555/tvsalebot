#!/usr/bin/env bash
# PostToolUse hook: быстрая проверка стека tvsalebot после правки кода.
# Вызывается из .claude/settings.json после Edit / Write / MultiEdit.
# Выход всегда 0 — хук диагностический, не блокирующий.
# Стек: Python 3.11+, FastAPI, aiogram 3.x, Redis, pytest, ruff, mypy
# (см. architecture/05-стек.md).

set +e
ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
cd "$ROOT" || exit 0

# Пока в проекте нет .py-кода (только architecture/ и idea/) — молча выходим,
# чтобы не шуметь на правках markdown. Как только появятся api/, bot/ и т.д. —
# проверки начнут работать автоматически.
if ! find api bot features domain infrastructure composition scripts tests \
       -maxdepth 3 -name '*.py' 2>/dev/null | grep -q .; then
  exit 0
fi

run() {
  local label="$1"; shift
  if command -v "$1" >/dev/null 2>&1; then
    echo "[post-edit] $label"
    "$@" || true
  fi
}

run "ruff check"               ruff check .
run "ruff format --check"      ruff format --check .
run "mypy"                     mypy --ignore-missing-imports \
                                   api bot features domain infrastructure composition
[ -d tests ] && run "pytest -q" pytest -q --no-header -x

exit 0
