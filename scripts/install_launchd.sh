#!/bin/bash
# launchd に平日7:00の朝ルーティンを登録する
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_SRC="$ROOT/launchd/com.connectsisters.morning.plist.template"
PLIST_DEST="$HOME/Library/LaunchAgents/com.connectsisters.morning.plist"
LABEL="com.connectsisters.morning"

mkdir -p "$ROOT/output/logs"
mkdir -p "$HOME/Library/LaunchAgents"

sed -e "s|__PROJECT_ROOT__|$ROOT|g" -e "s|__HOME__|$HOME|g" "$PLIST_SRC" > "$PLIST_DEST"
chmod +x "$ROOT/scripts/morning_routine.sh"

# 既存ジョブをアンロード（エラーは無視）
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || launchctl unload "$PLIST_DEST" 2>/dev/null || true

launchctl bootstrap "gui/$(id -u)" "$PLIST_DEST" 2>/dev/null || launchctl load "$PLIST_DEST"

echo "✅ 登録完了: 平日 7:00 に朝ルーティンが実行されます"
echo "   Plist: $PLIST_DEST"
echo ""
echo "手動テスト: bash $ROOT/scripts/morning_routine.sh"
echo "登録解除:   bash $ROOT/scripts/uninstall_launchd.sh"
echo "ログ:       $ROOT/output/logs/"
