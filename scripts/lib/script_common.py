"""台本生成の共通ユーティリティ."""

from __future__ import annotations

import json
import re
from typing import Any

from .config import PROMPT_PATH


def load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def build_user_prompt(articles: list[dict[str, Any]]) -> str:
    lines = ["以下のニュースをもとに、ラジオ台本を作成してください。\n"]
    for i, article in enumerate(articles, start=1):
        lines.append(f"## ニュース{i}")
        lines.append(f"- タイトル: {article['title']}")
        lines.append(f"- 要約: {article['summary']}")
        lines.append(f"- 出典: {article['source']}")
        lines.append(f"- URL: {article['url']}\n")
    return "\n".join(lines)


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    else:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]
    return json.loads(text)


def parse_script_json(raw_text: str) -> dict[str, Any]:
    script = extract_json(raw_text)
    required_keys = {"title", "lines"}
    if not required_keys.issubset(script.keys()):
        raise RuntimeError(f"台本JSONの形式が不正です: {script.keys()}")
    return script
