# 検証進捗

最終更新: 2026-10-14（継続作業）

## 2026-10-14 会話シミュレーション実験（最新）

- 作業開始時にGitHubの`codex/full-system-verification`をfetchし、HEAD `a5fa30c100c6fffdf22b63e9d740c3157584ed7f`がローカル/remote/PR #4で一致することを確認。PR #4は`feat/ui-local-backend-v1`宛てDraft、未マージ。
- 既存のPROGRESS、TEST_MATRIX、FINAL_REPORTを読み、前回51項目・PASS 50/BLOCKED 1を引き継いだ。
- Windows/Python 3.12.10/Node.js 25.9.0/Firefox 157。Chromeには触れていない。
- 127.0.0.1:8765の既存Uvicorn PID 39504を確認。既存プロセスは本アプリと断定できる追加操作をせず、停止・変更していない。前回のWindows `start.bat`再確認はポート衝突でBLOCKEDのまま。
- 架空プロフィールを作成し、専用の一時SQLiteへ登録。相手役の開始メッセージ1件がSQLiteとJSONに保存されていることを再開時に照合。
- 既存FastAPI `/api/generate`に対し、指定順の最初のAPI1 / `gemini-3.5-flash-lite`で実通信を1回実施。アプリのHTTP 502（「Gemini APIキーまたはモデルの利用権限を確認してください。」）となり、候補生成前にBLOCKED。根本原因は認証・権限・接続のどれか特定できない。レート制限応答ではなかったためAPI2へ切り替えていない。API2/3.1は今回未使用。
- 結果: `conversation_001.json`に1回の失敗、実送信0通、相手役1通を保存。架空のGemini候補や会話継続は作っていない。HTMLとプロフィール、分析も生成。
- `scripts/simulate_conversation.py`、`scripts/render_conversation_report.py`、`tests/test_conversation_simulation.py`を追加。候補を保存してから段階再開できるCLI、APIエラー後のJSON/一時DB照合、送信数20通の上限制御、成功条件の人による最終確認を実装。HTMLは値をエスケープし、外部依存なし。
- pytest最終ローカル実行: 43 passed、警告1件（Starlette/httpx deprecation）。`node --check app.js`成功。FirefoxでHTMLを実際に開き、会話1件、架空プロフィール、BLOCKED状態、採点未実施の10項目、外部読込なしを確認。スクリーンショットを保存。
- 実験結果・レポートをcommit `df7110205b8e522475cdcad7e08c8152ace360cb`としてpush済み。Push Actions [38525998484](https://github.com/kenkyu0909/aichatapp/actions/runs/38525998484)とPR Actions [38526003199](https://github.com/kenkyu0909/aichatapp/actions/runs/38526003199)は同SHAを対象に成功。pytest 43 passed、Node構文チェック成功。
- 今回の実験はGemini実応答がないため、会話品質・約束成立はT56 BLOCKEDとして追加。今回のマトリクスは56件（PASS 53 / BLOCKED 3）。料金・プロジェクト別割当も不明。旧APIキーの失効は確認できていない。
- 最新検証HEAD `8a0097c1ad648692e6e93714b2e98e47b5e6cc43`（T56追加）に対するActionsも成功。Push [38526380171](https://github.com/kenkyu0909/aichatapp/actions/runs/38526380171)、PR [38526386149](https://github.com/kenkyu0909/aichatapp/actions/runs/38526386149)、ともに43 passed。
- PR #4本文へ会話HTML・JSON・分析、T52–T56、Actions URL、残課題を追記する。PRはDraft維持・未マージ。

## 2026-10-14 継続検証の最新状況

- 対象: `codex/full-system-verification`、開始時HEAD `63b972811e32996d6fdcf0cf248d49c21efc4b9b`。最新検証コードSHA: `dcf5dbd6838117b1fd28dde99efcc8e2227538b8`。PR #4はDraft、未マージ。
- CI修正: `e27df38846ffd02baf8c3a4293188a9e84a4f3a4`でPush/PR両トリガーを実行。`dcf5dbd`のPush run [#38518482078](https://github.com/kenkyu0909/aichatapp/actions/runs/38518482078)とPR run [#38518486199](https://github.com/kenkyu0909/aichatapp/actions/runs/38518486199)が成功。Ubuntu/Python 3.11/Firefox 157で33 passed、`node --check app.js`成功。結果とスクリーンショットはActions artifactに保存。
- Windowsローカル: Python 3.12.10、Node.js 25.9.0、Mozilla Firefox/Selenium。実装の回帰スイート33 passed、1件のStarlette/httpx非推奨警告。Firefoxのruntime/console.error監視はいずれも空。追加した会話削除UI操作はFirefoxで個別再試験し成功。
- T05、T19、T30、T35、T36、T47、T48を実施し、TEST_MATRIXへ方法・制限を記録。T51（保存先をimport時点から使えない場合）も追加。
- T02の今回再確認は`BLOCKED`: 127.0.0.1:8765を既存の`python3.12`がlistenしていたため`start.bat`内のUvicornがWinError 10048。既存プロセスは停止・変更していない。前回の起動成功記録は履歴として維持。
- 実API追加試験は2リクエスト。API1の3.5 Flash-Liteは429相当で失敗し、指定順にAPI2の3.5 Flash-Liteへ切替。敵対的な架空プロフィール試験は成功。API1/2の3.1は未使用。秘密情報や生成本文をログへ出していない。
- 修正: Gemini SDK下限を`>=1.74`へ引き上げtimeout/retry設定との互換性を確保。SQLite/写真保存先の初期化を遅延し、保存障害を安全なHTTPエラーへ変換。写真保存失敗時の一時ファイル掃除、Gemini timeoutと無制限再試行防止、Firefoxテストの起動失敗時後始末を追加。
- TEST_MATRIXは51項目、PASS 50 / BLOCKED 1 / FAIL 0 / NOT_TESTED 0。未解決の注意: 旧APIキーの失効状態は確認できず、ユーザー側で失効確認が必要。
- 最終ドキュメントをpushした後、Actionsを再実行し、PR #4最新HEADのSHAと成功結果を確認する。

## 継続作業の開始記録（履歴）

- 開始時のローカル・GitHub HEAD: `63b972811e32996d6fdcf0cf248d49c21efc4b9b`（一致を確認）
- 既存PR #4: Open、Draft。ベースは`feat/ui-local-backend-v1`。
- 既存の進捗・マトリクス・最終報告を読み、前回未実施の7項目を引き継いだ。
- 通常CIを`codex/full-system-verification` Pushと`feat/ui-local-backend-v1`宛てPRで起動する設定に修正。Workflow変更commit `e27df38846ffd02baf8c3a4293188a9e84a4f3a4`でPush runとPR runが成功。
- Push run: https://github.com/kenkyu0909/aichatapp/actions/runs/38516050254
- PR run: https://github.com/kenkyu0909/aichatapp/actions/runs/38516055938 （15 passed、Node構文確認成功）
- これはCI初回修正コミットの実行結果。後続のコード修正後、最終HEADで再実行する。
- 実APIキーは参照・使用していない。旧キーの有効性も確認していない。

## 作業開始

- 作業開始日: 2026-10-14（開始時刻は記録なし）
- 元ブランチ: `feat/ui-local-backend-v1`
- 作業ブランチ: `codex/full-system-verification`
- 作業開始時のGitHub先端: `78a66c9cba0e6ddb7bc1441e65e1eae75a5e304b`（取得時点で指定コミットと一致）
- GitHub Pages版、`main`、`arena/072200f4-aichatapp`には変更なし。
- 初期進捗コミット: `e0410c8`（ローカルのみ。pushは権限エラー）

## 実行環境

- OS: Windows
- Python: 3.12.10
- Node.js: v25.9.0
- ブラウザー: Mozilla Firefox（Seleniumで実画面を操作。Firefoxのバージョン値は未記録）
- DB: 一時保存先をリポジトリ外に設定したSQLite
- 架空の人物・プロフィール・会話だけを使用。

## 状態

- 準備・依存導入: `PASS`
- FastAPI起動とローカルUI: `PASS`
- 基本機能とSQLite再起動確認: `PASS`
- Gemini実通信: `PASS`（API1の3.5 Flash-Liteで割当上限応答を受け、指定順にAPI2の3.5 Flash-Liteへ切替）
- API更新後の再確認: `PASS`（API1の3.5 Flash-Liteで実API返信・いいねを確認）
- UI実操作: `PASS`（Firefox）
- 不具合修正後のpytest: `PASS`（15件成功、警告1件）
- GitHub push・Draft PR: `PASS`（再試行でpush成功。PR #4をDraftで作成）
- 継続作業CI初回: `PASS`（commit `e27df38846ffd02baf8c3a4293188a9e84a4f3a4`でpush/PR run成功。pytest 15件、Node構文確認成功。最終HEADでは再確認待ち）

## 完了した作業

- 指定ブランチをクローンし、作業ブランチを作成。
- README、FastAPI、UI、起動バッチ、依存関係、既存テスト、Gemini smoke testを確認。
- Python仮想環境を作成し、依存関係を導入。
- `start.bat` と直接のUvicorn起動を実行。`127.0.0.1`のローカルURL、HTML、CSS、JavaScriptがHTTP 200を返すことを確認。バッチがWindows既定ブラウザーを起動しないようFirefox専用に修正し、再実行でFirefox表示を確認。
- Firefoxでプロフィール保存、相手3人、写真表示、会話分離、検索、切替、再読込、返信生成、いいね生成、コピー、送信記録、履歴・設定・使い方、JSON export、キーボード操作、相手削除を実施。
- サーバー再起動後も架空プロフィール、相手、会話がSQLiteに残ることを確認。
- APIキーの指定後は、API1・API2のキーでGemini実通信。API1 3.5の割当制限応答後、API2 3.5へ切替。
- `.env`、SQLite、写真のGit除外、localhost bind、プロンプト文脈の写真・他相手履歴分離、出力エラー処理を確認。
- 不正画像、壊れた画像データ、5MB超、16メガピクセル超の画像を拒否し、画像を実デコードして検証するよう修正。
- 生成ボタンが起動時に全モーダルを開いていたUI不具合と、smoke testのimport path不具合を修正。
- 生成文で本人のプロフィールにない好みを補う事例を確認し、返信・いいね用プロンプトを修正。追加の実APIいいね再試験では本人の好みを捏造しない3案を確認。
- 既存の`python scripts/live_gemini_smoke.py`をAPI2で実行。返信・いいねの3案生成と履歴不変を確認。
- pytest: `15 passed, 1 warning`。

## 発見・修正した不具合

1. `app.js`: 起動時にモーダル関数を呼び出してしまうイベント登録。クリック時に呼ぶ形へ修正。
2. `app.py`: 画像のマジックバイトだけを見て不正画像を受け入れる。Pillowで形式確認、16メガピクセル上限、`verify()`、再オープン後の`load()`を追加。
3. `scripts/live_gemini_smoke.py`: `python scripts/live_gemini_smoke.py`でアプリをimportできない。リポジトリルートをimport pathへ追加し、実行確認。
4. `prompts/reply.txt`・`prompts/like.txt`: 本人が書いていない嗜好や共通点を生成する例。根拠のない一人称の好み・経験を禁止する指示を追加。
5. `start.bat`: Windows既定ブラウザーを起動してFirefox指定に反する動作を修正。Firefoxを明示し、見つからない場合はURLを案内。

## 未実施

- ブラウザーのJavaScript Consoleを直接採取する確認。
- 会話方針の表示切替、無効APIキー・利用不可モデル、ネットワーク切断、保存先権限エラー、サーバー停止中UIを個別に再現する確認。
- プロフィールへ敵対的な命令を含めた実API生成確認。
- Gemini API1/API2の3.1モデル。API2の3.5が成功したため、指定順に沿って未使用。
- Windows以外の環境。
- 実利用者データによる試験（仕様どおり未使用）。

## API利用とプライバシー

- ユーザー指定のAPIファイルは作業元フォルダーの`API/chat1.md`と`API/chat2.md`。キーは出力・リポジトリ・`.env`へ保存しない運用。
- API更新前の指定フォルダー由来の実API試行は12回（API1 3.5が1回、API2 3.5が11回）。API1 3.5は割当上限応答後にAPI2へ切替。API2 3.5は10回応答成功し、1回は誤ったローカルキー抽出で認証/モデル権限エラー。
- ユーザーからAPI更新の連絡後、API1 3.5で既存smoke testを実施。返信・いいね2回とも成功。更新後のAPI2キーは今回未使用。
- GitHubへのpushに成功し、`feat/ui-local-backend-v1`をマージ先とするDraft PR #4を作成。
- プロンプトを修正する品質再試験とUI/smoke test確認で追加実通信。API1/2の3.1は未使用。
- APIキーを読み取った際、秘密値を伏せる処理が失敗し、この会話のツール出力に更新前の両キーが露出した。Gitには保存していない。ユーザーから更新連絡があったが、更新前キーがGoogle側で失効したかは確認できない。API2の更新後キーも実通信では未確認。
- APIフォルダー指定前に、既存の環境変数キーで失敗リクエストを1回行った。指定後は当該キーを使っていない。環境変数キーの出所・状態は要確認。
- Google公式の料金・利用規約で無料枠と入力データ取扱条件を確認。無料枠への入力は製品改善に使われる場合がある。プロジェクト固有の課金状態は確認できない。

## GitHub・ブロッカー

- 初回pushとSecret一覧参照はHTTP 403だったが、後のpushは成功。
- 作業ブランチ`codex/full-system-verification`をGitHubへpushし、Draft PR #4を作成。
- Secret一覧の有無は引き続き未確認。

## 初期再検証時の進捗（履歴）

- CI初回修正・Actions確認: `e27df38846ffd02baf8c3a4293188a9e84a4f3a4`。Push/PRの両runが成功。最終HEADの再実行は後続修正push後。
- T05、T19、T30、T35、T36、T47、T48: 今回の再検証を開始。結果はTEST_MATRIX.mdに証拠とともに追記する。
- UI検証はFirefoxのみ。Chromeは使用しない。

## 開始時点の残作業（今回の結果で更新）

1. 露出した旧API1・API2キーがGoogle側で失効済みか確認し、環境変数の別キーがあれば状態を確認する。
2. 7件の`NOT_TESTED`項目は今回検証済み。T02のWindows `start.bat`再実行のみ、既存の8765 listenerによりBLOCKED。

## GitHub

- 最終実装コミットSHA: `ae042ea41b3b1439abc6c8c27c8945a1fd915682`
- 検証報告コミットSHA: `80d2349ebfd53cbc87a6df0a10d786b7634451be`
- 前回進捗コミットSHA: `998a84b511bb154082b6ce0e238f95adaf8a15b6`
- API更新後のsmoke testコミットSHA: `ba1a45205167ab1830982d8dc1bcb7e74822f701`
- 最終検証内容のGitHub公開確認SHA: `3fcedae1e67e867c41be4692265145bb2498fa05`（PROGRESSのSHA記録を追加する直前に確認）
- Pull Request URL: https://github.com/kenkyu0909/aichatapp/pull/4（Draft）

## 今回の最終状態

- 完了: CI修正、未実施7項目、主要回帰テスト、SQLite/写真障害処理、Firefox UI E2E、PR #4本文更新。各修正・報告を作業ブランチへpush済み。
- 今回の状態: TEST_MATRIX 51項目、PASS 50 / BLOCKED 1 / FAIL 0 / NOT_TESTED 0。テスト実行: 33 passed（WindowsローカルとUbuntu Actions）、Node構文チェックPASS。
- 実API: 追加2リクエスト。API1 3.5は429相当、API2 3.5の敵対的架空プロフィール生成は成功。3.1は未使用。秘密文字列・生成本文はログに保存していない。
- セキュリティスキャン: Git履歴と直近12件のActionsログでGoogle API key形式`AIza...`は見つからなかった。過去の会話出力への露出は残るため旧キー失効の確認が必要。GitHub Secrets一覧は権限がなく確認できていない。
- Windows再起動: `start.bat`の今回再試行は既存の`127.0.0.1:8765` listenerとの競合で完了せず。既存プロセスに手を触れず、成功扱いにしていない。
- 今回の検証コードSHA: `dcf5dbd6838117b1fd28dde99efcc8e2227538b8`。これ以降の更新があれば、PR checksページで最新HEADの実行を確認する。
- PR #4: https://github.com/kenkyu0909/aichatapp/pull/4。Draftのままレビュー待ち。マージしていない。
