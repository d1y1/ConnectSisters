"""Gemini APIで掛け合い台本を生成する（CI / ヘッドレス用）."""

from __future__ import annotations

from typing import Any

from google import genai

from .config import GEMINI_API_KEY, GEMINI_FALLBACK_MODELS, GEMINI_MODEL
from .script_common import build_user_prompt, load_system_prompt


def _call_gemini(model: str, system_prompt: str, user_prompt: str) -> str:
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=model,
        contents=user_prompt,
        config={
            "system_instruction": system_prompt,
            "temperature": 0.8,
        },
    )
    return response.text or ""


def generate_script_with_gemini(articles: list[dict[str, Any]]) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY が設定されていません。"
            " GitHub Secrets に登録するか、.env に設定してください。"
        )

    system_prompt = load_system_prompt()
    user_prompt = build_user_prompt(articles)

    models_to_try: list[str] = []
    for model in [GEMINI_MODEL, *GEMINI_FALLBACK_MODELS]:
        if model not in models_to_try:
            models_to_try.append(model)

    last_error: Exception | None = None
    for model in models_to_try:
        try:
            print(f"   モデル: {model} (Gemini)")
            return _call_gemini(model, system_prompt, user_prompt)
        except Exception as exc:
            last_error = exc
            err = str(exc)
            if any(code in err for code in ("429", "503", "404", "RESOURCE_EXHAUSTED", "UNAVAILABLE", "NOT_FOUND")):
                print(f"   {model} は利用不可のためスキップ")
                continue
            raise

    raise RuntimeError(
        "すべての Gemini モデルで台本生成に失敗しました。"
        " API キーとクォータを確認してください。"
    ) from last_error
