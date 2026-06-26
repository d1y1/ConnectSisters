"""プロジェクト共通設定."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
PUBLIC_DIR = ROOT_DIR / "public"
OUTPUT_DIR = ROOT_DIR / "output"

RSS_SOURCES_PATH = DATA_DIR / "rss_sources.json"
PROMPT_PATH = DATA_DIR / "prompts" / "system_prompt.txt"
NEWS_CACHE_PATH = OUTPUT_DIR / "news.json"
SCRIPT_JSON_PATH = PUBLIC_DIR / "script.json"
SCRIPT_MD_PATH = PUBLIC_DIR / "script.md"
STATUS_PATH = PUBLIC_DIR / "status.json"
AUDIO_PATH = PUBLIC_DIR / "latest.mp3"
AUDIO_WAV_PATH = PUBLIC_DIR / "latest.wav"

MAX_NEWS_ITEMS = 3

# VOICEVOX 話者ID（東北ずん子=姉、春歌ナナ=妹）
SPEAKER_IDS = {
    "姉": 107,
    "妹": 54,
}

load_dotenv(ROOT_DIR / ".env")

CURSOR_API_KEY = os.getenv("CURSOR_API_KEY", "")
CURSOR_MODEL = os.getenv("CURSOR_MODEL", "composer-2")
CURSOR_MODEL_FAST = os.getenv("CURSOR_MODEL_FAST", "false").lower() in (
    "true",
    "1",
    "yes",
)
CURSOR_FALLBACK_MODELS = [
    m.strip()
    for m in os.getenv("CURSOR_FALLBACK_MODELS", "").split(",")
    if m.strip()
]
VOICEVOX_URL = os.getenv("VOICEVOX_URL", "http://127.0.0.1:50021")
