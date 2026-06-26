"""プロジェクト共通設定."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
PUBLIC_DIR = ROOT_DIR / "public"
DOCS_DIR = ROOT_DIR / "docs"
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

# GitHub Actions では Gemini、ローカルでは Cursor をデフォルト使用
_default_provider = "gemini" if os.getenv("GITHUB_ACTIONS") == "true" else "cursor"
SCRIPT_PROVIDER = os.getenv("SCRIPT_PROVIDER", _default_provider).lower()

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

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
GEMINI_FALLBACK_MODELS = [
    m.strip()
    for m in os.getenv(
        "GEMINI_FALLBACK_MODELS",
        "gemini-2.5-flash,gemini-flash-lite-latest",
    ).split(",")
    if m.strip()
]
VOICEVOX_URL = os.getenv("VOICEVOX_URL", "http://127.0.0.1:50021")
