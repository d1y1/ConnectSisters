# ニュース・コネクト・シスターズ！

姉妹がニュースを掛け合いで解説する、参加型 Web ラジオサービスです。

## セットアップ

### 1. 依存関係のインストール

Python 3.10 以上が必要です（`cursor-sdk` の要件）。Homebrew で入れた場合は `python3.12` を使います。

```bash
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 環境変数の設定

```bash
cp .env.example .env
```

`.env` に [Cursor API キー](https://cursor.com/dashboard/integrations) を設定してください。

### 3. VOICEVOX の起動（音声合成時）

[VOICEVOX](https://voicevox.hiroshiba.jp/) をインストールし、エンジンを起動してください（デフォルト: `http://127.0.0.1:50021`）。

音声合成をスキップする場合は `--skip-audio` オプションが使えます。

### 4. ffmpeg（MP3 変換、任意）

```bash
# macOS
brew install ffmpeg
```

ffmpeg がない場合、WAV ファイルとして保存されます。

## エピソード生成（Phase 0）

```bash
# フルパイプライン（RSS → 台本 → 音声）
python scripts/run_episode.py

# 台本のみ生成（VOICEVOX 不要）
python scripts/run_episode.py --skip-audio

# キャッシュ済みニュースで再生成
python scripts/run_episode.py --skip-fetch
```

## ローカルプレビュー

```bash
python -m http.server 8080 --directory public
```

ブラウザで http://localhost:8080 を開いてください。

## プロジェクト構成

```
public/           # 静的サイト（GitHub Pages の公開ディレクトリ）
data/             # RSS ソース・プロンプト
scripts/          # 生成パイプライン
output/           # 中間生成物（gitignore）
.github/          # GitHub Actions（Phase 1: 台本自動生成）
```

## 話者設定

| キャラクター | VOICEVOX 話者 | 話者ID |
|-------------|--------------|--------|
| 姉 | 東北ずん子（ノーマル） | 107 |
| 妹 | 春歌ナナ（ノーマル） | 54 |

`scripts/lib/config.py` で変更できます。

## デプロイ（GitHub Pages）

### 方法 A: ブランチ公開（おすすめ・Actions 不要）

GitHub Actions が billing エラーで動かない場合でも、この方法で公開できます。

**初回セットアップ（GitHub 上で1回だけ）**

1. **Settings → Pages → Build and deployment**
2. **Source**: `Deploy from a branch` を選択
3. **Branch**: `main`、**Folder**: `/docs`

**更新手順（毎回）**

```bash
python scripts/run_episode.py          # 生成後、自動で docs/ にコピーされる
git add docs/
git commit -m "chore: update site"
git -c http.postBuffer=524288000 push origin main
```

手動コピー: `python scripts/sync_docs.py`

**公開 URL**: https://d1y1.github.io/ConnectSisters/

---

### 方法 B: GitHub Actions（billing 解消後）

Actions が使えるようになったらこちらに切り替え可能です。

1. **Settings → Pages → Source**: `GitHub Actions`
2. **Settings → Actions → Workflow permissions**: Read and write
3. Secrets に `GEMINI_API_KEY` を登録

### トラブルシューティング

| 症状 | 対処 |
|------|------|
| `account is locked due to a billing issue` | カード認証完了まで待つ（**Payment method verification in progress**）。その間は **方法 A** を使う |
| push が HTTP 400 で失敗 | `git -c http.postBuffer=524288000 push origin main` |
| サイトが 404 | Pages 設定が `/docs` か確認。反映まで 2〜3 分待つ |

### MP3 化（push を軽くする）

```bash
brew install ffmpeg   # 初回のみ

# 既存の WAV を MP3 に変換
python scripts/convert_to_mp3.py

# 以降、音声合成時に自動で MP3 になる
python scripts/run_episode.py
```

WAV（約7MB）→ MP3（約2MB）に圧縮されます。

## 朝のルーティン（Phase 2）

平日朝に自動で「生成 → 公開」する設定です。GitHub Actions は使いません。

### 手動で1回実行（テスト）

```bash
bash scripts/morning_routine.sh
```

処理内容:
1. VOICEVOX を起動（未起動の場合）
2. `python scripts/run_episode.py`（ニュース → 台本 → 音声 → docs/ 同期）
3. `git commit` & `push`（`AUTO_PUSH=true` のとき）

ログ: `output/logs/morning-*.log`

### 平日 7:00 に自動実行（macOS）

```bash
bash scripts/install_launchd.sh
```

解除する場合:

```bash
bash scripts/uninstall_launchd.sh
```

### .env の設定

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| `AUTO_PUSH` | `true` | 生成後に自動 push |
| `SKIP_WEEKEND` | `true` | 土日はスキップ |

push だけ試したくないとき: `AUTO_PUSH=false bash scripts/morning_routine.sh`

### 注意

- **Mac が起動・ログイン済み**である必要があります（スリープ中は実行されません）
- git push には SSH キーまたは credential の設定が必要です
- 時刻を変える場合は `launchd/com.connectsisters.morning.plist.template` の `Hour` / `Minute` を編集して再インストール

## ライセンス

仕様・実装は個人プロジェクトです。ニュースの著作権は各メディアに帰属します。
