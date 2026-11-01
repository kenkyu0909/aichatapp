# AI_README.md — このリポジトリをAIエージェント／生成AIが扱うためのガイド

このファイルは、**人間ではなくAI（コーディングエージェント・LLM）がこのリポジトリを理解・改修・別PCへ展開する**ための要点をまとめたものです。
人間向けの詳しい操作説明は [`README.md`](README.md)、Codex運用中の継続開発ルールは [`AGENTS.md`](AGENTS.md) を参照してください。

対象リポジトリ: `https://github.com/kenkyu0909/aichatapp`
主な開発ブランチ: `codex/full-system-verification`（マージ後は `feat/ui-local-backend-v1`）

---

## 1. これは何か（30秒サマリ）

マッチングアプリの**返信文作成を支援する、個人専用のWindowsローカルアプリ**。

- サーバー: Python **FastAPI**（`app.py` 1ファイル、約14,600行）
- データ: **SQLite**（`data/app.sqlite3`）＋ 相手の識別用写真（`data/photos/`）
- 画面: 素の **HTML / CSS / JavaScript**（`index.html` / `style.css` / `app.js`。ビルド工程・フレームワークなし）
- 生成AI: **Google Gemini API**（`google-genai`）。4つの生成モード（初回・通常返信・追いメッセージ・メッセージ付きいいね）
- 待受: **`127.0.0.1` のみ**（外部公開しない）。ログインなし・自動送信なし。

**最重要の設計原則（不変条件）:** 未確認の「本人の事実」を**捏造しない**。プロフィールや `confirmed_facts` に根拠がない本人情報は生成せず、`needs_user_info` としてユーザーへ確認質問を返す。プロフィール・会話・写真といった実データは**すべてローカル保存**で、Gitには一切コミットしない。

---

## 2. 別PCでの最短セットアップ

```powershell
git clone -b codex/full-system-verification https://github.com/kenkyu0909/aichatapp.git
cd aichatapp
.\start.bat            # 初回は .venv 作成・依存導入・.env 生成を自動実行。最後に Firefox で http://127.0.0.1:8765/ を開く
```

- **Python 3.11 以上**が必要（検証済み: 3.12.10 / CIは 3.11）。
- 画面を出さずにバックグラウンド起動したい場合: `start_hidden.bat`（サーバーログは `logs\server.log` に出力）。
- 停止: 前面起動なら `Ctrl+C`、バックグラウンド起動なら `stop.bat`（`MRA_PORT` のLISTENプロセスを終了）。
- Gemini を使う場合のみ、`API/chat1.md`・`API/chat2.md`（または `.env` の `MRA_API_1_KEY` / `MRA_API_2_KEY`）にAPIキーを置く。**キーが無くても `LOCAL · DEMO` として固定サンプルで全UIを操作確認できる。**

---

## 3. ファイル構成マップ

| パス | 役割 |
| --- | --- |
| `app.py` | すべてのバックエンド。FastAPIルート、SQLite入出力、プロンプト組立、Gemini呼び出し、返信候補の安全・形式検査 |
| `index.html` | UIの骨格（サイドバー＝相手一覧、生成モード切替、プロフィール設定など） |
| `app.js` | すべてのフロント挙動（状態管理、API呼び出し、下書き、トグル、確認フォーム）。ビルド無し |
| `style.css` | スタイル |
| `prompts/common.txt` | 共通の会話規則（口調・記号・禁止事項など） |
| `prompts/first.txt` / `reply.txt` / `followup.txt` / `like.txt` | 4生成モード別のプロンプト |
| `scripts/start_server.py` | `start.bat` から呼ばれる起動＆終了ヘルパー（ポート確認、Firefox起動、停止確認） |
| `scripts/quality_eval.py` / `scripts/run_quality_checks_*.py` | 生成品質の独立採点／回帰ランナー |
| `tests/test_app.py` | 架空データ＋一時SQLiteによるオフラインAPIテスト |
| `tests/test_ui_firefox*.py` | Selenium + Firefox によるUIテスト |
| `docs/verification/` | 進捗・テストマトリクス・会話シミュレーション記録（PROGRESS.md が現在地） |
| `data/`（Git対象外） | 実データ。`app.sqlite3` と `photos/` |

---

## 4. データモデル（SQLite: `data/app.sqlite3`）

- `profile`（1行）: `content` にJSON。名前・年齢・地域・仕事・趣味・性格・話し方の好み・関係の希望・メモ・`avoid`（避けたい表現）・**`confirmed_facts`（確認済み事実）** を保持。
- `matches`: 相手。名前・プロフィール文・写真パス・`last_message_at`（UTC `YYYY-MM-DD HH:MM:SS`）。
- `messages`: 会話。`role` は `me`（自分）/ `them`（相手）。`created_at` はUTC文字列。
- `orphaned_photos`: 未使用写真の管理。`api_usage`: API試行の上限管理台帳。

保存先は `.env` / 環境変数 **`APP_DATA_DIR`** で変更可能（既定は repo直下 `data/`）。

---

## 5. HTTP API 一覧（`app.py`）

