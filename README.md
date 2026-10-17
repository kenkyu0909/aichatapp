# Matching Reply Assistant — Windows ローカルアプリ

PC向けのローカルWeb UIに、Python (FastAPI)・SQLite・Gemini APIを接続した個人専用の返信作成支援アプリです。プロフィール・相手情報・会話履歴・識別用写真はすべてPC内に保存されます。ログイン機能・外部サーバー送信（Gemini API呼び出しを除く）・自動送信機能はありません。

## 1. 取得とWindowsでの起動・終了手順

### 1.1 リポジトリの取得

検証済みブランチ（`codex/full-system-verification`、またはマージ後の `feat/ui-local-backend-v1`）を取得します。

**Gitでクローンする場合（推奨）：**

```powershell
git clone -b codex/full-system-verification https://github.com/kenkyu0909/aichatapp.git
cd aichatapp
```

**ZIPで取得する場合：**

1. GitHubリポジトリ（`https://github.com/kenkyu0909/aichatapp`）で対象ブランチ（`codex/full-system-verification`）を開きます。
2. **Code → Download ZIP** で取得し、任意のフォルダへ展開してそのフォルダを開きます。

### 1.2 起動手順（`start.bat` / `uvicorn`）

1. **Python 3.11以降**（Windows 11では **Python 3.12.10**、CIでは **Python 3.11** で検証済み）をインストールします。Python Launcher (`py`) がある場合は利用可能なPython 3が自動選択されます。
2. フォルダ内の **`start.bat`** をダブルクリック（またはPowerShell/コマンドプロンプトから `.\start.bat` を実行）します。
   - 初回起動時は `.venv` 仮想環境の作成、必須ライブラリの導入（`requirements.txt`）、`.env.example` から `.env` の作成が自動で行われます（初回のみインターネット接続が必要です）。
   - すでに `.venv` がある場合、`start.bat` は主要モジュール（`fastapi`, `uvicorn`, `PIL`, `google.genai`）の `import` 確認のみを行います。検証済みバージョンへ明示的に揃える場合は「5. 検証済み環境・開発・テスト」のコマンドを実行してください。
3. `scripts/start_server.py` がサーバーを `127.0.0.1` 限定で前面起動し、`/api/status`（`app_id: "matching-reply-assistant"`）の応答確認後にFirefoxで **http://127.0.0.1:8765/** を開きます（Firefoxが見つからない場合は手動でURLを開いてください）。
   - 8765番ポートで既にこのアプリが起動している場合は既存アプリのURLを開きます。
   - 別のプログラムがポートを使用している場合は、既存プロセスを停止せずに案内を表示して終了します。
   - ポート番号を変更する場合は、起動前に環境変数 `MRA_PORT`（例：`$env:MRA_PORT="8000"`）を設定してください。
4. 右上の「⚙ 設定」から「架空の相手を2人追加して試す」を押すと、実際の個人情報なしで全機能を操作確認できます。

**コマンドラインから直接 `uvicorn` で起動する場合（開発・別ポート検証用）：**

```powershell
# 既定ポート（8765）で起動する場合
.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8765

# ポート8000等で起動する場合
.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000
```

### 1.3 終了手順

1. 起動用の黒い画面（ターミナル／コマンドプロンプト）をアクティブにし、**`Ctrl+C`** を押します。
2. `start.bat`（`scripts/start_server.py`）経由で起動している場合、サーバー停止処理の後にポート解放が確認され、`Stopped. Port 8765 no longer accepts connections.`（別ポート指定時は該当ポート番号）と表示されて安全に終了します。
3. バックアップや復元の前には、必ずこの表示が出てサーバーが完全停止したことを確認してください。

## 2. Gemini APIを使う

APIキーがない状態でも、相手の登録・写真管理・会話履歴の編集・候補表示の操作確認が可能です（未設定時は `LOCAL · DEMO` となり、**会話を解析しない固定サンプル**を返します）。

