#!/usr/bin/env python3
"""エピソード生成パイプライン（Phase 0: ローカル実行）."""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# scripts/ を import パスに追加
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.config import (  # noqa: E402
    AUDIO_PATH,
    NEWS_CACHE_PATH,
    OUTPUT_DIR,
    PUBLIC_DIR,
    SCRIPT_JSON_PATH,
    SCRIPT_MD_PATH,
    STATUS_PATH,
)
from lib.fetch_news import fetch_news, save_news  # noqa: E402
from lib.generate_script import generate_script, save_script  # noqa: E402
from lib.synthesize_audio import synthesize_audio  # noqa: E402


def _update_status(
    *,
    status: str,
    title: str,
    duration_sec: int | None = None,
    audio_file: str | None = None,
    error: str | None = None,
) -> None:
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    episode_id = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")

    payload: dict = {
        "status": status,
        "episode_id": episode_id,
        "title": title,
        "published_at": datetime.now(timezone.utc).astimezone().isoformat(),
    }
    if duration_sec is not None:
        payload["duration_sec"] = duration_sec
    if audio_file:
        payload["audio_file"] = audio_file
    if error:
        payload["error"] = error

    with STATUS_PATH.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description="Connect Sisters エピソード生成")
    parser.add_argument("--skip-fetch", action="store_true", help="キャッシュ済みニュースを使用")
    parser.add_argument("--skip-audio", action="store_true", help="音声合成をスキップ")
    args = parser.parse_args()

    start = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # 1. ニュース取得
        if args.skip_fetch and NEWS_CACHE_PATH.exists():
            print("📰 キャッシュ済みニュースを使用します")
            with NEWS_CACHE_PATH.open(encoding="utf-8") as f:
                articles = json.load(f)["articles"]
        else:
            print("📰 ニュースを取得中…")
            articles = fetch_news()
            save_news(articles, NEWS_CACHE_PATH)
            print(f"   {len(articles)} 件取得しました")

        # 2. 台本生成
        print("✍️  台本を生成中（Cursor API）…")
        script = generate_script(articles)
        save_script(script, SCRIPT_JSON_PATH, SCRIPT_MD_PATH)
        print(f"   タイトル: {script['title']}")
        print(f"   台本行数: {len(script['lines'])}")

        duration_sec: int | None = None

        # 3. 音声合成
        if args.skip_audio:
            print("🔇 音声合成をスキップしました（--skip-audio）")
            _update_status(status="script_only", title=script["title"])
        else:
            print("🎙️  音声を合成中（VOICEVOX）…")
            duration_sec, audio_path = synthesize_audio(script)
            print(f"   保存先: {audio_path}")
            print(f"   再生時間: {duration_sec} 秒")
            _update_status(
                status="ok",
                title=script["title"],
                duration_sec=duration_sec,
                audio_file=audio_path.name,
            )

        elapsed = time.time() - start
        print(f"\n✅ 完了！（所要時間: {elapsed:.1f} 秒）")
        print(f"   台本: {SCRIPT_MD_PATH}")
        if not args.skip_audio:
            print(f"   音声: {audio_path if not args.skip_audio else AUDIO_PATH}")
        print(f"\n   ローカルプレビュー: python -m http.server 8080 --directory public")

        return 0

    except Exception as exc:
        elapsed = time.time() - start
        print(f"\n❌ エラー: {exc}", file=sys.stderr)
        _update_status(status="failed", title="生成に失敗しました", error=str(exc))
        print(f"   所要時間: {elapsed:.1f} 秒", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
