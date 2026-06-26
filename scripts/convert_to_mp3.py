#!/usr/bin/env python3
"""既存の WAV を MP3 に変換し、status.json を更新する."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.config import AUDIO_PATH, AUDIO_WAV_PATH, PUBLIC_DIR, STATUS_PATH
from sync_docs import sync_docs


def _wav_duration(wav_path: Path) -> int:
    with wave.open(str(wav_path), "rb") as wf:
        return int(wf.getnframes() / wf.getframerate())


def convert_wav_to_mp3(wav_path: Path, mp3_path: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError(
            "ffmpeg が見つかりません。先にインストールしてください:\n  brew install ffmpeg"
        )

    result = subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(wav_path),
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "128k",
            str(mp3_path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"MP3 変換に失敗しました:\n{result.stderr}")


def main() -> int:
    wav_path = AUDIO_WAV_PATH
    if not wav_path.exists():
        wav_path = PUBLIC_DIR / "latest.wav"
    if not wav_path.exists():
        print("latest.wav が見つかりません。", file=sys.stderr)
        return 1

    mp3_path = AUDIO_PATH
    print(f"変換中: {wav_path} → {mp3_path}")
    convert_wav_to_mp3(wav_path, mp3_path)

    wav_size = wav_path.stat().st_size / 1024 / 1024
    mp3_size = mp3_path.stat().st_size / 1024 / 1024
    duration_sec = _wav_duration(wav_path)

    wav_path.unlink()
    print(f"   完了: {wav_size:.1f} MB → {mp3_size:.1f} MB（{duration_sec} 秒）")

    if STATUS_PATH.exists():
        with STATUS_PATH.open(encoding="utf-8") as f:
            status = json.load(f)
        status["audio_file"] = mp3_path.name
        status["duration_sec"] = duration_sec
        STATUS_PATH.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    sync_docs()
    print(f"   docs/ を更新しました")
    print(f"\n次: git add public/ docs/ && git commit && git push")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
