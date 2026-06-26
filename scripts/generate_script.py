#!/usr/bin/env python3
"""Cursor APIで台本を生成する（単体実行用）."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.config import NEWS_CACHE_PATH, SCRIPT_JSON_PATH, SCRIPT_MD_PATH
from lib.generate_script import generate_script, save_script


def main() -> int:
    if not NEWS_CACHE_PATH.exists():
        print("ニュースキャッシュがありません。先に fetch_news.py を実行してください。", file=sys.stderr)
        return 1

    with NEWS_CACHE_PATH.open(encoding="utf-8") as f:
        articles = json.load(f)["articles"]

    script = generate_script(articles)
    save_script(script, SCRIPT_JSON_PATH, SCRIPT_MD_PATH)
    print(f"台本を生成しました: {SCRIPT_MD_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
