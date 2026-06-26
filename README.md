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

### 初回セットアップ

1. このリポジトリを GitHub に push する
2. リポジトリの **Settings → Pages → Build and deployment**
   - **Source**: `GitHub Actions` を選択
3. **Settings → Actions → General → Workflow permissions**
   - **Read and write permissions** を選択して Save
4. **Settings → Secrets and variables → Actions** に以下を登録:
   - `GEMINI_API_KEY` … 台本自動生成用（[Google AI Studio](https://aistudio.google.com/apikey)）
   - `CURSOR_API_KEY` … ローカル用（Actions では不要）

### 公開 URL

push 後、Actions の **Deploy GitHub Pages** が完了すると公開されます。

```
https://<ユーザー名>.github.io/ConnectSisters/
```

例: `https://d1y1.github.io/ConnectSisters/`

### 運用フロー（Phase 1）

```
1. GitHub Actions「Generate Episode Script」を手動実行 → 台本がコミットされる
2. ローカルで python scripts/synthesize_audio.py → 音声を生成
3. public/latest.wav（または latest.mp3）をコミット & push
4. Deploy GitHub Pages が自動実行 → サイトに反映
```

`public/` 以下が変わると push のたびに自動デプロイされます。

### トラブルシューティング

| 症状 | 対処 |
|------|------|
| Deploy GitHub Pages が失敗 | Settings → Actions → Workflow permissions を **Read and write** にする |
| Generate Episode Script が失敗 | `GEMINI_API_KEY` が Secrets に登録されているか確認 |
| サイトが 404 | Deploy ワークフローが成功するまで 2〜3 分待つ |
| push が HTTP 400 で失敗 | `git -c http.postBuffer=524288000 push origin main` を試す |

### MP3 推奨

GitHub リポジトリの容量を抑えるため、ffmpeg で MP3 に変換してからコミットすることを推奨します。

```bash
brew install ffmpeg
python scripts/synthesize_audio.py   # MP3 が生成されれば latest.mp3 をコミット
```

## ライセンス

仕様・実装は個人プロジェクトです。ニュースの著作権は各メディアに帰属します。
