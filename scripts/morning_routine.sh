#!/bin/bash
# 朝のルーティン: VOICEVOX起動 → エピソード生成 → docs同期 → git push
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT/output/logs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/morning-$(date +%Y-%m-%d_%H%M%S).log"

exec >>"$LOG" 2>&1
echo "=== $(date '+%Y-%m-%d %H:%M:%S') morning routine start ==="
echo "ROOT=$ROOT"

# .env を読み込み（AUTO_PUSH など）
if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi

AUTO_PUSH="${AUTO_PUSH:-true}"
SKIP_WEEKEND="${SKIP_WEEKEND:-true}"

# 土日スキップ（手動実行時も有効。無効化: SKIP_WEEKEND=false）
if [[ "$SKIP_WEEKEND" == "true" ]]; then
  DOW=$(date +%u) # 1=月 … 7=日
  if [[ "$DOW" -ge 6 ]]; then
    echo "週末のためスキップします（SKIP_WEEKEND=false で無効化）"
    exit 0
  fi
fi

PYTHON="$ROOT/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  echo "ERROR: .venv が見つかりません。先に pip install を実行してください。"
  exit 1
fi

# VOICEVOX 起動待ち
wait_for_voicevox() {
  local i
  for i in $(seq 1 30); do
    if curl -sf "http://127.0.0.1:50021/version" >/dev/null 2>&1; then
      echo "VOICEVOX ready"
      return 0
    fi
    if [[ "$i" -eq 1 ]]; then
      echo "VOICEVOX を起動しています…"
      open -a VOICEVOX 2>/dev/null || true
    fi
    sleep 2
  done
  echo "ERROR: VOICEVOX が起動しませんでした"
  return 1
}

wait_for_voicevox

cd "$ROOT"
echo "エピソード生成中…"
"$PYTHON" scripts/run_episode.py

EPISODE_TITLE=$("$PYTHON" -c "
import json
from pathlib import Path
print(json.loads(Path('public/status.json').read_text()).get('title', 'update'))
")

if [[ "$AUTO_PUSH" != "true" ]]; then
  echo "AUTO_PUSH=false のため push をスキップしました"
  echo "手動: git add docs/ public/ && git commit && git push"
  exit 0
fi

cd "$ROOT"
git add docs/ public/
if git diff --staged --quiet; then
  echo "変更なし。push をスキップします"
  exit 0
fi

COMMIT_MSG="chore: morning episode - ${EPISODE_TITLE} ($(date +%Y-%m-%d))"
git commit -m "$COMMIT_MSG"
git -c http.postBuffer=524288000 push origin main

echo "=== $(date '+%Y-%m-%d %H:%M:%S') done: $EPISODE_TITLE ==="

# 成功通知（macOS）
osascript -e "display notification \"${EPISODE_TITLE}\" with title \"Connect Sisters 配信完了\"" 2>/dev/null || true
