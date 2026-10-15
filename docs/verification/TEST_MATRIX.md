# テストマトリクス

架空のプロフィール・人物・会話のみで実施。結果は実際の確認に基づき記録。

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T01 | アプリ起動（Python） | Python 3.12.10、Uvicorn | PASS | `127.0.0.1:8767`で起動。再起動も実施。 |
| T02 | Windows `start.bat`起動（既定ポート8765） | 実機で実行 | BLOCKED | 2026-10-14に加え、2026-10-15も127.0.0.1:8765をPID 39504のPython 3.12プロセスが占有。HTTP 200だが`/api/status`の`app_id`が空で、今回のアプリか確認できないため停止せず、既定ポートの起動は未実施。別ポートでの実機起動はT286を参照。 |
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
- HEAD `c740141cf2b7b9f7b9143cf6750dc26add8c86d5`のPush Actions [38555557284](https://github.com/kenkyu0909/aichatapp/actions/runs/38555557284)とPR Actions [38555564007](https://github.com/kenkyu0909/aichatapp/actions/runs/38555564007)は成功。両方成功: Push [38556958055](https://github.com/kenkyu0909/aichatapp/actions/runs/38556958055)、PR [38556965533](https://github.com/kenkyu0909/aichatapp/actions/runs/38556965533)。両runともHEAD `5ddcd020747eb8eb8971e991515d1004c0625114`を対象。pytest・Firefoxを含むUIテスト・Node構文検査・結果Artifactの保存が成功。

### 2026-10-14 実API品質確認004の再評価とオフライン修正

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T101 | 購買行動の具体性と回答矛盾 | FastAPI関数テスト、確認済みプロフィールと架空回答 | PASS | `tests/test_app.py`。一般的な「買い物が好き」は「すぐ買う」行動の根拠にしない。確認回答が「調べてから」なら「すぐ買う」候補を拒否。 |
| T102 | カレーの好み・頻度・最近の経験の分離 | 質問分類・本人確認と未確認の頻度/最近経験候補のFastAPI単体テスト | PASS | `tests/test_app.py`。具体的なカレーの好みだけで摂食頻度や最近の経験を確認済みにしない。 |
| T103 | カフェ趣味から店の雰囲気を推測しない | FastAPI候補事実チェッカー | PASS | `tests/test_app.py`。カフェ巡りだけのプロフィールで「落ち着いた雰囲気が好き」という活用形を含む本人談を不支持として検出。 |
| T104 | 前向きな`consider_invite`理由と候補の整合性 | Gemini SDKモック、FastAPI `/api/generate` | PASS | 会話履歴から相互質問・共有話題・関心を推定し、慎重さや過去の誘いを除外して判断。機会が揃ったconsider_inviteで候補がない場合は1回だけ修復。 |
| T105 | 実API品質評価器の回答事実・4モデル優先順 | オフラインpytest | PASS | `tests/test_quality_checks_004.py`。自然な言い換えと引用符除去を受け入れ、モデル名とAPI別名の完全な優先順を検査。 |
| T106 | 実Gemini生成品質004の人手再評価 | 8論理要求の保存JSONを読み、候補と根拠を照合 | FAIL | `quality_checks_004.json`と[`quality_checks_004_analysis.md`](simulations/quality_checks_004_analysis.md)。8論理要求/9 provider attempts。購買回答との矛盾、未確認のカフェ嗜好、前向きな誘い方針と候補の不一致を検出。最近の映画回答は逐語一致テストの誤判定。追加実API要求なし。 |
| T107 | 会話004の開始条件 | T106の失敗と8要求上限を確認 | NOT_TESTED | 会話シミュレーションは開始していない。今回の実出力に事実性と方針整合性のFAILがあり、上限も使用済みのため安全に保留。 |

| T108 | 買い物の否定表現と反対行動の検出 | FastAPI候補検証のpytest | PASS | 「衝動買いを避ける」「控える」「すぐ買うのは避ける」「即決購入を控える」が確認済みの否定事実として扱われ、肯定候補を拒否する。`tests/test_app.py`。 |
| T109 | カレー根拠の項目結び付け・カフェ嗜好の極性 | FastAPI候補検証のpytest | PASS | 本に関する「よく/最近」をカレー頻度・経験の根拠にしない。「落ち着いた雰囲気よりにぎやかな店が好き」から落ち着いた店好きとは生成しない。`tests/test_app.py`。 |
| T110 | 誘い機会の話題一貫性と拒否判定 | 会話履歴関数テスト・Gemini SDKモックpytest | PASS | 古いカフェ話題と新しい無関係質問を組み合わせず、最新2件の関連する話題のみで判断。明確な外出への消極表現と「カフェは好きですか？」だけの質問は誘い意欲と扱わない。過去の誘い・拒否は維持し、遅い返信への謝罪は拒否と誤判定しない。`tests/test_app.py`。 |

### 最新指示による句読点・質問粒度・API品質ゲート

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T111 | 句読点なしで連結された日本語文の検出と引用符の誤検出防止 | FastAPI関数のpytest | PASS | レビューで提示された「帰りは…」「途中で犬…」を含む既知の連結例を拒否。接続表現「学生ですが…」と引用内の感嘆符を含む単文を許容。静的判定のため未列挙パターンを網羅保証しない。`tests/test_app.py`。 |
| T112 | 最近のカフェ場所・映画館頻度・カフェ頻度に対する本人確認 | FastAPI事前判定pytest | PASS | 質問粒度を「最近の店/場所」「映画館の頻度」「カフェの頻度」に保つ。プロフィールの一般的な趣味だけでは回答済みとしない。`tests/test_app.py`。 |
| T113 | 既知のカフェ頻度への言い換え再質問 | FastAPI候補検査pytest | PASS | 「カフェってよく行きますか」「喫茶店にはよく行くんですか」「カフェにはどのくらいの頻度で」を、相手が頻度を既に話している場合に拒否。店名などの深掘りは許容。`tests/test_app.py`。 |
| T114 | 限定Gemini品質テストの件数と検査範囲 | APIなしのpytest | PASS | `scripts/run_quality_checks_005.py`は8論理要求以内。読書ジャンル、最近の映画、購買回答、断り後の再勧誘・既知情報再質問、プレースホルダー、誘い整合、改行、共感反復を扱う。実API結果はT118。 |
| T115 | 実API検証の認証情報ソース隔離 | APIなしのpytest | PASS | スクリプトは明示された`MRA_API_DIR`だけを選び、`app.py`のdotenv読込に既存環境値が差し込まれないようAPIキー環境変数を空にする。値は表示・記録しない。`tests/test_quality_checks_005.py`。 |
| T116 | 許可済みAPI/モデル優先順の構成確認 | ローカル設定の存在確認。秘密値非表示 | PASS | API別名とモデルだけを出力し、API1/3.5 → API2/3.5 → API1/3.1 → API2/3.1の4経路を確認。認証有効性・現在のクォータはこの確認だけでは判定しない。 |
| T117 | 対象モデルの公式一覧確認 | Google Gemini公式モデル/料金/レート制限資料 | PASS | `gemini-3.5-flash-lite`と`gemini-3.1-flash-lite`は安定版として一覧掲載。Free tierは一部モデル・利用枠限定で、プロジェクト別の現在枠や課金状態はAI Studioで確認が必要。参照: [Models](https://ai.google.dev/gemini-api/docs/models)、[Pricing](https://ai.google.dev/gemini-api/docs/pricing)、[Rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)。 |
| T118 | 新しい限定Gemini品質チェック005 | 既存FastAPI `/api/generate`、隔離SQLite、架空データ、最大8論理要求 | FAIL | 実施済み。8論理要求/13 provider attempts、API1/`gemini-3.5-flash-lite`。未確認の感想・買い方、候補と誘い方針の不一致、未完成プレースホルダーを確認。断りケースは構造化応答を得られず。詳細は`quality_checks_005_analysis.md`。会話004は開始せず。 |
| T119 | conversation_004の開始ゲート | T118の全候補品質判定後のみ実施 | NOT_TESTED | T118が全候補PASSし、明示された許可上限内で実施できる場合だけ開始。失敗時は架空の会話記録を作らない。 |
| T120 | 最新変更を含む全pytest・Firefox UI回帰 | Windows `.venv`、全pytestとPush Actions | PASS | 2026-10-14、ローカル**257 passed, 1 warning, 76.93秒**、Actions**257 passed, 1 warning, 62.58秒**。Firefox UI自動テストを含む。警告はStarletteからの`httpx` TestClient利用非推奨通知。Chromeは使用していない。Actionsは`c69e92f2ce6731083785322463e028f53fbdcd8d`。 |
| T121 | 断り後の再勧誘と既知情報の再質問を同時に拒否する品質ゲート | APIなしのrunner関数テスト | PASS | `respect_decline_and_no_reask`ケースで、カフェ頻度の共有→本人の誘い→相手の慎重な拒否を設定。再勧誘候補（「今度会いませんか」「カフェでもご一緒しませんか」等）と既知頻度の再質問を拒否し、「カフェの話をしませんか」のような会話提案は会う誘いと誤判定しない。`tests/test_quality_checks_005.py`。 |
| T122 | GitHub Actionsが最新Pushコミットで成功 | `gh run view`と実ログ確認 | PASS | [Actions 38579919967](https://github.com/kenkyu0909/aichatapp/actions/runs/38579919967)、SHA `c69e92f2ce6731083785322463e028f53fbdcd8d`、`257 passed, 1 warning`、Firefox準備・JavaScript構文チェック・Artifact uploadも成功。 |

この節の当時点は122項目（PASS 107 / FAIL 5 / FIXED 1 / BLOCKED 4 / NOT_TESTED 5）。T118の実施結果は後段でFAILへ更新し、変更前の記録は履歴として保持する。

### 2026-10-15 実API品質006の評価と事実検査回帰修正

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T123 | 買い物の本人事実・質問・相手情報の区別 | FastAPI候補検査pytest、架空プロフィール/会話 | PASS | 断定後の質問を見逃さないこと、くだけた質問を許容すること、相手の肯定済み習慣を受け止めること、否定・「わけではない」と矛盾する受け止めを拒否することを確認。関連テスト27件がPASS。`tests/test_app.py`。 |
| T124 | 最新コードの全pytestとFirefox UI回帰 | Windows `.venv`、pytest全件 | PASS | 最終コードで**307 passed, 1 warning, 77.98秒**。Firefox UIテストを含む。警告はStarlette/httpx TestClientの非推奨通知。Chromeは使用していない。 |
| T125 | 実Gemini品質006の候補品質 | 隔離SQLite、既存アプリAPI、指定APIディレクトリ、架空データ | FAIL | 7論理要求/11 provider attempts、API1/`gemini-3.5-flash-lite`のみ。映画の感想/因果関係、買い方の未確認詳細、断りに対する不自然な表現、`consider_invite`と誘い候補の不一致を確認。最終改行ケースはHTTP 502 `invalid_response`。429なし、フォールバックなし。`quality_checks_006.json` / `_analysis.md`。追加API要求は行わない。 |
| T126 | conversation_004の品質ゲート | T118/T125の保存済み出力と判定 | NOT_TESTED | T118とT125でFAILがあるため未開始。会話や生成候補を捏造していない。再開には修正後の実API品質ゲートを別許可・利用枠確認のもとで通す必要がある。 |
| T127 | 最新コードのPush/PR GitHub Actions | GitHub Actions run詳細とpytestログ | PASS | コードSHA `7ce0a6c4853cb241c621fe0988ac951960f534c8`を対象にPush [38588182566](https://github.com/kenkyu0909/aichatapp/actions/runs/38588182566)とPR [38588189420](https://github.com/kenkyu0909/aichatapp/actions/runs/38588189420)が成功。両方307 passed, 1 warning、Firefox準備・Node構文検査・Artifact upload成功。 |

最新集計: 127項目、PASS 110 / FAIL 7 / FIXED 1 / BLOCKED 4 / NOT_TESTED 5。旧FAILは履歴として保持し、T118の実施結果、T125の実API評価、T127のCI結果を反映した。

## 2026-10-15 夜間品質改善（オフライン）

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T128 | 未確認の本人事実35表現 | pytest候補検査 | PASS | 趣味、好き嫌い、頻度、最近の経験、買い物、否定、比較、予定、場所を含む35種類で根拠なしの主張を検出。`tests/test_app.py`。 |
| T129 | 相手への疑問文と本人断定の区別 | pytest | PASS | 8種類の相手向け質問を本人の事実として誤検出しない。`tests/test_app.py`。 |
| T130 | 生成経路での未確認事実ブロック | FastAPI + Gemini SDKモック | PASS | 架空の相手8人それぞれにunsafeな候補を2回返しても、APIは`needs_user_info`を返し送信可能な候補を返さない。実Geminiではない。 |
| T131 | 本人への質問30ケースの粒度 | FastAPIローカルpytest、隔離テストDB | PASS | 本、映画、買い物、旅行、カフェ、休日、仕事、趣味、場所、予定など30質問で本人確認を行い、指定した質問粒度と一致。質問粒度の1件を修正後、対象テスト再実行に成功。 |
| T132 | 相手が明言した休日/カフェ情報の聞き直し | pytest候補検査 | PASS | 15種類の言い換え質問を再質問として拒否。 |
| T133 | 既知情報からの自然な深掘り | pytest候補検査 | PASS | 店の雰囲気、最近の店、おすすめ等5件を既知頻度の再質問とは扱わない。 |
| T134 | 全pytest・Firefox UIを含む回帰 | Windows Python 3.12 `.venv` | PASS | 修正後の最新コードで**372 passed, 1 warning, 78.87秒**。警告はStarlette/httpx TestClient非推奨通知。 |
| T135 | Firefox UI単独実行 | Selenium/Firefox、`tests/test_ui_firefox.py` | PASS | **5 passed, 70.32秒**。Chromeは使用していない。 |
| T136 | Python構文 | `py_compile app.py tests/test_app.py` | PASS | 終了コード0。 |
| T137 | JavaScript構文 | Node.js 25.9.0 `node --check app.js` | PASS | 終了コード0。 |
| T138 | 差分空白検査 | `git diff --check` | PASS | 終了コード0。 |
| T139 | APIキー形式の作業ツリースキャン | `AIza...`パターンのファイル名のみ出力する検索 | PASS | 一致ファイルなし。秘密値を出力していない。 |
| T140 | Gemini実API利用可否と品質確認 | 課金・残枠の確認状態を確認 | BLOCKED | 課金状態と現在のプロジェクト利用枠を確認できない。API通信0論理要求/0 provider attempts。課金を発生させる可能性を避け、会話004は開始しない。 |
| T141 | ミラーリング/反復/意味的多様性の新規実出力採点 | 実Geminiの連続応答が必要 | NOT_TESTED | 今回の実API応答なし。過去の会話003/品質006は失敗の参考記録として保持し、現在のコードの成功証拠に転用しない。 |
| T142 | 最新コード/検証commitのPush・PR Actions | GitHub Actions実行記録とログ | PASS | SHA `f12dc9751496e4bf981fb152231fcf6c052a3f71`。Push [38593027083](https://github.com/kenkyu0909/aichatapp/actions/runs/38593027083)とPR [38593036072](https://github.com/kenkyu0909/aichatapp/actions/runs/38593036072)が成功。両方372 passed, 1 warning、Firefox準備/Node構文検査/Artifact upload成功。 |
| T143 | 最終報告commitのPush・PR Actions | GitHub Actions実行記録とpytestログ | PASS | SHA `ad427ef48562c02a205c376f16b78f74ffb53e2e`。Push [38593518484](https://github.com/kenkyu0909/aichatapp/actions/runs/38593518484)とPR [38593529499](https://github.com/kenkyu0909/aichatapp/actions/runs/38593529499)が成功。同SHAで各372 passed, 1 warning、Firefox準備/Node構文検査/Artifact upload成功。 |
| T144 | 進捗・集計追記commitの最新Push・PR Actions | GitHub Actions実行記録とpytestログ | PASS | SHA `321a43e8be6bba2722e860af63d43efb2d7355eb`。Push [38593909339](https://github.com/kenkyu0909/aichatapp/actions/runs/38593909339)とPR [38593921411](https://github.com/kenkyu0909/aichatapp/actions/runs/38593921411)が成功。同SHAで各372 passed, 1 warning、Firefox準備/Node構文検査/Artifact upload成功。 |

本節を含む集計: 144項目、PASS 125 / FAIL 7 / FIXED 1 / BLOCKED 5 / NOT_TESTED 6。旧FAILは履歴として維持。T140/T141は実装成功や文章品質PASSを意味しない。

## 2026-10-15 実Gemini品質確認007と質問ゲート修正

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T145 | 実API疎通と返信3案 | 架空会話、隔離SQLite、既存FastAPI `/api/generate` | PASS | API1 / `gemini-3.5-flash-lite`。HTTP 200、3候補、1 provider attempt。実文は`quality_checks_007.json`。 |
| T146 | 短文相手への返信量 | 実Gemini、1文の架空入力 | PASS | 返信は各2文まで。プロフィール確認済みのカフェ趣味を使った候補を含む。 |
| T147 | 冗談への適応と相手事実の扱い | 実Gemini、架空の「休日ほぼ寝て終わりました笑」 | FAIL | 冗談への自然な反応が弱く、相手プロフィールにない仕事を仮定する候補が出た。 |
| T148 | 直接質問の本人確認粒度 | `/api/generate`ローカル事前確認 | PASS | 「映画好きですか？」に「映画はお好きですか？」と質問し、相手向け候補なし。API試行0。実Gemini評価ではない。 |
| T149 | 確認済み買い方の回答後生成 | 実Gemini、架空の本人回答 | FAIL | 買い方へ答える代わりにカフェ頻度・店の好みを本人へ質問。候補は出さなかった。詳細は品質分析。 |
| T150 | 相手が答えたカフェ頻度の再質問防止 | 実Gemini、架空履歴 | PASS | 既知の「友達とカフェへ行く頻度」を聞き直す候補なし。候補間の共感は一部類似。 |
| T151 | カフェ会話からの誘い候補 | 実Gemini、相互質問を含む架空履歴 | FAIL | 3 provider attempts後も候補を返さず停止。自然な誘いが生成できたと確認できない。 |
| T152 | 会うことに慎重な相手への応答 | 実Gemini、架空の不安表明 | FAIL | 再勧誘はなかったが、未確認の仕事を仮定し、断り直後にカフェ嗜好を聞く候補が含まれた。 |
| T153 | 実生成候補の句読点・改行・プレースホルダー | `quality_checks_007.json`の候補を実文で検査 | PASS | 取得できた候補の「、」「。」、空行、文間の改行漏れ、プレースホルダーは0件。候補なし応答は対象外。 |
| T154 | 返信候補の意味的多様性 | 実候補を手動分類 | FAIL | 応答形式上は異なるが、受け止め＋質問の型に寄るケースがあり、15ケースで2方針以上という基準は未達。 |
| T155 | 無関係な未確認事実を本人質問へ変換しない | FastAPI + Gemini SDKモック | PASS | 直接質問と異なる話題の未確認主張が残った場合、質問へ置換せず候補なしで終了。`test_unrelated_unsupported_claim_does_not_become_user_question`。 |
| T156 | 不要なモデル本人質問の回復 | FastAPI + Gemini SDKモック | PASS | 不要質問を受けた後、最大1回の安全な再生成で候補を返す。追加質問が続く場合の無制限ループなし。 |
| T157 | 誘い判断と候補の一致 | FastAPI + Gemini SDKモック | PASS | `invite_gently`時に誘い候補を含み、不必要な本人質問から1回の再生成で回復する。実モデルの誘い判断を証明するものではない。 |
| T158 | 全pytestとFirefoxを含む回帰 | Windows `.venv`、pytest全件 | PASS | **375 passed, 1 warning, 79.01秒**。警告はStarlette/httpx TestClient非推奨。 |
| T159 | Firefox UI単独回帰 | Selenium Firefox、`tests/test_ui_firefox.py` | PASS | **5 passed, 71.86秒**。Chromeは使用していない。 |
| T160 | Python/JavaScript構文と差分検査 | `py_compile`、`node --check app.js`、`git diff --check` | PASS | すべて終了コード0。追加の秘密形式スキャンも不一致。 |
| T161 | conversation_004 | 品質ゲート後に実施 | NOT_TESTED | T147/T149/T151/T152/T154がFAILのため開始しなかった。会話を捏造せず、既存001〜003も変更していない。 |

最新集計: 161項目、PASS 136 / FAIL 12 / FIXED 1 / BLOCKED 5 / NOT_TESTED 7。品質007の実API結果は失敗を含み、会話004は未実施。旧FAILは履歴として維持。

Actions対象HEAD `2e6a34410548915c79409a8388821699cb6de95c`:

- [Push run 38569943665](https://github.com/kenkyu0909/aichatapp/actions/runs/38569943665) — success, 195 passed, 1 warning。
- [PR run 38569953895](https://github.com/kenkyu0909/aichatapp/actions/runs/38569953895) — success, 195 passed, 1 warning。
- どちらも同じ最新PR HEADを対象とし、JavaScript構文検査とテスト結果Artifact保存も成功。

| T162 | 最新実装SHAのPush CI | GitHub Actions / pytest・JavaScript構文・Artifact | PASS | SHA `44fbe733e00652774d942109fe2a2411fb67029d`。375 passed, 1 warning。[run 38658096934](https://github.com/kenkyu0909/aichatapp/actions/runs/38658096934)。 |
| T163 | PR #4の最新実装SHA CI | GitHub Actions / Pull Request | PASS | 同SHA。375 passed, 1 warning。[run 38658104233](https://github.com/kenkyu0909/aichatapp/actions/runs/38658104233)。PRはOPEN/Draft、未マージ。 |

最新集計: 163項目、PASS 138 / FAIL 12 / FIXED 1 / BLOCKED 5 / NOT_TESTED 7。実API品質007のFAILを保持し、修正後の実API品質は未確認。

## 2026-10-15 品質確認008と安全候補優先の再検証

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T164 | 候補ごとの安全判定と不足数通知 | FastAPI + Gemini SDKモック | PASS | 安全な候補を残し、危険候補は除外。requested / available数と不足通知を返す。 |
| T165 | 安全候補と不足通知のUI表示 | Firefox + Selenium | PASS | 1件の安全候補と指定3件に対する不足通知を同時に確認。Chrome未使用。 |
| T166 | 拒否後の再勧誘抑止 | FastAPI + Gemini SDKモック | PASS | ためらい・無関係な外出・一人旅の発言では拒否状態を維持し、明確な再考・受諾でのみ解除。 |
| T167 | 本人回答による作品名の根拠確認 | FastAPI + Gemini SDKモック | PASS | 確認済み回答中の作品名は許容し、別の未確認作品名は拒否。 |
| T168 | Gemini初回疎通 | 実Gemini、既存API | FIXED | 初回HTTP 502を保持。同一入力の限定再試行でAPI1 / gemini-3.5-flash-liteがHTTP 200、3候補。 |
| T169 | 短文への返信 | 実Gemini | PASS | 短い候補1件を取得。指定3件との差2件を通知し、候補を水増ししない。 |
| T170 | 冗談への返信 | 実Gemini | PASS | 短文候補2件。冗談に応答し、未確認の職業を仮定しない。不足通知あり。 |
| T171 | 映画の好みが未確認の直接質問 | ローカル事前確認 | PASS | 本人への確認質問を返し、相手向け候補0件。Geminiプロバイダー呼び出し0回。 |
| T172 | 映画の本人回答を使った候補検査 | 実Gemini + 候補安全フィルター | FIXED | 初回の不適切候補は履歴に保持。修正後は安全候補1件と2件不足の通知を確認。 |
| T173 | 確認済み買い物習慣との整合 | 実Gemini | PASS | 架空の本人回答「少し調べてから買う」と矛盾する候補なし。 |
| T174 | 相手が述べた情報の聞き直し | 実Gemini | PASS | 友達とカフェへ行く頻度を聞き直す候補なし。 |
| T175 | 誘い表現の候補判定 | 実Gemini + 修正後フィルター | FIXED | 「今度一緒に行ってみませんか」の検出漏れを修正。再試行で誘い候補と安全な別案を確認。 |
| T176 | 会うことへの不安の尊重 | 実Gemini | PASS | 再勧誘候補なし。 |
| T177 | API上限・選択順・秘密情報非出力 | 実行ログとファイル検査 | PASS | 11論理要求 / 14 provider attempts、上限12 / 24以内。API1 / gemini-3.5-flash-liteのみ。秘密値は出力・保存していない。 |
| T178 | 全pytest（Firefox UIを含む） | Windows / pytest | PASS | 406 passed in 93.32s。 |
| T179 | Python/JavaScript構文・差分・秘密形式検査 | py_compile、node --check、git diff --check、rg | PASS | 構文・差分検査終了コード0。秘密形式の一致なし。 |
| T180 | 最新HEADのGitHub Actions | GitHub Actions Push/PR | PASS | SHA f800fbeabb146258c6a20c583ea62c74f0cf4f46。Push [run 38664505348](https://github.com/kenkyu0909/aichatapp/actions/runs/38664505348)・PR [run 38664508934](https://github.com/kenkyu0909/aichatapp/actions/runs/38664508934)とも成功。各406 passed, 1 warning。Firefox準備、JavaScript構文検査、Artifact uploadも成功。 |

## 2026-10-15 自律品質確認009（進行中）

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T181 | 趣味から具体的な好み・経験・頻度を推測しない | pytest候補検査 | FIXED | 開始時のquality008再監査で、カフェ趣味から雰囲気嗜好を推測した候補が通ることを再現。最近の旅行・映画・映画館頻度・読書範囲も追加検査。節単位の根拠確認と質問誤検出防止を含む関連20件はPASS。`tests/test_app.py`。意味検査は限定的なルールであり、日本語全体を保証しない。 |
| T182 | 会うことへの不安直後に店・日程の質問へ移らない | pytest候補検査 | FIXED | quality008の「まだ会うのはちょっと不安」直後の店質問を再現。外出/日程関連質問を除外し、中立な本の質問や短い受容文は残す。focused testを更新し、現行コードで再確認。`tests/test_app.py`。 |
| T183 | 肯定情報と別属性への否定情報を分離する | pytest候補検査 | FIXED | 映画・旅行・カフェの肯定情報と別属性の否定情報を同じ文に記録した架空プロフィールで検証。関連13件はPASS。 |
| T184 | FastAPI / 全pytest / Firefox UI回帰 | Windows Python 3.12 / pytest | NOT_TESTED | 現行修正適用後の全件は未実行。 |
| T185 | Gemini実API品質確認009 | 既存アプリ経由・架空データ・隔離SQLite | FAIL | 10論理要求 / 12 provider attemptsで疎通と限定ケースの自動条件は通過。ただし手動レビューで誤字「どんな雰囲い」、候補の意味的重複、確認済み回答を使わない代替案、未確認の「私もお出かけが好き」を修正前に表示した実見逃しを確認。詳細は`simulations/quality_checks_009_analysis.md`。 |
| T186 | conversation_004 | 品質ゲート後の実Gemini会話 | NOT_TESTED | 品質009は手動評価FAILのため開始条件を満たさず未実施。 |
| T187 | 異なるプロフィール項目の根拠を混ぜない | pytest候補検査 | FIXED | 旅行趣味＋仕事の最近情報、映画館趣味＋ジム頻度、静かなカフェ好み＋店舗探索を別々に記録した架空プロフィールで不正な根拠合成を拒否。節単位の照合を追加。 |
| T188 | 新しい経験/頻度検査で相手への質問を誤拒否しない | pytest候補検査 | FIXED | 「最近旅行に行きましたか」「最近映画を観ましたか」「映画館には月に何度行きますか」に加え、「最近映画観た？」「映画館によく行くの？」「最近どんな映画観たの？」「映画館よく行くかな？」を本人の断定として扱わない。 |
| T189 | 未確認の外出嗜好を実Gemini候補から除外 | 実Gemini API + 安全候補フィルター、架空データ | FIXED | 修正前の実生成「私もお出かけが好きなので新しいお店は気になります！」を実際に記録。修正後の同系ケースでは2候補を残し、禁止された本人事実を除外、不足を通知。上限内のquality_checks_009、JSONと手動分析を参照。 |
| T190 | 会う不安後の中立話題と外出質問の区別 | pytest候補フィルター | PASS | 店の好み質問は拒否、本の話題への質問は保持。謝意と中立な質問を同一候補に含む場合も保持。`python -m pytest tests/test_app.py -q -k "new_experience_patterns_do_not_reject_partner_questions or meeting_unease_filters_outing_questions"`: 10 passed。 |
| T191 | 質問フィルターの自然な疑問形境界 | pytest / 自然な疑問語尾 | PASS | 「観た？」「行くの？」「観たの？」「行くかな？」「映画館によく行く？」「旅行に出かけた？」を本人の断定から除外。T190と同一の10 focused testsで確認。 |
| T192 | 現行コード全pytest | Windows / pytest | NOT_TESTED | 直近の2件のレビュー境界修正を反映した最終回を実行中。 |
| T193 | Firefox UI回帰（現行コード） | Firefox/Selenium | PASS | `python -m pytest tests/test_ui_firefox.py -q`: **6 passed in 79.98s**。Chromeは使用していない。今回の直近変更はサーバー候補判定のみ。 |
| T194 | Python/JavaScript構文・差分・秘密情報検査 | py_compile / node / git diff / scan | PASS | 最新差分で`py_compile`、`node --check app.js`、`git diff --check`成功。変更diffのGeminiキー形式検索0件。CRLF変換の注意だけ。 |
| T195 | 誘い後の明確な保留表現を継続拒否として扱う | pytest refusal-state + candidate filter | FIXED | レビューで「もう少し話してから」「今は会うのを控えたい」「会うのはまだ考えていない」を見逃し、再誘いを通す問題を再現。保留語を拒否状態に加え、再誘い候補を除外。focused testsで確認。 |
| T196 | 相手の経験を受け止める文を本人事実と誤判定しない | pytestの履歴帰属テスト | FIXED | 相手が話した最近の旅行、カフェ探索、映画館頻度に対する「〜なんですね」型の反応を本人の経験として誤拒否する問題を修正。相手履歴に該当する肯定事実がある場合のみ帰属表現を許可。 |
| T197 | 実API品質ランナーの重複ケース排除 | スクリプト定義レビュー | PASS | 同一入力の修正前/後重複を新規実行ケースから除き、修正後1回の確認を残す。既存JSONの実行履歴は保持。今回追加のAPI呼び出しなし。 |
| T198 | 追加レビュー後の現行全pytest | Windows / pytest | PASS | 拒否表現・相手帰属の追加回帰を含め`python -m pytest -q`: **438 passed in 89.89s**。Firefox UIテストを含む。 |
| T199 | 相手の否定発言を肯定事実へ反転させない | pytest / 履歴節の極性確認 | FIXED | 「好きじゃない」「旅行に行けなかった」「映画館によく行かない」という架空発言を肯定形で受け止める候補が通る問題を再現。相手の同一肯定節だけを根拠に許可し、否定発言からの逆転を拒否。 |
| T200 | 疑問符のない会う関連質問を抑止 | pytest / question-clause判定 | FIXED | 「カフェならどんなところが好き」のように明示記号のない質問が、不安表明後の候補を通る問題を修正。中立的な本の話題は保持。 |
| T201 | 最終差分の全pytest | Windows / pytest | PASS | 否定情報・疑問符なし質問の境界を含め`python -m pytest -q`: **441 passed in 92.12s**。Firefox UIテストを含む。 |

この追記時点の履歴集計: 204項目。T181〜T183、T187〜T189、T195、T196、T199、T200は修正前の問題を再現し、範囲を限定した修正を確認。T185の実生成品質はFAILとして保持し、T186会話004は品質条件未達のため未実施。T190/T191はfocused 10 tests、T192/T198/T201全pytest、T193 Firefox、T194静的検査、T197ランナー重複確認でPASS。Actionsは最終コミットPush後に確認する。過去のFAILは履歴から削除しない。

集計: 204項目、PASS 160 / FAIL 13 / FIXED 14 / BLOCKED 5 / NOT_TESTED 12。過去のFAIL・BLOCKEDは履歴として維持する。quality_checks_009は自動ゲートがPASSでも文章品質の手動判定はFAIL。conversation_004は未実施。

| T202 | 相手の否定・未経験を肯定の受け止めへ反転しない | pytest / 同一節の極性検査 | FIXED | 追加レビューで「旅行には行かなかった」「行っていなかった」「行けていない」「行ったことがない」「行くことがない」および映画館の対応表現を含む候補が通ることを再現。否定パターンを追加し、後続ケースを含め旅行・映画館25形を重点確認。`tests/test_app.py`。自由文全体の意味検出を保証するものではない。 |
| T203 | 否定表現の最終修正を含む全pytest | Windows / pytest | PASS | `python -m pytest -q`: **455 passed in 92.87s**。Firefox UIテストを含む。 |
| T204 | Python/JavaScript構文・差分検査 | py_compile / node --check / git diff --check | PASS | `app.py`、品質009スクリプト、`tests/test_app.py`のPython構文、`app.js`構文、差分検査が成功。 |
| T205 | 最新コミットのGitHub Actions | Push workflow | PASS | SHA `2c4e0805a5d3d79b8af91c4755428422f8802445`を対象とした[run 38670690590](https://github.com/kenkyu0909/aichatapp/actions/runs/38670690590)が成功。pytest **455 passed, 1 warning**、JavaScript構文検査とFirefox準備、Artifact uploadも成功。 |
| T206 | 「行けない/行けなくて」から正の経験を推定しない | pytest / 相手履歴の極性検査 | FIXED | 独立レビューで「最近旅行には行けない」「行けなくて」「行けなくなって」、映画館の同形を見逃す問題を再現。肯定の受け止め候補を拒否する回帰を追加。重点回帰29 passed。 |
| T207 | 負のプロフィール記述を信頼済み事実にしない | pytest / `_trusted_fact_clauses` | FIXED | プロフィール本文の「行けない」「行けなくて」「行けなくなって」を肯定事実の根拠一覧に入れない。6つの境界を確認。`tests/test_app.py`。 |
| T208 | 最新否定形修正を含む全pytest | Windows / pytest | PASS | `python -m pytest -q`: **467 passed in 92.31s**。Firefox UIテストを含む。 |
| T209 | 最新否定形修正のPython/JavaScript構文・差分検査 | py_compile / node --check / git diff --check | PASS | `app.py`、`tests/test_app.py`のPython構文、`app.js`構文、差分検査成功。 |
| T210 | 最新コードSHAのGitHub Actions | Push workflow | NOT_TESTED | 次のcommitをPushして同一SHAの成功を確認する。 |

更新後集計: **213項目**。PASS 165 / FAIL 13 / FIXED 17 / BLOCKED 5 / NOT_TESTED 13。T208とT209を含む最新コードのPush Actions確認が残る。過去のFAIL・BLOCKEDは履歴として維持する。品質009の手動評価はFAILのまま、conversation_004は未実施のまま。

| T211 | 相手の過去経験・習慣と願望/予定を区別し、否定形を反転しない | pytest / 履歴・プロフィール双方の根拠検査 | FIXED | 独立監査で「好きではありません/好きじゃありません」「行く機会がない/時間がなくて/行けず」「行きたい/予定/つもり/かもしれない」から肯定の受け止めや過去経験を誤認する問題を再現。旅行は時点付きの完了形、映画館は肯定的な習慣形を共通ヘルパーで照合。旅行・映画館・場所探しの重点66件が成功。 |
| T212 | 時制・極性境界の最終修正を含む全pytest | Windows / pytest | PASS | 最新実装commit `38abb1ce3855f5843a29da7d27821cb6ee2a16fd`で`python -m pytest -q`: **517 passed in 92.24s**。Firefox UIを含む。 |
| T213 | 最新コミットSHAのGitHub Actions | Push workflow | NOT_TESTED | 最新コードと文書のPush後に同一SHAで確認する。 |

更新後集計: **216項目**。PASS 166 / FAIL 13 / FIXED 18 / BLOCKED 5 / NOT_TESTED 14。T213は当時のActions未実施履歴として残す。品質009の手動文章判定はFAILのまま、conversation_004は未実施のまま。

| T214 | 趣味の弱い否定と句読点なし口語質問を事実根拠にしない | pytest / 履歴・プロフィール根拠 | FIXED | Pythonレビューで「趣味ってほどじゃない/というほどではない」と「最近旅行行ったことあるの」「映画館によく行くの」「カフェを探すのが好きなの」等が肯定根拠として通る漏れを発見。修正前focused runは6 failures、修正後は**79 passed**。profile根拠・相手発言の両方を確認。曖昧な形は安全側に倒し候補不足となる場合がある。 |
| T215 | 現行コードの構文・差分・キー形式検査 | py_compile / node / git diff / regex scan | PASS | `py_compile`対象Python、`node --check app.js`、`git diff --check`成功。最新コードcommit diffのAPIキー形式検索0件。 |
| T216 | 最新コード・報告のGitHub Actions | Push workflow | NOT_TESTED | docs更新後にcommit/Pushし、Actionsが同じSHAを対象に成功したことを確認する。 |

更新後集計: **219項目**。PASS 167 / FAIL 13 / FIXED 19 / BLOCKED 5 / NOT_TESTED 15。過去のFAIL・BLOCKEDは維持。実API品質009の手動評価はFAIL、今回のGemini追加呼び出しは0、conversation_004は品質ゲート未達のため未実施。


## 2026-10-15 12:30 JST：年齢・勤務年数の具体度境界

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T217 | 年代の前半・後半と確認済み年齢の整合 | pytest / 21歳・28歳の架空プロフィール | FIXED | 修正前は21歳を「20代後半」、28歳を「20代前半」とする候補を安全と判定。確認済み年齢と前半/後半を照合し、20〜24歳を前半、25〜29歳を後半として検証。修正後4ケース成功。日本語の年代表現すべてを保証するものではない。 |
| T218 | 勤務年数の完全一致と単位整合 | pytest / 架空の職歴情報 | FIXED | 修正前は確認済み「15年」が「5年」や「5年目」を支えた。数字の部分一致を廃止し、数値と「年／年間／年目」を照合。修正後4ケース成功。 |
| T219 | 最新事実境界修正を含む全pytest | Windows / pytest | PASS | 2026-10-15 12:28 JST、最新作業ツリーで **583 passed in 83.39s**。Firefox UIテストを含む。Gemini実API呼び出し0。 |
| T220 | Python/JavaScript構文・差分・秘密形式検査 | `py_compile`、`node --check app.js`、`git diff --check`、変更内容の秘密形式スキャン | PASS | 2026-10-15 12:29 JST、全コマンド成功。変更対象の秘密形式一致0件。 |
| T221 | Firefox UI単独実行 | Selenium Firefox / `tests/test_ui_firefox.py` | PASS | 2026-10-15 12:31 JST、**6 passed in 81.18s**。Firefoxのみを使用。Chromeは使用していない。 |
| T222 | 最新コードのGitHub Actions | Push workflow / 最新PR HEAD | NOT_TESTED | コード・報告をcommit/push後、同一SHAの実行を確認する。 |

この追記直前の表には216個のID行があり、説明文の旧集計219件と3件の差があった。履歴は保持し、今回以降のID行集計を基準とする。現在222 ID行: PASS168 / FAIL13 / FIXED21 / BLOCKED5 / NOT_TESTED15。品質009実出力の手動判定FAILを維持し、Gemini実通信0回、conversation_004未実施。


## 2026-10-15 12:45 JST以降：勤務年数の範囲と安全候補の保持

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T227 | 確認済み勤務年数と「以上／未満」等の一致 | pytest / 架空の職歴5年 | FIXED | 修正前、確認済み「5年」に対する「5年未満」「5年以上」が通る3ケースを再現。修正後は一致する範囲だけ許可し、範囲付きの質問文は本人事実として誤検出しない。関連13ケースを通過。 |
| T228 | 全pytest・Firefox UIを含むスナップショット | Windows / pytest | PASS | 2026-10-15 12:45 JST、**612 passed in 96.69s**。ただし、後続の安全候補併合変更より前の作業ツリーを対象とする。最新変更を含む全体再実行は時間制約により未実施。 |
| T229 | 勤続範囲とカフェ嗜好から場所探索嗜好への拡張防止 | pytest focused suite | PASS | **19 passed**。5年/5年以上/5年未満の一致・矛盾、質問形、年目区別、および「カフェ巡りが好き」だけでは「静かな場所を探すのが好き」を支えない対照を含む。 |
| T230 | 誘い候補の再生成後も安全候補を併合 | pytest / 2応答のGeminiモック | PASS | 修正前、1回目の安全1案へ置換し2回目の安全中立案を失うことを再現。修正後、各回で独立に通過した案を重複除去して保持。句読点違反の誘い案は除外し、指定数未満なら不足を通知。関連12ケース通過。 |
| T231 | 最新差分の構文・空白・秘密形式検査 | `py_compile` / `node --check` / `git diff --check` / 変更差分スキャン | PASS | 2026-10-15 12:53 JST、Python/JavaScript構文、差分検査成功。変更差分のAPIキー形式一致0件。GitのLF/CRLF警告は改行設定に関するもので、差分検査は成功。 |
| T232 | 職歴「ちょっと／強／弱」の限定詞一致 | pytest回帰 / 確認済み5年 | FIXED | 独立レビューで確認済み「5年」に「5年ちょっと」「5年強」「5年弱」が通る問題を発見。追加した3件は修正前にすべてFAIL。修正後は限定詞を含めて値全体を照合。 |
| T233 | 勤続限定詞・質問形・数値/単位境界のfocused回帰 | pytest | PASS | 2026-10-15 12:56 JST、21 passed。未知の限定詞を同一事実とみなさず、確認済み限定詞との一致と質問形の対照を確認。

現在ID行234件。暫定集計: PASS178 / FAIL13 / FIXED24 / BLOCKED5 / NOT_TESTED14。T228の612件は候補併合変更を含まない。Gemini実API呼び出し0、quality_checks_009の生成品質FAILは継続、conversation_004および新会話HTMLは未実施。

### 2026-10-15 14:19 JST：直接質問・頻度・誤字の再現修正

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T234 | カフェ頻度の表記揺れを含む根拠照合 | pytest / 「週1くらい」と確認済み頻度 | FIXED | 「月1回」根拠で「毎日」が通る既知の漏れに加え、「週1くらい」が頻度検査に入らず通る問題を修正前FAILで再現。週/月/年の数値頻度を正規化して比較し、同一頻度の対照は許可。 |
| T235 | 分類外の本人向け直接質問と回答一致 | pytest / 得意料理・得意なこと | FIXED | 「得意料理は？」を話題そらし候補が通ることを再現。質問を本人確認へ送り、確認回答と異なる料理/技能の候補を除外。安全候補のみ残し不足を通知する既存フィルターは維持。日本語自由文全般の意味判定保証ではない。 |
| T236 | 品質009で記録された高確度誤字 | pytest / 雰囲い | FIXED | 「どんな雰囲いのお店」「お店の雰囲い」を候補単位で除外し、正しい「雰囲気」は保持。自動置換はしない。 |
| T237 | 今回の重点回帰 | pytest focused / frequency・直接質問・安全候補・誤字 | PASS | 最新重点ケース **29 passed**。途中の修正前FAILは履歴として維持。 |
| T238 | バックエンド単体全体 | `python -m pytest tests/test_app.py -q` | PASS | 現行コード **634 passed in 16.51s**。 |
| T239 | 最新差分の全pytest・Firefox UI | `python -m pytest -q` | PASS | 2026-10-15 14:21 JST、**713 passed in 98.60s**。Firefox UIを含む。Chromeは使用していない。 |
| T240 | Python・JavaScript構文および差分検査 | `py_compile` / `node --check app.js` / `git diff --check` | PASS | 現在の差分に対して全て成功。 |
| T241 | 最新コミットのGitHub Actions | Push workflow | NOT_TESTED | 追跡対象のみcommit/push後、同一SHAの結果を確認する。 |

更新後ID行は241件: **PASS181 / FAIL13 / FIXED27 / BLOCKED5 / NOT_TESTED15**。QUALITY009の実生成文手動評価FAILは継続し、今回のGemini呼び出し0回。conversation_004と新しい会話HTMLは作成しない。


## 2026-10-15 12:37 JST：プロフィール具体度・肯定節・頻度の独立監査

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T223 | 年齢、職歴、映画/読書経験、カフェ頻度、ジャンル範囲、接続助詞「し」の根拠境界 | read-only監査 + pytest回帰 | FIXED | 監査で、20代だけの入力から前半/後半を推測、数値型のプロフィールを見落とす、最近観た映画/読んだ本の感想、月頻度、ジャンル情報から映画全般の好みへの拡張、肯定節と否定節を結ぶ「し」のスコープ不良を再現。全項目を固定回帰で修正。 |
| T224 | 新規境界と安全な対照ケース | pytest focused suite | PASS | 年齢・勤務年数・最近の経験・カフェ頻度・ジャンル・肯定節の**20 passed**。数字型、年/年間の同等な期間、年目の区別、確認済み頻度の対照を含む。 |
| T225 | 最新コードの全pytestとFirefox UI | Windows / pytest | PASS | 2026-10-15 12:37 JST、**599 passed in 82.63s**。Firefox UIテストを含む。 |
| T226 | 最新コードの構文・差分・秘密形式検査 | Python compile、Node構文、git diff、秘密形式スキャン | PASS | Python/JavaScript構文と差分検査成功。APIキー形式の一致0件。 |

T221は単独Firefox **6 passed in 81.18s**へ更新。行基準の現在集計は226項目: PASS172 / FAIL13 / FIXED22 / BLOCKED5 / NOT_TESTED14。過去の品質009実出力FAILを保持。今回の実Gemini呼び出し0。conversation_004は指示どおり未実施。最新SHAのGitHub Actions T222は未テスト。


### 2026-10-15 14:25 JST：UI質問言い換えと頻度同義語のレビュー修正

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T242 | 本人確認UIが生成した言い換え質問と直接質問の対応 | pytest / 実際の `missing_personal_fact_question()` 出力を保存して候補検査 | FIXED | `何か得意なことありますか？` に対しUIの「相手の…にどう答えたいか…」という確認文と本人回答を使うと、根拠のある候補も拒否する不具合を修正前に再現。確認質問に元の質問が含まれる場合に限り回答を照合し、正しい回答を通す回帰を追加。|
| T243 | 毎週/週1回など同義頻度の根拠照合 | pytest / 日・週・月・年の頻度同義語 | FIXED | 毎週と週に1回、毎月と月1回、毎年と年1回が異なるシグネチャとなり安全な候補を誤って落とす問題を修正前FAILで再現し、周期ごとに正規化。異なる頻度を同一視しない既存ケースも維持。|
| T244 | レビュー指摘の修正前後再現 | pytest focused | PASS | 変更前4件失敗（頻度3件、実UI質問1件）。修正後重点セット5 passed。|
| T245 | 最新コードの全pytest・Firefox UI | `python -m pytest -q` | PASS | 2026-10-15 14:25 JST、**717 passed in 98.36s**。Firefox UIを含む。Chrome未使用。|
| T246 | 最新差分のPython/JavaScript構文と空白 | `py_compile` / `node --check app.js` / `git diff --check` | PASS | 2026-10-15 14:25 JST、すべて成功。|

最新ID行は246件。累計: PASS184 / FAIL13 / FIXED29 / BLOCKED5 / NOT_TESTED15。旧FAILは履歴として維持。今回Gemini実API 0回。`conversation_004`・新会話HTMLは指示どおり未実施。


### 2026-10-15 14:29 JST：会うことへの抵抗表現の安全判定

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T247 | 「抵抗があります」の慎重・拒否判定と否定の対照 | pytest / 候補フィルター | FIXED | 「直接会うのは少し抵抗があります」「実際に会うことにはまだ抵抗があります」を修正前に2件再現し、既存条件が認識せず再勧誘候補を通す穴を修正。明示的な肯定「直接会うことに抵抗はありません」は拒否扱いしない。中立候補は残る。|
| T248 | 抵抗表現と既存の不安・中立候補回帰 | pytest focused | PASS | 不安/抵抗/中立候補の重点セット **5 passed**。修正前2 failures、肯定文の対照1 passed。|
| T249 | 現行バックエンド全体 | `python -m pytest tests/test_app.py -q` | PASS | **641 passed in 17.92s**。|
| T250 | 最新コードの全pytest・Firefox UI | `python -m pytest -q` | PASS | 2026-10-15 14:29 JST、**720 passed in 101.07s**。Firefox UIを含む。Chrome未使用。|
| T251 | 最新差分のPython/JavaScript構文と空白 | `py_compile` / `node --check app.js` / `git diff --check` | PASS | 2026-10-15 14:29 JST、すべて成功。|

最新ID行は251件。累計: PASS188 / FAIL13 / FIXED30 / BLOCKED5 / NOT_TESTED15。修正後の最新Actionsは未実施（前コミット `029f86a` のPush/PR Actionsは成功）。今回Gemini実API 0回。`conversation_004`・新会話HTMLは指示どおり未実施。


### 2026-10-15 14:34 JST：候補の進め方が重なる場合の通知

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T252 | V2候補のreply_move重複通知と安全候補保持 | pytest / filter_safe_candidates | FIXED | 3案が同じ `reply_move` の場合に、候補を削除せず進め方が重なる可能性を通知。異なるreply_moveなら通知しない。UIが `candidate_notice` を表示する実装も確認。意味的な同一内容を完全検出する機能ではない。|
| T253 | 候補ロールと誘い判断の重点回帰 | pytest focused | PASS | 候補重複/進め方の注意・自然な誘い条件 **3 passed**。修正前は重複ロールの注意がなく1件FAIL。|
| T254 | 最新バックエンド全体 | `python -m pytest tests/test_app.py -q` | PASS | **642 passed in 17.63s**。|
| T255 | 最新コードの全pytest・Firefox UI | `python -m pytest -q` | PASS | **721 passed in 98.68s**。Firefox UIを含む。Chrome未使用。|
| T256 | 最新差分のPython/JavaScript構文と空白 | `py_compile` / `node --check app.js` / `git diff --check` | PASS | 2026-10-15 14:34 JST、すべて成功。|

最新ID行は256件。累計: PASS192 / FAIL13 / FIXED31 / BLOCKED5 / NOT_TESTED15。過去FAILとQUALITY009の実生成評価FAILは維持。今回Gemini実API 0回。`conversation_004`・新会話HTMLは実施しない。

### 2026-10-15 14:39 JST：候補ロール重複の境界条件を修正

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T257 | 3候補中2候補だけ進め方が重複する境界 | pytest / reply_move の重複検査 | FIXED | 独立レビューで `react, react, expand` では注意が出ない境界を指摘。修正前のテストで再現し、異なる進め方の数が候補数より少なければ警告するよう変更。安全な候補3案は保持。|
| T258 | 全重複・部分重複・全て異なる進め方 | focused pytest | PASS | 重複通知のfocused回帰3件成功。部分重複では警告、全て異なる場合は警告なし。|
| T259 | 最新変更の全pytest・Firefox UI | `python -m pytest -q` | PASS | 2026-10-15 14:39 JST、**721 passed in 98.90s**。Firefox UIを含む。|
| T260 | 構文・差分検査・独立レビュー | Python compile、Node構文、`git diff --check`、code reviewer | PASS | Python/JavaScript構文・空白検査成功。レビュー指摘0件。|

最新ID行は260件。累計: PASS195 / FAIL13 / FIXED32 / BLOCKED5 / NOT_TESTED15。過去FAILとQUALITY009の実生成評価FAILは維持。今回Gemini実API 0回。`conversation_004`・新会話HTMLは実施しない。

### 2026-10-15 15:09 JST：直接質問への読書ジャンル回答の根拠範囲

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T261 | 確認済みジャンルへの広い聞き返しを拒否 | pytest / 候補フィルター | FIXED | 「小説を読むことが多いです」の回答後に「本は好きですか？」だけを出す候補が通る既存穴を再現。候補内容アンカーを求め、安全な回答候補は保持し不足数を通知。|
| T262 | 最近の作品と習慣ジャンルの混同 | pytest / 本人確認回答 | FIXED | 最近読んだ一作品だけから「普段読むジャンル」を断定しない。複合質問でも最近の節を別扱い。習慣が明示された別節は利用可能。|
| T263 | 頻度・好みの矛盾検査 | pytest / 節別照合 | FIXED | 「読むことが多い」を「たまに読む」へ変える候補を拒否。プロフィールの好きなジャンルだけから頻度を創作しない。候補内の頻度矛盾も拒否。|
| T264 | 複合回答のジャンル・頻度分離 | pytest / 節の境界と根拠アンカー | FIXED | 「普段は漫画が多くてミステリーはたまに」「漫画はたまに読むし小説はよく読む」、接続助詞・改行で区切られる回答を検証。異なるジャンルの頻度を相互に流用しない。|
| T265 | 本人への質問だけで直接回答を装う候補を拒否 | pytest / 候補フィルター | FIXED | 「小説って普段読みますか？」「…読みますかね」「…読みますか！」等の疑問だけの候補を拒否。回答文＋追加質問の候補は許可。|
| T266 | 読書ジャンル・回答範囲focused回帰 | `python -m pytest tests/test_app.py -q -k 'book_genre or reading_habit or recent_book_answer or recent_only_answer_to_mixed_genre or verified_book_genre'` | PASS | 17 passed, 644 deselected。修正前に主要な漏れ・誤拒否を再現。|
| T267 | 最新全体pytestとFirefox UI回帰 | `python -m pytest -q` | PASS | 2026-10-15 15:10 JST、**740 passed in 99.63s**。Firefox UIを含む。Chrome未使用。|
| T268 | Python/JavaScript構文・差分検査・独立レビュー | `py_compile`、`node --check app.js`、`git diff --check`、Python reviewer | PASS | 構文/差分検査成功。レビュー指摘を反映後に再レビューされ、新たな指摘なし。|

最新ID行は274件。累計: PASS203 / FAIL13 / FIXED38 / BLOCKED5 / NOT_TESTED15。過去FAILとQUALITY009の実生成評価FAILは維持。今回Gemini実API 0回。`conversation_004`・新会話HTMLは実施しない。規則ベースの日本語根拠照合であり、未登録のあらゆる言い換えを理解できる保証はない。最新差分のGitHub ActionsはPush後に確認する。|

### 2026-10-15 15:24 JST：最近観た映画の直接質問に対する回答候補の検査

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T269 | 確認済み作品名だけを疑問形で返す穴の再現と修正 | 修正前 pytest / `filter_safe_candidates` | FIXED | 「最近どんな映画を観ましたか？」への本人回答に作品名があると、「青い灯台を観ましたか？」等が送信候補に残ることを修正前テストで再現。作品名が疑問・伝聞・希望・否定にだけ含まれる場合は直接回答として認めない。 |
| T270 | 作品名入りの質問・未視聴・否定候補を送信前に除外 | pytest / 候補安全フィルター | PASS | 13種類の疑問・意図・伝聞・否定表現を拒否。安全な視聴回答を保持し、3案要求時は1案と不足通知を返す。架空作品「青い灯台」を使用。 |
| T271 | 視聴完了表現と対比節を含む回答 | pytest / 候補安全フィルター | PASS | 「観終わりました」「見終えました」と「観るつもりでしたが実際に観ました」は受け入れる。確認回答に続く改行付き追加質問も保持。 |
| T272 | 最近観た映画への回答関連ケース | `python -m pytest tests/test_app.py -q -k 'recent_movie_title_in_question or recent_movie_answer_can_include_verified_title or recent_movie_answer_does_not_accept_topical_followup or direct_question_filter_keeps_answer'` | PASS | **21 passed**。直接回答、疑問形回避、矛盾候補、改行付き追質問と安全候補の不足通知を確認。モック/ローカル試験。 |
| T273 | 全pytestとFirefox UI回帰 | `python -m pytest -q` | PASS | **756 passed in 100.64s**。Firefox UIテストを含む。Chromeは使用していない。 |
| T274 | 構文検査・差分検査・独立レビュー | Python `py_compile`、`node --check app.js`、`git diff --check`、code reviewer | PASS | 構文・差分検査成功。独立レビュー指摘を順次テストに追加し、最終差分レビューで未解決指摘なし。 |

### 2026-10-15 15:36 JST：品質009の候補反応重複警告

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T275 | QUALITY009に保存された同じ肯定反応候補の意味重複 | オフライン再現・候補フィルター | FIXED | 3案要求に対して「新しいお店を見つけるのワクワクしますよね！」と「新しいお店を開拓するの楽しいですよね！」の安全な2候補を保持し、中心的反応の類似警告と1案不足通知の両方を返す。|
| T276 | 異なる話題・反対の感情・後続節にある否定の対照 | focused pytest | PASS | 2 tests passed。異なる話題では警告せず、肯定/否定の反応差も誤警告せず、同じ肯定反応の後に別の否定節が続く場合は反応部分を比較できる。いずれも安全候補を保持。|
| T277 | 最新コードの全pytest・Firefox UI | `python -m pytest -q` | PASS | **757 passed in 99.50s**。ブラウザUIテストはFirefoxを使用しChrome未使用。 |
| T278 | Python/JavaScript構文・差分検査・独立レビュー | `py_compile`、`node --check app.js`、`git diff --check`、code reviewer | PASS | 構文・差分検査成功。独立レビューは最終差分に未解決指摘なし。 |

最新ID行: 278。累計: PASS206 / FAIL13 / FIXED39 / BLOCKED5 / NOT_TESTED15。Gemini実APIは今回0回。前回のQUALITY009実生成品質FAILは履歴として維持し、意味的多様性全般の解決とは扱わない。今回コードのGitHub Actionsは未実施。 |

| T279 | コピーのみでは送信履歴に記録されず、手動確認後は1件だけ保存 | Firefox UI / SQLite連携 | PASS | 改行付き返信をコピーした直後の本人送信バブル0件を確認。手動保存後は本文・改行を保持した1件だけが表示され、再読み込み後も1件のまま。Firefox単独テスト1 passed。 |

最新ID行: 279。累計: PASS207 / FAIL13 / FIXED39 / BLOCKED5 / NOT_TESTED15。全pytestはコード変更後757 passed in 99.50sで、最後のFirefox回帰T279は個別に1 passed。Gemini実APIは今回0回。 |

| T280 | 候補重複警告・Firefox送信分離を含むGitHub Actions | Push / PR workflow・artifact確認 | PASS | SHA `c6ea0337d525746463936c9e6c28f366e4190648`を対象にPush [run](https://github.com/kenkyu0909/aichatapp/actions/runs/38693787481) とPR [run](https://github.com/kenkyu0909/aichatapp/actions/runs/38693794221) が成功。Push artifactのpytest.xml: 757 tests / 0 failures / 0 errors / 0 skipped。Firefox 157.0とJavaScript構文検査も成功。|

最新ID行: 280。累計: PASS208 / FAIL13 / FIXED39 / BLOCKED5 / NOT_TESTED15。対象SHA `c6ea0337d525746463936c9e6c28f366e4190648`のActionsは成功。 |

### 2026-10-15 16:02 JST：本人質問の分類漏れとカフェ嗜好の回答すり替え

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T281 | インドア/アウトドア等の二択質問で本人確認へ誘導 | pytest / 直接質問分類 | FIXED | 未分類だった「インドア派ですか？それともアウトドア派ですか？」を本人情報の確認へ送り、未確認の候補を除外する。元の質問文を確認フォームに保持。|
| T282 | 確認済みカフェ情報による質問すり替えを防止 | pytest / 候補フィルター | FIXED | カフェ好みの質問に対し、別の質問・「話題が好き」・質問のみ・確認済み情報と逆の否定形を拒否。根拠のある肯定形は許可。|
| T283 | カフェへの誘い承諾を嗜好質問と誤判定しない | pytest / 招待候補フィルター | FIXED | 単独の「今度カフェに行きませんか？」を本人の嗜好質問として扱わず、前向きな承諾と日程相談を保持する。|
| T284 | 個人質問と誘いが同じ文にある場合の分離 | pytest / 直接質問と招待分類 | FIXED | 映画館/自宅の二択と映画への誘いが同居する入力で、誘い部分を除いて本人質問を検出。回答確認前の承諾候補は送信可能にしない。|

この追補後のTEST_MATRIXは284件: PASS208 / FAIL13 / FIXED43 / BLOCKED5 / NOT_TESTED15。最新コードの全pytest **761 passed in 97.39s**（Firefox UI含む）、直接質問 focused suite **5 passed**。`py_compile app.py`、`node --check app.js`、`git diff --check`成功。Gemini実API 0回。独立レビューの指摘を修正し再レビューで未解決指摘なし。最新Push済み `9e2b8fd3ba8e917f8aa51dc3ccb43009d58ebdb9` のPush/PR Actions成功は確認済みだが、現在の未コミットコード差分を含まない。 |

| T285 | 直接質問・カフェ嗜好の安全ゲートを含む最新GitHub Actions | Push / PR workflow、artifactのpytest.xml | PASS | SHA `199d6b6c6b3caa6799f4ac5e0a61eb28237cfb00`でPush [run 38696117197](https://github.com/kenkyu0909/aichatapp/actions/runs/38696117197) とPR [run 38696124835](https://github.com/kenkyu0909/aichatapp/actions/runs/38696124835) が成功。Push artifactは761 tests / 0 failures / 0 errors / 0 skipped。Firefox UIとJavaScript構文検査も成功。|

最新ID行: 285。累計: PASS209 / FAIL13 / FIXED43 / BLOCKED5 / NOT_TESTED15。対象SHA `199d6b6c6b3caa6799f4ac5e0a61eb28237cfb00` のPush/PR Actionsを確認。過去のQUALITY009実生成品質FAILは維持し、今回のGemini実API呼び出しは0回。 |

| T286 | Windows `start.bat`別ポート起動とFirefoxの架空データUI確認 | Windows 11、`MRA_PORT=8767`、一時`APP_DATA_DIR`、空`MRA_API_DIR`、Firefox/Selenium | PASS | `start.bat`が127.0.0.1:8767で起動し、準備完了後Firefoxを開いた。HTML/CSS/JSとAPIを読み込み、架空の相手・相手発言をUIから登録し、再読込後もSQLiteに保持。JS例外0件。テスト用サーバーは終了し8767を解放。Gemini通信なし。既定8765は別PIDのため変更していない。統合実行環境からCtrl+Cを子プロセスへ送れず、対話コンソールでのCtrl+C終了はNOT_TESTED。|

| T287 | Windows起動スクリプトのポート競合時に既存プロセスを維持 | Windows 11、8767番で隔離HTTPテストサーバーを起動して競合を再現 | PASS | 起動スクリプトはexit 2と「Port 8767 is occupied by another process」を返し、テストサーバーのPIDが引き続きlistenしていることを確認。既存プロセスは停止しない。確認後は起動したテストサーバーだけを終了し8767解放を確認。|

最新ID行: 287。累計: PASS211 / FAIL13 / FIXED43 / BLOCKED5 / NOT_TESTED15。T02は既定ポートを特定できない既存プロセスが占有するためBLOCKEDのまま。T286は一時データと8767でのWindows/Firefox実機確認に成功。対話コンソールでのCtrl+C終了は未検証。 |

| T288 | QUALITY009保存済みGemini候補の現行送信前フィルター再生 | 架空データJSONをローカルで再生し`filter_safe_candidates`を実行。focused pytestも併用 | PASS | 短文ケースの誤字「雰囲い」、最近観た映画への直接質問を避ける代替2案、未確認の「私もお出かけが好き」、会う不安直後の「安心してください」を現行フィルターが除外。残る安全候補はそれぞれ2/3、1/3、2/3、1/2案で保持され、不足通知あり。誘い機会ケースは自然な誘いを含む3案を維持。focused pytest **12 passed**。保存済み候補のオフライン再生であり、新しいGemini実通信ではない。|

最新ID行: 288。累計: PASS212 / FAIL13 / FIXED43 / BLOCKED5 / NOT_TESTED15。過去の品質009手動FAILは維持し、現在フィルターが既知候補を除外したことと、モデル自体が自然な候補を生成できることを区別する。|

| T289 | 確認済みの本人回答を直接質問の各候補に含める指示 | reply prompt静的検査とpytest | PASS | reply用指示に「各候補が確認済み回答を含み、別質問だけですり替えない」と明記。`test_v2_user_info_question_is_separate_and_answers_are_ephemeral`を拡張し、`python -m pytest -q tests/test_app.py -k "v2_user_info_question or answers_verified_partner_question or recent_movie_answer or test_prompt"`で**8 passed**。実Geminiでの文章品質は未検証。|

最新ID行: 289。累計: PASS213 / FAIL13 / FIXED43 / BLOCKED5 / NOT_TESTED15。|

| T290 | 直接質問への回答済み候補を残し、すり替え案を返さず不足を通知 | FastAPI TestClient + Gemini SDKモック | PASS | 架空の最近観た映画に対し、確認回答を含む候補1案と直接回答を避ける候補2案をモック応答。API経路は確認済み候補だけを返し、代替欄を空にし、3案中1案しか安全に表示できない旨を通知。プロンプトにも各案で回答する指示が渡ることを検証。pytest **3 passed**。実Geminiの追従性は未検証。初回テストではレスポンスに内部`candidate_rejections`が露出すると誤想定して失敗。アプリはその内部情報を返さない設計であり、公開契約（候補の除外・不足通知）を確認するassertに直して再実行した。|

最新ID行: 290。累計: PASS214 / FAIL13 / FIXED43 / BLOCKED5 / NOT_TESTED15。|

| T291 | 直接質問の回帰を含む全pytest・構文・最新Actions | Windows 11でpytest、構文検査、GitHub Actions Push/PR | PASS | `python -m pytest -q`: **762 passed in 110.09s**（Firefox UIを含む）。`py_compile`、`node --check app.js`、`git diff --check`も成功。SHA `b7c55affef071a88b2fdf46f5e02134ca571c707` のPush [Actions](https://github.com/kenkyu0909/aichatapp/actions/runs/38699527292)とPR [Actions](https://github.com/kenkyu0909/aichatapp/actions/runs/38699532641)は成功。Firefoxでの新しい手動実操作はしていない。|

最新ID行: 291。累計: PASS215 / FAIL13 / FIXED43 / BLOCKED5 / NOT_TESTED15。|

| T292 | 直接質問回帰を含む最新HEADのPush/PR Actions | GitHub Actions、pytestログ、PR HEAD照合 | PASS | SHA 5e269301c6618571a4724b6918c4e50fe1d97bf6のPush [run 38699841263](https://github.com/kenkyu0909/aichatapp/actions/runs/38699841263)とPR [run 38699846020](https://github.com/kenkyu0909/aichatapp/actions/runs/38699846020)が成功。両方とも同じ最新HEADを対象。pytest **762 passed, 1 warning**。Firefoxを含むオフラインテスト、JavaScript構文検査も完了。警告はStarlette TestClientとhttpxの非推奨通知。コードはSHA b7c55affef071a88b2fdf46f5e02134ca571c707の全テスト成功から変更なし。|

最新ID行: 292。累計: PASS216 / FAIL13 / FIXED43 / BLOCKED5 / NOT_TESTED15。品質009の実生成手動FAILは未解決。実Gemini APIは0回。|

| T293 | 品質009評価ランナーが安全な候補不足と完全候補集合・実API呼出しを区別 | 保存済み架空JSONの読取、pytestによる純関数検証 | FIXED | 実APIなし。ランナーは要求3案に対して安全候補2案の応答をpartial_safeと記録し、3案完全生成と混同しない。smoke PASSには実プロバイダー試行とモデル名も必要。既存quality_checks_009.jsonは未変更。記録済みsmoke_replyはAPI1・gemini-3.5-flash-lite・試行1回・安全候補2/3案なのでpartial_safeと再分類できる。focused pytest **2 passed**、py_compileとdiff検査成功。|

最新ID行: 293。累計: PASS216 / FAIL13 / FIXED44 / BLOCKED5 / NOT_TESTED15。品質009の実生成手動FAILは未解決。実Gemini APIは0回。|

| T294 | 評価ランナー変更後の全pytestと構文検査 | Windows 11、Firefox UIを含むpytest、Python/JavaScript構文、diff検査 | PASS | 最終ローカル状態で全pytest **765 passed in 106.62s**、失敗/skipなし。Firefox UIテストを含む。py_compileでapp.pyと関連スクリプト成功、node --check app.js成功、git diff --check成功。実Gemini APIは0回。SHA 9863edeのActionsは成功だが、次の変更を含む最新SHA ActionsはPush後に確認する。|

最新ID行: 294。累計: PASS217 / FAIL13 / FIXED44 / BLOCKED5 / NOT_TESTED15。品質009の実生成手動FAILは未解決。|

| T295 | 品質記録にreply_moveを保持し、秘密らしい候補を非保存 | pytest / 保存関数のユニット試験 | FIXED | 新規記録では各候補のlabel・reply_move・textを保存し、認証情報検出時は候補メタデータと本文をともに保存しない。品質009の既存JSONは変更していない。focused runner suite **3 passed**。コードレビューで未解決指摘なし。|

最新ID行: 295。累計: PASS217 / FAIL13 / FIXED45 / BLOCKED5 / NOT_TESTED15。QUALITY009の実生成文面FAILは未解決。今回Gemini APIは0回。|

| T296 | QUALITY009の映画回答フィクスチャからテスト注記を除去 | pytest / 架空データフィクスチャ検査 | PASS | 本人の架空回答を「最近は『青い灯台』を観ました」に整え、会話文にメタ注記「架空作品」が混入しないことを検査。修正前の回帰テストは失敗し、修正後focused suite **4 passed**、全pytest **766 passed in 104.03s**。これはテストデータの品質確認であり、Geminiの生成品質を確認したものではない。|

最新ID行: 296。累計: PASS218 / FAIL13 / FIXED45 / BLOCKED5 / NOT_TESTED15。実Gemini APIは0回。QUALITY009の文章手動FAILは未解決。|

| T297 | 最近の旅行回答の場所・行動・時期・確実性を照合 | Windows 11 / pytest、旅行回答スコープのユニット・TestClient検証 | FIXED | 架空の回答で修正前の誤認「東京が好きです 先週映画に行きました」を再現。地名と移動動作が離れた回答、数年前・学生時代・幼少期の旅行、疑問形、推量、後置否定、記憶の曖昧さ、映画/会議/ハイキングへの外出、旅行についての会話や計画を未確認として扱い、先週の北海道旅行・最近の沖縄旅行・金沢への旅行・札幌への帰省・北海道からの帰着は確認できることを検証。過去会話の根拠経路は、確実な旅行行動と時期が同じ叙述にある場合のみ有効。focused pytest **35 passed**。Gemini実APIは0回。|

| T298 | 旅行回答の誤認修正後の全pytest・構文確認 | Windows 11 / pytest、Firefox UIテストを含む全回帰 | PASS | 最終作業コードで`python -m pytest -q`: **797 passed in 105.70s**。失敗・skipなし。`python -m py_compile app.py tests/test_app.py`、`node --check app.js`、`git diff --check`も成功。実Gemini APIは0回。PR ActionsはPush後に確認。|

最新ID行: 298。暫定累計: PASS219 / FAIL13 / FIXED46 / BLOCKED5 / NOT_TESTED15。QUALITY009実生成の手動品質FAILは未解決。|

| T299 | 別イベント時期・過去/否定経験形・第三者旅行を本人の最近の旅行に誤帰属しない | Windows 11 / pytest、架空の本人回答でユニット・TestClient検証 | FIXED | 別イベント時期の誤結合、`ことあります`/`経験はありません`等の経験形、友人・上司・先生・氏名の第三者旅行を再現。修正前FAILを確認。述語境界、過去経験形、第三者主語と直結する既知の旅行先＋行動を検証し、関係節（住む/働く/紹介する/勧める）と本人も同行した明記を有効対照として保持。focused suite **52 passed**。最新コードの全pytest実行中。Gemini 0回。|

最新ID行: 299。暫定累計: PASS219 / FAIL13 / FIXED47 / BLOCKED5 / NOT_TESTED15。QUALITY009実生成の手動品質FAILは未解決。|

| T300 | 旅行実績の本人帰属・時期引き継ぎ・目的地表現の誤判定を防ぐ | Windows 11 / pytest、架空プロフィール回答による単体・TestClient検証 | FIXED | 修正前に第三者の後置主語、伝聞、第三者旅行への本人の誤結合、同日旅行の取りこぼし、目的地補助表現の取りこぼしを再現。後置帰属・伝聞を未確認扱いにし、直近の同日表現は先行する最近の旅行に限って引き継ぐ。本人の別旅行を後続の第三者旅行が打ち消さない。旅行関連focused suite **73 passed**。最新全pytest **844 passed in 114.10s**、Firefox UIテストを含む。py_compile、
ode --check app.js、git diff --check成功。実Gemini API 0回。|

最新ID行: 300。累計: PASS219 / FAIL13 / FIXED48 / BLOCKED5 / NOT_TESTED15。品質009の実生成文面FAILは未解決のため総合NO-GO。|

| T301 | カフェの一般的な好みと雰囲気の好みを区別し、直接質問へ本人の回答を返す | Windows 11 / pytest、架空プロフィールと一時回答の単体検証 | FIXED | 「カフェは好き」という回答だけで「どんな雰囲気のカフェが好きか」が確認済みになる失敗を修正前に再現。否定極性の矛盾、相手の好みへのすり替え、反応だけ、質問だけ、希望・興味を確定好みに拡張する候補を拒否。二重否定・「好きというより」比較表現を曖昧として確認へ回し、並列スタイルの極性を分離し、同一スタイルの相反する限定は未確定にする。丁寧な否定「好みではありません」「好きではありません」と同系統表現も確認。focused **5 passed / 758 deselected**。最新全pytest **846 passed in 112.64s**（Firefox UI込み、失敗・skipなし）。py_compile、node --check app.js、git diff --check成功。Gemini実API 0回。|

最新ID行: 301。累計: PASS219 / FAIL13 / FIXED49 / BLOCKED5 / NOT_TESTED15。QUALITY009実生成の手動品質FAILは未解決。|

| T302 | 生成前に本文の日本語表記・文法を読み直す共通プロンプト要件 | Windows 11 / pytest、first/reply/followup/likeのprompt loaderを確認 | FIXED | 全4モードの共通プロンプトに誤変換・助詞抜け等の最終読み直しと、校正時に事実を足さない指示を追加。`test_all_sendable_modes_require_a_final_language_quality_readthrough` **1 passed**。最終全pytest **847 passed in 118.15s**（Firefox UI込み、失敗・skipなし）。Python/JavaScript構文、diff検査成功。これはプロンプト継承の静的確認であり、Gemini実生成の文章品質を立証しない。実Gemini 0回。|

最新ID行: 302。累計: PASS219 / FAIL13 / FIXED50 / BLOCKED5 / NOT_TESTED15。品質009の実生成手動FAILは未解決。|

| T303 | 最近観た映画への直接質問で安全な回答を保ち、回避する代替案だけを除外する | Windows 11 / pytest、隔離されたSuggestionsV2候補選別の架空データ試験 | FIXED | 品質009の保存済み出力で推奨案は回答、代替案2件は最近の作品名を答えず別の質問へ移っていた。現行フィルターが確認済みの作品名回答を残し、未回答の代替案2件だけを除外して不足通知を返す回帰を追加。focused **1 passed / 764 deselected**。最新全pytest **848 passed in 113.98s**（Firefox UI込み、失敗・skipなし）。Python/JavaScript構文、diff検査成功。Gemini実API0回。|

最新ID行: 303。累計: PASS219 / FAIL13 / FIXED51 / BLOCKED5 / NOT_TESTED15。品質009の実生成手動FAILは未解決。|

| T304 | 最新コード・仕様書コミットのGitHub Actions（Push・PR） | GitHub Actions実行ログをSHA照合 | PASS | コードSHA `532634105d9d7204aed931e36fe63b3541ad4fa3` のPush [38716723005](https://github.com/kenkyu0909/aichatapp/actions/runs/38716723005)・PR [38716730421](https://github.com/kenkyu0909/aichatapp/actions/runs/38716730421)、その後の仕様書のみのSHA `b76b8a3620b6c05dbc4017646268dd94c3f47f76` のPush [38717510713](https://github.com/kenkyu0909/aichatapp/actions/runs/38717510713)・PR [38717516553](https://github.com/kenkyu0909/aichatapp/actions/runs/38717516553) がすべてsuccess。各実行でpytest、Firefox確認ステップ、JavaScript構文チェック、結果Artifactアップロードが成功。|

最新ID行: 304。累計: PASS220 / FAIL13 / FIXED51 / BLOCKED5 / NOT_TESTED15。品質009の実生成手動FAILは未解決。|

| T305 | 品質009の保存済み実Gemini候補を現行フィルターで再生 | 架空の保存済みJSONを隔離バックエンドへ入力するオフラインpytest | FIXED | 原文を変更せず、現行`filter_safe_candidates`へ再投入。誤字、最近の映画への直接質問を避ける案、未確認の本人趣味、相手の不安を軽視する案がそれぞれ除外され、安全候補が残ることを確認。実Gemini通信は0回。focused suite **5 passed / 765 deselected**。全pytest **849 passed in 108.16s**（Firefox UIを含み失敗・skipなし）。|

最新ID行: 305。累計: PASS220 / FAIL13 / FIXED52 / BLOCKED5 / NOT_TESTED15。品質009の保存済み文章品質手動FAIL・意味的候補多様性はなお未解決。|

| T306 | 本人プロフィールに明記されたカフェの雰囲気を直接回答する候補 | 架空プロフィールを使うFastAPIバックエンドのpytest | FIXED | `favorite_places`に「落ち着いた雰囲気のお店が好きです」とある場合、直接回答「落ち着いた雰囲気が好きなんです！」を現行フィルターが通すことを確認。対照として、逆の比較表現とプロフィールにない週次頻度を引き続き除外。修正前は直接回答を誤って除外。focused cafe tests **3 passed / 763 deselected**。全pytest **850 passed in 110.92s**。Gemini実通信0回。|

最新ID行: 306。累計: PASS220 / FAIL13 / FIXED53 / BLOCKED5 / NOT_TESTED15。QUALITY009の実生成手動FAIL・意味的候補多様性はなお未解決。|

| T307 | Firefox実UI回帰（Console・first/質問・サーバー停止復帰・改行コピー保存・APIエラー） | `python -m pytest -q tests/test_ui_firefox.py`、Firefox上のブラウザー自動操作 | PASS | Firefoxで実画面を操作する6ケースが成功（**6 passed in 84.73s**）。表示、JavaScript例外監視、候補改行の表示・コピー・履歴保存、サーバー停止/再起動、情報確認UI、エラー状態を確認。Chrome不使用。|

最新ID行: 307。累計: PASS221 / FAIL13 / FIXED53 / BLOCKED5 / NOT_TESTED15。QUALITY009の実生成手動FAIL・意味的候補多様性はなお未解決。|

| T308 | カフェ好み修正コミットのGitHub Actions（Push・PR） | Actionsログで対象SHAとジョブ結果を照合 | PASS | `25f365fab245e83a46bd9f4236921429f3069639`を対象とするPush [38719831848](https://github.com/kenkyu0909/aichatapp/actions/runs/38719831848)とPR [38719837338](https://github.com/kenkyu0909/aichatapp/actions/runs/38719837338)がsuccess。pytest、Firefox確認、JavaScript構文、Artifacts保存に成功。PR #4はOPEN/Draft。|

最新ID行: 308。累計: PASS222 / FAIL13 / FIXED53 / BLOCKED5 / NOT_TESTED15。最新コードコミットのActionsは成功。品質009の実生成手動FAIL・意味的候補多様性はなお未解決。|

| T309 | 保存済み候補に`reply_move`がない場合の多様性通知 | 架空の候補を使ったバックエンドpytestと保存済みQUALITY009の再生 | FIXED | 未記録の方針を既定値`react`として重複警告に数える問題を修正。明示された方針だけを比較し、ラベル欠落は推測しない。2つ以上の明示ラベルが重複する場合は、ほかの案のラベルが欠けていても通知する。最新focused tests **2 passed / 765 deselected**。全pytest **851 passed in 103.89s**（Firefox UI込み）。Firefox専用UI **6 passed in 83.77s**。Gemini実通信0回。|

最新ID行: 309。累計: PASS222 / FAIL13 / FIXED54 / BLOCKED5 / NOT_TESTED15。QUALITY009の生成文章自然さ・意味的多様性はなお未解決。|

| T310 | 最新候補方針修正のGitHub Actions（Push・PR） | Actionsログで対象SHA・Push・PR結果を照合 | PASS | SHA `2ec2f11c51078096170a46d4543f5b6975553dad`のPush [38721061798](https://github.com/kenkyu0909/aichatapp/actions/runs/38721061798)・PR [38721069405](https://github.com/kenkyu0909/aichatapp/actions/runs/38721069405)がともにsuccess。両方でbackend tests、Firefoxチェック、JavaScript構文検査、Artifacts保存が成功。PR #4 OPEN/Draft。|

最新ID行: 310。累計: PASS223 / FAIL13 / FIXED54 / BLOCKED5 / NOT_TESTED15。|

| T311 | 部分的な`reply_move`重複修正のGitHub Actions（Push・PR） | Actionsログで最新SHA・Push・PR結果を照合 | PASS | SHA `18c29a6d35705e392bb7258ef218f6960c505257`のPush [38722645521](https://github.com/kenkyu0909/aichatapp/actions/runs/38722645521)・PR [38722651123](https://github.com/kenkyu0909/aichatapp/actions/runs/38722651123)がsuccess。両方でpytest、Firefoxチェック、JavaScript構文検査、Artifacts保存に成功。PR #4 OPEN/Draft。|

最新ID行: 311。累計: PASS224 / FAIL13 / FIXED54 / BLOCKED5 / NOT_TESTED15。QUALITY009の実生成品質FAILは継続。|


| T312 | 映画館に関する本人確認質問の意図・範囲 | 架空の質問文を使ったpytest（正常系と誤判定対照） | FIXED | 映画館の利用経験・頻度・雰囲気・行きつけ場所を区別し、対応する一時確認質問を返す。映画館自体の所在地を尋ねる質問を本人情報確認に誤分類しない。本人情報の確認範囲も一致させる。重点65 passed / 774 deselected、関連199 passed / 647 deselected、全pytest930 passed。Python/JavaScript構文検査とdiff check成功。Firefox UIは全pytest内で実行。モック・ローカル検証のみ、Gemini実通信0回。Actionsは未実行。|

最新ID行: 312。累計: PASS224 / FAIL13 / FIXED55 / BLOCKED5 / NOT_TESTED15。QUALITY009の実生成品質FAILは継続。

| T313 | invite_gently後に安全な誘い候補が生成されない場合の方針・段階整合性 | 架空会話を使うFastAPIバックエンドpytest（準備済み/未準備の両条件） | FIXED | Geminiが`invite_gently`を返しても、許可された再生成後に安全な誘い候補がない場合は方針と段階を安全候補へ合わせて降格する。準備済みなら`consider_invite` / Stage 3、未準備なら`continue_conversation` / Stage 2。安全な既存候補は保持。方針修正のfocused tests **4 passed**。段階不一致の回帰は修正前2 failed、修正後2 passed。最終全pytest **932 passed in 113.98s**（Firefox UI込み）。Gemini実通信0回。最新SHAのActions確認待ち。|

最新ID行: 313。累計: PASS224 / FAIL13 / FIXED56 / BLOCKED5 / NOT_TESTED15。QUALITY009の実生成自然さ・候補方針多様性FAILは未解決。

| T314 | 誘い方針の安全候補同期修正に対する最新HEADのGitHub Actions | Push/PR Actionsのhead SHA・ジョブ結果を照合 | PASS | SHA `a8ceaa1d5d7cb7948186812c627abc5ed930fdf7`のPush [38729897573](https://github.com/kenkyu0909/aichatapp/actions/runs/38729897573)・PR [38729902486](https://github.com/kenkyu0909/aichatapp/actions/runs/38729902486)がsuccess。backend pytest、Firefox確認、JavaScript構文検査、Artifactアップロードに成功。PR #4はOPEN/Draft、head SHA一致。|

最新ID行: 314。累計: PASS225 / FAIL13 / FIXED56 / BLOCKED5 / NOT_TESTED15。QUALITY009の実生成自然さ・候補方針多様性FAILは未解決。

| T315 | 品質方針修正後のFirefox主要UI回帰 | `python -m pytest -q tests/test_ui_firefox.py`。Firefox実ブラウザー操作 | PASS | コードSHA `a8ceaa1d5d7cb7948186812c627abc5ed930fdf7`、同コードを含むHEAD `331b61f1c09a7ca092cf170551c5cd440bde3182`。Firefox UI **6 passed in 82.61s**。既存の主要画面操作・ブラウザー例外監視を実行。Chrome不使用、Gemini実通信0回。|

| T316 | 保存済みQUALITY009出力を現行安全フィルターで再生 | `python -m pytest -q tests/test_quality_checks_009.py`。架空の過去出力を隔離バックエンドへ投入 | PASS | コードSHA `a8ceaa1d5d7cb7948186812c627abc5ed930fdf7`。**5 passed in 0.33s**。保存済みの元文章は変更せず、安全候補を残し問題候補を理由付きで除外する回帰を確認。Gemini実通信0回。モデル文章の自然さ・意味的多様性全般の解決を示すものではない。|

最新ID行: 316。累計: PASS227 / FAIL13 / FIXED56 / BLOCKED5 / NOT_TESTED15。QUALITY009の実生成自然さ・候補方針多様性FAILは未解決。

| T317 | 会話段階同期修正と検証資料の最新HEADに対するGitHub Actions | Push/PR Actionsログのhead SHA・pytest・Firefox・JS検査を確認 | PASS | コードSHA `058ec382c8d734a5273d33af1bbf93609cefa61f`のPush [38731667450](https://github.com/kenkyu0909/aichatapp/actions/runs/38731667450)・PR [38731677887](https://github.com/kenkyu0909/aichatapp/actions/runs/38731677887)がsuccess。検証資料HEAD `5081dcaf7acddceef30b09b3aeb4cd7b6380e954`のPush [38731751338](https://github.com/kenkyu0909/aichatapp/actions/runs/38731751338)・PR [38731758965](https://github.com/kenkyu0909/aichatapp/actions/runs/38731758965)もsuccess。各runでbackend tests、Firefox準備、JavaScript構文検査、Artifact upload成功。PR #4はOPEN/Draft。|

最新ID行: 317。累計: PASS228 / FAIL13 / FIXED56 / BLOCKED5 / NOT_TESTED15。QUALITY009の実生成自然さ・候補方針多様性FAILは未解決。


| T318 | Firefoxで初回生成から返信・コピー・手動記録・履歴・再読込までの一連操作 | `python -m pytest -q tests/test_ui_firefox.py::test_firefox_first_to_reply_copy_manual_record_and_history_flow` および全pytest | PASS | Windows上のFirefox実ブラウザー。架空の「あおい」、一時DB、Gemini APIモックを使用。コピーのみでは会話に追加されず、手動記録後に履歴・再読込で改行を含む本文が保持され、first/replyモード、JS runtime/consoleエラーなしを確認。レビュー指摘反映後の対象テスト1 passed in 11.39s、全pytest933 passed in 123.63s（Firefox UIを含む）。レビュー前のFirefox UI全体7 passed in 90.08s。実Gemini通信0回。Chrome不使用。|

最新ID行: 318。累計: PASS229 / FAIL13 / FIXED56 / BLOCKED5 / NOT_TESTED15。保存済みQUALITY009の実生成自然さ・候補方針多様性FAILは未解決。

| T319 | 本人への直接質問に対する確認済み回答の範囲・追加事実・矛盾の安全検査 | `python -m pytest -q`。架空プロフィールと一時回答を使うFastAPI/フィルター回帰 | FIXED | Windows、Python 3.12、Firefoxを含む全pytest **949 passed in 125.37s**。本人への確認済み回答以外に予定・場所・習慣・経験・別の好みを足す候補、肯定/否定の矛盾を送信可能にしない。安全な確認済み回答と相手への関連質問は維持し、安全候補が減る場合は候補不足を通知。focused tests **15 passed, 849 deselected**。`py_compile`、`node --check app.js`、`git diff --check`も成功。Gemini実通信0回。QUALITY009の自然さ/意味的候補多様性は未解決。変更SHA `691999ad4f5238f233107688ffb75bbed3b1090e`。|

最新ID行: 319。累計: PASS229 / FAIL13 / FIXED57 / BLOCKED5 / NOT_TESTED15。保存済みQUALITY009の実生成自然さ・候補方針多様性FAILは未解決。
最新T319コードSHA `691999ad4f5238f233107688ffb75bbed3b1090e`を対象にしたGitHub Actions: Push [38737598550](https://github.com/kenkyu0909/aichatapp/actions/runs/38737598550) とPR [38737604331](https://github.com/kenkyu0909/aichatapp/actions/runs/38737604331)がともにsuccess。両runでbackend pytest、JavaScript構文検査、test artifact upload成功。|

| T320 | 保存済みQUALITY009の買い物傾向回答から未確認の性格を推定する候補を遮断 | 架空プロフィール・一時回答を使ったFastAPIフィルターpytest、QUALITY009保存出力の再生、全pytest | FIXED | 修正前に実出力候補「けっこう慎重なほうかもしれません」を再現。買い物傾向の明示根拠だけを使用し、無関係なプロフィール欄、AI生成履歴、否定/対比、候補と本人回答の極性不一致、相反する確定情報では候補を通さない。安全な確認済み候補は保持し、不足通知を行う。肯定/否定・句分割・無接尾断定形・慎重派・短文断片を含むfocused tests **23 passed**。全pytest **972 passed in 120.06s**（Firefox UI込み）。`py_compile`、`node --check app.js`、`git diff --check`成功。Gemini実通信0回。SHA `de93027d1b3b9206df92f14dd22375faec492f59`。同SHAのPush Actions [38742628326](https://github.com/kenkyu0909/aichatapp/actions/runs/38742628326) とPR Actions [38742640254](https://github.com/kenkyu0909/aichatapp/actions/runs/38742640254)はいずれもsuccessでhead SHA一致。各runでpytest、Firefox準備、JavaScript構文検査、Artifact保存が成功。日本語意味判定は列挙形式の保守的な検査であり、あらゆる表現の網羅を示さない。|

最新ID行: 320。累計: PASS229 / FAIL13 / FIXED58 / BLOCKED5 / NOT_TESTED15。保存済みQUALITY009の実生成自然さ・意味的候補多様性FAILは未解決。

### 2026-10-15 21:52 JST 追補：最新コードSHAのGitHub Actions

- T319のコード/test SHA `691999ad4f5238f233107688ffb75bbed3b1090e`を対象に、Push [Actions 38737598550](https://github.com/kenkyu0909/aichatapp/actions/runs/38737598550) とPR [Actions 38737604331](https://github.com/kenkyu0909/aichatapp/actions/runs/38737604331) が両方success。pytest、JavaScript構文検査、Artifact保存に成功。
- PR #4はOPEN/Draft、head SHAは `691999ad4f5238f233107688ffb75bbed3b1090e`。未マージ。
- 次: 検証資料をこのCI証拠とともにPushし、品質009の実出力から直接質問に答えない候補・意味的に似た候補の残存経路を調べる。会話004、新規会話HTML、Gemini実通信は行わない。

| T321 | V2候補の意味的重複を一度だけ修復し、安全な候補と生成元を保つ | 架空データのGemini SDKモックで重複案、部分的に安全な再生成、429切替、試行上限、不要な本人確認質問を再現。`python -m pytest -q tests/test_app.py -k 'diversity or repeated_reply_purposes or all_unsafe_retry or unnecessary_questions'` | FIXED | Windows / Python 3.12 / FastAPI TestClient。実API不使用。Focused **9 passed, 886 deselected in 2.09s**。最新全pytest **980 passed in 116.15s**（Firefox UIテストを含む）。`py_compile`、`node --check app.js`、`git diff --check`成功。候補修復は最大1回。安全候補を保持し、不足・意味的類似の通知を残す。429時の後続プロバイダーや上限到達時も、返却候補の実際のAPI別名・モデルを記録する。QUALITY009の実Gemini文章品質FAIL全般を解決した証拠ではない。コミット `3df1847fcadf8f1ea811d84176ca275861310a6c`。Push Actions [38748340047](https://github.com/kenkyu0909/aichatapp/actions/runs/38748340047)、PR Actions [38748347116](https://github.com/kenkyu0909/aichatapp/actions/runs/38748347116) は記録時点で実行中。|

| T322 | 候補多様性修正コードのPush/PR Actions | `gh run view`でrunのhead SHA、結論、ジョブを確認 | PASS | コードSHA `3df1847fcadf8f1ea811d84176ca275861310a6c`のPush [38748340047](https://github.com/kenkyu0909/aichatapp/actions/runs/38748340047)とPR [38748347116](https://github.com/kenkyu0909/aichatapp/actions/runs/38748347116)はいずれもsuccess、head SHA一致。pytest、Firefox準備、JavaScript構文検査、テスト結果Artifactアップロードに成功。Gemini実通信0回。|

最新ID行: 322。累計: PASS230 / FAIL13 / FIXED59 / BLOCKED5 / NOT_TESTED15。QUALITY009の実生成自然さ・意味的候補多様性FAILは未解決。

| T323 | ペット情報の根拠・対象者・極性・確度の分離 | 友人/同僚や母/父を区別する架空プロフィール・会話のFastAPI候補フィルターpytest | FIXED | 未確認の第三者情報、関係性や親族の取り違え、曖昧/伝聞/仮定情報、後続訂正、否定された飼育歴を再現。関連pet focused tests **18 passed**。最新全pytest **1002 passed in 128.39s**（Firefox UI込み）。Python compile・JS構文・diff検査成功。Gemini実API不使用。日本語すべてを網羅する保証ではない。|
| T324 | QUALITY009の休息・慰労共感候補の意味的重複通知 | 保存済みの`joke_mirroring`実出力2候補を多様性判定・安全フィルターへ再生するpytest | FIXED | 修正前は「ゆっくり休めましたか？」と「体を休めるのも大事ですね」が多様性不足として検出されなかった。休息・慰労の共感が重なる場合は候補を残したまま不足通知を表示する。修正前テスト**1 failed**、修正後focused tests **2 passed**。全pytest **1002 passed in 128.39s**。Gemini実API不使用。これは警告検出であり、モデル文章自体の品質改善を示さない。|
| T325 | ペット飼育の婉曲な否定・留保を肯定根拠にしない | 架空プロフィールの`とは言えない`・`とは限らない`を使ったFastAPI候補フィルターpytest | FIXED | 独立レビューで「犬を飼っているとは言えない」を肯定飼育の根拠にしうる問題を確認。該当表現を確定根拠から除外し、肯定候補を拒否する回帰を追加。後続の口語否定形テストも含むpet focused tests **18 passed**、全pytest **1002 passed in 128.39s**。Python/JS構文検査成功。Gemini実API不使用。|
| T326 | 複数の動物を含む飼育・好みの極性を個別に判定 | 一文内の犬/猫の肯定・否定を分けるFastAPI候補フィルターpytest | FIXED | 初回の再現テストは**1 failed**。動物と述語の間を最短一致にし、各動物に対応する述語区間だけで肯定/否定を判定する。犬だけの根拠で猫の好みを述べる候補を拒否し、両方の根拠がある候補は保持。pet focused tests **18 passed**、全pytest **1002 passed in 128.39s**。独立コードレビューで修正を確認。Gemini実API不使用。|
| T327 | ペット根拠修正のPush/PR GitHub Actions | `gh run view`でPush/PRの実行SHAと結果を照合 | PASS | HEAD `518d1a7fc6d6d7bf35cea667ae11e5de5fd992ef`を対象とするPush [38758432156](https://github.com/kenkyu0909/aichatapp/actions/runs/38758432156)とPR [38758438161](https://github.com/kenkyu0909/aichatapp/actions/runs/38758438161)がsuccessし、両方のhead SHA一致。pytest・JavaScript構文検査・テストArtifact保存成功。警告: ActionsがNode.js 20互換に関する通知と、`ubuntu-latest`の今後のイメージ移行通知を表示。|

最新ID行: 327。累計: PASS231 / FAIL13 / FIXED63 / BLOCKED5 / NOT_TESTED15。保存済みQUALITY009の実生成自然さ・候補間の意味的多様性は一部未解決で、総合判定NO-GO。

| T328 | 保存済みQUALITY009の休息共感重複ペアを返信生成APIで一度だけ再修復 | `python -m pytest -q tests/test_app.py -k 'repeated_rest_empathy_from_quality009 or quality009_rest_empathy_pair_triggers_one_diversity_repair'` と全pytest | FIXED | Windows / Python 3.12 / FastAPI TestClient / Gemini SDKモック。QUALITY009の実出力2候補を再現入力として使用。重複候補検知後に専用指示を付けた再生成が1回だけ行われ、異なる安全候補3案を返し、旧2案を再利用しないことを確認。focused **2 passed, 916 deselected**。全pytest **1003 passed in 130.78s**（Firefox UI込み）。Gemini実通信0回。これは修復経路のオフライン確認であり、生成品質の改善を実証しない。SHA `8f18f2a364b5fa579938190d219e21d7beea6078`のPush Actions [38760638954](https://github.com/kenkyu0909/aichatapp/actions/runs/38760638954)とPR Actions [38760649322](https://github.com/kenkyu0909/aichatapp/actions/runs/38760649322)は両方successし、head SHA一致。|

最新ID行: 328。累計: PASS231 / FAIL13 / FIXED64 / BLOCKED5 / NOT_TESTED15。保存済みQUALITY009の実生成自然さ・意味的候補多様性FAILは残り、総合判定NO-GO。

| T329 | 「もう少し仲良く/メッセージしてから」という延期表現の後に、即時再勧誘を拒否 | `python -m pytest -q tests/test_app.py -k 'wants_more_conversation_before_meeting or general_positive_message_about_getting_along or explicit_wait_before_meeting or soft_reinvitation_after_refusal or explicit_reconsideration or refusal_filter_keeps_neutral_candidate'` と全pytest | FIXED | Windows / Python 3.12 / 架空会話・FastAPI候補安全判定。修正前に「もう少し仲良くなってから」「もう少しメッセージしてから」の3表現を拒否状態として扱わず、再勧誘候補が阻止されないことを再現（3 failed）。待つ表現と条件付きの前向き表現「もう少し仲良くなってから一緒に行けたらうれしいです」は延期として即時再勧誘を止める一方、一般的な肯定「もっと仲良くなれたらうれしいです」は拒否扱いしないよう判定とテストを追加。focused **17 passed, 906 deselected**。全pytest **1008 passed in 131.85s**（最後の条件付きケースを含み、Firefox UI込み）。`py_compile`、`node --check app.js`、`git diff --check`成功。Gemini実通信0回。 T329の旧コミット`9d64e15990d83fec52477d9934450644214c69b6`のPush [Actions 38762044607](https://github.com/kenkyu0909/aichatapp/actions/runs/38762044607)とPR [Actions 38762147748](https://github.com/kenkyu0909/aichatapp/actions/runs/38762147748)はsuccessしSHA一致。ただしT330の追加対照ケースより前のCIである。|

最新ID行: 329。累計: PASS231 / FAIL13 / FIXED65 / BLOCKED5 / NOT_TESTED15。保存済みQUALITY009の実生成自然さ・意味的候補多様性FAILは未解決、総合判定NO-GO。

| T330 | 延期表現の口語差を認識し、単なる会話希望を拒否と誤判定しない | `python -m pytest -q tests/test_app.py -k 'wants_more_conversation_before_meeting or general_positive_message_about_getting_along or explicit_wait_before_meeting or soft_reinvitation_after_refusal or explicit_reconsideration or refusal_filter_keeps_neutral_candidate'` と全pytest | FIXED | Windows / Python 3.12 / 架空会話。修正前に「もうちょっと話してから」「もうちょっとやり取りしてから」を延期として認識しないことを再現。最初の拡張案が「もう少し仲良くしたい」「もう少し話したいことがある」も拒否扱いする過剰判定を発見し、修正前失敗として記録。パターンを「してから／なってから」に限定し、条件付き延期は即時再勧誘を止める一方、一般的な会話希望は拒否扱いしない。focused **21 passed, 906 deselected**。全pytest **1012 passed in 131.45s**（Firefox UI込み）。Pythonレビューで誤判定の残存指摘なし。構文・差分検査成功。実Gemini通信0回。|

最新ID行: 330。累計: PASS231 / FAIL13 / FIXED66 / BLOCKED5 / NOT_TESTED15。過去QUALITY009の実生成自然さ・意味的候補多様性FAILは解消していないため総合NO-GO。

| T331 | 延期表現境界修正の最新SHAに対するGitHub Actions Push/PR | `gh run view`でrun結果、head SHA、ジョブとpytestログを確認 | PASS | SHA `af1038c636341595c1d0eedbf443d72568fd0a6c`のPush [Actions 38763118050](https://github.com/kenkyu0909/aichatapp/actions/runs/38763118050)とPR [Actions 38763126584](https://github.com/kenkyu0909/aichatapp/actions/runs/38763126584)がともにsuccessし、head SHA一致。両方ともpytest **1012 passed**、Firefox 157準備、JavaScript構文検査、結果Artifact保存に成功。Gemini実通信0回。PR #4 OPEN/Draft。|

最新ID行: 331。累計: PASS232 / FAIL13 / FIXED66 / BLOCKED5 / NOT_TESTED15。QUALITY009の実生成自然さ・意味的候補多様性FAILは残るため総合NO-GO。

| T332 | 句読点を省いた口語の本人質問と平叙表現の切り分け | `python -m pytest -q tests/test_app.py -k 'unknown_nonpersonal_question_is_not_misclassified_as_user_fact_question or colloquial_personal_questions_require_matching_user_confirmation or unpunctuated_movie or movie_user_question_matches_asked_experience_scope'` | FIXED | Windows 11 / Python 3.12 / FastAPIモック、架空の質問文。修正前は「音楽何聴く」が本人確認を迂回する一方、「誰でも行く」「どんな本でも読む」「どこにだって行く」等を質問と誤認。直接質問は確認質問へ誘導し、今回レビューで見つかった一般的な平叙形は `None` にする分岐と回帰ケースを追加。映画の否定疑問も確認質問として保つ。Focused **70 passed, 861 deselected**、最終全pytest **1017 passed in 137.53s**（Firefox UI込み）。`py_compile`、`node --check app.js`、`git diff --check`成功。Gemini通信0回。コードレビューでは最終の平叙/疑問境界で明確な問題なし。|
| T333 | 返信候補を生成した相手と異なる相手への送信記録を拒否 | `python -m pytest -q tests/test_ui_firefox.py::test_firefox_stale_candidate_cannot_be_recorded_after_switching_match` と全pytest | PASS | Windows 11 / Python 3.12 / Firefox Selenium、架空の「あおい」「ゆき」。相手Aの候補記録確認中にBへ切替後、Aの候補を送信扱いにできず、両方の画面履歴・API/SQLite履歴が維持されること、Firefox runtime/console errorがないことを確認。Focused **1 passed**、最終全pytest **1017 passed**。Gemini通信0回。|

| T334 | Firefoxで追いメッセージ候補のコピー・未送信状態・手動記録・改行付き再読込 | `python -m pytest -q tests/test_ui_firefox.py::test_firefox_followup_copy_and_manual_record_preserve_multiline_history` と全pytest | PASS | Windows 11 / Python 3.12 / Firefox Selenium、架空の「さくら」。followupモードをUIから呼び、2行の候補本文・`pre-wrap`表示・コピーのみでは履歴不変・明示的記録後の発言者順と改行保持・再読込後のSQLite/API/UI履歴一致を確認。操作中と再読込後のFirefox runtime/console errorを別々に確認。Focusedは最終編集後 **2 passed**（T334/T335）、全pytest **1019 passed in 159.21s**（最後のtoast待機強化より直前。強化後はfocused再実行成功）。Gemini通信0回。|
| T335 | Firefoxでマッチ前いいね候補のコピーが送信履歴を変更しない | `python -m pytest -q tests/test_ui_firefox.py::test_firefox_like_candidate_can_be_copied_without_creating_match_history` と全pytest | PASS | Windows 11 / Python 3.12 / Firefox Selenium、架空の「りお」。likeモードのpayloadとmatch_id未指定、候補コピー、送信記録操作が存在しないこと、DB/API/画面履歴がコピー・モーダル終了・再読込後も空であることを確認。操作中と再読込後のFirefox runtime/console errorを別々に確認。Focusedは最終編集後 **2 passed**（T334/T335）、全pytest **1019 passed in 159.21s**（最後のtoast待機強化より直前。強化後はfocused再実行成功）。Gemini通信0回。|

| T336 | Firefox followup / like追加後のコミットでPush・PR CIが同じHEADで成功 | `gh run view`とGitHub Actionsのpytest/Nodeログ | PASS | Windows 11ローカルで作業SHA `528d101a50b5b853ddf5044d1a5441aff64ceddb`をPush。Push run [38770088351](https://github.com/kenkyu0909/aichatapp/actions/runs/38770088351)とPR run [38770097358](https://github.com/kenkyu0909/aichatapp/actions/runs/38770097358)がともにsuccessし、両方のhead SHAが一致。Actions pytest **1019 passed, 1 warning**、Firefox準備・JS構文検査・artifact upload成功。PR #4 OPEN/Draft。|
| T337 | Firefoxでプロフィールを保存しfirst/reply生成時と再読込後に保持 | `python -m pytest -q tests/test_ui_firefox.py::test_firefox_saved_profile_is_available_during_first_and_reply_generation`、全pytest | PASS | Windows 11 / Firefox / 隔離SQLite / 架空人物「ひなた」「なな」。UIからプロフィールを保存し、first/replyモードで生成UIを操作。生成API呼出し直前にprofile endpointの保存内容が読み取れること、候補3件表示、送信記録、再読込後のプロフィール・履歴維持を確認。生成エンドポイントはモックのため、実Gemini品質・実際のサーバー側プロンプト内容は未検証。Firefox runtime/console errorなし。最終全pytest **1089 passed in 178.94s**。|
| T338 | 本人確認回答の質問範囲・事実の帰属検査 | `python -m pytest -q tests/test_app.py`と関連focused tests | FIXED | 学校在籍と専攻、職業と職種・業界・業種、複合質問の両方の回答要件、第三者・固有名・伝聞・読点区切りのカフェ好みを分けて検証。修正前の最終読点回帰ケース **1 failed, 19 passed**、修正後focused **21 passed**、全`tests/test_app.py` **1000 passed**。全pytest **1089 passed**。本人情報の確認済み回答と第三者情報を分ける検査であり、すべての日本語意味表現を完全に判定できる保証ではない。Gemini実通信0回。|
| T339 | 最新のローカル全体検証 | `python -m pytest -q`、Python compile、`node --check app.js`、`git diff --check` | PASS | Windows 11、Python 3.12、Firefox。隔離テストデータ。全pytest **1089 passed in 178.94s**。`app.py`と実験スクリプトのPython構文、JavaScript構文、差分検査も成功。Gemini実通信0回。現時点の未コミット差分はGitHub Actions未実行のため、最新HEADのCI結果は別途確認する。|

現在の集計: **339項目**（PASS238 / FAIL13 / FIXED68 / BLOCKED5 / NOT_TESTED15）。過去のQUALITY009実生成品質FAILは維持し、総合判定はNO-GO。|

最新ID行: **339**。累計: PASS238 / FAIL13 / FIXED68 / BLOCKED5 / NOT_TESTED15。最新ローカル全pytestは1089 passed。未コミット差分のActionsは未実行。過去QUALITY009の実生成品質FAILは維持し、総合NO-GO。

| T340 | 確認済みの最近の映画回答に時期・作品名の矛盾を含む候補を遮断 | 映画回答/候補フィルターpytestと全pytest | FIXED | Windows 11 / Python 3.12 / FastAPIのオフライン回帰、架空の相手質問と一時回答を使用。修正前に「前に観た」「最近ではない」等の候補が回答として通過することを再現。15種の矛盾候補（過去時期、最近ではない、作品名の否定、別作品、以外/とは別/除いて）を拒否し、同じ作品の明示的な最近の再視聴を許容、別作品の再視聴は拒否。Focused 25 passed。最終全pytest 1105 passed in 171.74s。Gemini実通信0回。全日本語意味表現を網羅する保証ではない。|
| T341 | Firefoxプロフィール保存E2Eのtoast待機フレーク修正 | 2件のFirefoxプロフィール保存E2Eと全pytest | FIXED | 同SHA cb04a58c8e9cb53d6dd5abf97de947462525f3adのPush Actions 38777573869でFirefox保存テストがtoastの一時表示を取りこぼしfailure（1 failed / 1088 passed）。同SHAのPR Actions 38777582476はsuccess。関連する二つのプロフィール保存UIテストは保存成功後に閉じるモーダル状態を待ち、APIから保存値も確認するよう変更。Firefox focused 2 passed in 20.56s。最終全pytest 1105 passed。修正HEADのGitHub Actionsは未確認。|

最新ID行: 341。累計: PASS238 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。既存QUALITY009の実生成自然さ・意味的候補多様性FAILは継続。|


### 2026-10-16 03:02 JST 同一HEADのCI確認

| T342 | 修正後の最新コミットでGitHub Actions再検証 | Push run / PR run、1105 pytest、JavaScript構文チェック | PASS | SHA `029b45fe9a2c4f98d24e1253880e09c4eed24dbc`。Push [38781778539](https://github.com/kenkyu0909/aichatapp/actions/runs/38781778539) とPR [38781788477](https://github.com/kenkyu0909/aichatapp/actions/runs/38781788477) は同一SHAでsuccess。Pushログ: 1105 passed, 1 warning in 114.85s。現在集計342項目: PASS239 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。既存実生成品質FAILは解消扱いにしない。|

最新ID行: 342。累計: PASS239 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。Actionsが確認したSHAは `029b45fe9a2c4f98d24e1253880e09c4eed24dbc`。記録更新後のSHAでも再実行して照合する。


| T343 | Firefoxでfirst/reply/followup/likeの中核操作を再確認 | Selenium Firefox、架空データ、アプリ生成モック、隔離SQLite | PASS | 4 UIテスト: `test_firefox_first_to_reply_copy_manual_record_and_history_flow`, `test_firefox_first_message_and_temporary_profile_questions`, `test_firefox_followup_copy_and_manual_record_preserve_multiline_history`, `test_firefox_like_candidate_can_be_copied_without_creating_match_history`。**4 passed in 47.17s**。コピーのみでは送信記録されず、明示記録と再読込後の履歴順/本文・改行を確認。Chrome不使用、Gemini実通信0回。現在343項目: PASS240 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|

最新ID行: 343。累計: PASS240 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|


T342の追加確認: docs-only SHA `872095d9c3accb5f6f3527632e713574e9c79700` のPush [38782221008](https://github.com/kenkyu0909/aichatapp/actions/runs/38782221008) とPR [38782228105](https://github.com/kenkyu0909/aichatapp/actions/runs/38782228105) もsuccess。コードはT342に記したSHAと同一。


| T344 | QUALITY009由来の誤字・事実根拠・既知情報・拒否・共感重複の重点回帰 | pytestの固定架空ケース、オフライン | PASS | typo rejection、未確認のshared preference拒否、既知の相手カフェ/週末情報を再質問しない判定、拒否後の中立候補維持、QUALITY009休息共感ペアの多様性検出と1回修復、最近観た映画回答の時期矛盾を含む**36 passed in 2.46s**。Gemini実通信0回。過去の実生成自然さ/候補多様性FAILを覆さない。総計344: PASS241 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|

最新ID行: 344。累計: PASS241 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|


### 2026-10-16 03:11 JST 最終記録SHAのCI

| T345 | 最終記録SHAのPush/PR Actions・全pytest・JS構文 | GitHub Actions PushとPull Request | PASS | SHA `963be64f989c53a0ef19f2114672743c738d9e30`。Push [38783196561](https://github.com/kenkyu0909/aichatapp/actions/runs/38783196561) / PR [38783205142](https://github.com/kenkyu0909/aichatapp/actions/runs/38783205142) は同一HEADでsuccess。GitHub **1105 passed / 1 warning in 113.81s**、JS syntax check成功。集計345: PASS242 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。保存済み実Gemini品質FAILは残る。|

最新ID行: 345。累計: PASS242 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|


### 2026-10-16 03:12 JST 本人確認質問と直接回答の整合

| T346 | 本人確認質問の粒度と回答後候補の質問整合性 | pytest固定架空ケース、FastAPI/モック・オフライン | PASS | `test_missing_fact_question_matches_the_specific_information_requested`, `test_movie_user_question_matches_asked_experience_scope`, `test_unpunctuated_movie_past_question_checks_the_movie_not_movie_preference`, `test_unclassified_personal_direct_question_requires_matching_user_answer`。好み/ジャンル/頻度/最近・過去の経験の区別を含む **66 passed in 2.59s**。Gemini実通信0回。現在346項目: PASS243 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|

最新ID行: 346。累計: PASS243 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|


### 2026-10-16 03:16 JST 最新報告SHAのActions

| T347 | 最新報告SHAでPush/PR Actionsを確認 | GitHub Actions、1105 pytest、JS構文検査 | PASS | SHA `473aa1e5705d6b630b8bc1cdcb195769f5cfc8fb`。Push [38783750674](https://github.com/kenkyu0909/aichatapp/actions/runs/38783750674) / PR [38783757484](https://github.com/kenkyu0909/aichatapp/actions/runs/38783757484) success、同一head。1105 passed / 1 warning in 129.75s。Matrix合計347: PASS244 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。品質009の実生成FAILは残す。|

最新ID行: 347。累計: PASS244 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|


### 2026-10-16 03:19 JST docs-only報告SHAのActions再確認

| T348 | docs-only報告SHAで最新のPush/PR Actionsを確認 | GitHub Actions Push/PR、全pytest、JS構文 | PASS | SHA `79c22f1f11f906e313d0f79b717a56663a8ab06e`。Push [38784229399](https://github.com/kenkyu0909/aichatapp/actions/runs/38784229399) / PR [38784237425](https://github.com/kenkyu0909/aichatapp/actions/runs/38784237425) success、同一HEAD。1105 passed / 1 warning in 148.17s。コードは `473aa1e` と同一。合計348: PASS245 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|

最新ID行: 348。累計: PASS245 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|


### 2026-10-16 03:23 JST 最終報告コミットのActions

| T349 | 最新の報告SHAでPush/PR Actions | GitHub Actions、pytest、JS syntax | PASS | SHA `a2a087901e6b596967e0903f4b147aa42e998ac7`。Push [38784707757](https://github.com/kenkyu0909/aichatapp/actions/runs/38784707757) / PR [38784712072](https://github.com/kenkyu0909/aichatapp/actions/runs/38784712072) success、同一HEAD。1105 passed / 1 warning in 126.15s、JS構文検査成功。349項目: PASS246 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|

最新ID行: 349。累計: PASS246 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|


### 2026-10-16 03:27 JST 最新HEAD Actions

| T350 | 最終記録HEADのPush/PR Actions、全pytest、JS構文 | GitHub Actions | PASS | SHA `1af80fb2e225eb11818354408accf9b422ab8dfa`。Push [38785310873](https://github.com/kenkyu0909/aichatapp/actions/runs/38785310873) / PR [38785319260](https://github.com/kenkyu0909/aichatapp/actions/runs/38785319260) 同一headでsuccess。1105 passed / 1 warning in 114.78s。集計350: PASS247 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|

最新ID行: 350。累計: PASS247 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|


### 2026-10-16 03:30 JST 最新報告HEAD CI

| T351 | 最新報告HEADでPush/PR Actions・全pytest・JS構文を確認 | GitHub Actions | PASS | SHA `fcfd2ed07b8337a90dcc86b3e3729c883dac3492`。Push [38785759890](https://github.com/kenkyu0909/aichatapp/actions/runs/38785759890) / PR [38785767020](https://github.com/kenkyu0909/aichatapp/actions/runs/38785767020) 同一headでsuccess。1105 passed / 1 warning in 141.88s。合計351: PASS248 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|

最新ID行: 351。累計: PASS248 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|


### 2026-10-16 03:34 JST 最新report SHA CI

| T352 | 最新報告HEADのPush/PR Actions | GitHub Actions、pytest、JS syntax | PASS | SHA `5780a8cf61ad128018916d096695fb26314b33ae`。Push [38786313156](https://github.com/kenkyu0909/aichatapp/actions/runs/38786313156) / PR [38786324398](https://github.com/kenkyu0909/aichatapp/actions/runs/38786324398) 同一HEADでsuccess。1105 passed / 1 warning in 129.40s。合計352: PASS249 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|

最新ID行: 352。累計: PASS249 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|

| T353 | 当日活動に関する相手の直接質問と一時回答のスコープ保護 | pytest (FastAPI/候補フィルターのオフライン回帰) | PASS | 架空の今日/昨日の過ごし方・現在の活動を使い、本人未確認時に質問へ分岐、回答なし候補を拒否、同じ日/同じ時制の回答だけを許可。丁寧形、第三者の活動、店舗営業時間の誤検出、回答後の未確認追加行動、現在回答と過去質問の交差利用を確認。焦点27 passed、関連群52 passed、全pytest1125 passed、Firefox UI11 passed。Gemini実通信なし。コードSHAは未コミット（起点 `e28195c`）。Actionsは未実施。|

最新ID行: 353。累計: PASS250 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|

T353追補: T353の修正コードはコミット `27e8ad28027d0585e435f3154463b46b5039bb2e`。Push Actions [38790459970](https://github.com/kenkyu0909/aichatapp/actions/runs/38790459970) / PR Actions [38790468366](https://github.com/kenkyu0909/aichatapp/actions/runs/38790468366) は同SHAでsuccess（1125 passed / 1 warning、JS構文成功）。その後の日課質問追加変更はT354に記録。

| T354 | 起床・就寝時刻の日課質問での本人確認、回答範囲、非該当質問の誤分類防止 | pytest (オフライン/候補フィルター) | PASS | 架空データで「朝は何時に起きる」「平日は何時に起きることが多い」「週末は何時に起きる」「何時ごろ就寝しますか」「起床/就寝するんですか」「何時に寝ることが多いか教えて」をテスト。回答前は候補拒否、確認回答との不一致時刻も拒否。健康・理想時刻の一般助言、第三者の時刻、営業時間質問は本人確認へ誤誘導しない。focused 22 passed、全pytest1143 passed、Firefox専用11 passed、構文検査PASS。Gemini実通信なし。最新コードは未コミット、Actions未確認。|

最新ID行: 354。累計: PASS251 / FAIL13 / FIXED70 / BLOCKED5 / NOT_TESTED15。|

| T355 | 本人の未来/過去予定に対する日時スコープ分離と確認質問 | pytest (FastAPI/候補フィルターのオフライン回帰) | FIXED | 修正前に月日・年・「再来月」の交差利用、最近の過去活動質問、引用された先行イベント+「その時」の本人確認漏れ2件を再現。年月日、相対月、曜日、週末、時間帯、過去の参照質問と引用括弧の確認往復を分離し、別スコープ回答を拒否する。focused quote/past group 17 passed、全pytest1237 passed in 182.83s（Firefox UI 11件を含む）、Python/JavaScript構文・diff検査成功。Firefox専用の別実行は未実施。Gemini実通信0回。 |

最新ID行: 355。累計: PASS251 / FAIL13 / FIXED71 / BLOCKED5 / NOT_TESTED15。

| T356 | 明示的な連絡終了希望・否定/撤回の節順・映画鑑賞経験の第三者帰属 | pytest（FastAPI/候補フィルターのオフライン回帰） | FIXED | 修正前に「今後メッセージを送らないで」「話しかけないで」「関わらないで」、後続の肯定的な終了希望、友人の「によると/曰く/も/の話では」鑑賞を再現。修正過程で継続希望・否定された撤回・友人の発言を停止扱いする逆誤判定も再現し、節ごとの極性/帰属と最新の直接意思で修正。本人の「私も観ました」は対照として保持。焦点44 passed、全pytest 1286 passed in 180.23s（Firefox UI含む）。`py_compile`、`node --check app.js`、`git diff --check` PASS。Gemini実通信0回。|

最新ID行: 356。累計: PASS251 / FAIL13 / FIXED72 / BLOCKED5 / NOT_TESTED15。

| T357 | 連絡を控えることへの否定表現と、第三者の引用に続く本人の明示回答 | pytest（候補安全フィルターのオフライン回帰） | FIXED | レビューで「連絡を控えていただく必要はありません」「連絡を控えてもらう必要はないです」「連絡を控えるべきではありません」を停止要求と誤認するケース、および友人の引用に続く本人の「私も観ました」を拒否するケースを確認。否定表現を継続希望として扱い、引用部分を除いて本人の直接回答を判定する。焦点49 passed。全pytest 1298 passed in 183.59s、Firefox専用11 passed in 146.93s。`py_compile`、`node --check app.js`、`git diff --check` PASS。Gemini実通信なし。GitHub Actionsは未コミットのため未確認。 |

最新ID行: 357。累計: PASS251 / FAIL13 / FIXED73 / BLOCKED5 / NOT_TESTED15。

T357追補: コミット 3a2dadd1437b47cbce20a66a119776ac426da665のPush Actions [38806233543](https://github.com/kenkyu0909/aichatapp/actions/runs/38806233543)とPR Actions [38806241260](https://github.com/kenkyu0909/aichatapp/actions/runs/38806241260)は同一SHAでsuccess（各1298 passed / 1 warning、JavaScript構文検査成功）。

| T358 | 複数の直接質問と同一トピック別スコープの本人確認 | pytest（FastAPI/TestClient、オフライン） | FIXED | 架空入力「映画は好きですか？普段どんな本を読みますか？」で映画の確認済みプロフィールだけでは未回答の本ジャンルを含む候補が通る問題を再現・修正。`movie_preferences`を既知事実と認識し、最初の未確認質問だけを事前確認、全てに答えない候補を拒否する。同じ映画トピックでも好み/最近の視聴経験を別スコープとして確認。二択・引用過去活動も維持。focused 7 passed、全pytest 1302 passed in 184.98s（Firefox UI suiteを含む）、構文とdiff検査成功、独立レビュー済み。Gemini実通信0回。 |

最新ID行: 358。累計: PASS251 / FAIL13 / FIXED74 / BLOCKED5 / NOT_TESTED15。

T358 CI追補: 最新コミット `9389aa937df569a2aa7c2e683544fe8101e92766` のPush Actions [38809221895](https://github.com/kenkyu0909/aichatapp/actions/runs/38809221895)とPR Actions [38809228016](https://github.com/kenkyu0909/aichatapp/actions/runs/38809228016)がsuccess。同SHAのPushログは1302 passed / 1 warningとJavaScript構文検査成功を確認。

| T359 | 意味的に重なる候補の再生成失敗後の安全な縮退 | pytest（FastAPI/TestClient、Gemini SDKモック） | PASS | 架空の休日メッセージを使い、同義の共感候補が初回・修正リクエストで繰り返される応答を固定。再生成は合計1回で止まり、安全な2案を維持し不足数と類似通知を返す。focused 2 passed、全pytest 1303 passed in 183.71s。モックのみ、Gemini実通信なし。コミット`27c1ea252a976b3394ee877e96c926d32e9064b8`のPush Actions [38810579428](https://github.com/kenkyu0909/aichatapp/actions/runs/38810579428)とPR Actions [38810585298](https://github.com/kenkyu0909/aichatapp/actions/runs/38810585298)がsuccess。各1303 passed / 1 warning、JavaScript構文検査成功。|

| T360 | Firefox追いメッセージの対象相手・コピー/送信記録・編集後改行の永続化 | Firefox UI（空の一時SQLite、API履歴照合） | PASS | 架空相手を使用。生成payloadの`match_id`が選択相手IDと一致。コピー前後でDOM/API履歴不変。送信記録ダイアログで編集した複数行本文はSQLite/API履歴と再読み込み後の表示に完全一致。Firefox focused 1 passed。Gemini生成はUIモック。上記同一SHAのPush/PR Actionsもsuccess。|

最新ID行: 360。累計: PASS253 / FAIL13 / FIXED74 / BLOCKED5 / NOT_TESTED15。

| T361 | 未分類の直接本人質問に対する確認必須化と話者/質問範囲境界 | pytest（FastAPI/TestClient、オフライン） | FIXED | 「何のスポーツをしている？」「何語を話せる？」「タバコ/魚/ペット/車/料理/同居/交際/結婚/休日」「日本語話せますか」「猫はいますか」「子どもの頃は何になりたかった？」などの直接質問を本人確認へ送る。確認済み回答の範囲内だけを許可し、回避候補と追加未確認事実を拒否。友達・妹についての質問、一般的なスポーツ/語学助言、公共施設の場所は本人確認へ誤分類しない。修正前は既存テストで1 FAIL。修正後focused 34 passed、全pytest 1337 passed、Firefox専用UI 11 passed、Python compile/JS syntax/diff check成功。独立レビュー済み。Gemini実通信なし。GitHub Actionsは修正を含むコミットPush後に確認。|

最新ID行: 361。累計: PASS253 / FAIL13 / FIXED75 / BLOCKED5 / NOT_TESTED15。

| T362 | 短い相手発言に対する返信文量の上限と安全な候補縮退 | pytest（FastAPI/TestClient、Gemini SDKモック） | FIXED | 1〜2文の短い相手発言が4文の長い候補を許可する問題を再現。返信モードの相手側文数を上限に候補を保持し、安全候補数が不足したら不足通知を返す。初回メッセージは別扱い。重大話題でも上限を無制限解除しない。回帰群・全pytestを実行中。Gemini実通信なし。変更SHA `4c5c8158efa7f0b8340c0d0fd68f98406828b879`。|

| T363 | 競合する一時回答と頻度レンジ正規化 | pytest（FastAPI/TestClient、オフライン） | FIXED | 「週1〜2回」と「週12回」を同一視しないよう数値範囲を保持し、区切り記号の表記揺れだけを正規化。矛盾する同一スコープの一時回答はGemini呼び出し前にHTTP 400で拒否し、意味的に同じ回答の重複登録を抑止。focused・全pytest成功（最終件数を下記T364追補に記録）。実API 0回。変更SHA `4c5c8158efa7f0b8340c0d0fd68f98406828b879`。|

| T364 | Firefox UIから実FastAPI生成ルートを通る統合確認 | Firefox E2E、空の一時SQLite、FastAPI実サーバー、Gemini SDKのみサーバープロセス内モック | PASS | 架空の相手を使用。ブラウザーfetchの差し替えは行わず `/api/generate` まで実通信。API1・`gemini-3.5-flash-lite`・入力会話・system instructionの到達をテストログで確認。外部Gemini通信0回。候補表示、コピー時の未記録、手動記録、再読み込み後の複数行履歴保持を確認。focused 1 passed、全pytest 1364 passed in 202.96s、Firefox専用UI 12 passed in 157.28s、Python/JS構文とdiff検査PASS。コードレビュー指摘なし。テストは `tests/test_ui_firefox.py` と `tests/firefox_mocked_gemini_server.py`。変更コミットとActionsは後続追補。|

| T362–T364 集計 | 短文ミラーリング、回答競合、Firefox生成経路統合 | ローカルpytest / Firefox | PASS・FIXED | 364項目: PASS254 / FAIL13 / FIXED77 / BLOCKED5 / NOT_TESTED15。全pytest 1364 passed in 202.96s、Firefox専用UI 12 passed in 157.28s。最新同一HEADのActions結果は後続追補へ記録する。 |

| T365 | Firefoxから実FastAPI first / followup / like 生成ルート | Firefox E2E、空の一時SQLite、FastAPI実サーバー、Gemini SDKモック | PASS | 3モードのFirefox操作を実 `/api/generate` に到達させ、サーバー内SDKモックログで mode・モデル・system instructionを確認。firstは候補だけではDBを変えず、手動記録後に保存。followupはコピーのみで履歴を変えず、明示記録後に保存。likeは保存ボタンがなく履歴に影響しない。firstモードでは候補検証がfixture候補のうち安全な1案だけを残したため、候補不足状態を含めて確認（安全性検証は緩和していない）。focused T364/T365 2 passed、全pytest 1365 passed in 199.68s（Firefox UIを含む）、外部Gemini通信0回。独立レビュー指摘なし。最新SHA Actionsは後続追補。|

最新ID行: 365。累計（T365 focused結果を追加）: PASS255 / FAIL13 / FIXED77 / BLOCKED5 / NOT_TESTED15。

T359/T360 CI追補: 同一SHA `27c1ea252a976b3394ee877e96c926d32e9064b8` を対象とするPush Actions [38810579428](https://github.com/kenkyu0909/aichatapp/actions/runs/38810579428)とPR Actions [38810585298](https://github.com/kenkyu0909/aichatapp/actions/runs/38810585298)はsuccess。各1303 passed / 1 warning、JavaScript構文検査成功。PR #4はOPEN/Draft・未マージ。

T361 CI追補: 最新コードSHA `43a214dcaa4657aaf21094ddb7b311299f7567df` のPush Actions [38814001025](https://github.com/kenkyu0909/aichatapp/actions/runs/38814001025)とPR Actions [38814006313](https://github.com/kenkyu0909/aichatapp/actions/runs/38814006313)は同一SHAでsuccess。Pushログで1337 passed / 1 warning、JavaScript構文検査とArtifact upload成功を確認。PR #4はOPEN/Draft・未マージ。
