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
| T55 | HTMLレポートのFirefox表示 | Windows、Firefox 157 headlessでローカルfile URLを開き、DOM・順序・件数・状態確認 | PASS | 架空プロフィールと1件の開始発言、BLOCKED状態、10項目の未評価を表示。外部リソースなし。スクリーンショット: `simulations/conversation_001_firefox.png`。生成候補がないため候補詳細は存在しない。 |
| T56 | 実返信の品質評価・会う約束の成立 | 実API会話からの生成出力を人が評価 | BLOCKED | T52のHTTP 502でGemini候補0件。10の評価項目、誘い、日時・場所の合意を評価できない。成功・不成功を捏造せず、`simulations/analysis.md`に未評価と記録。 |

今回の全項目は56件: PASS 53 / FAIL 0 / BLOCKED 3 / NOT_TESTED 0（T01–T51の前回値を維持し、T52–T55を追加）。会話品質10項目は点数を付ける実生成結果がないため、実験レポートで未評価と明記。

詳細な実施条件、期待値、実結果、API/モック区分は上記各行および`simulations/analysis.md`を参照。

## 2026-10-14 最終修正・Windows起動ライフサイクル

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T72 | 初回メッセージの好意・喜び・候補差 | プロンプト確認、FastAPI/SDKモック | PASS | `prompts/first.txt`に軽い好意とマッチできた喜びを原則各候補へ含める指示を追加。候補間で表現を変える指示も追加。実Geminiの品質確認はT77以降に分ける。 |
| T73 | 会話方針内部値の日本語表示 | Firefox/Selenium、架空の固定API応答 | PASS | `Stage 3`と`consider_invite`を返し、Firefox上で「Stage 3 — 食事などへの誘いを検討する段階」「食事などへの誘いを検討」と表示。内部コードは画面に表示されない。API値は変更なし。 |
| T74 | `conversation_002`の隔離と初回モード | pytest、架空データ | PASS | `conversation_001`のパスを維持し、002用JSON/HTML/SQLiteを別パスに分離。初回モードは`first`、次ターン既定は`reply`。実験IDのパストラバーサルを拒否。 |
| T75 | Windows起動・二重起動・終了・再起動・ポート競合 | Windows、`%TEMP%`へソースを隔離コピー、Firefox、18768/18769番ポート | PASS | 起動後にFirefoxがHTTP 200で表示。2回目の起動は既存アプリを識別して再利用。Ctrl+CでUvicornを終了し18768番が接続を受けなくなった後、再起動を確認。18769番を占有した独立のテスト用HTTP serverは終了せず、競合案内を表示。8765番は既存プロセスがあるため停止・再起動を行っていない。 |
| T76 | Python 3.11+検出と起動スクリプトの構文 | Windows環境、`start.bat`/`start_server.py`確認 | PASS | Python 3.12.10の仮想環境を使用して隔離コピーを起動。仮想環境がない場合にPython Launcherの`py -3`または`python`で3.11以上を確認して作成する。 |

## 2026-10-14 実API品質試験（進行中）

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T77 | 実Gemini初回メッセージ・通常返信・情報確認・誘い・断り | 既存アプリの実API、架空プロフィールのみ | FAIL | 品質確認5回。全件HTTP 200・非デモ・API1/`gemini-3.5-flash-lite`、各1試行。未知の映画の好みを尋ねられた場面で「映画はときどき観ます」と未確認事実を生成したためFAIL。相互のカフェ会話はStage 3/consider_inviteだが即時の誘い候補はなく、誘い確認が未完。断りには謝罪し再誘いなし。回答を渡した後の再生成は実API未実施。詳細は`quality_checks_002.json`と分析。 |
| T78 | 会話シミュレーション002とHTML評価 | Windows、隔離SQLite、既存`/api/generate`実API、Firefox | PASS | 初回`first`と以後`reply`でGemini実生成20回成功。アプリ20通・相手20通、計40発言をJSON/HTMLへ保存。20通目への相手返事の後LIMIT_REACHED、21通目なし。FirefoxでHTML40件、折りたたみ詳細、CSS、日本語、外部読込なしを確認しPNG保存。具体的な約束は不成立。 |
| T79 | 実Gemini初回メッセージ3案の初回品質評価 | Windows/Python 3.12、既存FastAPI `/api/generate`実通信、架空プロフィール | FIXED | 初回3候補で句読点違反や必須要素の欠落が発生した履歴は維持。候補ごとの要件を`prompts/first.txt`で明確化し、別の実API再確認T80で改善を確認。 |

