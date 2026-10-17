# Claude向け開発引き継ぎ資料（2026-10-17）

この文書は Matching Reply Assistant（個人用ローカルアプリ）の開発を Claude へ引き継ぐための資料です。作成時点で作業は切りのよいところで停止しています。未コミット差分はありません。

対象リポジトリ: `C:\Users\poiuy\desktop\aichatapp2\verification-repo`
作業ブランチ: `codex/full-system-verification`（PR #4 → `feat/ui-local-backend-v1`、OPEN/Draft、未マージ維持）

## 1. 現在の状態（この文書が最新の基準）

- コードHEAD: `916ec41`（T440）。docs HEAD: `f84c95f`（T439/T440記録）。
- 作業ツリーはクリーン。未追跡は保護対象の3ファイルのみ。
  - `docs/verification/simulations/codex_autonomous_until_1300_20261015.txt`
  - `docs/verification/simulations/codex_quality_rebuild_instructions.txt`
  - `docs/verification/simulations/指示.txt`
  - この3つはユーザー提供の未追跡ファイル。add/commit/上書きしないこと。
- 全pytest: **1901 passed**（Windows、約6.5〜7分。`python -m pytest`。`pytest.exe`は使えない）。
- CI（すべて success）:
  - `c145368`（T438）: Push https://github.com/kenkyu0909/aichatapp/actions/runs/39012335427 / PR https://github.com/kenkyu0909/aichatapp/actions/runs/39012446977
  - `da8ba20`（T439）: Push https://github.com/kenkyu0909/aichatapp/actions/runs/39013957467 / PR https://github.com/kenkyu0909/aichatapp/actions/runs/39013960710
  - `916ec41`（T440）: Push https://github.com/kenkyu0909/aichatapp/actions/runs/39015113395 / PR https://github.com/kenkyu0909/aichatapp/actions/runs/39015116861
  - `f84c95f`（docs）: Push https://github.com/kenkyu0909/aichatapp/actions/runs/39015159289 / PR https://github.com/kenkyu0909/aichatapp/actions/runs/39015162524
- 総合判定は引き続き**条件付きGO**（多様性ゲートの決定性など未確認項目が残る）。
- agmsg: チーム `chat`、当方エージェント名 `ds4`、glm=`glm`、Claude=`claude`（type claude-code, project aichatapp2）。送信例は末尾。

## 2. 直近で完了した作業（T438〜T440）

詳細は `docs/verification/{PROGRESS,TEST_MATRIX,FINAL_REPORT}.md` の2026-10-17項を参照。

- **T438**（`c145368`）: アプリ自身が尋ねた確認質問に回答しても、相手文と確認質問のスコープ分類が食い違うと同じ質問を無限再発する欠陥を修正。`_topic_is_verified` の末尾で「アプリ自身が尋ねた確認質問への回答」を検証済み扱いに。カレー頻度のひらがな頻度語も補完。
- **T439**（`da8ba20`）: 返信の相槌・質問量を改善。
  - ミラーリングの文数推定が句読点付きの相手文を1文と数えていた（`SENTENCE_BOUNDARY_PATTERN` が「。」を見ない）ため、2文の相手に2行しか返せず、相槌か質問が必ず欠落していた。`estimate_message_style` 内の `sentence_estimate` に `[!?！？。．]` を追加。
  - 相槌と質問を併せ持つ返信に限り、文量上限を1行緩和（最大3行）。`_candidate_is_acknowledgment_plus_question` / `_candidate_exceeds_mirrored_length`。
  - `prompts/common.txt` を「新情報には相槌を1つ」「相手が既に答えた話題・深い相談・拒否・別れ際を除き、原則どの候補にも質問を1つ」へ変更。
- **T440**（`916ec41`）: `_ephemeral_answer_addresses_question` を追加し、topic別分岐で臨時回答を照合する箇所を置換。アプリ自身の確認質問への回答が照合されない再発（休日トピックで実測）を解消。回帰テスト追加。

## 3. 会話テスト（実API）の成果物

