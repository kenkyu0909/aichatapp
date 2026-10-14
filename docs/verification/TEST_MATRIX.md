# テストマトリクス

架空のプロフィール・人物・会話のみで実施。結果は実際の確認に基づき記録。

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T01 | アプリ起動（Python） | Python 3.12.10、Uvicorn | PASS | `127.0.0.1:8767`で起動。再起動も実施。 |
| T02 | Windows `start.bat`起動 | 実機で実行 | BLOCKED | 2026-10-14の再確認では127.0.0.1:8765を既存の`python3.12`プロセスが占有しており、バッチ内UvicornはWinError 10048で起動できなかった。既存プロセスには触れていない。前回成功の履歴は下記の旧報告を参照。 |
| T03 | ローカルURL HTTP 200 | HTTP確認 | PASS | `/`が200。 |
| T04 | HTML・CSS・JavaScript配信 | HTTP確認 | PASS | `/`、`/style.css`、`/app.js`が200。 |
| T05 | ブラウザーJavaScript Console | Windows 11、Python 3.12.10、Selenium Firefox。アプリ起動・プロフィール・相手追加/切替・メッセージ追加/編集/削除・返信・いいね・設定・再読込を操作し、ページへ例外・未処理Promise拒否・console.error監視を追加 | PASS | Firefox UI自動操作でruntime/console errorsはいずれも空。直接の開発者ツールConsole採取ではなく、ページ側監視。ログ・スクリーンショットはActions [38518482078](https://github.com/kenkyu0909/aichatapp/actions/runs/38518482078) の`offline-test-results` artifact（実行SHA `dcf5dbd6838117b1fd28dde99efcc8e2227538b8`）。テスト: `tests/test_ui_firefox.py`。 |
| T06 | 自分のプロフィール保存・読込・更新 | Firefox UI、API、再起動後読込 | PASS | UI保存後、サーバー再起動後もSQLiteから読み込めた。APIテストで更新も確認。 |
| T07 | 相手3人の追加・表示・検索・切替 | Firefox UI | PASS | 架空の3人を登録、検索絞込・解除、相手切替を確認。 |
| T08 | 相手プロフィール編集・削除 | Firefox UI、API | PASS | UI編集・削除を実施。相手削除後、一覧から消えた。 |
| T09 | 写真追加・表示・差替え | Firefox UI、API/SQLite | PASS | 架空PNGのUI登録と表示を確認。APIテストで差替え時の旧ファイル削除も確認。 |
| T10 | 不正画像・壊れた画素・画素数上限・5MB超の拒否 | API異常系 | PASS | Pillowで画像を全デコードし、16メガピクセル上限を追加。pytestで400を確認。 |
| T11 | メッセージ追加・時系列・発言者表示 | Firefox UI/API | PASS | 相手・自分の交互発言と吹き出し表示を確認。 |
| T12 | メッセージ編集・削除 | Firefox UI/API | PASS | UI編集、APIテストで編集後削除と空履歴を確認。 |
| T13 | 相手切替時の会話分離 | Firefox UI/API | PASS | 相手ごとに別履歴を表示。Gemini送信文脈も別相手を除外。 |
| T14 | 再読み込み・アプリ再起動後のSQLite永続化 | Firefox、サーバー再起動、HTTP | PASS | プロフィール、相手2人、会話（3件・1件）が再起動後も残った。 |
| T15 | 相手削除時の会話・写真削除 | UI/API/ファイル確認 | PASS | 相手削除、外部キーによる会話削除、写真差替え後ファイル削除を確認。 |
| T16 | 返信生成1案・3案・5案 | Firefox UI・API・pytest | PASS | UIで1/3/5案、APIテストで1/3/5案の数を確認。 |
| T17 | 自動・敬語・混合・タメ口 | Firefox UI・生成文脈テスト | PASS | UIで4設定を選択。モック文脈では敬語設定を確認。 |
| T18 | 返信方向・追加指示 | Firefox UI・モック | PASS | 方向と自由入力を設定。追加指示がGemini送信文脈に含まれることを確認。 |
| T19 | 会話方針の表示切替 | Firefox UI、固定Geminiモック応答にstrategyを含める | PASS | ON→生成、OFF→再生成、ON→再生成。状態`[true,false,true]`、各回返信3案を確認し、OFF時は方針を隠し、前回の表示を残さない。ログはActions artifact。テスト: `tests/test_ui_firefox.py`。 |
| T20 | 候補コピーと送信記録の分離 | Firefox UI | PASS | コピー後は履歴件数が不変。明示的な記録操作後だけ自分の発言が増えた。 |
| T21 | 追いメッセージ生成 | Firefox UI・API | PASS | 最後が本人の発言の履歴で生成し、通常返信と別の見出しで表示。 |
| T22 | メッセージ付きいいね3案 | Firefox UI、Gemini実通信 | PASS | API2の3.5 Flash-Liteで3案を生成・UI表示。 |
| T23 | 履歴・設定・使い方画面 | Firefox UI | PASS | 3つの画面を開閉。起動時に設定モーダルが誤表示される問題も修正。 |
| T24 | JSONエクスポート | Firefox UI | PASS | JSONダウンロードを確認。 |
| T25 | キーボード操作 | Firefox UI | PASS | Ctrl+Enterで入力文を会話履歴へ追加。 |
| T26 | Gemini返信実通信・日本語品質 | API1/2、実API・Firefox UI | PASS | API更新前はAPI1 3.5制限後にAPI2へ切替。更新後のAPI1 3.5で返信・いいね各3案も再確認。 |
| T27 | Geminiいいね実通信・品質 | API2 3.5、実API・Firefox UI | PASS | プロンプト修正後の再試験でプロフィール由来の3案を確認。 |
| T28 | 候補数・重複・形式検証 | モック異常系 | PASS | 形式不正、重複、候補数不足を502で拒否。固定文を生成結果として表示しない。 |
| T29 | APIキー未設定時の表示・生成 | API/Firefox UI | PASS | 固定サンプルを「会話を解析していない」と明示。 |
| T30 | 無効キー・権限なし・未使用モデルのエラー | Gemini SDKモック/API異常系 | PASS | 401無効キー、403権限拒否、404モデル不在、キー未設定をモック。利用者向けエラー、キー/内部詳細の秘匿、生成失敗扱い、SQLite会話不変を確認。実APIへ無効キーは送信していない。テスト: `tests/test_app.py`、Actions run [38518047903](https://github.com/kenkyu0909/aichatapp/actions/runs/38518047903)。 |
| T31 | Gemini JSON不正・429時の処理 | pytestモック、API1実通信 | PASS | JSON不正と429を確認。実API1の制限応答後はAPI2へ切替。SDKの詳細は応答へ出ない。 |
| T32 | 空入力・空プロフィール | API異常系 | PASS | 必須プロフィール空欄は400、空白の名前は422。 |
| T33 | 存在しない相手ID | API異常系 | PASS | 404を確認。 |
| T34 | 長い会話履歴 | SQLite/API | PASS | 65件登録時、最新60件を文脈に含めることを確認。 |
| T35 | 保存先アクセス失敗 | Windows一時領域の実ファイル操作、DB/写真先の障害注入 | PASS | DB保存先の親を通常ファイルにしてHTTP 500の汎用エラーを確認。写真先がファイルの場合は部分ファイルとDB参照を残さない。写真フォルダー欠落時は安全に再作成。DB書込後の異常・中断時の一時ファイル削除もpytestで確認。NTFS ACLの拒否設定はユーザー環境を変えないため未実施。テスト: `tests/test_app.py`。 |
| T36 | サーバー停止中のUIエラー・再起動 | Firefox UI、別DBのUvicornプロセス停止/再起動 | PASS | 停止中にメッセージ追加、プロフィール保存、相手追加、返信生成を操作。失敗表示、入力保持、ボタン再操作可能、JS例外なしを確認。再起動後の保存と履歴を再確認。Actions artifact、テスト: `tests/test_ui_firefox.py`。 |
| T37 | 起動ホストが127.0.0.1 | Uvicornプロセス・バッチ確認 | PASS | 起動引数と実際のlisten addressが127.0.0.1。 |
| T38 | 写真がGeminiへ送られない | SDKモック・文脈確認 | PASS | リクエストに画像内容・ファイル名・パスがないことを確認。 |
| T39 | 他の相手の会話がGeminiへ送られない | SDKモック | PASS | 対象相手の会話だけが文脈に含まれる。 |
| T40 | APIキーがリクエスト本文・エラーに出ない | SDKモック・エラー試験 | PASS | 本文にキーなし。429時にSDK詳細を返さない。キー値はテストログにも記録していない。 |
| T41 | `.env`・SQLite・写真のGit追跡 | gitignore確認 | PASS | `.env`とローカルデータのignoreを確認。追跡対象なし。 |
| T42 | XSS・パストラバーサル対策 | ソースレビュー・画像異常系 | PASS | UIは`textContent`とDOM APIを使用。写真名はUUID生成で受取パスを使わない。 |
| T43 | プロンプトインジェクション対策の実装 | プロンプト・送信文脈レビュー | PASS | 相手の命令文をデータ扱いする指示あり。実APIへの攻撃文注入は別項目で未実施。 |
| T44 | APIエラー後の履歴保全 | 429/不正JSONのモック | PASS | 生成失敗の前後で会話件数が変わらない。 |
| T45 | 無料枠のプライバシー条件 | Google公式資料 | PASS | 無料枠入力が製品改善に利用される場合があることを確認し、READMEに記載済み。 |
| T46 | Windowsでの利用手順 | `start.bat`実行、README確認 | PASS | Python環境から起動確認。通常はCtrl+Cで終了。 |
| T47 | 悪意あるプロフィール命令への耐性 | SDKモックとGemini実API 1回、架空プロフィールのみ | PASS | モックでreply system instruction、対象相手以外の履歴排除、canary秘密文字列の非混入を確認。実APIはAPI2の3.5 Flash-Liteで1リクエスト。返答3案がプロフィール話題に触れ、注入文・秘密開示要求を反復せず、履歴は不変。API1 3.5は先に429相当だったため指定順にAPI2へ切替。実API出力本文はログに保存せず、smoke testは秘密・本文を出力しない。テスト: `tests/test_app.py`、`scripts/live_gemini_smoke.py`。 |
| T48 | ネットワーク・接続切断時のUI/API処理 | Firefoxでローカルサーバー停止、Gemini timeout/connection errorモック | PASS | Firefox停止テストで画面エラーと再試行を確認。SDK timeoutと接続例外はモックで1回の呼出、30秒timeout設定、再試行なし、キー/SDK詳細秘匿、履歴維持を確認。インターネット全体は切断していない。テスト: `tests/test_ui_firefox.py`、`tests/test_app.py`。 |
| T49 | 作業ブランチpush・Draft PR作成 | GitHub操作 | PASS | 作業ブランチpush成功。PR #4を`feat/ui-local-backend-v1`宛てのDraftで作成。 |
| T50 | CIが作業ブランチPush・PRで実行 | GitHub Actions、Firefox E2E、pytest、Node構文確認 | PASS | SHA `dcf5dbd6838117b1fd28dde99efcc8e2227538b8`のPush run [#38518482078](https://github.com/kenkyu0909/aichatapp/actions/runs/38518482078)とPR run [#38518486199](https://github.com/kenkyu0909/aichatapp/actions/runs/38518486199)が成功。Python 3.11、Ubuntu、Firefox 157.0で33 passed、Node構文成功。artifactにpytest XML、Firefox JSONログ、スクリーンショット。後続の報告専用commitは[PR checks](https://github.com/kenkyu0909/aichatapp/pull/4/checks)で最新HEADを確認。 |
| T51 | 保存先が起動時から使えない場合の遅延初期化 | Windows一時領域、アプリimportとTestClient | PASS | `APP_DATA_DIR`が通常ファイルを指す状態でもimportが失敗せず、profile要求は内部パスを漏らさない日本語500を返す。これはTestClientであり、別Uvicornプロセスの起動試験ではない。テスト: `tests/test_app.py`。 |

## 集計

- 合計: 51
- PASS: 50
- FAIL: 0
- FIXED: 0（修正後の再テストはPASSとして記録）
- BLOCKED: 1（T02: port 8765使用中のため、今回のstart.bat再実行を完了できず）
- NOT_TESTED: 0

## 2026-10-14 会話シミュレーション追加項目

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T52 | 実Geminiによる架空会話実験 | Windows、既存FastAPI `/api/generate`実通信。専用一時SQLiteに架空プロフィール・開始文を保存。API1/3.5を1回試行 | BLOCKED | HTTP 502。アプリ表示は「Gemini APIキーまたはモデルの利用権限を確認してください。」。認証・権限・接続の根本原因は未確定。候補0、アプリ送信0、相手発言1。固定文で補完せず中断。API2へは切替なし（429ではない）。JSON: `simulations/conversation_001.json`。|
| T53 | 会話ハーネス送信数上限・相手役分離・成功条件 | pytest。架空データ。モック/オフライン | PASS | 19→20送信可、21拒否。相手発言・未送信候補では送信数不変。候補順と429時のみの切替関数、条件付き承諾の除外、明示確認後のみSUCCESSを検証。`tests/test_conversation_simulation.py`。 |
| T54 | HTMLエスケープ・外部通信なし | オフライン生成テスト、FirefoxでDOMとリソース確認 | PASS | `<script>`/`onerror`文字列が実行可能なHTMLとして出ない。CSS内蔵、外部script/stylesheet/imageなし。テスト: `tests/test_conversation_simulation.py`。 |
| T55 | HTMLレポートのFirefox表示 | Windows、Firefox 157 headlessでローカルfile URLを開き、DOM・順序・件数・状態確認 | PASS | 架空プロフィールと1件の開始発言、BLOCKED状態、10項目の未評価を表示。外部リソースなし。スクリーンショット: `simulations/conversation_001_firefox.png`。生成候補がないため候補詳細の展開操作はNOT_TESTED（候補欄は存在しない）。 |

今回の全項目は55件: PASS 53 / FAIL 0 / BLOCKED 2 / NOT_TESTED 0（T01–T51の前回値を維持し、T52–T55を追加）。会話品質10項目は点数を付ける実生成結果がないため、実験レポートで未評価と明記。

詳細な実施条件、期待値、実結果、API/モック区分は上記各行および`simulations/analysis.md`を参照。ローカル検証コミットSHAはGitHub Push後に追記する。