前回集計: 現時点の項目数は79件: PASS 71 / FAIL 1 / BLOCKED 3 / NOT_TESTED 4。T01–T71は前回の報告値を保持。T79は実API品質上の指示未達をそのまま記録し、実験条件を保つためプロンプト修正は会話002終了後に行う。

- 実験ツールSHA: `df7110205b8e522475cdcad7e08c8152ace360cb`。T56を含む最新レポート/マトリクスHEAD: `8a0097c1ad648692e6e93714b2e98e47b5e6cc43`。
- GitHub Actions Push: https://github.com/kenkyu0909/aichatapp/actions/runs/38526380171 （最新HEAD、成功、pytest 43 passed）
- GitHub Actions PR #4: https://github.com/kenkyu0909/aichatapp/actions/runs/38526386149 （最新HEAD、成功、pytest 43 passed）
- Node構文: 同runで`node --check app.js`成功。
- Firefox表示画像: `simulations/conversation_001_firefox.png`。

## 2026-10-14 利用制限時フォールバック追加検証

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T57 | 429時にAPI/モデルを指定優先順で切替 | Windows Python 3.12、FastAPI TestClient、Gemini SDKモック。架空会話のみ。APIファイル読込も一時ディレクトリで検証 | PASS | API1/3.5→API2/3.5→API1/3.1で生成成功する順序、および全4枠が制限された場合にAPI2/3.1まで各1回試すことを確認。別試験で403はAPI1/3.5の1回のみで停止。`chat1.md`/`chat2.md`から読み取った値が応答に含まれないこと、空の`MRA_API_DIR`時に既定の隣接APIフォルダを使うこと、通常の`GEMINI_API_KEY`を使用しないことも確認。実API呼び出しなし。`tests/test_app.py`の新規5ケース。 |

更新後のテストマトリクスは57項目: PASS 54 / FAIL 0 / BLOCKED 3 / NOT_TESTED 0。既存56項目の結果は維持し、T57のモック試験を追加。

