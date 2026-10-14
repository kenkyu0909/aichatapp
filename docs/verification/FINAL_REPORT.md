# 最終検証報告（2026-10-14 会話シミュレーション追加）

## 2026-10-14 返信品質・初回メッセージ・会話制御の最終報告

### 総合判定

**CONDITIONAL PASS（条件付き合格）**。プロンプト構造、FastAPI応答契約、会話シミュレーター、Firefox UIのオフライン検証は成功しました。ただし、今回の指示によりGemini実APIを呼んでいないため、自然な日本語、候補の多様性、誘い判断の実モデル品質は未評価です。Windowsの`start.bat`も実際には起動しておらず、静的条件の確認に限ります。

### テスト集計

- テストマトリクス: **71項目** — PASS 66 / FAIL 0 / BLOCKED 3 / NOT_TESTED 2。
- pytest: **103 passed, 1 warning**。警告はStarlette/httpxの非推奨通知です。
- Firefox UI: 3件成功。質問、回答、スキップ、初回候補、会話方針、コピー、手動送信記録を架空データと固定APIモックで確認。
- JavaScript構文: `node --check app.js` 成功。
- 差分整合: `git diff --check` 成功。
- GitHub Actions: 実装HEAD `5954b06c418158a48c60aa57b55e17f47a52c54a`のPush [run 38536298397](https://github.com/kenkyu0909/aichatapp/actions/runs/38536298397)とPR [run 38536305576](https://github.com/kenkyu0909/aichatapp/actions/runs/38536305576)が成功。最新の完了済みPR HEAD `ef5f232a1ec6b10d07396f2a704dd419923549f2`もPush [run 38536709582](https://github.com/kenkyu0909/aichatapp/actions/runs/38536709582) / PR [run 38536717824](https://github.com/kenkyu0909/aichatapp/actions/runs/38536717824)で成功。最終の進捗記録はドキュメントのみ。最新ブランチのrun一覧は[Actions](https://github.com/kenkyu0909/aichatapp/actions/workflows/test.yml?query=branch%3Acodex%2Ffull-system-verification)。
- 実Gemini API: 0回（ユーザー指示による未実施）。品質評価結果は今回なし。

### 実装内容・変更ファイル

| ファイル | 内容・理由 | 確認方法 |
|---|---|---|
| `app.py` | `first`モード、構造化プロフィール、不足情報確認、回答の一時利用/スキップ終端、v2会話段階と判断出力、API試行メタデータと安全なエラー情報を追加。 | FastAPI TestClientとGemini SDKモック。 |
| `prompts/common.txt` | 事実保護、入力の信頼境界、自然な日本語、「！」・絵文字・「笑」、情報質問、Stage 1–6と誘い基準を共通化。 | 静的検査、モックテスト。 |
| `prompts/first.txt` | マッチ後初回メッセージ専用。挨拶、喜び、プロフィール話題、質問1つを指示。 | 履歴0件のモックテスト、Firefox。 |
| `prompts/reply.txt` / `prompts/followup.txt` / `prompts/like.txt` | 通常返信、追いメッセージ、マッチ前いいねの用途と禁止事項を分離。 | 各モードのプロンプト読込テスト。 |
| `app.js` / `index.html` / `style.css` | 初回生成ボタン、質問/回答/スキップ、終端状態表示、構造化会話方針、生成見出し維持。回答をプロフィールへ自動保存しない。 | Firefox/Selenium。 |
| `scripts/simulate_conversation.py` | API/モデル切替をバックエンドへ一本化、実選択メタデータを記録、20通目後の相手返信と安全停止、複数ターン合意、JSON復元とロールバックを追加。通信/JSON不確実時は結果をBLOCKED保存して自動再送しない。 | 架空データ、一時SQLite、モックテスト。 |
| `start.bat` | 既存プロセスを終了せず、固有`app_id`確認、サーバー準備後にFirefox起動。 | 静的スクリプトテスト。実起動は未実施。 |
| `tests/test_app.py` / `tests/test_conversation_simulation.py` / `tests/test_ui_firefox.py` | 新機能、異常系、制限・復元・拒否文・通信失敗・Firefox UIの回帰テストを追加。 | 全pytest 103件成功。 |
| `docs/verification/prompt_spec.md` | 仕様、禁止事項、段階、モード、架空の入力・期待返信例12件を記録。 | ドキュメント確認。期待例は実API結果ではない。 |
| `docs/verification/PROGRESS.md` / `TEST_MATRIX.md` / `FINAL_REPORT.md` | 今回の実施状況、未実施事項、結果を追記。 | GitHub push後に最終SHA/Actionsを追記。 |

### オフライン確認の結果

- 本人プロフィールがJSONなら項目を構造化し、未記載の経験・趣味・予定を作らない指示と入力を確認。相手のプロフィール補足を含む質問回答はその生成要求だけに渡し、プロフィール・会話履歴へ保存しません。
- 回答を求める質問は、返信候補と別の配列で返します。スキップ状態はAPIに明示し、同じ質問を繰り返さず、安全な候補または理由付き終端を返す契約をモックで確認しました。
- 初回メッセージを履歴0件で生成でき、メッセージ付きいいねとは別のプロンプトを使います。コピーだけでは履歴に追加せず、手動の送信記録を選んだときだけ会話へ追加します。
- 会話段階と誘い判断10シナリオのテストは構造化応答のモック試験です。モデルが実際に各判断を正しく行うかは未確認です。
- 全429では4モデルまでの試行履歴を秘密値なしで返し、シミュレーターがその応答を保存するモック試験を追加しました。認証・モデル・通信エラーでも利用者向け`detail`と安全な試行情報だけを返し、キーや生SDK例外を含めません。
- 会話シミュレーターは送信上限20通、20通目への相手返信、断り発言の保存後の`SAFETY_STOP`、日時/場所/明確な承諾の人手確認、JSON復元の事前検証とSQLiteロールバックをテストしました。
- `start.bat`がFirefoxをサーバー応答後に開くこと、固有アプリIDで既存サーバーを見分けること、ポート占有プロセスを終了しないことをスクリプトテストで確認。今回、Windowsでバッチを実行した結果ではありません。

### Gemini実APIと生成品質

実通信は行っていません。モデル名、成功数、失敗数、料金、候補文章の品質は今回の結果として記載しません。過去の実API記録は過去の検証記録であり、今回のコードの品質証明に使っていません。次回許可後に、明るい/落ち着いた/冗談/相談の架空会話で「！」・絵文字・「笑」、事実性、自然さ、段階判定、誘いの距離感を評価してください。

### 未解決事項と利用判断

- 実モデルが自然な口語、指定文体、プロフィールの事実、本人情報質問、誘い段階をどう判断するかは未確認。
- Windows `start.bat`の実プロセス起動、既存の8765番待受の識別、Firefox起動は今回未実施。静的テストだけでは実機の起動成功を保証しません。
- ローカルpytestのStarlette/httpx非推奨警告が1件残っています。
- 現時点の利用判断は**一部条件付きで実用可能**。AI未接続のモック/固定デモとUIフローは確認済みですが、実APIの回答品質とこの修正後のWindows起動は確認できていません。実送信前に本人が候補を確認し、事実と距離感を確かめる必要があります。

### GitHub

- ブランチ: `codex/full-system-verification`
- 実装コミットSHA: `5954b06c418158a48c60aa57b55e17f47a52c54a`。直近CI成功コミットSHA: `ef5f232a1ec6b10d07396f2a704dd419923549f2`。以降の最終記録更新はドキュメントのみ。
- PR #4: https://github.com/kenkyu0909/aichatapp/pull/4（Draft維持、未マージ）
- 今回のGitHub Actions: 最終記録更新直前のHEADについてPush [38536709582](https://github.com/kenkyu0909/aichatapp/actions/runs/38536709582) / PR [38536717824](https://github.com/kenkyu0909/aichatapp/actions/runs/38536717824)が成功。最終記録のみのコミット後はbranch workflow [一覧](https://github.com/kenkyu0909/aichatapp/actions/workflows/test.yml?query=branch%3Acodex%2Ffull-system-verification)で最新runを確認。
- `prompt_spec.md`: `docs/verification/prompt_spec.md`

---

## 2026-10-14 利用制限時の自動切替追加

- 通常のアプリ生成処理へ、429 / `RESOURCE_EXHAUSTED`時に限る4組の順次フォールバックを追加: API1 3.5 → API2 3.5 → API1 3.1 → API2 3.1。
- APIキーは指定されたAPIフォルダの`chat1.md`/`chat2.md`、または`MRA_API_1_KEY`/`MRA_API_2_KEY`からだけ読み込む。`GEMINI_API_KEY`等ほかの認証情報には切り替えない。値はレスポンス・ログ・Gitへ出さない。
- モックで429後の優先順、全4枠を試す上限、403での即時停止、APIファイル読込、キー非露出、空の`MRA_API_DIR`の既定動作、旧環境変数を使わないことを確認。実API呼び出しは今回なし。
- 更新後ローカルpytest: 48 passed / warning 1（Starlette/httpx deprecation）。Node構文チェック成功。マトリクス: 57項目、PASS 54 / FAIL 0 / BLOCKED 3 / NOT_TESTED 0。
- この追記は前段の会話シミュレーション結果を変更せず、アプリの次回以降の実生成動作と追加回帰テストを記録する。

## 総合判定

**CONDITIONAL PASS（条件付き合格）**。既存アプリの回帰テスト・Firefox UI検証と、会話実験ハーネスのオフラインテストは成功しました。一方、今回必須のGemini会話実験はAPI1の最初の実通信がアプリHTTP 502となり、返信候補の生成前に`BLOCKED`です。会話継続・約束成立・生成品質を確認したとは扱いません。

## テスト集計

- 最新テストマトリクス: 57件 — PASS 54 / FAIL 0 / BLOCKED 3 / NOT_TESTED 0（会話品質評価は今回実験の生成がなかったため採点せず）
- 最新pytest: `48 passed, 1 warning`（Windows Python 3.12.10、`2026-10-14`）。Starlette/httpxの非推奨警告1件。
- JavaScript構文: `node --check app.js` 成功。
- Firefox E2E: 既存の隔離DB UI回帰テストがpytest内で成功。今回作成のHTMLをFirefox 157で実際に開き、1メッセージ、両プロフィール、BLOCKED状態、未評価10項目、外部リソースなしを確認。スクリーンショット: `simulations/conversation_001_firefox.png`。
- 最新の利用制限フォールバック実装commit `d5513f620b55758cc1a22957d431f61d1a4233ec`対象のGitHub Actions: [Push 38528562779](https://github.com/kenkyu0909/aichatapp/actions/runs/38528562779)と[PR 38528568834](https://github.com/kenkyu0909/aichatapp/actions/runs/38528568834)はいずれも成功。pytest 48 passed、`node --check app.js`成功。

## 今回の実験

- 架空の本人「佐倉みなと」と相手「小川あかり」を登録。相手役の内部設定はアプリ/Geminiのプロフィール欄へ送っていない。
- API1 / `gemini-3.5-flash-lite`で実通信を1回試行。既存アプリの`/api/generate`がHTTP 502と「Gemini APIキーまたはモデルの利用権限を確認してください。」を返した。
- 実APIリクエスト試行1、成功0、失敗1。API2と3.1モデルは未使用。429応答ではなかったため、ユーザー指定のレート制限時フォールバックは発動させていない。
- APIキーまたはモデル権限・接続のどれが原因かは特定できない。根本原因が分からないため、認証失敗として他キーを試すこともしなかった。キー、生のSDK例外、認証ヘッダーはJSON/HTML/出力へ記録していない。
- 生成候補0件、アプリ側送信0通、架空相手役の開始発言1通。食事の誘いなし、日時・場所の合意なし。会話品質10項目はすべて未評価（T56 BLOCKED）。固定文やモックで結果を補っていない。
- 会話とプロフィール: `simulations/conversation_001.json`、`simulations/profiles.md`。説明: `simulations/analysis.md`。単体HTML: `simulations/conversation_001.html`。

## 8765番ポート・起動

127.0.0.1:8765を既存Uvicornプロセス(PID 39504)がlistenしているのを確認しました。既存プロセスは今回の実験用と特定できず、停止・変更していません。前回の`start.bat`再確認はWinError 10048でBLOCKED。今回のGemini試験は一時SQLiteを使ったTestClient経由で実際のFastAPI `/api/generate`を呼びました。Firefoxで開いたのは今回のHTMLファイルです。新しいWindows `start.bat`起動を今回PASSとは扱いません。

## 修正・追加したファイル

- `scripts/simulate_conversation.py`: API優先順、15 RPM間隔を超えない4.1秒待機、実アプリ生成、生成候補の永続化、段階再開、SQLite履歴照合、20通上限、相手からの明確な返答、手動確認後のみSUCCESSを追加。
- `scripts/render_conversation_report.py`: 保存済みJSONから単体HTMLを生成。
- `tests/test_conversation_simulation.py`: 19/20/21通、相手発言と未送信候補の非計上、モデル順序・429時の切替、曖昧な承諾、成功確認、プロフィール分離、HTMLエスケープを検証。
- `docs/verification/simulations/*`: 架空プロフィール、実験JSON、BLOCKEDのHTML、Firefox画像、制約を記録。
- `PROGRESS.md`、`TEST_MATRIX.md`、本報告書: 今回の結果を追記。履歴は削除していない。

## セキュリティ・プライバシー

実験はアプリ本番DBから分離した一時SQLiteです。利用者のデータや実在人物は使用していません。相手内部設定は生成APIへ渡さず、HTML文字列はエスケープし、CSSをインライン化して外部通信・外部スクリプトを使いません。前回からのポート8765プロセスは触れていません。秘密値はログ・成果物に出していません。

Googleの公式資料では`gemini-3.5-flash-lite`の無料枠と、無料枠の内容が製品改善に使われる扱いが掲載されています。プロジェクト固有の課金状態・残り枠はこの環境から確認できません。失敗したアプリHTTP 502は上流Google HTTPステータスを記録していないため、請求有無を断定しません。最新条件は[公式料金表](https://ai.google.dev/gemini-api/docs/pricing)と[公式課金説明](https://ai.google.dev/gemini-api/docs/billing)を確認してください。

## 未解決事項・利用開始判断

1. **最優先:** API1ファイルにある更新済み認証情報の有効性、プロジェクト、`gemini-3.5-flash-lite`アクセス権または接続を確認する。原因が解消した後に`--resume`で同じ隔離SQLiteの架空実験を再開できる。
2. 今回は実会話、生成品質、候補選択、デート提案のタイミング、具体的な日時・場所の合意を検証できていない。
3. API2/3.1へのライブ切替、プロジェクト別課金・無料枠残数、API1/2の旧キー失効は未確認。キー更新前にツール出力へ露出した履歴があるため、旧キーの失効を利用者側で確認する必要がある。
4. 8765番の既存プロセスが動作中のため、Windows `start.bat`の新規起動は未確認。既存プロセスを止める前に所有者と用途の確認が必要。
5. JSONとSQLite更新の間でプロセスが強制終了した場合は再開時に不一致として停止する。APIエラー後の通常再開は検証したが、強制終了の全クラッシュ地点は未試験。

この状態でアプリのローカル保存・UI機能の回帰検証は良好ですが、今回依頼の**AI会話シミュレーションを含めて正式に実用可能とは判定できません**。認証・モデル権限が解消するまでは、AI返信機能の利用を保留するのが妥当です。

## GitHub

- リポジトリ: https://github.com/kenkyu0909/aichatapp
- ブランチ: `codex/full-system-verification`
- PR #4: https://github.com/kenkyu0909/aichatapp/pull/4（Draft、未マージ）
- 検証対象SHA: `df7110205b8e522475cdcad7e08c8152ace360cb`。
- Actions Push: https://github.com/kenkyu0909/aichatapp/actions/runs/38525998484
- Actions PR: https://github.com/kenkyu0909/aichatapp/actions/runs/38526003199
- T56を含む最新の検証HEAD: `8a0097c1ad648692e6e93714b2e98e47b5e6cc43`。
- 同HEADのActions Push: https://github.com/kenkyu0909/aichatapp/actions/runs/38526380171
- 同HEADのActions PR: https://github.com/kenkyu0909/aichatapp/actions/runs/38526386149
- 今回の進捗・マトリクス・最終報告とHTML/JSONが当該ブランチに含まれる。
- [進捗](PROGRESS.md) / [テストマトリクス](TEST_MATRIX.md) / [会話HTML](simulations/conversation_001.html) / [会話JSON](simulations/conversation_001.json) / [分析](simulations/analysis.md)

---

## 以前の検証履歴

# 最終検証報告

## 今回の継続検証（2026-10-14）

### 総合判定

**CONDITIONAL PASS（条件付き合格）**。前回の報告から未実施7項目を検証し、CI・Firefox E2E・SQLite保存障害処理を追加しました。検証コードSHA `dcf5dbd6838117b1fd28dde99efcc8e2227538b8` はGitHub ActionsのPushとPR両方で成功しました。利用開始は可能ですが、旧APIキーの失効確認が必要であり、今回の`start.bat`再実行は使用中の8765ポートによりBLOCKEDでした。

### テスト集計

- テスト項目: 51
- PASS: 50
- FAIL: 0
- BLOCKED: 1（T02。127.0.0.1:8765を既存Pythonプロセスが使用中。プロセスは停止・変更していない）
- NOT_TESTED: 0
- ローカルpytest: **33 passed, 1 warning**。Python 3.12.10、Windows。警告はStarlette/httpxの非推奨通知。
- GitHub Actions: **33 passed**、Firefox 157、Ubuntu、Python 3.11。`node --check app.js`成功。Push [run 38518482078](https://github.com/kenkyu0909/aichatapp/actions/runs/38518482078)、PR [run 38518486199](https://github.com/kenkyu0909/aichatapp/actions/runs/38518486199)。両方ともSHA `dcf5dbd6838117b1fd28dde99efcc8e2227538b8`。
- E2E: Firefoxで2テスト成功。画面操作、メッセージ追加/編集/削除、返信3案、コピーと送信記録の分離、方針ON/OFF/ON、いいね、設定、再読込、サーバー停止中4操作、再起動後の保持を確認。
- JavaScript構文: `node --check app.js`成功。Firefox内の例外と`console.error`監視も空。ブラウザー開発者ツール自体のConsole出力を直接採取したわけではない。

### 未実施だった7項目

| ID | 結果 | 今回の確認 |
|---|---|---|
| T05 | PASS | WindowsのFirefox上で主要操作を行い、`error`、未処理Promise拒否、`console.error`監視は空。直接Console採取ではない。 |
| T19 | PASS | Firefox UIで方針をON→OFF→ON。モック応答を用い、返信3案は各回表示、OFF時は方針を隠し、前回表示も残らない。 |
| T30 | PASS | SDKモックでキーなし、401、403、404を再現。安全な日本語エラー、認証情報の秘匿、履歴不変を確認。実APIへ無効キーは送っていない。 |
| T35 | PASS | Windows一時領域でDB/写真の保存障害、保存中断、DB更新失敗後の掃除を実ファイル操作で検証。起動時から利用できない保存先も安全な500を返す。NTFS ACLの拒否設定は未実施。 |
| T36 | PASS | Firefoxを開いたままテスト用サーバーを停止し、メッセージ・プロフィール・相手追加・生成を操作。失敗の表示と入力保持を確認し、再起動後に保存を確認。 |
| T47 | PASS | モック検査とGemini API2 3.5 Flash-Liteの実通信1回。架空の悪意あるプロフィールを含む応答で、3案の形式・話題反映・注入文字列と秘密要求の非反復・履歴不変を確認。1回の応答で耐性を完全保証するものではない。 |
| T48 | PASS | Firefoxでローカルサーバー停止を再現。Gemini timeout/接続失敗はSDKモックで確認し、30秒timeout、再試行なし、再操作可能、履歴維持とエラー秘匿を確認。PC全体の回線は切断していない。 |

### 今回の修正

- `.github/workflows/test.yml`: 作業ブランチPushと`feat/ui-local-backend-v1`宛てPRでオフラインpytest、Firefox E2E、JS構文確認を実行し、ログ・スクリーンショットをartifactへ保存。
- `.github/workflows/live-gemini.yml`: 実API試験を手動起動に限定し、対象ブランチを制限。キーがなければSKIPPEDとし、通常CIからの実API通信を防止。
- `requirements.txt`: `google-genai>=1.74,<2`。timeout/retry optionsに対応しない旧SDKを排除。
- `app.py`: Geminiリクエストを30秒で打ち切り、SDKの自動再試行を無効化。保存エラー詳細を一般化。DB・写真ディレクトリ初期化を遅延し、import中の書込失敗でサーバーが起動前に終了する問題を修正。写真を一時ファイル経由で保存し、DB/ファイル失敗時の後始末を追加。
- `tests/test_app.py`, `tests/test_ui_firefox.py`, `requirements-test.txt`: API異常系、実ファイル障害、Firefox UI、T19/T36、プロンプトインジェクション、timeoutを追加。UI試験は空の一時DBと架空データのみ。
- `scripts/live_gemini_smoke.py`: 敵対的プロフィールの実API試験モードを追加。秘密値・生成本文をログに出さない。
- コード修正SHA: `f73c1649efa614f51d88547dc1fdb33ca92cefbb`、保存先初期化修正SHA: `4647f2ba8ec432ca3d79bccc24bb03fb73f528eb`、Firefox会話削除UIと検証記録SHA: `dcf5dbd6838117b1fd28dde99efcc8e2227538b8`。

### Gemini実API

- 今回の追加実通信: **2回**。API1・Gemini 3.5 Flash-Liteは1回、429相当の利用枠応答。ユーザー指定順にAPI2・3.5 Flash-Liteへ切り替え、悪意ある架空プロフィールの返信生成1回に成功。API2は3案のJSONと履歴不変を確認。
- 累積実通信は前回報告の14回に今回2回を加え16回。API1/2の3.1 Flash-Liteは未使用。API1の応答で切替を行っており、制限時の優先順位に従った。
- API1/2で実際に利用できる残りの割当、RPM/TPM/RPD消費、プロジェクトの課金状態は確認していない。Google公式資料では3.5 Flash-Liteと3.1 Flash-Liteに無料枠価格が掲載されているが、利用可能性と上限は個別プロジェクトに依存する。無料枠では入出力がGoogle製品改善に使われる場合があり、有料サービスと条件が異なる。[Gemini API料金表](https://ai.google.dev/gemini-api/docs/pricing)、[Billingと利用階層](https://ai.google.dev/gemini-api/docs/billing)。
- 旧API1/API2キーがGoogle側で失効済みか確認できない。ユーザー側で失効を確認し、未失効なら直ちに失効させること。新しい値は本レポート・PR・ログに記録していない。

### セキュリティ・プライバシーと残る制限

- pytestとFirefox E2Eは一時ディレクトリの空SQLiteと架空データだけを使用。Firefoxのみを使用し、Chromeは開いていない。
- localhost bind、写真/他の相手の会話をGeminiへ送らないこと、SDKエラー時の秘密値秘匿、プロンプトインジェクション処理、画像検証、送信済み記録の明示操作を確認。
- APIキーのGit履歴/Actionsログへの混入をこの最終更新で確認することは残作業。過去に会話のツール出力へ更新前キーが露出した履歴はあり、リポジトリへ含まれていないことだけでは失効を代替できない。
- `start.bat`の再確認では既存の127.0.0.1:8765 listenerと衝突したため、既存プロセスを触らず中断。前回報告にある起動成功の記録は保持する。今回は新しいバッチ起動の成功を主張しない。
- 外部環境でのNTFS ACL拒否、ブラウザー開発者ツールからのConsole直採取、プロジェクト固有のAPI課金/割当は未確認。

### Windowsでの利用

Python 3.11以降を用意し、既に同じアプリが8765番ポートで起動していない状態で`start.bat`を実行してください。Firefoxで`http://127.0.0.1:8765/`を開きます。Geminiを使う前に旧キーを失効確認し、新しいキーを`.env`へ設定してください。無料枠へ送信する会話には個人情報を含めないでください。

### GitHub

- リポジトリ: https://github.com/kenkyu0909/aichatapp
- ブランチ: `codex/full-system-verification`
- 検証したコードSHA: `4647f2ba8ec432ca3d79bccc24bb03fb73f528eb`
- PR #4: https://github.com/kenkyu0909/aichatapp/pull/4（Draft維持、未マージ）
- [PROGRESS.md](PROGRESS.md) / [TEST_MATRIX.md](TEST_MATRIX.md)
- GitHub Actions: [Push run 38518047903](https://github.com/kenkyu0909/aichatapp/actions/runs/38518047903)、[PR run 38518053494](https://github.com/kenkyu0909/aichatapp/actions/runs/38518053494)
- 最新のPR HEADチェックは[PR #4 Checks](https://github.com/kenkyu0909/aichatapp/pull/4/checks)で確認。

## 前回報告（以下は履歴として維持）

## 判定

**条件付き合格**。実API接続と主要UI・SQLite機能を確認し、15件のpytestが成功しました。作業ブランチをGitHubへpushし、`feat/ui-local-backend-v1`宛てのDraft PR #4を作成しました。7項目は未実施です。また、更新前のAPIキーが作業会話のツール出力に露出したため、旧キーの失効を確認してください。

## テスト集計

- 総数: 49
- PASS: 42
- FAIL: 0
- FIXED: 0（修正後の再試験はPASSに計上）
- BLOCKED: 0
- NOT_TESTED: 7
- pytest: `15 passed, 1 warning`
- 詳細: [TEST_MATRIX.md](TEST_MATRIX.md)

## 修正したファイル

- `app.js`: 起動時に全モーダルを呼び出してしまうイベント登録を修正。
- `app.py`: 画像をPillowで形式確認・検証・全デコードし、16メガピクセルを上限とする。壊れた画像や大量メモリを使う画像を拒否。
- `requirements.txt`: 画像デコードにPillowを追加。
- `tests/test_app.py`: 画像差替え・削除、画素数上限、長い履歴、存在しないID、不正JSON、重複・不足候補、429時の秘匿と履歴保全を検証。
- `prompts/reply.txt`, `prompts/like.txt`: プロフィールに書かれていない本人の経験・好み・共通点を生成しない指示を追加。
- `scripts/live_gemini_smoke.py`: リポジトリのルート外から実行した場合もアプリをimportできるよう修正。
- `start.bat`, `README.md`: Windowsの既定ブラウザーを開かず、Firefoxを起動するよう変更。Firefoxが見つからない場合はURLを表示。
- `docs/verification/PROGRESS.md`, `docs/verification/TEST_MATRIX.md`, `docs/verification/FINAL_REPORT.md`: 検証結果、制限、未実施項目を記録。

## Gemini API実通信

ユーザー指定の`API/chat1.md`と`API/chat2.md`にある認証情報をAPI1→API2の優先順で使用しました。ユーザー提示の上限は15リクエスト/分、250kトークン/分、500リクエスト/日です。

- API1・Gemini 3.5 Flash-Lite: 1回目に利用枠・レート制限応答。指定順にAPI2へ切り替えました。
- API2・Gemini 3.5 Flash-Lite: 返信といいねの実生成に成功。最終的に返信3案、いいね3案をFirefox UIにも表示しました。既存のsmoke testも実APIで実行し、返信・いいね各3案と履歴不変を確認しました。
- API1/2のGemini 3.1 Flash-Lite: 未使用。API2の3.5で成功したため、優先順どおり試験対象になりませんでした。
- API更新前の指定フォルダーのキーを使ったリクエスト試行は12回（API1 3.5が1回、API2 3.5が11回）。API2のうち10回で生成応答を確認し、1回は認証/モデル権限エラーでした。
- API更新後、更新されたAPI1の3.5 Flash-Liteで既存smoke testを再実行しました。返信といいねの2リクエストが成功し、各3案と会話履歴が変わらないことを確認しました。更新後のAPI2は今回未使用です。これを含む指定フォルダー経由の試行は計14回です。250kトークン/分と500回/日のプロジェクト別消費量はGoogle側で確認できないため、数値を推測していません。
- Gemini 429相当エラー: 実APIのAPI1制限応答と、詳細を伏せるモック試験で確認。画面/APIへ固定文を実生成として返しません。
- Googleの料金表ではGemini 3.5 Flash-Liteに無料枠が掲載されています。無料枠へ送った入力・出力はGoogleの製品改善に使用される場合があります。個別プロジェクトの課金状態・割当状況は確認していません。[公式料金表](https://ai.google.dev/gemini-api/docs/pricing.md)・[Gemini API利用規約](https://ai.google.dev/gemini-api/terms?hl=en)

### 出力品質評価

各項目を1〜5点で評価しました。返信・いいねとも、最終の実API出力を確認しています。

| 項目 | 返信 | いいね | 根拠 |
|---|---:|---:|---|
| 会話理解 | 5 | 5 | カフェ、ケーキ、美術館、水族館、旅行など相手が書いた内容に反応。 |
| 自然さ | 4 | 4 | 日本語として自然。候補により定型的な言い回しがある。 |
| 文体 | 4 | 5 | 指定した敬語と短めの口調に概ね一致。 |
| 多様性 | 4 | 5 | 異なる質問や話題の切り口を提示。 |
| 正確性 | 4 | 5 | プロンプト修正後のいいね案は、本人の好み・共通点を捏造しなかった。修正前には未記載の共通趣味を補う出力があった。 |
| 距離感 | 5 | 5 | 初回の挨拶と質問中心で、強い誘いや返信の催促なし。 |
| 指示追従 | 4 | 4 | 最終出力は避けたい捏造を回避。文字数は一部の案で短文目安を超える。 |

## UI実操作

Firefoxで画面を開き、プロフィール保存、架空の相手3人、写真表示、検索、切替、会話追加・編集、返信3案、いいね3案、コピー、手動送信記録、追いメッセージ、履歴・設定・使い方、JSON export、Ctrl+Enter、削除を操作しました。起動時に設定ダイアログが出る問題を修正し、修正後は初期表示で閉じていることを確認しました。

Chromeを操作しないよう指示を受けた後、UI確認にはFirefoxのみを使いました。先行実行時に起動バッチがWindowsの既定ブラウザーを開き、Chromeが立ち上がった件はユーザーが閉じました。その後、`start.bat`をFirefox専用起動に変更し、バッチを再実行してFirefoxでの表示とHTTP 200を確認しました。JavaScript Consoleの直接採取は未実施です。

## SQLite保存・再起動

プロフィール、相手ごとの会話、写真をSQLiteとローカルファイルへ保存しました。ページ再読み込みとサーバー再起動後に、プロフィール、残した相手2人、会話件数3件・1件が残ることを確認しました。写真の差替えでは旧ファイルを削除し、相手削除では会話と写真を削除することをテストしました。

## セキュリティ・プライバシー

- Uvicornのbind先は`127.0.0.1`のみ。
- `.env`、SQLite、写真はGit追跡対象外。
- 写真と他の相手の会話はGemini送信文脈に含まれないことをSDKモックで確認。
- APIキーはSDKの認証引数で渡し、会話文脈に含めない。429相当時の生エラー詳細も返さない。
- UIは文字列をDOMのテキストとして表示し、`innerHTML`や`eval`は使用していない。受取ファイル名を保存先パスに使わず、写真名はUUIDを生成。
- 返信・いいねのプロンプトに、相手プロフィール中の命令に従わない指示を確認。ただし、敵対的なプロフィールを実APIへ送る試験は未実施。
- 無料枠のプライバシー条件はREADMEに記載。

### 認証情報の取り扱い

APIキーを読み取ったとき、秘密値を伏せる処理が失敗し、更新前のAPI1とAPI2のキーがこの会話のツール出力に表示されました。これらはリポジトリへ保存していません。ユーザーからAPI更新の連絡があり、更新後のAPI1キーで2回の実通信に成功しましたが、更新前の両キーがGoogle AI Studioで失効したかは確認できません。**旧API1・API2キーの失効を確認してください。** API指定前に既存の環境変数`GEMINI_API_KEY`で失敗リクエストを1回行ったため、その環境変数が別キーなら併せて確認してください。

## 未修正・未実施の項目

- ブラウザーConsole採取、会話方針表示切替、無効キー・未使用モデル、保存先権限エラー、サーバー停止時のUI、ネットワーク切断、敵対的プロフィールの実API試験。
- GitHubのSecret一覧は権限エラーで確認できませんでした。作業ブランチとDraft PR #4は作成済みです。PRは未マージで、既存PR #3も操作していません。
- pytest依存のStarlette/httpxについて非推奨警告が1件あります。テストはすべて成功。

## Windowsでの利用手順

1. Python 3.11以降を用意し、プロジェクトフォルダーで`start.bat`を実行します。
2. Firefoxがあれば自動で開きます。見つからない場合はFirefoxで`http://127.0.0.1:8765/`を開きます。
3. Geminiを使う場合は、キーを失効・交換した後、新しいキーを`.env`に設定して起動し直します。`.env`をGitへ追加しないでください。
4. 終了時は起動したコンソールでCtrl+Cを押します。
5. Gemini無料枠へ送る会話文には個人情報を含めないようにしてください。無料枠の入力データ取扱条件は上記公式資料で確認できます。

## GitHub

- 元ブランチ: `feat/ui-local-backend-v1`
- 作業ブランチ: `codex/full-system-verification`
- 作業開始時コミット: `78a66c9cba0e6ddb7bc1441e65e1eae75a5e304b`
- 初期進捗コミット: `e0410c8`（ローカル）
- 最終実装コミットSHA: `ae042ea41b3b1439abc6c8c27c8945a1fd915682`
- 報告書コミットSHA: `3fcedae1e67e867c41be4692265145bb2498fa05`（この報告書の最新内容を含むコミット）
- Pull Request URL: https://github.com/kenkyu0909/aichatapp/pull/4（Draft、`feat/ui-local-backend-v1`宛て）


# 2026-10-14 最終検証追加報告（会話002）

## 判定: CONDITIONAL PASS

主要な起動、SQLite隔離、生成、20通上限、会話復元可能なJSON、Firefox HTML表示、CI向けオフラインテストは確認できた。ただし、実Geminiが本人の未登録の好みを一人称で作った実例がある。プロンプトは修正したが、変更後の実API確認は今回の25論理リクエストに達したため残っている。通常利用前に、本人の直接質問への確認動作を実APIで再評価する必要がある。

## 今回の結果

- 会話002: `LIMIT_REACHED`、アプリ側20通、架空相手20通、合計40メッセージ。会う提案なし、約束成立なし。20通目の後に相手の返信を保存し、21通目を生成・送信していない。
- 実Gemini: 合計25論理リクエスト（会話20、別品質確認5）。25成功、0 API失敗、API1 / `gemini-3.5-flash-lite`のみ、各バックエンド試行1回。429/フォールバックなし。API2/3.1は未使用。内訳は`conversation_002.json`、`quality_checks_002.json`。
- 出力品質: 初回メッセージは初回生成で句読点と候補構成に問題があった。`first.txt`を強化した後の再確認では3案の構成と句読点が改善（T79 FIXED/T80 PASS）。通常返信は相手の話題を拾う一方、映画話題の反復と本人の未確認情報が候補に含まれた。未知の好みを問う別実APIテストでは未確認の映画趣味を生成しT77 FAIL。共通プロンプトに本人への確認ルールを追加し、モックテストは成功したが、変更後の実APIテストは未実施。カフェ会話ではStage 3/consider_invite、断りケースでは謝罪・再誘いなしを確認。
- SQLite: 会話002と品質試験は本番DBと分離した一時SQLiteを使用。会話002のJSONは40件、送信数20/20。HTML内容はJSONから生成。ユーザーの実データを初期化していない。
- Firefox: 実際にHTMLを開き、40メッセージ、左右の話者、送信番号、20個の生成詳細、詳細の展開、CSS、日本語、外部リソースなしを確認。スクリーンショット [`conversation_002_firefox.png`](simulations/conversation_002_firefox.png)。Chromeは使用していない。
- Windows起動: 8765番は既存プロセスが使用中のため終了・再起動はしなかった。隔離コピーと一時DBでPython 3.12、別ポート18768の起動、Firefox表示、二重起動、Ctrl+C終了、ポート解放と再起動、18769番の独立listenerを停止しない競合案内を確認。
- pytest: 104 passed, 1 warning（Starlette/httpxの非推奨警告）。`node --check app.js`成功。Firefox UIテストを含む。最新HEADのGitHub ActionsはPush後に確認する。実行履歴: https://github.com/kenkyu0909/aichatapp/actions/workflows/test.yml?query=branch%3Acodex%2Ffull-system-verification

## プロンプト修正

- `prompts/first.txt`: 3案それぞれに挨拶、軽い好意、マッチへの喜び、プロフィール話題、質問を含める自己点検を追加。句読点も案ごとに確認。変更後の実API3案をT80で確認。
- `prompts/common.txt`: 本人の趣味・経験・予定への直接質問に登録情報がない場合、曖昧な一人称回答を作らず本人への確認質問のみ返す指示を追加。T77の実生成問題を受けた修正。静的・モック確認は成功。変更後の実API再確認は未実施。
- `tests/test_app.py`: 初回プロンプト必須要件と、本人への直接質問ルールが共通プロンプトにあることを確認するアサーションを追加。

## APIモデル・利用制限・料金

Google公式一覧では`gemini-3.5-flash-lite`と`gemini-3.1-flash-lite`がStableとして掲載される。公式料金表では標準の3.5 Flash-Liteに無料ティアが表示され、無料ティアの入出力はGoogleの製品改善に使用される条件。RPM/TPM/RPDや利用可能枠はプロジェクト・ティアで異なり、AI Studio上で確認する必要がある。今回の個別プロジェクト残量・ティア・請求状態・実費は確認しておらず、課金設定は変更していない。

- [Google Gemini API モデル一覧](https://ai.google.dev/gemini-api/docs/models.md)
- [Google Gemini API レート制限](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Google Gemini API 料金表](https://ai.google.dev/gemini-api/docs/pricing.md)

## テスト集計

Git履歴69 refsとworking treeをAPIキー形式で確認し、一致はありませんでした。秘密値は表示していません。GitHub Actionsの保存期間外を含む全ログは個別に走査していません。

既存マトリクスの前回71項目にT72〜T81を追加して81項目。現在状態はPASS 74 / FAIL 1 / FIXED 1 / BLOCKED 3 / NOT_TESTED 2。T77のFAILは未登録の好みを生成した実例であり、修正後実API再試験が残る。

## ファイル

- [`conversation_002.json`](simulations/conversation_002.json): 全40発言、3案、選択、モデル・API別名、送信数、終了状態
- [`conversation_002.html`](simulations/conversation_002.html): 全会話と折りたたみ候補の単体HTML
- [`conversation_002_analysis.md`](simulations/conversation_002_analysis.md): 10観点の品質評価と会話分析
- [`quality_checks_002.json`](simulations/quality_checks_002.json): 会話本体とは分離した実API品質確認5回
- [`conversation_002_firefox.png`](simulations/conversation_002_firefox.png): Firefox表示確認画像

## GitHub状態

- ブランチ: `codex/full-system-verification`
- PR #4: https://github.com/kenkyu0909/aichatapp/pull/4（Draft維持・未マージ）
- 検証済みHEAD: `cf24e2398ab428cb9e3beef2b0029f34aa73d4b4`。Push Actions [38544684207](https://github.com/kenkyu0909/aichatapp/actions/runs/38544684207) とPR Actions [38544689940](https://github.com/kenkyu0909/aichatapp/actions/runs/38544689940) 成功。ソース修正コミット: `d431b79f159a7e7fc499a7acf06a12e13454c4b4`。報告書更新コミット`a40c251c62c400401c9aef3e77beeaf7ceb76079`のPush Actions [38544920718](https://github.com/kenkyu0909/aichatapp/actions/runs/38544920718) とPR Actions [38544928533](https://github.com/kenkyu0909/aichatapp/actions/runs/38544928533)も同SHAで成功。ソース修正SHAは`d431b79f159a7e7fc499a7acf06a12e13454c4b4`。

## 2026-10-14 実API品質確認003と修正（途中報告）

初回実API品質確認は隔離SQLiteと架空人物を使って9論理要求を実行し、API1の`gemini-3.5-flash-lite`へ合計10回到達した。T77の回答後にGeminiが同じ趣旨を再質問したケース、候補なしになったケース、本人が登録していない休日の体験談、誘い方針と候補が一致しないケースを確認した。初回JSONの記録は残し、成功扱いにはしていない。

事実確認と方針整合性を見直し、休日の具体的な活動・場所の照合、否定的な映画情報の扱い、回答済み情報の再質問抑止、一般的な誘い文句の判定を追加した。オフライン全体テストは149件成功し、警告が1件ある。実API追試T93と会話003、HTMLのFirefox表示確認はまだ実施していないため、総合判定は保留する。

修正コミット`aee118313bd8a05bbae30cb03e2cb37330e36ab0`のGitHub Actions Push run [38554061358](https://github.com/kenkyu0909/aichatapp/actions/runs/38554061358)とPR run [38554066709](https://github.com/kenkyu0909/aichatapp/actions/runs/38554066709)は成功した。両方とも同一HEADを対象にしている。

### 実Gemini品質確認003の確定判定

T77の事前確認はAPI呼び出しなしで本人への質問を返した。最初の回答後テストは失敗し、別ファイルでの再確認では2試行後に3候補を得たため、回答後生成をPASSとする。初回失敗の詳細は削除していない。

短文、複数文、落ち着いた話題のケースは3候補の返却と句読点形式を確認したが、複数の候補に未確認の本人談が見つかった。特に複数文ケースのコーヒー嗜好、落ち着いた喫茶店の好み、映画ケースの直近視聴状況はプロフィールに根拠がなかった。最後の型は候補検査へ追加し、オフラインテストで再現を防ぐことを確認した。カフェ/コーヒー等のあらゆる意味上の誤りを捕捉できるわけではない。

誘いケースでは、Geminiの方針と候補が繰り返し矛盾したため、安全検査が候補を拒否した。相手へ矛盾した誘いを送らないことは確認できたが、自然な誘い候補の安定生成は未達である。T93はFAIL、T99はT77回答後の実API再確認としてPASSとした。

APIはAPI1の`gemini-3.5-flash-lite`。初回・限定追試・再確認の合計16論理要求、22プロバイダー試行。429、モデル切替、他モデル利用なし。個別利用枠・課金状態・費用は確認していない。会話003本体の実験結果はまだない。

### 2026-10-14 最新コミット/会話003の途中状況

- `bf1b4a168ae27f754045b5e89741dd6c561e9b27`のPush/PR Actionsが成功: [Push 38555213713](https://github.com/kenkyu0909/aichatapp/actions/runs/38555213713)、[PR 38555220234](https://github.com/kenkyu0909/aichatapp/actions/runs/38555220234)。テストは151 passed, 1 warning。PR #4はDraftのまま。
- 会話003は実APIで進行中。架空プロフィールと隔離SQLiteを使用し、アプリ7通・相手7通、論理要求8回・プロバイダー試行9回を保存。初回生成と各ターンの候補をJSON/HTMLへ逐次保存している。
- 現時点では会話終了条件に未到達のためT90はNOT_TESTEDのまま。成功を前提にせず、相手の自然な反応を続けて最終判定する。


## 2026-10-14 返信品質改善と会話003 最終追記

### 判定

**FAIL（返信AI品質の実用判定）**。ローカルアプリ、オフラインテスト、FirefoxのHTML確認は成功しましたが、実Gemini候補が本人未確認の習慣を3案とも断定したため、15通で送信前に安全停止しました。候補選別を人が行う前提でも、本人情報の正確性と会話の前進に重大な課題が残ります。PR #4はDraftのままです。

### 会話003

- 実験ID: `conversation_003`。本人役は橘はる、相手役は瀬戸りん。公開プロフィールと架空会話のみで、空の隔離SQLiteを使用しました。
- 終了状態: `BLOCKED`。アプリ側15通、相手側15通、計30件。最終メッセージは相手からの質問で、アプリ側の16通目はありません。
- 最初の初回メッセージはGemini `first`候補から1案を選択。会話中に食事・カフェへの誘いは送信せず、具体的な約束は成立していません。Stage 3/`consider_invite`が複数回出ましたが、自然な誘い候補を生成できませんでした。
- 最後の相手質問「気になる新作を見つけたらすぐ買うタイプですか？」への候補3案は、いずれも本人の未確認習慣を断定しました。候補を選ばず、理由と全文をJSON/HTMLへ保存して安全停止。会話SQLiteと送信カウンターは変えていません。
- 品質評価（1〜5）: 日本語の自然さ3、句読点禁止5、文章量ミラーリング3、関連性3、文脈一貫性3、本人事実性2、会話の前進2、候補多様性2、距離感4、総合実用性2。評価根拠は`conversation_003_analysis.md`にあります。Codexが相手役と評価役を兼ねるため評価バイアスがあります。

### 実API品質と利用量

- 使用: API1 / `gemini-3.5-flash-lite`。実験中のフォールバックなし。429は記録されていません。
- 品質確認16論理要求・22 provider attempts、会話003 16論理要求・18 provider attempts。合計32論理要求・40 provider attempts。品質確認は再試行を含み、会話003は候補受信後に人が選ぶ運用でした。事前目安の約30論理要求を2回超えました。この逸脱を記録し、追加呼び出しはしません。
- Gemini API応答自体の失敗数と、アプリの品質ゲートで候補を拒否した結果は別です。会話003の16論理要求はすべてprovider応答成功でした。最後の候補はモデル応答としては返りましたが、安全に送れる候補としては不合格です。
- 個別プロジェクトの残り枠、請求設定、実費は確認していません。無料枠や費用を推測しません。

### 実験002との比較

| 評価項目 | 実験002 | 実験003 |
|---|---:|---:|
| Geminiが選択したアプリ送信数 | 20 | 15 |
| 「、」「。」を含む送信文 | 7/20 | 0/15 |
| 絵文字を含む送信文 | 1/20 | 1/15 |
| 「笑」を含む送信文 | 0/20 | 0/15 |
| 同じ話題・共感表現の反復 | 多い | 多い。甘味と季節限定の話題で言い換えが続いた |
| 本人の未確認情報 | 送信文に未確認経験あり | 送信文に明確な虚偽事実は見つからなかったが、未送信候補3案が未確認習慣を断定 |
| 会う提案 | なし | なし |
| 会う約束 | なし | なし |

プロフィールと会話条件が異なるため、数値だけでモデル改善の効果を断定できません。今回の主な安全性は、問題候補を送らずに止めたことです。生成品質そのものは未達です。

### HTML・Firefox・オフラインテスト

- `conversation_003.html`はFirefox 157.0.1で実際に開きました。30メッセージ、話者の左右、送信数15/15、詳細16件、拒否した3候補の展開、日本語表示を確認しました。画像は`simulations/conversation_003_firefox.png`。Chromeは使用していません。
- 全pytest: **153 passed, 1 warning**（Starlette/httpxの非推奨警告）。追加2件は未送信候補の拒否状態とHTMLエスケープを確認。`node --check app.js`、`py_compile`、`git diff --check`も成功。
- Test matrix: 100項目、PASS 89 / FAIL 4 / FIXED 1 / BLOCKED 4 / NOT_TESTED 2。T90は安全停止のためBLOCKED。T100は候補を送らず記録した安全動作としてPASS。旧FAILは履歴として保持。

### 変更・証拠

- `scripts/simulate_conversation.py`: 保留中の危険候補を理由付きで拒否・保存し、送信やSQLite履歴を変更せずBLOCKEDへ移行。HTMLへ候補を安全にエスケープして表示。
- `tests/test_conversation_simulation.py`: 拒否保存、カウンター不変、HTMLエスケープを検証する2件を追加。
- `simulations/conversation_003.json`、`conversation_003.html`、`conversation_003_analysis.md`、`profiles_003.md`、`conversation_003_firefox.png`を保存。過去001/002は変更していません。
- `conversation_003.json`の本人・相手データはすべて架空。APIキーや認証情報は含めていません。拒否候補のHTML出力もXSSエスケープを検査しました。

### GitHub

- 作業ブランチ: `codex/full-system-verification`。PR #4は`feat/ui-local-backend-v1`宛てOPEN/Draftで、マージしていません。
- 会話 checkpoint `c740141cf2b7b9f7b9143cf6750dc26add8c86d5`のPush Actions [38555557284](https://github.com/kenkyu0909/aichatapp/actions/runs/38555557284)とPR Actions [38555564007](https://github.com/kenkyu0909/aichatapp/actions/runs/38555564007)は成功。コミット`5ddcd020747eb8eb8971e991515d1004c0625114`のPush Actions [38556958055](https://github.com/kenkyu0909/aichatapp/actions/runs/38556958055)とPR Actions [38556965533](https://github.com/kenkyu0909/aichatapp/actions/runs/38556965533)は、いずれも同一HEADで成功しました。
- レポート: [PROGRESS.md](PROGRESS.md)、[TEST_MATRIX.md](TEST_MATRIX.md)、[prompt_spec.md](prompt_spec.md)。会話資料: [HTML](simulations/conversation_003.html)、[JSON](simulations/conversation_003.json)、[分析](simulations/conversation_003_analysis.md)、[Firefox画像](simulations/conversation_003_firefox.png)。

## 2026-10-14 実Gemini品質確認004の再評価

### 判定

**FAIL（生成品質）**。実APIは応答しましたが、保存済みの候補に本人の確認回答と矛盾する購買行動、プロフィールにない具体的なカフェ嗜好、前向きな誘い判断と不一致の候補が含まれました。安全に送信できる品質には達していません。実API呼び出しは追加せず、会話004は開始していません。

### 実API記録

- 前回の品質確認: 8論理要求、9 provider attempts。API1 / `gemini-3.5-flash-lite`のみ。429・切替なし。
- 初回の自動評価: 7 PASS / 1 FAIL。ただし手動レビューで見逃し3件と誤判定1件が分かった。自動評価のPASS数は最終的な品質PASS数として扱わない。
- 映画回答は引用符を省いた言い換えとして正確だった。全回答の逐語一致を求めた評価器を修正した。
- 個別の残利用枠、料金プラン、実請求額は未確認。料金を推測しない。

### 修正内容

- `app.py`: 購買行動の具体性と確認回答の矛盾を照合。カレーの好み・頻度・最近の経験を分離。カフェの話題だけで雰囲気の好みを本人事実としない。会話履歴から誘い機会を判断し、相互質問・共有話題・相手の関心があり、慎重さや過去の誘いがない場合の`consider_invite`で候補が欠ければ一度だけ修復する。理由文の決まった言い回しには依存しない。
- `prompts/common.txt`: 購買行動、カレー情報、カフェ嗜好の具体性を明記。
- `scripts/run_quality_checks_004.py`: 回答の主要事実で意味的一致を確認し、API名とモデル名を含む4経路の優先順を厳密に照合。
- `tests/test_app.py`, `tests/test_quality_checks_004.py`: 上記の不具合を再現・確認するオフライン回帰テストを追加。
- `docs/verification/simulations/quality_checks_004.json`: 実行時の内容は維持し、人手による独立レビューを追記。
- 詳細は[`quality_checks_004_analysis.md`](simulations/quality_checks_004_analysis.md)。

### 検証

- pytest: **195 passed, 1 warning**（Starlette/httpx非推奨通知）。Firefox UI自動テストを含む。
- 実API再試験: 今回は0件。元の8論理要求・9 provider attemptsのみ。
- Firefox: 今回の新規機能の追加操作は未実施。全体pytest内の既存Firefox UIテストは成功。Chromeは使用していない。
- JavaScript構文・Python構文・差分チェック、秘密情報パターンスキャン、GitHub Actionsはいずれも成功。最新SHAのPush/PR Actions結果は下記。

### 実験004

**NOT_TESTED**。品質確認004でFAILが見つかり、論理要求上限も使用済みのため開始しなかった。安全と品質のゲートを満たすまで実API会話を開始しない。

### 集計・GitHub

- テストマトリクス: 110項目、PASS 97 / FAIL 5 / FIXED 1 / BLOCKED 4 / NOT_TESTED 3。過去のFAILは履歴として保持。
- 作業ブランチ: `codex/full-system-verification`。PR #4はDraftのまま、未マージ。
- 検証済み実装SHA `2e6a34410548915c79409a8388821699cb6de95c`を既存ブランチへPush。Actions [Push run 38569943665](https://github.com/kenkyu0909/aichatapp/actions/runs/38569943665)と[PR run 38569953895](https://github.com/kenkyu0909/aichatapp/actions/runs/38569953895)は同じSHAで成功し、両方で195 passed, 1 warning、JavaScript構文検査、テストArtifact保存を確認。後続の報告反映はドキュメントのみの変更。
- PR #4はOPEN/Draft、`feat/ui-local-backend-v1`宛てを維持。マージしていない。PR本文へ今回の修正・テスト・リンクを追記。
- 最終報告自体を更新するコミットのSHAとActionsは、次のPush後に追記する。

### 追加レビューで見つかった境界ケース

- 「衝動買いを避けています」「すぐ買うのは避けています」「即決購入を控えています」などの否定プロフィールを、反対の買い方を支持する根拠にしない。
- カレーの頻度・最近の経験は、プロフィール内の別趣味にある「よく」「最近」だけで裏付けない。カフェの雰囲気は「落ち着いた雰囲気よりにぎやかな店が好き」の比較極性を保持する。
- 誘い機会は直近2件の相手発言の同一話題に限定して評価する。「カフェは好きですか？」という質問だけを相手の関心と扱わず、明確な消極表現も除外する。遅い返信への謝罪だけで拒否と判断しない一方、過去の誘いや明確な拒否は全会話から確認する。
- 追加の回帰テストを含む全pytestは**195 passed, 1 warning**。`node --check app.js`、`py_compile`、`git diff --check`成功。新しい実Gemini API要求は0件。今回の報告追記を含むHEADとActionsは次のPush後に記録する。

## 2026-10-14 最新指示による再検証（品質005準備時点）

### 判定

**CONDITIONAL PASS（実API品質評価は保留）**。前回の実API品質確認004で残った問題に対するオフライン修正とFirefoxを含む回帰テストは成功しました。新しい実Gemini品質確認005はまだ未実施であり、今回のプロンプト品質合格やconversation_004開始条件を満たしたとは判断していません。

### 変更とテスト

- 追加レビューで、句読点を省いた文の連結、最近の場所/頻度の確認質問の粒度違い、カフェ頻度の言い換え再質問を新たに発見。`app.py`の高確度候補チェックと質問分類を拡張し、再現テストを追加しました。
- `scripts/run_quality_checks_005.py`と`tests/test_quality_checks_005.py`を追加。最大8論理要求、provider試行上限、許可されたAPIディレクトリのみの利用、秘密値の非表示、隔離SQLite、質問/回答、候補内容・改行・プレースホルダー・重複・誘い方針を記録します。
- レビュー修正後の最新pytest: **257 passed, 1 warning, 76.93秒**。Firefox UIテストを含みます。警告はStarletteの`httpx` TestClient利用非推奨です。`node --check app.js`、Python `py_compile`、`git diff --check`、秘密形式/API個人パスのファイルスキャンも成功。Chromeは使用していません。
- 今回の実Geminiリクエスト数: **0**（品質005の開始前）。設定確認では指定APIディレクトリに対応する4経路の名前/モデル順を確認しましたが、キー値は出力していません。実際の認証有効性、残クォータ、課金状態は未確認です。

### 公式資料と利用条件

Googleの公式モデル一覧には`gemini-3.5-flash-lite`と`gemini-3.1-flash-lite`がstableとして掲載されています。Free tierはモデル利用が限定され、実際のプロジェクト別の利用枠はAI Studioで確認する必要があります。料金ページのfree枠・paid価格は記載されていますが、このユーザーのプロジェクトの課金状態や利用料金は確認していません。[Models](https://ai.google.dev/gemini-api/docs/models) / [Pricing](https://ai.google.dev/gemini-api/docs/pricing) / [Rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)。

### 現在の状態

- TEST_MATRIXは121項目: PASS 106 / FAIL 5 / FIXED 1 / BLOCKED 4 / NOT_TESTED 5。履歴のFAILは削除していません。
- `quality_checks_005`はNOT_TESTED、`conversation_004`もNOT_TESTED。集中実API品質チェックで1件でも失敗した場合、conversation_004は開始しません。
- GitHub Actions、PR #4の更新、最終コミットSHAは今回の変更のPush後に追記します。PR #4はDraftのまま維持し、マージしません。
