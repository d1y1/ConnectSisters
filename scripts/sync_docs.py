#!/usr/bin/env python3
"""public/ の内容を docs/ にコピー（GitHub Pages ブランチ公開用）."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.config import DOCS_DIR, PUBLIC_DIR


def sync_docs() -> Path:
    if not PUBLIC_DIR.exists():
        raise RuntimeError(f"{PUBLIC_DIR} が見つかりません。")

    if DOCS_DIR.exists():
        shutil.rmtree(DOCS_DIR)
    shutil.copytree(PUBLIC_DIR, DOCS_DIR)
    return DOCS_DIR


def main() -> int:
    dest = sync_docs()
    print(f"✅ {PUBLIC_DIR} → {dest} にコピーしました")
    print("   git add docs/ && git commit && git push でサイトを更新できます")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