T57実装commit `d5513f620b55758cc1a22957d431f61d1a4233ec` のGitHub Actions: [Push 38528562779](https://github.com/kenkyu0909/aichatapp/actions/runs/38528562779)、[PR 38528568834](https://github.com/kenkyu0909/aichatapp/actions/runs/38528568834)。同SHAで両run成功、pytest 48 passed、Node構文チェック成功。

## 2026-10-14 返信生成品質・初回メッセージ・制御のオフライン検証

実行環境: Windows、Python 3.12、Node.js、Firefox/Selenium。架空プロフィール・会話のみ。GeminiはSDKモック、UIは`/api/generate`固定モックを使用し、実API通信はしていない。Firefoxの実操作記録は`test-results/firefox-first-message-user-info.json`、画像は`test-results/firefox-first-message-user-info.png`（pytest artifact対象）。バッチ本体の実起動は未実施。

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T58 | 「、」「。」・「！」・絵文字・「笑」の文体ルール | 共通プロンプト静的確認、架空例12件 | PASS | 文体ルールを4モード共通プロンプトと`prompt_spec.md`へ追加。記号数より自然さを優先。静的確認と期待例であり、実モデルの文章品質評価ではない。 |
| T59 | 本人プロフィールの構造化・一時回答の分離 | FastAPI/SDKモック、SQLite確認 | PASS | JSONプロフィールを`facts`として渡し、未知の情報を補わない。本人情報と相手プロフィール補足回答は今回の生成文脈だけで使用し、SQLite/会話履歴は不変。`tests/test_app.py`。 |
| T60 | 不足情報の質問・回答・スキップ | API/SDKモック、Firefox UI | PASS | v2の質問応答は候補を返さない。回答後は一時情報で再生成。スキップ時は同じ質問を再表示せず、安全な候補または理由付き終端を表示。Firefoxでプロフィール未保存を確認。 |
| T61 | 会話履歴0件での初回メッセージ | API/SDKモック、Firefox UI | PASS | `first`モードを追加。履歴なしで候補を作り、生成だけでは履歴に記録しない。実際に送る操作後のみ手動記録。いいねモードとは別プロンプト。 |
| T62 | `first`/`reply`/`followup`/`like`の分離 | 全モードのプロンプト読込テスト | PASS | 各モード固有ファイルと共通指示を読み、初回挨拶、通常返信、追いメッセージ、マッチ前いいねの混同防止を静的・モック確認。 |
| T63 | 会話段階と誘い判断10シナリオ | 構造化出力のSDKモック、プロンプト静的確認 | PASS | 10種類の架空シナリオで判断ラベルの受け渡しを確認。これはモック値のAPI往復確認であり、Gemini自体の判断精度を示さない。固定往復数だけで誘わない指示を共通プロンプトに記載。 |
| T64 | API選択、429フォールバック、認証/モデル/通信エラー | SDKモック、隔離認証ディレクトリ | PASS | 優先順と上限4回を確認。各エラーでAPI別名・モデル・試行数だけを返し、キーや生SDK例外は返さない。シミュレーターはバックエンド結果を記録し、独自切替しない。 |
| T65 | 最大20通、20通目への相手返信、拒否保存 | シミュレーター単体テスト | PASS | 21通目を拒否し、20通目の後の相手発言を保存してから終了。明確な拒否は保存後に`SAFETY_STOP`。通常の遅延謝罪だけでは停止しない。 |
| T66 | 複数ターンに分かれた日時・場所の合意 | 架空会話のシミュレーター単体テスト | PASS | 保存済みの複数発言を組み合わせて具体性を確認し、明確な承諾と人による最終確認後だけ`SUCCESS`。曖昧な「いつか行きたい」は不成立。 |
| T67 | JSONから新しい隔離SQLiteへの復元 | 一時SQLite、形式不正と書込失敗の注入 | PASS | 書込前に全体を検証し、トランザクション失敗時はロールバック。既存データのあるDBへの復元は拒否。JSON/SQLite一致を確認。 |
| T68 | `start.bat`の起動順・アプリ識別・ポート保護 | 起動スクリプト静的テスト | PASS | `/api/status`の固有`app_id`で判定し、Python/依存確認、サーバー応答待ち後にFirefoxを開く。`taskkill`なし。バッチ実起動は別項目。 |
| T69 | Windows `start.bat`の実起動と8765番ポート競合 | Windows実機で隔離実行 | NOT_TESTED | 今回はユーザーの既存アプリ/データを使うリスクを避けるため実行していない。静的条件テストのみPASS。 |
| T70 | 初回メッセージ・質問回答/スキップ・コピー・手動記録UI | Firefox/Selenium、空の一時DB、固定APIモック | PASS | Firefox UIテスト3件成功。質問と候補の分離、相手切替時の質問消去、回答の非保存、スキップ終端、安全な候補、会話方針、コピーと送信記録の分離を確認。スクリーンショット/ログはActions artifactへ保存。 |
| T71 | Gemini実APIの自然さ・絵文字・「笑」・誘い判断 | 実API | NOT_TESTED | 今回のユーザー指示により実通信は行っていない。実際の文章品質は今回PASSと扱わない。 |

## 今回の集計

- マトリクス: **71項目** — PASS 66 / FAIL 0 / BLOCKED 3 / NOT_TESTED 2。
- ローカル統合pytest: **103 passed, 1 warning**（Starlette/httpxの非推奨通知）。`node --check app.js`と`git diff --check`も成功。Firefox UIテスト3件を含む。
- 最終レビュー後のモック確認: transport/不正JSON失敗を成功記録にしないこと、明確な拒否4表現の安全停止、本人情報確認中の再送なし・回答後1回だけ生成を確認。関連: T59/T60/T64/T65。
- T63はプロンプト指示と構造化応答のモック確認に限る。モデルの実判断はT71で未実施。
- 実装コミット`5954b06c418158a48c60aa57b55e17f47a52c54a`のActions: [Push run 38536298397](https://github.com/kenkyu0909/aichatapp/actions/runs/38536298397) / [PR run 38536305576](https://github.com/kenkyu0909/aichatapp/actions/runs/38536305576)。両方成功。Ubuntu/Python 3.11、Firefoxセットアップ、pytest、`node --check app.js`、artifact uploadを確認。
- 報告コミット`baa9b89b2a28e9ce35a05f9f9e25a7c15fbeee6f`の[Push 38536510987](https://github.com/kenkyu0909/aichatapp/actions/runs/38536510987) / [PR 38536517187](https://github.com/kenkyu0909/aichatapp/actions/runs/38536517187)も成功し、両方同じHEADを確認。
- 最新の完了済みPR HEAD `ef5f232a1ec6b10d07396f2a704dd419923549f2`: [Push 38536709582](https://github.com/kenkyu0909/aichatapp/actions/runs/38536709582) / [PR 38536717824](https://github.com/kenkyu0909/aichatapp/actions/runs/38536717824)が成功。最終の進捗記録はドキュメントのみで、branch workflow list [Actions](https://github.com/kenkyu0909/aichatapp/actions/workflows/test.yml?query=branch%3Acodex%2Ffull-system-verification)にそのPush/PR検査が追加される。


## 2026-10-14 最終検証（会話002）

| ID | テスト項目 | 方法・環境 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T80 | 初回プロンプト修正後の3案品質 | 実Gemini API、隔離SQLite、架空プロフィール、Windows/Python 3.12 | PASS | 1回の実通信で3案。API1/`gemini-3.5-flash-lite`、非デモ、HTTP 200、試行1。挨拶・軽い好意・マッチへの喜び・公開プロフィールの話題・質問を各案で確認し、句読点違反なし。`quality_checks_002.json`の末尾に保存。初回の失敗T79も履歴として残す。 |
| T81 | APIキー形式の漏えいスキャン | `git grep`、全Git refsとworking tree | PASS | 69個の到達可能refとworking treeをAPI key形式で走査。一致0件。検索出力はパス以外も出さず、秘密値は表示していない。Actionsログの履歴全件は権限・保持期間の範囲外で別途確認していない。 |

## 会話002レビュー修正の再検証（2026-10-14）

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T82 | 候補本文の読点・句点禁止と品質修復上限 | FastAPI TestClient + Gemini SDKモック | PASS | 違反候補を表示せず最大1回だけ修復を試す。API1で違反→429→API2で再度違反の場合も合計1回の修復後に安全に失敗し、会話履歴は不変。追加した回帰テストを含め全体テストはこの表の後続進捗で記録。 |
| T83 | 相手の文章量・最近の分量計測 | オフライン関数・FastAPIテスト | PASS | 最新の相手文、直近相手文平均、文数推定を区別して計測。`role=me`の過去文を本人事実の根拠にしない。生成品質の実評価は実APIで別途実施。 |
| T84 | 会話002で見つかった未確認の一人称事実 | Gemini SDKモック | PASS | 「自分は幅広く読む」「横浜のほうによく行く」「お気に入りのお店があります」を候補検査が検出。本人へ確認できない旧応答v1は候補を返さない。否定プロフィールと一時回答（「映画は好きではありません」「映画は好きじゃありません」「映画には興味がありません」「カフェは苦手」）を肯定の根拠にしないことも確認。日本語の全ての言い換えを網羅する検査ではない。 |
| T85 | 事実確認の粒度・一時回答 | FastAPI TestClient + SDKモック | PASS | 「読書好き」だけでは最近の本・ジャンルを確認済みとしない。候補のカレンダー案は確定予定扱いしない。「映画好き」への「はい」だけでは洋画の頻度や最近の視聴経験を許可しない。回答はプロフィールDBへ保存しない。 |
| T86 | 会話再開時のプロフィールスナップショット保護 | 一時ディレクトリのオフラインテスト | PASS | 既存`profiles_003.md`がある場合にresume処理が上書きしない。会話001・002の既存ファイルは今回変更していない。 |
| T87 | 本人質問への旧API形式の迂回防止 | FastAPI TestClient + Gemini SDKモック | PASS | response_version省略時に直接質問への未確認回答を生成する前にHTTP 409で停止。生成後の候補に既知の未確認事実があればresponse v1でも候補を返さない。 |

### 今回の実施状態

- T82〜T87はオフラインで実施済み。使用データは架空のプロフィール・会話のみ。Geminiへの通信はこの区間では行っていない。
- Windows/Python 3.12.10で全`pytest -q`を実行し **134 passed, 1 warning**。Firefox UIテストを含む。`node --check app.js`、`git diff --check`も成功。
- T77修正後Gemini実通信、文体/mirroringの実API評価A〜H、会話003、HTMLのFirefox表示確認、GitHub Actions最新HEAD実行は未完了で、結果を後続に追記する。
- 追加検査は既知の表現を保守的に止めるルールであり、日本語の全ての暗黙の本人談を検出できる保証はない。完全な事実抽出として扱わない。

### 最終集計

- 合計81項目: PASS 74 / FAIL 1 / FIXED 1 / BLOCKED 3 / NOT_TESTED 2。T77は本人の未確認情報を生成したためFAIL。T79の初回品質不具合はT80の再確認でFIXED。
- pytest: 104 passed, 1 warning（Starlette/httpxの非推奨警告）。Firefoxを使ったUIテストを含む。
- `node --check app.js`、`git diff --check`成功。Firefoxの会話HTML確認は40メッセージ、展開詳細、外部ネットワーク参照なしを確認。
- 会話002: 実API20/20成功。別の品質確認5/5成功。計25論理リクエスト。すべてAPI1/`gemini-3.5-flash-lite`、各バックエンド試行1、429・フォールバック0。API1の追加枠残量、課金状態、実請求額は確認していない。
- T77の未知の本人情報への質問結果はFAIL。該当プロンプトは明確化したが、実APIでの変更後再試験は今回の25回上限に達したためNOT_TESTEDとして残す。
- 会話終端はLIMIT_REACHED。アプリ20通、相手20通。誘いなし、具体的な日時・場所合意なし。失敗を隠すための相手役操作は行っていない。
- 実験データ: [`conversation_002.json`](simulations/conversation_002.json)、[`conversation_002.html`](simulations/conversation_002.html)、[`conversation_002_analysis.md`](simulations/conversation_002_analysis.md)、別検証[`quality_checks_002.json`](simulations/quality_checks_002.json)。


### GitHub Actions 最終実行（検証HEAD `cf24e2398ab428cb9e3beef2b0029f34aa73d4b4`）

- Push: [run 38544684207](https://github.com/kenkyu0909/aichatapp/actions/runs/38544684207) — success
- PR #4: [run 38544689940](https://github.com/kenkyu0909/aichatapp/actions/runs/38544689940) — success
- workflowはpytestとNode構文検査を完了。作業ブランチの後続変更がある場合は、PR checksで当該HEADの実行を確認してください。

- 報告書更新HEAD `a40c251c62c400401c9aef3e77beeaf7ceb76079`のPush Actions [38544920718](https://github.com/kenkyu0909/aichatapp/actions/runs/38544920718) とPR Actions [38544928533](https://github.com/kenkyu0909/aichatapp/actions/runs/38544928533)も成功。該当PR HEADと一致。

## 2026-10-14 実API品質評価003

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T88 | T77修正後の本人情報確認と回答後生成 | 架空データ、隔離SQLite、既存`/api/generate`、実Gemini | FAIL | 事前確認はPASSでAPI試行0。回答後はAPI1/`gemini-3.5-flash-lite`が追加情報を再質問し候補0件。質問の回答に元の質問全文を紐づけず、会話パターンも再評価が不十分だったため、回答後に1回限りの制約付き再生成を追加。初回結果は`quality_checks_003.json`に保持。 |
| T89 | 短文/複数文/落ち着いた文/冗談/深刻な話/反復/誘い/断りの実生成 | 架空会話、隔離SQLite、実Gemini | FAIL | API1/`gemini-3.5-flash-lite`で8ケース・10プロバイダー試行。短文、落ち着いた文、冗談、深刻な話、反復、誘い候補、断り応答は構造的に3案を返した。一方、ケースBは不要な本人情報質問で候補なし、ケースCは未確認の「最近自宅で過ごした」経験、ケースGは`invite_gently`判定に対し明示的な誘い案なし。追加修正後の限定再試験T93を予定。 |
| T90 | 会話003（初回メッセージから最大20通） | Windows 11 / Python 3.12 / 空の隔離SQLite / 既存FastAPI `/api/generate` / 実Gemini / Codex相手役 | BLOCKED | 架空プロフィールで15通ずつ、全30メッセージを保存。実APIは16論理要求・18 provider attempts、API1 / `gemini-3.5-flash-lite`。最後の相手の直接質問に対し、3候補すべてが本人未確認の購買習慣を断定したため、いずれも送信せず安全停止。会う提案・合意なし。`conversation_003.json`/`.html`/`_analysis.md`、Firefox画像を参照。 |
| T91 | 同一APIキー・異なるモデル間の15 RPM間隔制御 | オフライン関数テスト、Windows/Python 3.12 | PASS | API1の3.5から3.1へ移っても同じ認証枠として4.05秒間隔を適用。レビュー指摘を受けた修正。全pytest 136 passed, 1 warning。 |
| T92 | 映画を観た経験と映画が好きという事実の区別 | FastAPI TestClient、架空データ | PASS | `映画を観たことがある`だけでは`映画好きです`を確認済みとしない。レビュー指摘を受けた回帰テスト。 |
| T93 | T77回答後/短文ミラーリング/不要質問/未確認経験/誘い段階の修正後実API再確認 | 架空データ、隔離SQLite、既存`/api/generate`、実Gemini | FAIL | `quality_checks_003_followup.json`と`quality_checks_003_recheck.json`。T77は再チェックで2試行後3案を返した。A/Bは3案、句読点なし。Cは3案の一つが未確認の最近の視聴状況を述べたためFAIL。Gは方針と候補の不一致を修復後も解消できず、アプリが候補を拒否したためFAIL（外部ブロックではなく応答検証失敗）。元の失敗記録は保持。 |
| T94 | `invite_gently`時の候補と方針の一致 | FastAPI TestClient + Geminiモック | PASS | 方針が誘いを示すのに全候補が相槌だけの場合は1回だけ再生成。再生成に誘い候補が含まれたことを確認。 |
| T95 | 未確認の最近の休日経験・喫茶店頻度の抑止 | FastAPI TestClient + Geminiモック | PASS | プロフィールの趣味だけで「最近家で過ごした」「よく喫茶店を巡る」という新しい経験・頻度を確定せず、1回限りの修正を行う。 |
| T96 | 休日事実・否定的な趣味・誘い方針の境界検査 | FastAPI TestClient/関数テスト + Geminiモック | PASS | 休日の直接質問を安全にユーザー確認へ送る。休日の「家で映画」と「映画館」の区別、映画の否定プロフィール、回答済み質問の反復、`respect_no`と矛盾する候補、一般的な「ご飯行きませんか？」を検査。 |
| T97 | 本人情報の質問再評価と候補事実修復の上限分離 | FastAPI TestClient + Geminiモック | PASS | 回答後に情報質問が一度出ても、候補品質修復を別の1回に制限し、最大3要求で確認済み範囲の候補を返すことを検証。 |
| T98 | 未確認の最近の映画視聴状況の検出 | FastAPI関数テスト | PASS | プロフィールに直近の視聴状況がない場合「最近は全然観れてない」という一人称の未確認経験を候補に含めない。 |
| T99 | T77修正後の実API回答 | 架空回答、隔離SQLite、既存`/api/generate`、実Gemini | PASS | `quality_checks_003_recheck.json`。API1/`gemini-3.5-flash-lite`、2試行後3候補。答えた映画・洋画の範囲で応答し、句読点禁止を守った。初回失敗T88は履歴として残す。 |

### 2026-10-14 最新オフライン確認

- 全pytest: **151 passed, 1 warning**（Starlette/httpxの非推奨通知）。`node --check app.js`、Python `py_compile`、`git diff --check`も成功。Firefox UI自動テストを含む。
- 最新の実API品質確認は`quality_checks_003.json`に保存。9論理要求、確定10プロバイダー試行、API1/`gemini-3.5-flash-lite`、429なし。出力品質にFAILが残ったため、後続の限定追試をT93で記録する。
- T93は実施してFAIL。T77回答後の再確認はT99としてPASS。会話003の本体T90は未実施。過去のT77/T88/T89の失敗履歴は維持する。

現時点の項目数は100: PASS 89 / FAIL 4 / FIXED 1 / BLOCKED 4 / NOT_TESTED 2。

#### 最新コードのActions

- HEAD `aee118313bd8a05bbae30cb03e2cb37330e36ab0`でPush run [38554061358](https://github.com/kenkyu0909/aichatapp/actions/runs/38554061358)とPR run [38554066709](https://github.com/kenkyu0909/aichatapp/actions/runs/38554066709)がsuccess。pytest、Firefox UIテスト、Node構文チェックを含む。


| T100 | Geminiの本人未確認候補を送信前に拒否し記録 | 会話003の実API結果を安全に停止、pytest、Firefox 157のローカルHTML表示 | PASS | 直近質問への3候補が未確認の購買習慣を一人称で断定したため、候補・拒否理由をJSON/HTMLへ保存。送信数15のまま、SQLite会話・既存送信数に変更なし。追加テスト2件で拒否とXSSエスケープを確認。Firefoxで30メッセージ、左右の話者、15/15、拒否候補の展開、スクリーンショットを確認。 |

### 2026-10-14 会話003最終確認

- 会話003は`BLOCKED`。アプリ15通、相手15通、30メッセージ。Geminiは16論理要求、18 provider attemptsで応答し、429・フォールバックはなし。API1 / `gemini-3.5-flash-lite`のみ。累計品質確認を含め32論理要求・40 provider attemptsとなり、事前の約30回目安を2論理要求超過した。理由と内訳は報告書に記録。以後、実API呼び出しは行わない。
- 終了理由は外部障害ではなく送信前の安全停止。本人未確認の購買行動を3候補すべてが断定した。候補を拒否し、送信数・SQLiteの会話は変更していない。会う提案なし、約束成立なし。
- Firefox 157.0.1で単体HTMLを開き、30発言、プロフィール、候補詳細16個、拒否した3候補、CSS、日本語を確認。画像は`simulations/conversation_003_firefox.png`。Chromeは使用していない。
- 全pytest **153 passed, 1 warning**。`node --check app.js`、Python `py_compile`、`git diff --check`成功。
- HEAD `c740141cf2b7b9f7b9143cf6750dc26add8c86d5`のPush Actions [38555557284](https://github.com/kenkyu0909/aichatapp/actions/runs/38555557284)とPR Actions [38555564007](https://github.com/kenkyu0909/aichatapp/actions/runs/38555564007)は成功。ただし今回は拒否記録コード・最終ログ・画像を追加するため、次のHEADでもActionsを確認する。
