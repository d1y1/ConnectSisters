#!/usr/bin/env python3
"""VOICEVOXで音声を合成する（単体実行用）."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.config import AUDIO_PATH, PUBLIC_DIR, SCRIPT_JSON_PATH, STATUS_PATH
from lib.synthesize_audio import load_script, synthesize_audio


def main() -> int:
    if not SCRIPT_JSON_PATH.exists():
        print("台本がありません。先に generate_script.py を実行してください。", file=sys.stderr)
        return 1

    script = load_script(SCRIPT_JSON_PATH)
    print(f"台本: {script['title']}")
    duration_sec, audio_path = synthesize_audio(script)

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    status = {
        "status": "ok",
        "episode_id": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d"),
        "title": script["title"],
        "published_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "duration_sec": duration_sec,
        "audio_file": audio_path.name,
    }
    with STATUS_PATH.open("w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)

    print(f"音声を保存しました: {audio_path}（{duration_sec} 秒）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