リポジトリ外、`C:\Users\poiuy\desktop\aichatapp2\会話テスト\` にあります。

- `run20.py`: 20通ドライバ。サブコマンド `start [--partner <開始文>] [--force]` / `turn [--first] [--partner <返信>] [--append-partner <追加発話>] [--select N] [--direction ...] [--answer <回答>] [--drop-pending] [--attempts N]` / `reset` / `profile` / `render` / `status`。
  - **初回はアプリ側から**: `start`（相手文なし）→ `turn --first`（mode=first）。
  - プロフィールはWeb UIと同じJSON形式（name/age/area/job/hobbies/personality/style/goal/memo）で保存。プレーンテキストだと構造化factsが空になり確認がループする。
  - `blocks[]` に停止理由、`conversation_test.html` に全候補と停止理由を出力。
- `conversation_test.json` / `conversation_test.html`: 直近の実API 20通。アプリ側プロフィール=水野そよか、相手役=黒川いつき。
- `probe.py`: 内部判定の切り分け（`probe_out.json` 出力、API消費なし）。
- 直近結果: 20/20、`LIMIT_REACHED`、候補停止8回（直接質問に未回答7 / 未確認の本人事実6 / 禁止句読点5 / 長すぎる候補1。1回に複数理由が付く）。相槌と質問がほぼ全候補に入った。

ユーザーからの直近フィードバック（今後も満たすこと）:
- 初回はアプリ側から話しかける。初回メッセージ条件は `prompts/first.txt`（挨拶＋主観的な軽い好意＋マッチできた喜び＋相手プロフィールの話題1つ＋答えやすい質問1つ、句読点禁止、😊/☺️を1つ、名前があれば使用）。
- 相手役（テストの相手）は基本質問しない。するなら5回に1回程度。
- 相槌（そうなんですか/そうなんですね等）を入れる。アプリ側の質問を増やす。

## 4. 次にやるべき作業（優先順）

### 4.1 未知WH質問のデッドエンド解消（ユーザー承認済み・未実装）

**症状**: 分類できない直接質問（`_topic_for_personal_question` が `本人情報` を返すもの。例「横浜でよく散歩される場所はありますか？」「静かな店とにぎやかな店どちらが好みですか？」）で、ユーザーが回答しても候補が全滅し、`生成を停止` のまま前進しない。実測2件（散歩場所、喫茶店の好み）。

**原因**: `_answers_verified_single_partner_question`（app.py 6326）→ `topic == "本人情報"` の最終ブロック（6679〜6754）で、候補の各節が回答と**逐語一致**（`answer_clause == normalized_answer`、6744）でないと `return False`。モデルは言い換えるため一致しない。`not topic` 側（6373〜6388）も逐語部分一致要求。

**検討したが却下した案**: 語彙重なり（内容語の一致率）で緩和。**実装して全pytestにかけたところ4件の正確性テストを壊したため破棄済み**（否定文「〜とは言えません」を回答として受理、値を追加した「英語と韓国語」を受理、値だけ違う「7時→8時」を受理）。この系統の緩和は安全保証を壊すので再導入しないこと。

**採用する案（ユーザー承認: 決定的フォールバック）**: ガードは維持したまま、ユーザーが回答済みでモデル候補が全滅したときだけ、サーバーが「相槌＋回答の逐語引用＋質問」の送信候補を決定的に1件組み立てる。

実装上の注意（重要）:
- 挿入点の候補は `generate()`（app.py 7560）。候補の絞り込みは `filter_safe_candidates`（7329、呼び出しは約7812/7815）。停止時の分岐は約8394〜8479（`blocking_reason` は約7539で設定）。
- 生成したフォールバック候補は `_candidate_rejection_reasons`（7154）を必ず通すこと。満たすべき条件: 本文に「、」「。」を含まない / 1文1行（空行なし） / プレースホルダーなし / 「相手からの直接質問に未回答」を出さない（回答を逐語で含める）/ 未確認の本人事実を足さない / 空行なし。
- 注意: ユーザーの回答には通常「。」「、」が含まれる。候補本文では禁止のため、句読点を除去する必要がある。`_answers_verified_single_partner_question` の照合は句読点を除去して比較するため、句読点を除いた同一文字列なら逐語一致で通る見込み。ただし回答を複数行に分割すると各節が回答全体と一致しなくなるため、回答本体は1行にまとめる。長期の1行は `candidate_has_missing_sentence_break`（5605）に掛かる可能性があるため、必ずオフライン単体テストで `_candidate_rejection_reasons` の戻りが空になることを確認する。
- 相槌は既存の許容語（例「そうなんですね」）を使い、質問は相手向けの追加質問で未確認事実を含めない。
- 期待する回帰テスト: (a) 未分類WH質問＋回答ありで、フォールバック候補が `_answers_verified_partner_question` を通り `_candidate_rejection_reasons` が空。(b) 回答が無い場合はフォールバックを出さない（従来どおり確認質問）。(c) 既存の `test_generic_confirmed_answer_does_not_ground_later_personal_claims` など正確性テストが引き続き通る。

### 4.2 その他の未着手（`docs/verification/DEEPSEEK_HANDOFF.md` の D項目）

- **D16**: READMEの取得先・起動終了・バックアップ/復元・検証済み依存組合せの整合。
- **D17**: 停止後dataバックアップ手順と復元テスト。
- D01〜D15 の残課題は DEEPSEEK_HANDOFF.md の第5章以降を参照（本人事実の見逃し、確認の取り違え、プロフィール項目消失、下書き持ち越し、古い生成結果の上書き等）。T434〜T436でD11の一部（利用台帳・原子性・要求期限）は対応済み。

## 5. 実装の地図（重要な関数と目安行番号・コードHEAD `916ec41`）

- `app.py`（8458行前後）。行番号は編集でずれるため関数名で再確認すること。
  - `_ephemeral_answer_addresses_question`（約1386）: アプリ自身の確認質問への回答照合。
  - `estimate_message_style` 内 `sentence_estimate`（約4962）: 「。．」を文末として数える。
  - `_topic_is_verified`（約1709〜）: トピック別の検証。カレー頻度（約1887）、旅行最近（1696）、休日（約2098）、本人情報（1956）、末尾の一般照合（約2160）。
  - `missing_personal_fact_question`（約2187）: 事前確認。本人情報は約2238。
  - `_candidate_sentence_count` / `_candidate_is_acknowledgment_plus_question` / `_candidate_exceeds_mirrored_length`（約7027〜7089）。
  - `_candidate_rejection_reasons`（7154）: 候補検査の集約。停止理由の文字列はここ。
  - `filter_safe_candidates`（7329）。
  - `generate`（7560）、停止・フォールバック分岐（約8394〜8479）。
  - `_answers_verified_single_partner_question`（6326）、本人情報の逐語一致（6744）。
  - `personal_fact_question`（新規: 約2238以降にある topic 別の確認質問生成）。
- `prompts/`: `common.txt`（共通＋文体＋段階）、`first.txt`（初回5要素）、`reply.txt`、`followup.txt`、`like.txt`。
- `app.js`: プロフィールは `:613-617`、`PUT /profile` は `:644`。
- `tests/test_app.py`（13700行超）: 追加した回帰は `test_hiragana_curry_frequency_answer_verifies_the_topic`、`test_answer_to_app_clarification_verifies_topic_across_scope_mismatch`、`test_reply_length_guard_allows_acknowledgment_and_question_for_two_sentence_partner`、`test_reply_length_guard_still_caps_acknowledgment_without_question`、`test_punctuated_partner_message_counts_sentences`、`test_shared_prompt_requires_acknowledgment_and_a_question`、`test_answer_to_app_weekend_clarification_verifies_across_scope_mismatch` 付近。
- `scripts/quality_eval.py` / `scripts/run_quality_checks_009.py`: D09の独立採点器と009ランナー（T431〜T433、T437）。

## 6. 守る制約・運用

- 応答は敬語のみ。
- Gemini実APIは小規模な品質確認のみ。無制限再試行禁止。キーは `aichatapp2\API\chat1.md`（API1）/`chat2.md`（API2）、`.env` の `MRA_API_1_KEY`/`MRA_API_2_KEY`。**キー実値は表示・保存禁止**。フォールバックは API1/3.5 → API2/3.5 → API1/3.1 → API2/3.1 の順、429/RESOURCE_EXHAUSTEDのみ。
- `verification-repo` 内に `conversation_004` や新しい会話HTMLを作らない（会話テストはリポジトリ外の `会話テスト` フォルダで実施）。既存 `quality_checks_009.json` は上書きしない（`MRA_QUALITY_OUTPUT` で別ファイルへ）。
- 指示ブランチ `codex/directive-control` は fetch + `git show` のみ。merge/cherry-pick 禁止。
- commit/push は30〜60分単位。PROGRESS/TEST_MATRIX/FINAL_REPORT を更新し、最新SHAのActions URLを記録。
- テスト: `python -m pytest`（`pytest.exe`不可）。全pytestは約6.5〜7分、Firefox UIが支配的。focusedは `-k`。`pytest-repeat` 未導入で `--count` 不可。
- 既知フレーク: `tests/test_ui_firefox.py::test_firefox_oversize_photo_is_rejected_before_creating_contact` が稀に `TimeoutException`（単体再実行でpass）。
- 環境: Windows + pwsh、Python 3.12.10、pytest 9.1.1、node v25.9.0、selenium 4.51.0、gh 2.98.0。`rg`/`rtk` 無し（`read`/`grep`/`glob` を使う）。
- 落とし穴:
  - pwshの `python -c "..."` は波括弧・和文・`%` で壊れる。一時ファイル（`C:\Users\poiuy\AppData\Local\Temp\opencode\*.py`）へ書いてから実行する。
  - `edit` は旧文字列が複数一致だと失敗。周辺文脈を増やす。編集後は `py_compile` と該当テストで確認。
  - 書込み毎に `jp-quality` が `can't open file '...jp-quality\check.py'` を出す（無視可）。gitはLF→CRLF警告（無害）。
  - Windowsパスは大文字小文字を無視（`desktop`/`Desktop` どちらでも可）。

