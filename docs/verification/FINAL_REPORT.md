# 最終検証報告

## 今回の継続検証（2026-10-14）

### 総合判定

**CONDITIONAL PASS（条件付き合格）**。前回の報告から未実施7項目を検証し、CI・Firefox E2E・SQLite保存障害処理を追加しました。コード検証SHA `4647f2ba8ec432ca3d79bccc24bb03fb73f528eb` はGitHub ActionsのPushとPR両方で成功しました。利用開始は可能ですが、旧APIキーの失効確認が必要であり、今回の`start.bat`再実行は使用中の8765ポートによりBLOCKEDでした。

### テスト集計

- テスト項目: 51
- PASS: 50
- FAIL: 0
- BLOCKED: 1（T02。127.0.0.1:8765を既存Pythonプロセスが使用中。プロセスは停止・変更していない）
- NOT_TESTED: 0
- ローカルpytest: **33 passed, 1 warning**。Python 3.12.10、Windows。警告はStarlette/httpxの非推奨通知。
- GitHub Actions: **33 passed**、Firefox 157、Ubuntu、Python 3.11。`node --check app.js`成功。Push [run 38518047903](https://github.com/kenkyu0909/aichatapp/actions/runs/38518047903)、PR [run 38518053494](https://github.com/kenkyu0909/aichatapp/actions/runs/38518053494)。両方ともSHA `4647f2ba8ec432ca3d79bccc24bb03fb73f528eb`。
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
- コード修正SHA: `f73c1649efa614f51d88547dc1fdb33ca92cefbb`、保存先初期化修正SHA: `4647f2ba8ec432ca3d79bccc24bb03fb73f528eb`。

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
