# HANDOFF — 継続開発の引き継ぎ（ds4 → 次担当 / 別PC）

作成: 2026-10-20 JST。作業ブランチとDraft PRの制約は下記のとおり。

## 1. リポジトリとブランチ

- リポジトリ: `https://github.com/kenkyu0909/aichatapp.git`
- 作業ブランチ: `codex/full-system-verification`
- Draft PR #4: OPEN / Draft / 未マージ（base `feat/ui-local-backend-v1`）。**マージ禁止**。
- 指示ブランチ（読み取り専用）: `codex/directive-control` の `docs/verification/CODEX_CONTINUOUS_DIRECTIVE.md` を15〜20分ごとに `git fetch` / `git show` で確認する。作業ブランチへ merge / rebase / cherry-pick しない。
- このドキュメント commit 以降の最新SHAは `git log --oneline -1` で確認する。

```bat
git fetch origin
git switch codex/full-system-verification
git pull --ff-only
git log --oneline -12
```

## 2. 現在の到達点（T500〜T507）

| Task | commit | 内容 | 状態 |
|---|---|---|---|
| T500 | `cc4dceb`〜`ad8c8c4` | memo決定的リレー廃止・質問の取り違え棄却・尊敬語・相手役整合 | FIXED |
| T501 | `51af300` `815ad9a` `693a19e` `c4b7165` | 自己回答の繰り返し・ペット所有の含み・既出話題の聞き返し・遠い誘いの自然な断り | FIXED |
| T502 | `f419042` | 直接質問（勧め・二択）への未回答解消、断りの前向きな一言、札幌の再提案への前向き応答、謙譲語 | FIXED（実走確認済み） |
| T503 | `4de1437` | memoの評価語だけで別話題を答えにしていた不具合 | FIXED |
| T504 | `23c8153` | 相手が答えた活動の聞き返し・猫への外歩き質問を棄却 | FIXED |
| T505 | `08c3f7d` | 断りの前向きな一言が承諾矛盾ガードで落ちる不具合 | FIXED |
| T506 | `ac2dd56` | 週末・普段などの習慣文を答えた話題として再質問を棄却 | FIXED |
| T507 | `ea504c9` | 外食と述べた相手へのお弁当質問を棄却・「分かります」連結検出 | FIXED |
| docs | `2cd1937` `cf886fb` | PROGRESS / TEST_MATRIX 記録 | 済 |

- 直近で最も良い実走は **t505**: アプリ送信20 / 相手19 / `LIMIT_REACHED` / 候補停止0 / 要求31、主指標（相手が話した11ターン）第1候補 **100.0%**、全候補 **100.0%**。代表HTMLはt505版（下記5参照）。
- t506 の実走は Gemini の 503/504 連続で17通 `BLOCKED`（コード不具合ではない）。

## 3. テスト

- 仮想環境: `verification-repo\.venv`（Windows / Python 3.12）。
- 全pytest:

```powershell
$env:GEMINI_MODEL="gemini-3.5-flash-lite"
.\.venv\Scripts\python.exe -m pytest tests -q
```

- 現状: Firefox UI を除くと **2048 passed**。`tests/test_ui_firefox.py` は単独実行で **29 passed**（一括実行時に Selenium タイムアウトが1件出ることがある環境依存）。
- 構文検査: `python -m py_compile app.py`、`node --check app.js`、`git diff --check`。
- 変更後は GitHub Actions（`Local app offline tests`）の Push / PR の両方が success か確認する。

## 4. 20通の実会話テスト（ハーネスはリポジトリ外）

- ハーネス: `C:\Users\poiuy\desktop\aichatapp2\会話テスト\scripts\`（`run_keigo20_t499.py`, `run20.py`）。**リポジトリには含めていない**。
- 実行:

```powershell
# workdir: C:\Users\poiuy\desktop\aichatapp2\会話テスト
$env:CONV_SUFFIX="t508"
$env:GEMINI_MODEL="gemini-3.5-flash-lite"
& "C:\Users\poiuy\desktop\aichatapp2\verification-repo\.venv\Scripts\python.exe" scripts\run_keigo20_t499.py
```

- 生成物: `conversation_test_keigo20_ds4_<suffix>.html` / `json\conversation_test_keigo20_ds4_<suffix>.json`。代表は `conversation_test.html` / `json\conversation_test.json` へ上書きする。
- 台本の相手行と `SAVED_ANSWERS` は `run_keigo20_t499.py` 内。新しい観点を足すときはここを編集する。
- Gemini は無料枠（500/日/キー、`API\chat1.md` / `chat2.md`）で、モデル側の 503/504 が続くことがある。その場合は追加通信を止め、時間を空けて再実行する。

## 5. リポジトリへ入れないもの（重要）

PUBLIC リポジトリのため、以下は **commit / push しない**。

- 個人情報: 旧アプリの本人名・会話・プロフィール・アンケート、`会話テスト\data\`（`self_profile_S.json` / `user_survey_answers.json` / `user_facts_from_legacy.json`）。
- 実会話の HTML / JSON（本人プロフィールを埋め込んでいるため）。代表 `conversation_test.html` / `json\conversation_test.json` も含む。
- API キー類（`API/` は `.gitignore` 済み。`data/`, `*.sqlite3`, `.env` も除外）。

別PCで続ける場合は、これらを**リポジトリ外の安全な手段で私的にコピー**する（例: `会話テスト\` フォルダごと、`API\` フォルダ、`.venv` は再作成）。テストコードは架空データのみを使う。

## 6. 次のタスク（T508候補）

1. 相手の状況と食い違う質問の一般化（T507はお弁当×外食の1パターン）。例: 相手が「外食」と述べた話題に対し、別の前提を置く質問をしない。
2. 相槌と本文が区切りなく連結する事例の残り（T507で「分かります」は検出追加。他の相槌語も同様に確認）。
3. プロフィール・確認済み回答にない具体名（サービス名・店名など）を質問の前提に置く事例の点検。
4. t505 以降の変更（T506/T507）を含む20通を再走行し、代表を更新する。

## 7. 制約（変更なし）

- PR #4 は Draft のまま、マージ・Ready化しない。
- `conversation_004` と新規会話HTMLの作成は、ユーザーの明示許可があるまで行わない（既存HTMLの閲覧は可）。
- テスト・回帰は**架空データ**で書く。個人情報を diff に入れない。
- `git add -A` を使わない（ファイルを明示して add）。
- Firefox を使う（Chrome を起動しない）。
- Gemini 実APIは無料枠を超えない。上限後はオフライン作業へ切り替える。
- 「完成」と断定せず、近い点・遠い点・残る点で記録する。

## 8. 参考ドキュメント

- `docs/verification/PROGRESS.md` — 変更履歴（最新は T500〜T506 の節）
- `docs/verification/TEST_MATRIX.md` — 検証マトリクス（最新ID行: 506）
- `docs/verification/CLAUDE_HANDOFF_20261017.md` / `DEEPSEEK_HANDOFF.md` — 過去の引き継ぎ
- リポジトリ外: `会話テスト\reports\ds4_T500_report.md` 〜 `ds4_T505_report.md`（実走メモ）