1. Google AI Studioで発行したAPIキーを、アプリフォルダの隣にある `API/chat1.md` と `API/chat2.md` へ保存します（または `.env` の `MRA_API_1_KEY` / `MRA_API_2_KEY` に設定します）。アプリはGoogle APIキーのみを読み込み、キーの実値を画面やログに表示しません。`MRA_API_DIR` でAPIファイル保存先フォルダを変更することもできます。
2. 起動中のアプリを `Ctrl+C` で停止し、再度起動します。
3. 生成は **API1の `gemini-3.5-flash-lite`** から開始します。レート制限・利用上限を示す HTTP 429 または `RESOURCE_EXHAUSTED` の場合のみ、**API1 (3.5) → API2 (3.5) → API1 (`gemini-3.1-flash-lite`) → API2 (3.1)** の順にフォールバックします。認証・権限・モデル不在・通信エラーでは別APIへ切り替えず、エラー理由を表示します。

APIキーは指定された2つのAPIファイル、または `.env` の `MRA_API_1_KEY` / `MRA_API_2_KEY` からのみ読み込みます。汎用環境変数 `GEMINI_API_KEY` や他の認証情報へは自動的に切り替えません。また、環境変数 `MRA_USAGE_LEDGER_LIMIT` と `MRA_USAGE_LEDGER_WINDOW`（`hour` / `day` / `week` / `month` / `none`）を設定すると、SQLiteの `api_usage` テーブルで期間内のプロバイダー試行回数を予約・上限管理できます。