```
GET    /                          画面（index.html）
GET    /style.css  /app.js        静的ファイル
GET    /api/status                死活・app_id 確認
GET    /api/profile               自分のプロフィール取得
PUT    /api/profile               プロフィール保存
POST   /api/profile/confirmed-facts 確認済み事実の更新
POST   /api/profile/learn         会話からプロフィールを学習反映
GET    /api/matches               相手一覧（last_message_at を含む）
POST   /api/matches               相手の新規作成
PUT    /api/matches/{id}          相手の更新
DELETE /api/matches/{id}          相手の削除
PUT    /api/matches/{id}/photo    写真アップロード
GET    /api/matches/{id}/photo    写真取得
GET    /api/matches/{id}/messages       会話履歴
POST   /api/matches/{id}/messages       メッセージ追加
PUT    /api/matches/{id}/messages/{mid} メッセージ更新
DELETE /api/matches/{id}/messages/{mid} メッセージ削除
POST   /api/generate              返信候補の生成（mode: first / reply / followup / like）
```

`POST /api/generate` の応答には候補本体に加え、`needs_user_info`（必須の確認質問）と `optional_user_questions`（任意質問）が含まれることがある。**フロントはこれらを必ず表示し、回答があれば再生成に回す。**

---

## 6. 返信生成まわりの規約（変更時に必ず守る）

- **捏造禁止**: プロフィール／`confirmed_facts` に無い本人事実を断定しない。根拠が無ければ質問に変換する。
- **形式**: 句読点（「、」「。」）を使わない、1文1行、空行を入れない。
- **相手の拒否尊重**: 相手が拒否・温度感が低い場合は誘いを強めない。`followup` は催促しない。
- **送信は手動**: 候補をコピーしただけでは履歴に追加しない。実際に送った文だけを記録する。
- **API フォールバック**: HTTP 429 / `RESOURCE_EXHAUSTED` のときのみ `API1(3.5) → API2(3.5) → API1(3.1) → API2(3.1)` の順に切替。認証・権限・通信エラーでは切替えない。

プロンプトを触る場合は `prompts/*.txt`、検査ロジックは `app.py` 内の該当関数、対応テストは `tests/` と `scripts/run_quality_checks_*.py` をセットで見ること。

---

## 7. フロントエンドの約束事（`app.js`）

- 依存ゼロ。`$()` は `getElementById` ラッパー。状態は単一の `state` オブジェクト。
- **innerHTML禁止**：要素は `node()` / `replaceChildren()` でDOM構築する（XSS・レイアウト崩れ防止）。
- 相手一覧の**古い相手の非表示**はUI側だけで実装している（サーバー変更なし）。`isStaleContact()` で `last_message_at` が2日以上前の相手を既定で隠し、`#toggle-stale` で全員表示に切替。選択中の相手は常に表示。設定は `localStorage` に保存。
- 生成リクエストは**競合防止**のため多重送信を抑止している。プロフィール編集は保護フローあり。
- 構文チェックは `node --check app.js`（CIでも実行）。

---

## 8. テストと検証コマンド

```powershell
python -m pip install -r requirements.txt -r requirements-test.txt
python -m pytest -q        # オフラインAPIテスト（架空データ・一時SQLite。本番 data/ は変更しない）
node --check app.js        # JS構文
```

- UIテストは **Firefox**（Chromium系ではなくSelenium+Firefox）を使う。
- 生成品質は `scripts/` の quality_check ランナーで回帰確認する。
- CI: `.github/workflows/test.yml`（オフラインテスト＋JS構文）。`live-gemini.yml` は手動トリガ専用の実APIスモーク。

---

## 9. 触ってはいけない／注意すべき制約

- **個人データをコミットしない**: `data/`（`app.sqlite3`・`photos/`）、`.env`、`API/*.md`、`*.log` は `.gitignore` 済み。**絶対にforce-addしない。** テストは架空データを使う。
- **既存 Draft PR #4 を守る**: 作業は `codex/full-system-verification` のみ。**PRをマージしない。**
- 本番／私的なデータを使った検証、認証情報の露出、有料設定の変更は行わない。
- ブラウザ検証は Firefox を使う。
- 会話シミュレーション `conversation_004` や新規会話HTMLは、品質ゲート通過だけでは作成しない（ユーザーの明示指示を待つ）。

---

## 10. よくあるタスクの入口

| したいこと | 触る場所 |
| --- | --- |
| 返信の口調・規則を変える | `prompts/common.txt` と各モードのプロンプト |
| 候補の安全検査を変える | `app.py` の検査関数 + 対応する `tests/` |
| APIやDBスキーマを増やす | `app.py`（ルート／テーブル）→ 必要なら `index.html`・`app.js` |
| UI挙動を変える | `index.html`・`app.js`・`style.css` → `node --check` → Firefox UIテスト |
| 別PCへ移す | 本ファイル §2。APIキーと `data/` は手動で別途移送（Gitには載らない） |

---

## 11. 参照

- 人間向けの起動・バックアップ・復元: [`README.md`](README.md)
- 継続開発の運用ルール（Codex向け）: [`AGENTS.md`](AGENTS.md)
- 現在地・進捗: [`docs/verification/PROGRESS.md`](docs/verification/PROGRESS.md)