## 7. 検証コマンド

```powershell
# リポジトリ
cd C:\Users\poiuy\desktop\aichatapp2\verification-repo
git fetch origin refs/heads/codex/directive-control:refs/remotes/origin/codex/directive-control
git show origin/codex/directive-control:docs/verification/CODEX_CONTINUOUS_DIRECTIVE.md
python -m pytest -q                     # 全件（約6.5-7分）
python -m pytest tests/test_app.py -k "verified or personal_fact or clarification or length_guard" -q

# 会話テスト（実API。小規模に）
$f = "C:\Users\poiuy\desktop\aichatapp2\会話テスト\run20.py"
python $f reset
python $f start
python $f turn --first --attempts 4
python $f turn --partner "<相手役の返信>" --attempts 4
python $f render

# agmsg（claudeへ送る場合）
& "C:\Program Files\Git\bin\bash.exe" -lc 'cd /c/Users/poiuy/.agents/skills/agmsg/scripts && AGMSG_AGENT=ds4 bash send.sh chat ds4 claude "<本文>"'
```

## 8. 着手時の最短手順

1. `git status` と `git log --oneline -5` でHEADが `f84c95f`（コード `916ec41`）であることを確認。未追跡の3ファイルを壊さない。
2. `docs/verification/PROGRESS.md` の2026-10-17項、`TEST_MATRIX.md` の最新ID行（440）、`FINAL_REPORT.md` の同日項を読む。
3. `python -m pytest -q` で1901 passedを再確認（基準の固定）。
4. 4.1 の決定的フォールバックを実装し、回帰テストを追加 → focused → 全pytest → commit/push → CI確認 → PROGRESS/TEST_MATRIX/FINAL_REPORT更新。
5. 次に D16 README（またはユーザー指定の優先）へ進む。

ユーザー判断が必要なのは、新しいAPI利用枠、別プロバイダー、課金・秘密設定の変更、本番データの削除/不可逆移行、会話004/新HTML、PRマージなど。通常のローカル修正・一時データ検証・進捗保存で逐一止まらない。