無料枠のモデル・プロジェクト・レート制限は [公式料金表](https://ai.google.dev/gemini-api/docs/pricing) と [AI Studio](https://aistudio.google.com/rate-limit) で確認してください。**すでに課金が有効なGoogleプロジェクトの料金上限や請求状態を、このアプリは自動的に管理しません。** 無料運用を行う場合は、課金を有効化していないプロジェクトのAPIキーを使用してください。

## 3. 主な機能（4つの生成モードと本人情報確認）

- **自分のプロフィールの登録・構造化保存**：名前・年齢・居住地域・仕事・趣味・性格・話し方の好み・希望する関係・自己紹介メモ・避けたい表現（`avoid`）、および確認済み事実（`confirmed_facts`）をJSON形式で保持
- **相手の管理**：相手の名前・プロフィール文・識別用写真（JPEG / PNG / WebP、最大5MB・16MP以下）の登録・編集・削除、相手ごとの下書き保持
- **会話履歴の管理**：相手・自分のメッセージ登録、履歴の編集・削除、送信済み文の一覧とコピー
- **4つの生成モード**：
  1. **初回メッセージ（`first`）**：登録済みの相手で会話履歴が0件のとき、挨拶・好意・マッチの喜び・相手プロフィールの話題・答えやすい質問1つを含む初回メッセージ候補を生成
  2. **通常返信（`reply`）**：相手の最新メッセージに対する返信候補（1・3・5案、文体・方向性・追加指示・会話方針の表示に対応）を生成。相手の直接質問への回答を最優先し、文量・テンションをミラーリング
  3. **追いメッセージ（`followup`）**：自分の発言の後に相手から返信がない場面で、返信を催促せず相手の拒否や温度感を尊重した追いメッセージ候補と会話方針を提案
  4. **メッセージ付きいいね（`like`）**：マッチ前の相手のプロフィール文と任意の名前をモーダルに貼り付け、相手登録なしでアプローチ文3案を生成
- **本人情報の確認フォーム（捏造防止・必須確認／任意確認）**：
  - **必須確認（`needs_user_info`）**：相手からの直接質問（経験・好み・頻度・予定・誘いへの意思など）に対し、プロフィールや確認済み事実に根拠がない場合、未確認の本人事実を創作せず確認質問を表示します。「回答して再生成」「回答してプロフィールにも保存」「回答せず再生成（スキップ）」を選択できます。
  - **任意確認（`optional_user_questions`）**：安全な候補を表示できる場合でも、本人の情報を少し補うとより自然になる場面では候補カードの下に任意質問を表示します（回答はその場の再生成にのみ使用します）。
- **フォーマット・安全検査**：句読点（「、」「。」）禁止、1文1行（空行なし）、未確認の本人事実や相手情報の創作除外、相手の拒否後の無理な誘い防止
- **手動送信記録**：候補をコピーしただけでは履歴に追加されず、実際に送った文章だけを「自分（送信済み）」として履歴に記録

## 4. 保存・プライバシーとバックアップ／復元手順

### 4.1 データの保存先とプライバシー

- アプリのサーバーは `127.0.0.1`（ローカルループバック）のみを待ち受け、Hostヘッダー許可リスト（既定：`127.0.0.1,localhost`）で保護されています。
- 永続データは **`data/app.sqlite3`**（SQLiteテーブル：`profile`［`content` JSON内に `confirmed_facts` を保持］、`matches`、`messages`、`orphaned_photos`、`api_usage`）および **`data/photos/`**（相手の識別用写真ファイル）に保存されます（いずれもGit追跡対象外）。
- 保存先ディレクトリを変更する場合は、`.env` または環境変数 **`APP_DATA_DIR`** に絶対パスを指定します（既定値：リポジトリ直下の `data/`）。
- **APIキー（`.env` や `API/chat1.md`・`API/chat2.md`）は `data/` フォルダ内には保存されません。** `.env` や `data/` をGitHubへコミット・公開しないでください。
- Gemini API生成時には、自分のプロフィール・対象相手のプロフィールと名前・対象相手の直近会話コンテキスト・生成オプションのみを送信します。**識別用写真、ファイルパス、他の相手の会話履歴は送信しません。**
- **Gemini APIの無料枠へ送信した入力データは、Googleの製品改善に使用される場合があります。** 必要に応じて個人情報の匿名化を行ってください。

### 4.2 会話JSONエクスポートと完全バックアップの違い（重要）

画面下部の「JSON出力」ボタンは、**現在選択している相手1人分の名前・相手プロフィール・会話履歴（`matching-chat-<id>.json`）のみを書き出す機能**です。自分のプロフィール（`confirmed_facts` や `avoid` を含む）、他の相手のデータ、識別用写真（`data/photos/`）は含まれないため、完全なバックアップ・復元には以下の **`data/` フォルダ停止後バックアップ手順** を使用してください。

### 4.3 オフライン `data/` バックアップ手順

1. **サーバーを完全停止する**：起動中の画面で `Ctrl+C` を押し、`Stopped. Port 8765 no longer accepts connections.` と表示されるまで待ちます（稼働中のコピーはSQLiteの書き込み競合を招くため避けてください）。
2. **`data/` ディレクトリ全体をコピーする**：`data/app.sqlite3` と `data/photos/` をまとめてバックアップ先へコピーします。

```powershell
# PowerShellでのバックアップ例（アプリ停止後にリポジトリ直下で実行）
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item -Path .\data -Destination ".\backup_data_$stamp" -Recurse
```

### 4.4 オフライン `data/` 復元手順と整合性確認（復元テスト）

1. **サーバーが停止していることを確認する**。
2. **既存の `data/` を退避し、バックアップから復元する**：

```powershell
# 現在のdataフォルダを念のため退避し、バックアップを復元する例
if (Test-Path .\data) { Move-Item -Path .\data -Destination .\data_before_restore -Force }
Copy-Item -Path .\backup_data_YYYYMMDD_HHMMSS -Destination .\data -Recurse
```

3. **起動前のデータベース・JSON整合性確認**：
   復元した `data/app.sqlite3` のSQLite整合性（`PRAGMA integrity_check`）と、データベース内に保存されている自分のプロフィールJSON（`profile.content`）が破損していないことを以下のコマンドで確認できます。

```powershell
.\.venv\Scripts\python.exe -c "import json, sqlite3; conn = sqlite3.connect('data/app.sqlite3'); assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'; raw = conn.execute('SELECT content FROM profile WHERE id = 1').fetchone()[0]; (json.loads(raw) if raw.strip().startswith('{') else None); print('OK: SQLite integrity and profile JSON verified')"
```

   個別に出力した会話JSONファイル（`matching-chat-*.json`）の構文整合性を確認する場合は以下を実行します。

```powershell
.\.venv\Scripts\python.exe -c "import json, pathlib; [json.loads(p.read_text(encoding='utf-8')) for p in pathlib.Path('.').glob('matching-chat-*.json')]; print('OK: Exported JSON files verified')"
```

4. **復元後の起動確認**：
   `start.bat` でアプリを起動し（または一時確認用に `$env:APP_DATA_DIR="C:\path\to\backup_data"` と別ポート `$env:MRA_PORT="8766"` を指定して起動し）、自分のプロフィール・相手一覧・写真・会話履歴が正しく表示されることを確認します。なお、`.env` や `API/chat1.md`・`API/chat2.md` のAPIキーは `data/` に含まれないため、別PCへ移行する場合は別途配置してください。

## 5. 検証済み環境・開発・テスト

### 5.1 検証済みPython・パッケージバージョン

- **対応確認済みPythonバージョン**：
  - **Python 3.12.10**（Windows 11 ローカル検証環境：全オフライン回帰・Firefox UIテスト通過）
  - **Python 3.11**（GitHub Actions `ubuntu-latest` オフラインCI環境）
  - ※Python 3.13は `start.bat` のバージョン条件（3.11以上）を満たしますが、現時点の自動テストスイートでは未検証です。
- **検証済み依存パッケージのバージョン組み合わせ**：
  - 実行時依存（`requirements.txt`）：
    - `fastapi==0.128.8`（`starlette==0.52.1`）
    - `uvicorn==0.46.0`
    - `pydantic==2.12.5`
    - `python-dotenv==1.2.1`
    - `python-multipart==0.0.27`
    - `google-genai==1.75.0`
    - `pillow==12.1.1`
  - テスト依存（`requirements-test.txt`）：
    - `pytest==9.1.1`
    - `httpx==0.28.1`
    - `selenium==4.51.0`（およびMozilla Firefox / Node.js `v25.9.0` で `node --check app.js` を確認済み）

検証済みバージョンを固定して導入する場合は以下を実行します。

```powershell
python -m pip install fastapi==0.128.8 uvicorn==0.46.0 pydantic==2.12.5 python-dotenv==1.2.1 python-multipart==0.0.27 google-genai==1.75.0 pillow==12.1.1 pytest==9.1.1 httpx==0.28.1 selenium==4.51.0
```

### 5.2 主なファイル構成とテスト実行

- `index.html` / `style.css` / `app.js`：画面とUI操作（プロフィール保護・相手別下書き管理・生成リクエスト競合防止を含む）
- `app.py`：FastAPI・SQLite・Gemini接続・本人事実確認・候補検査
- `prompts/common.txt` / `first.txt` / `reply.txt` / `followup.txt` / `like.txt`：共通規則と4モード別プロンプト
- `start.bat` / `scripts/start_server.py`：Windows用の起動・準備確認・終了スクリプト
- `scripts/quality_eval.py` / `scripts/run_quality_checks_009.py`：独立採点モジュールと品質確認ランナー
- `.env.example`：環境変数の設定例
- `tests/test_app.py` / `tests/test_ui_firefox.py`：架空データと一時SQLiteを使うオフラインAPIテスト・Firefox UIテスト

架空データによるオフラインテスト実行（本番の `data/` は変更されません）：

```powershell
python -m pip install -r requirements.txt -r requirements-test.txt
python -m pytest -q
node --check app.js
```

## 6. GitHub PagesのUIデモとの区別

[既存のUIデモ](https://kenkyu0909.github.io/aichatapp/) は `design/ui-only-v1` ブランチの静的デモであり、ローカルバックエンドやSQLite・Gemini APIには接続されません。**本アプリはPC内で `start.bat` を起動し、http://127.0.0.1:8765/ から使用します。**

