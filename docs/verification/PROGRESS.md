# 検証進捗

最終更新: 2026-10-14（継続作業）

## 2026-10-14 最終修正・実API会話検証（継続中）

- 開始時にリモートをfetchし、`codex/full-system-verification`のHEADが`4cb01c4e72de745295ed163c01802c60deda2273`であることを確認。PR #4は`feat/ui-local-backend-v1`宛てDraftで、マージなし。既存PROGRESS/TEST_MATRIX/FINAL_REPORT/prompt_specと共通・各モードのプロンプトを確認。Chromeは起動・操作していない。
- 環境: Windows 11系環境、Python 3.12.10 (`.venv`)、Node.js 25.9、Firefox。8765番は既存のPythonプロセスが使用中のため停止・変更せず。Firefoxは`start.bat`隔離テストで開いた。
- 修正: `start.bat`をPython 3.11+検出、前面起動の管理スクリプトへ変更。`scripts/start_server.py`は127.0.0.1のみで起動し、API応答確認後にFirefoxを開き、Ctrl+Cで自プロセスのUvicornだけを停止する。別プロセスがポートを占有すると終了させず案内する。Python 3.12で確認。
- 修正: `prompts/first.txt`に、初回候補ごとの軽い好意とマッチ成立の喜び、3案の表現差、容姿・趣味捏造防止を明示。`like`プロンプトは変更せず分離を維持。
- 修正: `app.js`の会話方針表示でStage 1–6と`invite_decision`内部値を日本語ラベルへ変換。APIの構造化値は保持。
- 修正: `scripts/simulate_conversation.py`に実験IDごとのJSON/HTML/一時SQLite分離、架空成人プロフィール002、初回`first`モードと以降`reply`を追加。既存001のパスとファイルは維持。
- Windows起動試験: 一時コピーと一時SQLiteで18768番を起動、Firefox表示とprofile API 200を確認。二重起動は同一アプリとして識別。Ctrl+C停止でポートが接続を受けなくなり、再起動も成功。18769番の一時HTTP listenerとの競合ではエラー案内を出し、listenerを動作状態のまま残した。8765番は既存プロセスのため未試験。
- 試験準備中に、隔離環境変数の指定に失敗した初回試行でリポジトリ直下のSQLiteを参照し、profile取得がHTTP 500になった。既存`data/app.sqlite3`の更新日時は試行前のまま（2026-10-14 13:33:44）、その後は接続していない。以後、テスト用アプリをTempへ複製してから確認した。既存データを意図的に変更・初期化していない。
- オフラインテスト: 修正対象のpytestとFirefox UIの37件が成功（1件の既知Starlette/httpx非推奨警告）。直前の全体pytestは104件成功。最新の全体再実行は実API後の最終確認で行う。`node --check app.js`、`git diff --check`成功。
- GitHubへ先に再現テストcheckpoint `ebd6fce497066c8fe04d58e203e39fa2ecef2f6c`をPush済み。今回の実装・文書更新は次の進捗commitでPushする。CI run URLはPush後に追記する。
- 修正checkpoint `b8b37e2b0503fcc83ed15ccf43bf40f20f51ec87` Push済み。GitHub Actions [Push run 38542247374](https://github.com/kenkyu0909/aichatapp/actions/runs/38542247374) は同SHAで成功（pytest・Firefox準備・Node構文・artifact upload）。runner再開修正checkpoint `2100b917eb0e58c727fc5f323b75492e8dfa7e7c` の[Push run 38542488356](https://github.com/kenkyu0909/aichatapp/actions/runs/38542488356)と[PR run 38542495182](https://github.com/kenkyu0909/aichatapp/actions/runs/38542495182)も同SHAで成功。
- 実API認証は指定フォルダー`C:\Users\poiuy\Desktop\aichatapp2\API`のみを参照するよう子プロセスを固定。API1/2の認証情報が読み出せることをbooleanだけで確認し、値は出力していない。初回生成の実通信は1 logical request成功、API1 / `gemini-3.5-flash-lite` / backend attempt 1。429切替は発生せず。`conversation_002.json`に候補3案と実際の使用モデル/別名を保存し、APIキーは含めていない。
- 初回3案の品質は一部FAIL: 推奨案は必須構成を満たしたが「、」「。」と不自然な詰まりがあり、2案目は好意/マッチの喜びが不足、3案目は質問がない。実験条件を崩さないため、送信前にプロンプトを変えず、この結果をT79として保存。会話終了後に修正・別リクエストで再評価する。
- 実験002は初回候補の承認前に、再開時に開始メッセージを求めるrunner不具合を検出。候補・SQLite履歴は変更せず`needs_partner_opening`判定を修正し、モックテスト2件を再実行してPASS。修正commitは次のpushに含める。
- 実験002状態: RUNNING、Gemini logical request 13件（成功13/失敗0、内部試行は全件1回）、アプリ送信13通、Codex相手役返信12通。全13件がAPI1 / `gemini-3.5-flash-lite`、フォールバック/制限なし。JSON/HTMLは実会話から逐次更新、APIキーパターンなし。初回候補選択後の各相手役返信は、保存済みの実送信文/履歴だけを見て作成。コード再開のrunner修正後、002を継続できた。
- 会話は書籍/映画の話題を続けている。相手役は現在、映画に関心を示すが、具体的に会う意思表示はしていない。日時や場所の合意はない。現時点で誘いはまだ送っていない。会話の成否を事前に決めず続ける。
- 次の作業: 最新JSON/HTMLと進捗をPushして途中保存。会話履歴を読み直し、Codex相手役として自然に応答を続ける。会う提案が自然と判断できた場合のみ本人情報の確認を行う。20通上限/安全停止/具体的な約束の成立条件に従って終了し、HTMLをFirefoxで確認。実API評価T77/T78を最終化し、失敗した初回生成指示は会話終了後に修正・少数回で再評価する。
- Pull Request: https://github.com/kenkyu0909/aichatapp/pull/4 （Draft維持、未マージ）

## 2026-10-14 返信品質・初回メッセージ・会話制御のオフライン改善

- 対象ブランチ: `codex/full-system-verification`。開始HEAD `5f52f80c33cc9af87538572479d5d60eff5284c4`。既存PR #4を継続し、Draftのまま。マージなし。
- この作業ではGemini実API通信を行わない指定に従い、すべての生成テストをSDKモックまたは固定UIモックで実施。Chromeは起動・操作していない。実ブラウザ操作はFirefoxのみ。
- 環境: Windows、Python 3.12（リポジトリ`.venv`）、Node.js（`node --check app.js`）、Firefox（Selenium）。
- 実装: 共通/モード別プロンプトを分割し、プロフィール事実の構造化、不足情報の一時質問、初回メッセージ、Stage 1–6と誘い判断、短文・句読点・「！」/絵文字/「笑」の文脈ルールを追加。質問回答はプロフィールへ自動保存しない。
- 実装: シミュレーターのAPI選択責任をバックエンドへ一本化。応答/エラーのAPI別名・モデル・試行回数を記録し、429全枠失敗も実際の順序で記録。20通目への相手の返答、拒否発言の保存、複数ターンの日時/場所合意、JSONからの隔離SQLite復元とロールバックを追加。
- 実装: `start.bat`はポートを占有するプロセスを終了せず、固有`app_id`を持つ応答を確認してからFirefoxを開く。起動順序・識別条件はテストで静的確認。今回、バッチを実際に起動する試験は未実施。
- 最終レビュー指摘も反映: 不正JSON/通信失敗はHTTP 200を含め成功扱いにせず、状態をBLOCKEDとして保存。明確な連絡終了表現を追加し、本人情報の確認中は回答があるまで再生成しないことを検証。
- 今回のローカル統合テスト: `pytest -q --junitxml=test-results\pytest.xml` は **103 passed, 1 warning**。警告はStarlette/httpxの非推奨通知。`node --check app.js` 成功。`git diff --check` 成功。Firefox UIテスト3件を含む。
- GitHub Actions: 実装コミット`5954b06c418158a48c60aa57b55e17f47a52c54a`のPush run [38536298397](https://github.com/kenkyu0909/aichatapp/actions/runs/38536298397)とPR run [38536305576](https://github.com/kenkyu0909/aichatapp/actions/runs/38536305576)が成功。Firefoxセットアップ、pytest、JavaScript構文チェック、artifact保存が完了。
- 報告コミット`baa9b89b2a28e9ce35a05f9f9e25a7c15fbeee6f`もPush [38536510987](https://github.com/kenkyu0909/aichatapp/actions/runs/38536510987) / PR [38536517187](https://github.com/kenkyu0909/aichatapp/actions/runs/38536517187)とも成功。両runの対象HEADは同じSHA。
- 完了: PR #4本文を更新。PRはDraft維持・未マージ。直近HEAD `ef5f232a1ec6b10d07396f2a704dd419923549f2`のPush [38536709582](https://github.com/kenkyu0909/aichatapp/actions/runs/38536709582) / PR [38536717824](https://github.com/kenkyu0909/aichatapp/actions/runs/38536717824)は成功。今回の残りはこの進捗記録のみで、push後に同じオフラインCIが自動起動する。
- 未実施: Gemini実APIの文章品質、Windows `start.bat`の実起動/ポート競合動作。前者は今回の明示的なAPI禁止、後者は既存データ/ポートを使わない安全な隔離実機試験を用意できていないため。
- 現在のブロッカー: なし。実API品質の判断はユーザーが後日許可するまで保留。
- 次: レビューフィードバック反映、全テスト再実行、報告書更新、意味単位でコミット・Push、PR #4最新HEADのCI結果を記録。
- 実装コミットSHA: `5954b06c418158a48c60aa57b55e17f47a52c54a`。最終記録の親コミットSHA: `ef5f232a1ec6b10d07396f2a704dd419923549f2`（Push/PR Actions成功）。本進捗更新はドキュメントのみ。Pull Request: https://github.com/kenkyu0909/aichatapp/pull/4

## 2026-10-14 利用制限時の優先フォールバック追加

- ユーザー指定の優先順を通常のFastAPI `/api/generate`にも実装: API1 / `gemini-3.5-flash-lite` → API2 / `gemini-3.5-flash-lite` → API1 / `gemini-3.1-flash-lite` → API2 / `gemini-3.1-flash-lite`。
- HTTP 429または`RESOURCE_EXHAUSTED`のときだけ次の組み合わせへ進む。401/403/404、接続失敗、形式不正では切り替えず、既存の安全なエラー表示を保つ。429時に最大4回まで試し、無制限再試行はしない。
- `MRA_API_DIR`（既定はアプリフォルダの隣の`API`）から`chat1.md`/`chat2.md`を読み、値は出力しない。現在の両ファイルが単一トークンとして受理されることを長さだけで確認。ファイル内容・キー値はログやレポートに含めていない。
- オフラインモック試験: API1 3.5とAPI2 3.5を429にし、API1 3.1で成功する順序、全4候補が制限された場合のAPI2 3.1到達、403時は1回で停止、APIファイル経由のキー選択と応答への秘密値非混入、空の`MRA_API_DIR`で既定隣接フォルダを選ぶ動作、旧`GEMINI_API_KEY`を使わない動作を確認。新規5テスト成功。全テストは空の認証ディレクトリに隔離され、実APIは呼び出していない。
- ローカル全pytest: 48 passed、警告1件（Starlette/httpx deprecation）。`node --check app.js`成功。
- commit `d5513f620b55758cc1a22957d431f61d1a4233ec` のPush Actions [38528562779](https://github.com/kenkyu0909/aichatapp/actions/runs/38528562779)とPR Actions [38528568834](https://github.com/kenkyu0909/aichatapp/actions/runs/38528568834)が両方成功。各runは同SHA、pytest 48 passed / warning 1、Node構文チェック成功。
- 差分レビューでは認証ソースの隔離と優先順に問題なし。通常テストが外部APIへ出ないよう共通fixtureを空の一時認証ディレクトリに固定。PR #4はDraftのまま。

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


## 2026-10-14 最終検証結果（完了）

- 最新開始状態はブランチ`codex/full-system-verification`、HEAD `4cb01c4e72de745295ed163c01802c60deda2273`。PR #4は`feat/ui-local-backend-v1`宛てのDraftで継続し、マージしていない。前進中の会話チェックポイント`b0845b3a21cc9803e14821e4097a462771e065c8`は既にPush済み。
- Windows 11系環境、Python 3.12.10、Node 25.9、Firefoxを使用。Chromeには触れていない。8765番の既存プロセスは維持。別の一時ポートで`start.bat`、二重起動、Ctrl+C、ポート解放、再起動、競合案内をFirefoxと一時SQLiteで確認。Windowsの実データディレクトリは使っていない。
- 実API: 会話002の20論理リクエストと別環境の品質確認5回、計25回がすべて成功。モデルは`gemini-3.5-flash-lite`、API別名API1、各試行1回。HTTP 200/非デモ/3候補を確認。429、フォールバック、失敗リクエストなし。API2および3.1系は使用していない。キー文字列は出力・記録していない。
- 会話002は架空プロフィールと一時SQLiteのみを使用。アプリ20通、相手20通、合計40件。最後の相手返信を保存し、`LIMIT_REACHED`。誘いなし、日時・場所の合意なし、21通目なし。JSON/HTML/分析ファイルに保存。会話001は維持。
- 別の品質確認で、本人が映画好きか直接問われた際に、未登録なのに「映画はときどき観ます」とする実生成を検出。`prompts/common.txt`へ直接質問に対する必須の本人確認ルールを追加し、SDKモックの質問/回答分離テストはPASS。実APIの変更後再確認は25リクエストで止めたため未実施。T77をFAILのまま記録。
- 初回メッセージの初回出力不具合後、`prompts/first.txt`で候補ごとの自己点検を追加。別実API呼び出しで3案の構成・句読点が改善したためT79をFIXED、T80をPASS。実生成結果は別ファイルへ保存。
- Firefoxで`conversation_002.html`を開き、40メッセージ、左右20件ずつ、詳細20件、詳細展開、終了状態、CSS、日本語、外部通信なしを確認。スクリーンショットは`simulations/conversation_002_firefox.png`。
- APIキー形式スキャン: 全69個のGit refsとworking treeで一致0件。秘密値は表示していない。Actionsログ全履歴までは調査していない。
- ローカルテスト: `python -m pytest -q` **104 passed, 1 warning**。`node --check app.js`成功。`git diff --check`成功（改行コードに関するGit警告のみ）。
- Google公式モデル一覧では3.5/3.1 Flash-LiteをStable掲載。公式料金表では3.5 Flash-Liteに無料ティアが掲載されるが、無料枠入力/出力はGoogle製品改善に使用される条件。個別プロジェクトの使用枠、請求状態、実費は確認していない。モデル枠はプロジェクトやティアで変動し、AI Studioで確認する仕様。課金設定は変更していない。
- テストマトリクスは81項目: PASS 74 / FAIL 1 / FIXED 1 / BLOCKED 3 / NOT_TESTED 2。FAILはT77（本人の未知の好みを生成）で、関連プロンプトは修正したが実API再試験が残る。
- ソース修正SHA: `d431b79f159a7e7fc499a7acf06a12e13454c4b4`。レポート/証拠の検証HEAD `cf24e2398ab428cb9e3beef2b0029f34aa73d4b4`のPush [38544684207](https://github.com/kenkyu0909/aichatapp/actions/runs/38544684207) / PR [38544689940](https://github.com/kenkyu0909/aichatapp/actions/runs/38544689940)は成功。Actions結果を記録する更新を`a40c251c62c400401c9aef3e77beeaf7ceb76079`へPushし、同SHAのPush [38544920718](https://github.com/kenkyu0909/aichatapp/actions/runs/38544920718) / PR [38544928533](https://github.com/kenkyu0909/aichatapp/actions/runs/38544928533)も成功。PR本文を最新HEADへ更新しDraft維持。
- PR #4: https://github.com/kenkyu0909/aichatapp/pull/4

## 2026-10-14 会話003準備・レビュー指摘の修正

### 作業状態

- 対象: `codex/full-system-verification`、既存Draft PR #4（base: `feat/ui-local-backend-v1`）。開始時にGitHubの最新ブランチをfetchし、ローカルHEADは`28f1a5dfc0e08279273fea50d198ec36010b8f88`と一致していた。
- ユーザー提供の`docs/verification/simulations/指示.txt`を確認した。これはユーザー資料として存在する未追跡ファイルであり、コミット対象へ追加しない。
- 既存の会話001・002のJSON/HTML・分析・quality JSONを保持。003のJSON/HTML・一時DBは開始時点では存在しない。APIファイル`chat1.md`・`chat2.md`は存在することだけを確認し、値は表示していない。
- 実環境はWindows、Python 3.12の`.venv`、Node、Firefox。Chromeは使用していない。実APIはまだ未実施。

### 修正済み・オフライン確認済み

- 送信候補本文の「、」「。」検査を維持し、候補品質の再生成をモデルフォールバックをまたいでも1回に制限する回帰テストを追加。
- 候補に「映画はときどき観る」「幅広く読む」「横浜によく行く」「お気に入りの店がある」等の既知の一人称主張が含まれる場合、根拠なしに表示しない検査を追加。response v2では本人確認へ回し、旧response形式では安全に失敗する。
- 「読書が趣味」だけでは本のジャンル・最近読んだ本を確認済みとせず、「映画好き」への肯定だけでは映画のジャンルや頻度を許可しない。未確定の予定は確定予定として扱わない。
- 会話履歴から本人事実を推定せず、本人プロフィールと今回の一時回答だけを根拠にする。プロフィール回答を永続保存しない。
- 会話003のresumeで`profiles_003.md`を上書きしない。
- 新しい回帰テストを含む全体`pytest -q`: **130 passed, 1 warning**（Starlette/httpxの非推奨通知）。Firefox UIテストを含む。旧response版、否定プロフィール、確認回答の事実粒度の試験も含めた最終テスト。`node --check app.js`と`git diff --check`成功。テストは`.venv`のPython 3.12.10を使用。実Gemini通信と最新HEAD CIは未実施。

### 未実施

- T77の修正後Gemini実通信、文体/mirroringの実API評価A〜H、会話003の実験、HTMLのFirefox表示確認。
- 変更後のFirefox UI E2E、pytest全体の再実行、GitHub Actions最新HEAD。
- `conversation_003.json`/`.html`/分析/プロフィール成果物。
- `FINAL_REPORT.md`およびPR #4本文の最終更新。

### 次の作業

1. レビューフィードバックを再確認し、全オフライン回帰テストを実行。
2. T77と最小の実API品質チェックを既定のAPI1→API2、3.5→3.1順で行い、429以外は切替えない。既知の会話情報だけを使い、各リクエストを数える。
3. 実APIが継続利用できる場合だけ会話003を開始。技術制約が出たら直ちに保存し`BLOCKED`にする。
4. JSON/HTML/分析/進捗・マトリクスを更新してcommit/push。Draft PR #4は維持し、mergeしない。

### GitHub

- PR #4: https://github.com/kenkyu0909/aichatapp/pull/4（Draftのまま）
- 今回のコード・進捗コミット、実API検証結果、最新Actions URL: 未作成。Push前に確認し追記する。
