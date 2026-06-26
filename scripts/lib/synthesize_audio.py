"""VOICEVOX Engineで台本から音声を合成する."""

from __future__ import annotations

import json
import shutil
import subprocess
import wave
from io import BytesIO
from pathlib import Path
from typing import Any

import requests

from .config import AUDIO_PATH, SPEAKER_IDS, VOICEVOX_URL


def _check_voicevox() -> None:
    try:
        response = requests.get(f"{VOICEVOX_URL}/version", timeout=5)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            f"VOICEVOX Engine に接続できません ({VOICEVOX_URL})。\n"
            "VOICEVOX を起動してから再実行してください。\n"
            "音声合成をスキップする場合は --skip-audio オプションを使ってください。"
        ) from exc


def _synthesize_line(text: str, speaker_id: int) -> bytes:
    query_response = requests.post(
        f"{VOICEVOX_URL}/audio_query",
        params={"text": text, "speaker": speaker_id},
        timeout=30,
    )
    query_response.raise_for_status()

    synthesis_response = requests.post(
        f"{VOICEVOX_URL}/synthesis",
        params={"speaker": speaker_id},
        data=query_response.content,
        headers={"Content-Type": "application/json"},
        timeout=60,
    )
    synthesis_response.raise_for_status()
    return synthesis_response.content


def _concat_wav(wav_chunks: list[bytes]) -> bytes:
    if not wav_chunks:
        raise RuntimeError("合成する音声がありません。")

    output = BytesIO()
    with wave.open(BytesIO(wav_chunks[0]), "rb") as first:
        params = first.getparams()
        frames = [first.readframes(first.getnframes())]

    for chunk in wav_chunks[1:]:
        with wave.open(BytesIO(chunk), "rb") as wf:
            frames.append(wf.readframes(wf.getnframes()))

    with wave.open(output, "wb") as out:
        out.setparams(params)
        for frame in frames:
            out.writeframes(frame)

    return output.getvalue()


def _save_audio(wav_data: bytes, mp3_path: Path) -> Path:
    """WAV を保存し、ffmpeg があれば MP3 に変換する。最終ファイルパスを返す."""
    wav_path = mp3_path.with_suffix(".wav")
    wav_path.write_bytes(wav_data)

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print(f"   ffmpeg なし → WAV で保存: {wav_path}")
        return wav_path

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
        print(f"   MP3 変換失敗 → WAV で保存: {wav_path}")
        return wav_path

    wav_path.unlink(missing_ok=True)
    return mp3_path


def _get_wav_duration(wav_data: bytes) -> float:
    with wave.open(BytesIO(wav_data), "rb") as wf:
        return wf.getnframes() / wf.getframerate()


def synthesize_audio(script: dict[str, Any], output_path: Path = AUDIO_PATH) -> tuple[int, Path]:
    """台本を音声合成し保存する。(再生時間秒, 保存パス) を返す."""
    _check_voicevox()

    wav_chunks: list[bytes] = []
    for line in script["lines"]:
        speaker = line.get("speaker", "")
        text = line.get("text", "").strip()
        if not text:
            continue

        speaker_id = SPEAKER_IDS.get(speaker)
        if speaker_id is None:
            raise RuntimeError(f"未知の話者です: {speaker}（姉 or 妹 を指定してください）")

        print(f"  合成中: [{speaker}] {text[:40]}…")
        wav_chunks.append(_synthesize_line(text, speaker_id))

    wav_data = _concat_wav(wav_chunks)
    duration_sec = int(_get_wav_duration(wav_data))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    saved_path = _save_audio(wav_data, output_path)
    return duration_sec, saved_path


def load_script(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)
