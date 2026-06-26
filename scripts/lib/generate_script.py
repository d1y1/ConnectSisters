"""Cursor APIで掛け合い台本を生成する."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cursor_sdk import (
    Agent,
    AgentOptions,
    CursorAgentError,
    LocalAgentOptions,
    ModelParameterValue,
    ModelSelection,
    RateLimitError,
)

from .config import (
    CURSOR_API_KEY,
    CURSOR_FALLBACK_MODELS,
    CURSOR_MODEL,
    CURSOR_MODEL_FAST,
    PROMPT_PATH,
    ROOT_DIR,
)


def _load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _build_user_prompt(articles: list[dict[str, Any]]) -> str:
    lines = ["以下のニュースをもとに、ラジオ台本を作成してください。\n"]
    for i, article in enumerate(articles, start=1):
        lines.append(f"## ニュース{i}")
        lines.append(f"- タイトル: {article['title']}")
        lines.append(f"- 要約: {article['summary']}")
        lines.append(f"- 出典: {article['source']}")
        lines.append(f"- URL: {article['url']}\n")
    return "\n".join(lines)


def _build_prompt(system_prompt: str, user_prompt: str) -> str:
    return f"{system_prompt}\n\n---\n\n{user_prompt}"


def _extract_json(text: str) -> dict[str, Any]:
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


def _build_model_selection(model_id: str) -> ModelSelection:
    return ModelSelection(
        id=model_id,
        params=[ModelParameterValue(id="fast", value="true" if CURSOR_MODEL_FAST else "false")],
    )


def _call_cursor(model_id: str, prompt: str) -> str:
    model = _build_model_selection(model_id)
    result = Agent.prompt(
        prompt,
        AgentOptions(
            api_key=CURSOR_API_KEY,
            model=model,
            local=LocalAgentOptions(cwd=str(ROOT_DIR)),
        ),
    )
    if result.status == "error":
        raise RuntimeError(f"Cursor Agent の実行に失敗しました (model={model_id})")
    return result.result or ""


def generate_script(articles: list[dict[str, Any]]) -> dict[str, Any]:
    if not CURSOR_API_KEY:
        raise RuntimeError(
            "CURSOR_API_KEY が設定されていません。.env ファイルを作成してください。"
        )

    system_prompt = _load_system_prompt()
    user_prompt = _build_user_prompt(articles)
    prompt = _build_prompt(system_prompt, user_prompt)

    models_to_try: list[str] = []
    for model in [CURSOR_MODEL, *CURSOR_FALLBACK_MODELS]:
        if model not in models_to_try:
            models_to_try.append(model)

    last_error: Exception | None = None
    raw_text = ""
    for model in models_to_try:
        try:
            fast_label = "fast" if CURSOR_MODEL_FAST else "standard"
            print(f"   モデル: {model} ({fast_label})")
            raw_text = _call_cursor(model, prompt)
            break
        except RateLimitError as exc:
            last_error = exc
            print(f"   {model} はレート制限のためスキップ")
            continue
        except CursorAgentError as exc:
            last_error = exc
            if exc.is_retryable:
                print(f"   {model} は一時的なエラーのためスキップ: {exc}")
                continue
            raise
        except RuntimeError as exc:
            last_error = exc
            print(f"   {model} は実行エラーのためスキップ: {exc}")
            continue

    if not raw_text:
        raise RuntimeError(
            "すべてのモデルで台本生成に失敗しました。"
            " Cursor Dashboard で API キーと利用状況を確認するか、しばらく待ってから再実行してください。"
        ) from last_error

    script = _extract_json(raw_text)

    required_keys = {"title", "lines"}
    if not required_keys.issubset(script.keys()):
        raise RuntimeError(f"台本JSONの形式が不正です: {script.keys()}")

    script["generated_at"] = datetime.now(timezone.utc).isoformat()
    script["sources"] = [
        {"title": a["title"], "url": a["url"], "source": a["source"]} for a in articles
    ]
    return script


def script_to_markdown(script: dict[str, Any]) -> str:
    lines = [
        f"# {script['title']}",
        "",
        f"*生成日時: {script.get('generated_at', '')}*",
        "",
        "## 台本",
        "",
    ]
    for line in script["lines"]:
        speaker = line.get("speaker", "???")
        text = line.get("text", "")
        lines.append(f"**{speaker}**: {text}")
        lines.append("")

    lines.append("## 出典")
    lines.append("")
    for source in script.get("sources", []):
        lines.append(f"- [{source['title']}]({source['url']})（{source['source']}）")

    lines.append("")
    lines.append("---")
    lines.append("*本台本は AI により自動生成されています。*")
    return "\n".join(lines)


def save_script(script: dict[str, Any], json_path: Path, md_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)

    md_path.write_text(script_to_markdown(script), encoding="utf-8")
