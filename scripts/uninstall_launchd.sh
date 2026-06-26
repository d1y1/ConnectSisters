#!/bin/bash
set -euo pipefail

LABEL="com.connectsisters.morning"
PLIST_DEST="$HOME/Library/LaunchAgents/com.connectsisters.morning.plist"

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || launchctl unload "$PLIST_DEST" 2>/dev/null || true
rm -f "$PLIST_DEST"

echo "✅ 朝ルーティンの自動実行を解除しました"
