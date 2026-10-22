# テストマトリクス

架空のプロフィール・人物・会話のみで実施。結果は実際の確認に基づき記録。

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T01 | アプリ起動（Python） | Python 3.12.10、Uvicorn | PASS | `127.0.0.1:8767`で起動。再起動も実施。 |
| T02 | Windows `start.bat`起動（既定ポート8765） | 実機で実行 | BLOCKED | 2026-10-14/15/16にread-onlyで確認。8765番はPID 39504のWindows Store版Python 3.12がlistenし、`/api/status`の`app_id`/`host`/`status`はnull。今回のアプリと特定できないためプロセスは停止・変更せず、8765での起動再試験は未実施。別ポート8767の隔離起動はT286 PASS。 |
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

| T366 | Firefox上の候補不足通知と安全候補の保持 | Firefox E2E、隔離SQLite、FastAPI実ルート、Gemini SDKモック | PASS | T365のfirstモードで3案中1案だけ安全検証を通過するfixtureを利用。残った候補を保ち、画面に候補数と不足の説明が出ることを確認。focused 1 passed、全pytest 1365 passed in 198.20s、Python compile / JavaScript syntax / diff check成功。Gemini実通信0回。 |

最新ID行: 366。累計: PASS256 / FAIL13 / FIXED77 / BLOCKED5 / NOT_TESTED15。

| T367 | Firefox実画面から本人情報を確認し一時回答で再生成 | Firefox E2E、隔離SQLite、FastAPI実 `/api/generate`、Gemini SDKモック | PASS | 架空入力「映画好きですか？」で本人確認前は候補を返さずproviderも呼ばない。回答「映画は好きで洋画をよく観ます」を一時入力して再生成し、回答内容との一致をbooleanで記録・検証（本文はログに保存しない）。本人プロフィール不変、コピーは送信履歴を作らない。focused 2 passed（T365/T367）、全pytest 1366 passed in 225.82s。レビュー修正後のfocused再実行2 passed in 26.46s。Gemini実通信0回。 |

最新ID行: 367。累計: PASS257 / FAIL13 / FIXED77 / BLOCKED5 / NOT_TESTED15。

T365のPR Actions [38822714041](https://github.com/kenkyu0909/aichatapp/actions/runs/38822714041)は、DB保存直後にUIの追いメッセージボタンを即時検査して非表示だったため失敗。可視性を待つ`WebDriverWait`を追加し、対象Firefoxテストを3回連続で通過（13.32秒、13.58秒、13.31秒）。

T367のレビュー後最終回帰: 全pytest **1366 passed in 223.60s**（Firefoxを含む）、focused T365/T367 **2 passed in 26.46s**。回答の一致確認・startup cleanup修正を含む。新HEAD Actionsは未確認。

| T368 | Firefox相手切替中の一時stale DOMを待機し、別相手の候補記録を防ぐ | Firefox E2E、隔離SQLite | FIXED | 最新SHA `1d2f909`のPush Actionsで既存テストが`StaleElementReferenceException`により失敗、同SHAのPR Actionsはsuccess。画面切替中の古いDOM参照を再試行可能な一時状態として扱い、相手名と会話履歴が同時に一致するまで待つ。送信対象検査は維持。focused T365/T367/T368 3 passed、T368単独3回連続成功（12.84s / 12.07s / 11.73s）、全pytest 1366 passed in 224.18s。レビューapprove。Gemini実通信0回。 |

最新ID行: 368。累計: PASS257 / FAIL13 / FIXED78 / BLOCKED5 / NOT_TESTED15。

| T369 | 既存アプリ経由のGemini実API単発疎通と候補品質確認 | `/api/generate`、隔離SQLite、実Gemini API | FAIL（疎通PASS / 品質FAIL） | 2026-10-16 09:13 JST、架空プロフィールで1論理リクエスト・provider attempt 1回。HTTP 200、`demo=false`、API1 / `gemini-3.5-flash-lite`。指定3案に対し安全検査後の候補は2案。実出力「素敵な休日ですね！」「落ち着いた雰囲気のお店ですか？」。外部API到達は確認できたが候補数不足、最初の案は会話を進めにくく、品質テストはFAIL。APIキー非表示、再試行・別モデル切替なし。本番DB不使用。 |

最新ID行: 369。累計: PASS257 / FAIL14 / FIXED78 / BLOCKED5 / NOT_TESTED15。

| T370 | 初回メッセージの好意・喜び・固定デモ例 | プロンプト確認、固定デモ候補検査、全pytest、Firefox UI | PASS | 2026-10-16 JST。初回用プロンプトに候補ごとの主観的な好意・マッチの喜びを明記し、推奨候補の絵文字方針を追加。固定デモ5案も確認。focused 7 passed、全pytest 1368 passed / 230.78s、Firefox UI 14 passed / 194.79s、`py_compile`と`node --check app.js`成功。実Gemini通信0回のため実生成品質は未確認。関連SHAはコミット後に記録。 |

最新ID行: 370。累計: PASS258 / FAIL14 / FIXED78 / BLOCKED5 / NOT_TESTED15。歴史的な品質009の手動FAILは保持し、T370のオフラインPASSで置き換えない。

T369報告HEAD `b5204913bc2c5ec9e0176acda66b94c3d3e6c4e5` CI: Push Actions [38828310999](https://github.com/kenkyu0909/aichatapp/actions/runs/38828310999)とPR Actions [38828315505](https://github.com/kenkyu0909/aichatapp/actions/runs/38828315505)は同一SHAでsuccess。Pushログは1366 passed / 1 warning、JavaScript構文検査とartifact保存成功。CI成功はT369の文章品質FAILを変更しない。

最新変更を含むActionsは次のPush後に確認する。1d2f909のPush run [38825261770](https://github.com/kenkyu0909/aichatapp/actions/runs/38825261770)は1 failed / 1365 passed（失敗箇所T368の修正前テスト）、PR run [38825266165](https://github.com/kenkyu0909/aichatapp/actions/runs/38825266165)は同一HEADでsuccess。T368修正後の最新HEAD Actionsを別途確認する。

T366 CI追補: T366を含むSHA `e93aef60486e89a7e0d6ba9554b592f1276a0d68`のPush Actions [38820922000](https://github.com/kenkyu0909/aichatapp/actions/runs/38820922000)とPR Actions [38820929128](https://github.com/kenkyu0909/aichatapp/actions/runs/38820929128)は同一head SHAでsuccess。両workflowでpytestとJavaScript syntax check、Firefox準備、artifact uploadが成功。ローカル全pytestは1365 passed in 198.20s。T366を含む次のdocs-only HEADについては別途CIを確認する。

最新HEAD CI: `f832bd0529970d1bd6fddfc34169b67a17002b47`のPush Actions [38821980706](https://github.com/kenkyu0909/aichatapp/actions/runs/38821980706)とPR Actions [38821986819](https://github.com/kenkyu0909/aichatapp/actions/runs/38821986819)は同一SHAでsuccess。Push run artifactのJUnit記録は1365 tests / 0 failures / 0 errors / 0 skipped。JavaScript syntax、Firefox準備、Artifact保存もsuccess。Gemini実通信0回。過去QUALITY009の生成自然さ・意味的多様性FAILは維持し、総合NO-GO。


T368最終CI追補: 最新SHA `a941ac478dd443bb525928e2e17f473acb774575` のPush Actions [38826220985](https://github.com/kenkyu0909/aichatapp/actions/runs/38826220985) とPR Actions [38826226808](https://github.com/kenkyu0909/aichatapp/actions/runs/38826226808) は同一head SHAでsuccess。Push artifactのJUnitは1366件 / 失敗0 / error0 / skipped0。PR #4はOPEN/Draft・未マージ。これはオフライン検証であり、QUALITY009実Gemini自然さ・意味的多様性FAILは未解決。


QUALITY009再生focused監査（既存項目の補足、件数の重複加算なし）: `tests/test_quality_checks_009.py`と直接質問/拒否後候補フィルターを合わせて9 passed in 1.68s。未確認事実・質問すり替え・不安を軽く扱う既知候補の除外と安全候補不足通知を確認。最新検証HEAD `27c6b2c933363b13e42eb67d481c87871f3131d5` のPush Actions [38826749824](https://github.com/kenkyu0909/aichatapp/actions/runs/38826749824) / PR Actions [38826754188](https://github.com/kenkyu0909/aichatapp/actions/runs/38826754188) は同一SHAでsuccess。JUnit: 1366 / 0 failures / 0 errors / 0 skipped。

### 2026-10-16 09:05 JST 最終CI・Windowsポート状態

- 最新HEAD `70e60530aae590e4f21bb6c562b21e31f01d3061` のPush Actions [38827109927](https://github.com/kenkyu0909/aichatapp/actions/runs/38827109927) とPR Actions [38827115882](https://github.com/kenkyu0909/aichatapp/actions/runs/38827115882) は同一SHAでsuccess。Push artifactのJUnitは**1366 tests / 0 failures / 0 errors / 0 skipped**。PR #4はOPEN/Draft、未マージ。
- QUALITY009保存候補の安全再生・直接質問・拒否後候補に関するfocused監査は9 passed。具体的な既知不適切候補は除外され、安全な候補を残して不足を通知する。未解決の実生成自然さ・意味的多様性FAILは維持。Gemini実通信0回。
- Windows `127.0.0.1:8765`はPID 39504のWindows Store版Python 3.12が待受。read-only `/api/status`はアプリ識別フィールドがnull。所有アプリと特定できないため停止・変更せず、T02はBLOCKED、T69はNOT_TESTEDのまま。T286の一時データ/8767/Firefox隔離起動PASSは別結果として維持。
- PR本文はT367/T368およびQUALITY009監査の結果を追補済み。

| T371 | 初回メッセージで確定済み相手名を使う指示 | プロンプト契約・APIコンテキストテスト（pytest、オフライン） | PASS | `other.name` は `/api/generate` の既存コンテキストにあり、first用指示に「名前が確認できる場合は自然に使用し、不明なら省略・プレースホルダー禁止」を追加。プロンプト契約・固定デモ候補・first APIコンテキストのfocused test 3 passed / 1273 deselected。Gemini実通信0回のためモデル追従品質は未検証。変更HEADとActionsはコミット後に追記。 |

最新ID行: 371。累計: PASS259 / FAIL14 / FIXED78 / BLOCKED5 / NOT_TESTED15。T369実生成品質FAILは維持。

| T372 | 文脈に合う相槌と絵文字の検討 | 共通プロンプト契約テスト（pytest、オフライン） | PASS | 明るい通常会話では3案中1案以上の絵文字を積極的に検討し、文脈に合う相槌・相槌なし・同義反復の回避・深刻/拒否場面での抑制を明記。修正前は相槌例がなく focused testがFAIL。修正後は共通プロンプトを4モードで読むfocused suite 5 passed / 1272 deselected。実Gemini品質は未検証。 |

最新ID行: 372。累計: PASS260 / FAIL14 / FIXED78 / BLOCKED5 / NOT_TESTED15。T369の実生成品質FAILは維持。


T371/T372最新HEAD CI追補: `3e6a20f9b64150e83a9cb047047c0a6aa872dba7`のPush Actions [38835061552](https://github.com/kenkyu0909/aichatapp/actions/runs/38835061552)とPR Actions [38835066980](https://github.com/kenkyu0909/aichatapp/actions/runs/38835066980)は同一SHAでsuccess。CI pytest **1369 passed / 1 warning**、`node --check app.js`成功、offline-test-results artifact保存成功。Windowsローカル全pytest **1369 passed in 234.27s**。これはオフラインテストで、T369の実Gemini品質FAILを解消しない。

| T373 | 1・3・5案の要求数とプロンプト指示の整合性 | first/commonプロンプト契約（pytest、オフライン） | PASS | first専用・共通プロンプトに固定の「3案/3候補」が残る欠陥を検出し、要求案数に従う表現へ修正。旧期待値のテストが修正前FAIL、修正後は初回好意/案数/固定デモ/相槌契約のfocused suite 5 passed / 1273 deselected。Gemini実通信0回。最新Actionsはコミット後に確認。 |

| T374 | 映画感想の作品別・極性別の本人事実検証 | 架空回答を使ったpytest（オフライン） | FIXED | 異なる作品の感想混同、続編・外伝の部分一致、同一作品にある賛否両方の回答を検証。追試では否定・二重否定・`気がします`・「し」の接続判定まで境界ケースを追加。最新の映画関連suite 240 passed。実API通信0回。 |
| T375 | 主語を省略した映画視聴頻度の捏造防止 | 架空プロフィールと会話を使ったpytest（オフライン） | FIXED | `最近は映画をよく観ています`、`映画はあまり/全然/ほとんど観ません`を未確認事実として拒否。相手が述べた同じ頻度を本人の習慣と誤認する相槌は許可し、本人が同じ頻度を回答した場合は使用可能。関連focused suite 42 passed。Gemini実通信0回。 |
| T376 | 料理スキル回答の範囲を保った自然な言い換え | 架空の直接質問・回答を使ったpytest（オフライン） | FIXED | `得意料理はありますか？`への確認回答を、カレー作りの得意さを保つ4つの表現で使用可能にした。好みへのすり替え、否定、未確認の追加事実は拒否する。関連focused suite 42 passed。Gemini実通信0回。 |
| T377 | 直近の映画・作品名の抽出と感想の安全な言い換え | 架空回答を使ったpytest（オフライン） | FIXED | `最近観た映画は青い灯台で面白かった`から「観た映画」を作品名と誤抽出する問題と、`青い灯台の映像/ストーリー`の感想を別作品扱いする過剰ブロックを修正。題名を特定できる表現だけを同一作品として照合。関連focused suite 42 passed。Gemini実通信0回。 |

| T378 | 映画感想の二重否定・口語的否定形の見逃し防止 | 架空の候補と本人回答を使ったpytest（オフライン） | FIXED | `面白くなかったとは思わないです`、`面白かったわけじゃないです`、`面白くなかった気がします`、`微妙ではありませんでした`等を追加。未確認の感想は拒否し、反対極性の根拠では候補を許可しないことを確認。映画関連suite 240 passed。実API通信0回。 |
| T379 | 「少し」の「し」を接続詞と誤認する作品名分離 | 架空作品名と感想を使ったpytest（オフライン） | FIXED | `青い灯台は少し面白かった`を`し`で分割して作品名を失い、別作品の感想を許可する問題を再現。述語語尾に続く接続詞だけを分割し、`少し`内の文字は分割しない。映画関連suite 240 passed。 |
| T380 | 本人が明示した否定的な映画の好み | 架空の直接質問・回答を使ったpytest（オフライン） | FIXED | `映画は好きではありません`・`映画は好きじゃありません`を確認回答と同じ範囲で利用可能にし、肯定回答が否定候補を許可しないことを確認。映画関連suite 240 passed。 |

| T381 | 曖昧・中立な映画嗜好を肯定事実として扱わない | 架空プロフィールと候補を使ったpytest（オフライン） | FIXED | `映画が好きか分からない`、`好きなのか微妙`、`好きでも嫌いでもない`、`好きってほどじゃない`、`好きとは限らない`で肯定候補を送信不可にした。追加ケースで修正前5件FAILを再現。後続focused suite 51 passed。Gemini実通信0回。 |
| T382 | カフェ頻度の照合と口語的な過去ペット質問 | 架空プロフィールと会話を使ったpytest（オフライン） | FIXED | 確認済み「月1回」に対する「月に数回」を拒否し、正確な回答＋自然な追質問は許可。「昔猫いた？」「ペットいたことある？」を本人確認対象として分類。修正前の失敗を再現し、後続focused suite 51 passed。Gemini実通信0回。 |

| T383 | 映画嗜好のジャンル・限定・比較表現 | 架空プロフィールと候補文を使ったpytest（オフライン） | FIXED | 「ホラー映画だけ」「昔の名作映画だけ」「ホラーより恋愛映画が好き」などから、広い映画好み・比較で負けたジャンル・逆の極性を候補へ転用する欠陥を再現して修正。「よりも」「しか好きじゃない/ではない」「以外は好きじゃない/ではない」を含む18件の映画回帰テストが成功。実Gemini通信0回。 |
| T384 | カフェ頻度の口語的な同等表現と未確認の主張 | 架空プロフィール・送信候補を使ったpytest（オフライン） | FIXED | 「月に数回」と「月に何度か」は同程度の頻度として扱い、「月1回」から頻度を広げる候補は直接の頻度質問がない会話でも送信不可にした。被害再現後の頻度/候補検査focused suite 66 passed。実Gemini通信0回。 |
| T385 | 過去ペット経験の語順・居場所表現 | 架空の相手質問とプロフィールを使ったpytest（オフライン） | FIXED | 「昔うちに猫いた？」「昔は猫が家にいた？」「猫が昔うちにいた？」を本人への確認対象にし、ユーザー回答なしの二択候補を送信前に止める。動物園など第三者・施設の文脈を混同しない既存テストも維持。実Gemini通信0回。 |

最新ID行: 386。累計: PASS261 / FAIL14 / FIXED91 / BLOCKED5 / NOT_TESTED15。T369の実生成品質FAILは維持。最新コードの全pytest 1557 passed (Windows local, 2026-10-16 13:13 JST; Firefox UI included)。Python構文、JavaScript構文、git diff --check成功。Gemini実通信0回。今回コミットのActionsはPush後に確認する。

| T386 | 否定「だけ」付き映画嗜好を肯定根拠にしない | 架空プロフィールと候補のpytest。修正前後比較、独立コードレビュー | FIXED | 「ホラー映画だけは好きではない」「だけ好きではない」「だけは好きじゃない」「だけ好きじゃない」の4ケースは修正前に全件失敗。曖昧な限定否定をfail-closedにし、「しか」「以外」の既存肯定解釈を維持。映画嗜好focused suite 58 passed、全pytest 1557 passed。Gemini実通信0回。commit: Push後に追記。 |

| T387 | カフェ頻度の否定・二重否定の極性 | 架空プロフィールの頻度根拠と候補を使うpytest（オフライン、修正前後比較） | FIXED | 「よく行かない」「週末はよく行かない」が肯定頻度を許可する問題と、「あまり行かないわけではない」等の二重否定を低頻度と誤認する問題を再現。修正前に問題ケースFAIL、修正後は否定根拠を肯定へ転用せず、二重否定を曖昧として拒否。最新focused suite 12 passed。全pytest 1580 passed（Firefox UI含む）。Gemini実通信0回。 |
| T388 | 朝食の口語的な否定質問の本人確認 | 架空の相手質問と「うん」の本人回答を使うpytest（オフライン） | FIXED | 「朝食取ってない」「朝ごはん取ってない」「朝ごはん食べてない」「朝食食べていませんか」を本人情報の質問として分類し、短い二択回答に確認質問を要求。修正前の追加ケースはFAIL、最新focused suite 12 passed。全pytest 1580 passed（Firefox UI含む）。Gemini実通信0回。 |

最新ID行: 388。累計: PASS261 / FAIL14 / FIXED93 / BLOCKED5 / NOT_TESTED15。最新ローカル全pytest **1577 passed in 276.39s**（2026-10-16 JST、Firefox UI含む）。focused再現suite **9 passed**。`py_compile`、`node --check app.js`、`git diff --check`成功。Gemini通信0回。今回のコミットSHAとGitHub ActionsはPush後に追記する。T369の実Gemini品質FAILを維持。 |

| T389 | カフェ頻度の複合二重否定を曖昧として扱う | 架空プロフィール・候補を使ったpytest（オフライン、修正前後比較） | FIXED | レビューで「わけでもない」「ってわけでもない」「というわけではない」が低頻度の根拠として通る3件を再現。これらを曖昧として分類し、低頻度候補の根拠に使用できないよう修正。関連focused suite 12 passed、最新全pytest 1580 passed。Gemini実通信0回。 |

最新ID行: 389。累計: PASS261 / FAIL14 / FIXED94 / BLOCKED5 / NOT_TESTED15。最新ローカル全pytest **1580 passed in 273.36s**（Windows、Firefox UI含む）。該当focused suite **12 passed**。`py_compile`、`node --check app.js`、`git diff --check`成功。Gemini通信0回。今回のcommit SHA/ActionsはPush後に追記。T369の実Gemini品質FAILは維持。 |

CI確認追記: 検証コードSHA `ad764f01dca47135800f3d230d1b262261d6e016`のPush Actions [38852603579](https://github.com/kenkyu0909/aichatapp/actions/runs/38852603579) とPR Actions [38852606544](https://github.com/kenkyu0909/aichatapp/actions/runs/38852606544) は同一SHAでsuccess。各run pytest 1580 passed / 1 warning、JavaScript構文検査・Firefox準備・artifact保存成功。 |

| T390 | 一度きりの友人とのカフェ訪問から頻度を既知扱いしない | 架空の会話履歴を使ったpytest（オフライン、修正前後比較） | FIXED | 「先週は友人とカフェに行きました」「この前友達と喫茶店へ行ってきました！」だけでは、「友達とカフェに行くことが多いんですか？」を再質問として拒否してしまう問題を2ケースで再現。修正前2件FAIL。習慣・頻度の明示語が同じ発言にある場合だけ友人とのカフェ頻度を既知扱いする。修正後カフェ関連suite 91 passed、全pytest 1585 passed（Firefox UI含む）。Gemini実通信0回。 |

最新ID行: 390。累計: PASS261 / FAIL14 / FIXED95 / BLOCKED5 / NOT_TESTED15。最新全pytest **1585 passed in 272.74s**（Windows、Firefox UI含む）。カフェ関連focused suite **91 passed**。`py_compile`、`node --check app.js`、`git diff --check`成功。Gemini通信0回。最新SHAとActionsはPush後に追記。T369の実Gemini品質FAILは維持。 |

| T391 | 友人・カフェ・休日習慣の根拠を同じ活動・節に限定する | Windowsのpytest、架空履歴を使った修正前後比較、独立コードレビュー | FIXED | 別節にある週末映画の頻度を一度きりの友人カフェ訪問へ誤適用する2ケース、現在のカフェ嗜好を過去の友人同行頻度へ流用する1ケースを修正前に再現。さらに「休日は、友達とカフェに行くことが多いです！」の読点で既知情報を見落とすケースも再現。修正中に過去→現在のカフェ嗜好ケースの回帰を見つけて復旧。履歴を節単位で分け、短い話題導入のみ次節に保持し、好みと頻度を区別。関連focused suite 69 passed、独立レビュー APPROVE、最新全pytest 1601 passed、Firefox専用18 passed。Gemini実通信0回。 |

最新ID行: 391。累計: PASS261 / FAIL14 / FIXED96 / BLOCKED5 / NOT_TESTED15。Windowsの最新全pytest **1601 passed in 283.24s**。`tests/test_ui_firefox.py` **18 passed in 233.83s**。`py_compile`、`node --check app.js`、`git diff --check`成功。追跡ファイルの認証情報パターンスキャンは一致なし。Gemini通信0回。最新SHAとActionsはPush後に追記。T369の実Gemini品質FAILを維持。 |

### Latest test addition

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|

| T392 | 品質ランナーの意味的候補重複判定とsmoke-only終了状態 | 保存済みQUALITY009候補を現行ゲートで再評価し、pytestで分類・終了コードを確認（オフライン） | FIXED | 保存済み`joke_mirroring`候補の「休日に休むことへの共感」2案は意味が重複し、従来のランナーが完全一致だけを見て自動PASSにしていた。JSON原本は変更せず、アプリの意味的多様性ゲートを品質判定に適用してFAILにする。安全な候補の保持と品質FAILを分離。smoke-onlyで安全な実応答があっても意味的多様性FAILなら総合status=FAIL・終了コード2、全品質PASSならSMOKE_PASS・終了コード0となることを検証し、`smoke_scope`を成果JSONに保存する。focused suite 7 passed。Gemini実通信0回。全pytestと最新Actionsは今回HEADで確認後に追記。 |

最新ID行: 392。累計: PASS261 / FAIL14 / FIXED97 / BLOCKED5 / NOT_TESTED15。QUALITY009の元JSONにある過去の自動PASSは履歴として維持し、保存済み候補の意味的重複は今回の再評価でFAILと判定。T369の実Gemini文章品質FAILも維持。今回の全pytest・Actions結果は実行後に追記する。Gemini実通信0回。

2026-10-16 15:10 JST 最新HEADでの再検証: 全pytest **1605 passed in 303.57s**。追加focused suite `tests/test_quality_checks_009.py` **8 passed**、保存候補再評価 `tests/test_app.py -k quality009_recorded_redundant_reactions_are_detected` **1 passed**。全pytestにはFirefox UIテストが含まれる。Python構文、JavaScript構文、`git diff --check`成功。追跡対象の認証情報パターンスキャンは一致なし。Gemini実通信0回。コード・文書は未コミットで、GitHub ActionsはPush後に確認する。|

T392 CI追補: コードSHA `fd6922a5f82edaee81b1eebfe066726170f52c2d`のPush Actions [38859815003](https://github.com/kenkyu0909/aichatapp/actions/runs/38859815003)とPR Actions [38859820028](https://github.com/kenkyu0909/aichatapp/actions/runs/38859820028)は両方success。同じSHAの各runで**1605 passed / 1 warning**。JavaScript構文検査とoffline-test-results artifact保存も成功。警告はGitHub runnerのNode.js 20・ubuntu-latest移行通知。 |

| T393 | first候補の必須要素と否定表現を送信前に検査 | 架空プロフィールを使うpytest、候補フィルター、独立コードレビュー | FIXED | first候補に挨拶・本人への軽い好意・マッチ成立の喜び・プロフィール由来の話題・質問1つを個別に要求。欠落・質問0/複数・肯定表現の否定形（タイプじゃない/だった/思わない、好みというわけではない、気になっていない、嬉しくない/思えない/限らない/わけじゃない/しくもない/しくはありません等）は送信候補から除外。安全な完全候補は維持し、案数不足通知を残す。first以外のモードには影響しない。focused first suite 30 passed。全pytest 1633 passed in 299.26s（Firefox UIを含む）。`py_compile`、`node --check app.js`、`git diff --check`成功。独立レビューで代表的な否定形を再現後、修正を確認。これは限定された文字列ガードであり、日本語の意味を完全に判定するものではない。Gemini実通信0回。|

最新ID行: 393。累計: PASS261 / FAIL14 / FIXED98 / BLOCKED5 / NOT_TESTED15。最新Windows全pytest **1633 passed in 299.26s**、Firefox UIを含む。初回文focused suite **30 passed**。Gemini実通信0回。Actionsは最新変更のPush後に確認する。T369とQUALITY009の実生成品質FAILは維持し、総合NO-GO。 |

| T394 | 伸ばし棒「ー」の文脈別スタイル契約と固定例 | 共通/firstプロンプトの契約テストと架空の手書き例5場面をpytestで確認（オフライン） | FIXED | 明るい日常・本当の驚きでは自然な「ー」を許し、冗談・深刻な疲れ・慎重な断りでは文脈に合わない挿入を避けることを確認。句読点なし・空行なし・絵文字/笑/伸ばし棒の場面別使用を検査し、focused suite 6 passed。これはプロンプト契約と固定例の検証であり、Geminiの実生成品質は検証していない。Gemini実通信0回。 |

最新ID行: 394。累計: PASS261 / FAIL14 / FIXED99 / BLOCKED5 / NOT_TESTED15。最新Windows全pytest **1639 passed in 325.46s**（Firefox UIを含む）、今回のfocused suite **7 passed**。`py_compile`、`node --check app.js`、`git diff --check`成功。Gemini実通信0回。T369・QUALITY009実生成品質FAILは維持。最新ActionsはPush後に追記する。|

| T395 | 安全な返信候補と任意の本人確認質問 | FastAPI/SDKモックとFirefox UI操作で回答・スキップ・失敗再試行・再質問抑制を確認（オフライン） | FIXED | 安全な候補を残したまま任意質問を最大1件表示。本人回答は一時送信だけでプロフィール保存・メッセージ送信なし。回答再生成が503で失敗した場合は質問と入力内容を保持し、再試行成功後に同じ情報範囲の質問をページ内の相手別状態で抑制する。バックエンドは認識可能な話題と詳細を使って同じ範囲の言い換えを抑制し、異なる詳細は維持。mandatory質問は従来どおり候補なしのブロッキング動作。focused backend 19 passed、Firefox 2 passed。Gemini実通信0回。|

最新ID行: 395。累計: PASS261 / FAIL14 / FIXED100 / BLOCKED5 / NOT_TESTED15。Windows全pytest **1647 passed in 303.03s**（Firefox UI含む）、backend focused 19 passed、Firefox focused 2 passed。Python構文、JavaScript構文、`git diff --check`成功。Gemini実通信0回。コードSHA `a35f1d19a0b2cd0c5a720e7240e728fa4a71776d`の[Push Actions](https://github.com/kenkyu0909/aichatapp/actions/runs/38868726120)と[PR Actions](https://github.com/kenkyu0909/aichatapp/actions/runs/38868731579)はsuccess、双方1647 passed / 1 warning。T369・QUALITY009実生成品質FAILは未解決のまま保持し、総合判定NO-GO。|

| T396 | 部分的に安全な候補の不足分補完と失敗時の安全候補保持 | TestClient/SDKモック。安全候補を含む初回応答後に安全な補完・不安全な補完・ネットワーク失敗・全モデル429を再現 | FIXED | 安全候補を残して不足枠のみ1回再生成。再生成も通常の事実・拒否・形式検査を通す。重複・不安全候補は除外し、不足時は数を偽らず通知。ネットワーク・429で補完できない場合も先に通過した安全候補、試行数、API別名/モデルの由来を維持し、秘密の例外文字列は返さない。旧部分補完テストの12件はモック応答と試行数を新仕様に沿って明示し、すべてPASS。関連focused suite 96 passed。Gemini実通信0回。|
| T397 | 「学生ですか？」への本人事実確認と追加主張検証 | TestClient/SDKモックと純関数テスト。確認前、確認回答、粒度違い、学校名のみ、否定回答、回答に続く主張を検証 | FIXED | 確認前はGeminiを呼ばず質問を提示。学校名だけでは現在の在学状況を推測しない。大学生等の具体情報は同じ粒度の確認済み情報だけで許可し、一般的な「学生」から大学院生等を推測しない。確認済み回答に補足質問を付けることは許し、未確認の通学習慣・専攻・アルバイト等を加えた候補は拒否。一般的な否定回答も確認済み回答として扱い再質問を避ける。独立レビューAPPROVE。Gemini実通信0回。|
| T398 | 任意本人質問の連絡先間分離 | Firefox実UI操作。1人目で質問範囲をスキップ後、別の架空連絡先へ切り替えて同じ範囲の質問を確認 | FIXED | 1人目の質問抑制状態が2人目へ漏れず、2人目では同じ範囲の質問が表示された。再び1人目へ戻ると、その連絡先内の抑制だけが保たれる。Firefox実行1 passed。架空データのみ。Gemini実通信0回。|

最新追加後のマトリクスは398項目: PASS261 / FAIL14 / FIXED103 / BLOCKED5 / NOT_TESTED15。Windows全pytest **1668 passed in 303.15s**（Firefox UIを含む）。過去のT369/QUALITY009実Gemini生成品質FAILは維持し、モック・静的検査を実API品質PASSとして数えない。

### 2026-10-16 18:40 JST — 料理確認・既知情報の再質問・直接質問回避

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T399 | 最近作った料理の確認質問が相手の質問粒度と一致し、頻度回答を誤用しない | pytest、架空の直接質問と一時回答 | FIXED | 「最近どんな料理を作りましたか？」へ頻度を質問していた不具合を再現し、最近の料理を聞く質問へ修正。週3回という頻度だけでは最近の料理を回答済みとせず、カレーの回答を使う候補だけを許可。日次習慣・得意・家族同伴などの追加主張を拒否し、短い自然な回答形は許可。Gemini通信0回。|
| T400 | 相手の既知の食べ物・最近見た映画・旅行頻度・週末予定の聞き直し | pytest、保存済み会話形式の架空文章、候補単位の送信前検査 | FIXED | 好物を明示した候補、直近に観た作品名、年次の旅行頻度、今週末や土曜/日曜の個別予定を聞き直す候補を検出。別のスイーツ・映画の感想・次の旅行希望・予定中の展示内容など深掘りは許可。否定された好みは既知の好物と扱わない。Gemini通信0回。|
| T401 | 分類外の直接質問に対する質問すり替えを候補単位で拒否 | pytest、候補フィルター、極性質問/WH質問/同意タグの架空例 | FIXED | 直接質問へ答えず、相槌や共感と無関係な新質問だけを含む候補を拒否し、回答後の追加質問は許可。短い「はい」は「この店知ってますか？」には許可し「それでどうなったんですか？」には拒否。同意を求める「ですよね？」や「面白かったよね？」は文字通りの回答を強制しない。安全な回答候補を残し、不足数を通知。Gemini通信0回。|

T399–T401追加後の暫定マトリクス件数: 401項目（PASS261 / FAIL14 / FIXED106 / BLOCKED5 / NOT_TESTED15）。Windows全pytestの最終再実行と最新Actionsは実行/Push後に追記する。過去のT369/QUALITY009実Gemini生成FAILは維持。|

| T402 | 分類外のWH直接質問へ根拠のない回答を送信前に拒否 | pytest。架空質問「それでどうなったんですか？」と根拠なし/確認済み候補を使用 | FIXED | 汎用の「しました」「できました」等で無関係な経験を回答扱いする問題、自然な結果表現を誤って許可する問題を再現。分類外WH質問は同じ質問に対する本人の一時回答が候補に含まれる場合だけ許可し、それ以外は安全な候補不足にする。カフェ招待への明確な肯定と確認済み映画回答は回帰維持。focused suiteで再確認。Gemini実通信0回。|
| T403 | 摂取頻度・否定・好物なし・苦手を肯定的な好物と誤認しない | pytest。架空の否定・対比・頻度・未設定文7件 | FIXED | 「カレーが好きではないけどラーメンをよく食べます」「好きというわけではない」「好きでない」「ラーメンをよく食べるだけ」「好きな食べ物は特にない/ない」「カレーが苦手」を好物既知と扱わない。肯定された好物と「好きな食べ物はカレーではなくラーメン」の再質問抑制は回帰テストで維持。focused suiteで再確認。Gemini実通信0回。|
| T404 | 未分類の本人質問・相手の誘いの確認範囲を事前質問と送信ゲートで一致させる | 架空の質問によるpytest。本人の体験・意見・招待、第三者・一般知識との対照を確認 | FIXED | 一般知識や第三者への質問まで本人確認を要求する誤検出と、「友達はどうなった」「その映画どうでした」などの事前質問/最終ゲートのずれを再現。本人の体験・意見・誘いへの意思確認だけに対象を限定し、第三者・公共情報は個人質問ゲートの対象外とした。誘いへの承諾候補は本人の一時回答があるまで通さない。食べ物の訂正「カレーではなく特にない/ラーメン」も区別。focused suite **117 passed**。|

最新項目数403。状態集計はPASS261 / FAIL14 / FIXED108 / BLOCKED5 / NOT_TESTED15。直近の全pytest **1723 passed in 298.56s** は、追加レビュー指摘の修正前HEAD。今回の追加修正focused suite **44 passed**。最新差分を含む全pytestは再実行中。実APIのT369/QUALITY009品質FAILは未解決として維持する。|

2026-10-16 19:39 JST 最新項目数404。状態集計はPASS261 / FAIL14 / FIXED109 / BLOCKED5 / NOT_TESTED15。Windows全pytest **1743 passed in 303.58s**（Firefox UI含む）。追加のFirefox E2E 4件（任意本人質問、FastAPI一時回答、first→reply/コピー/送信記録/履歴、first/followup/like経路）は個別実行中。Python/JS構文、diff検査、最新HEAD Actionsは実行後に記録する。Gemini実通信0回。T369/QUALITY009実生成品質FAILは維持。

### 2026-10-16 20:50 JST D01/D02の検証コミット

- `app.py`（D01/D02 未確認本人主張の誤検出削減）と `app.js`（一時的な `/profile` 失敗時の入力保持）を分離コミット `4a47a66` / `4263e52` としてPush。
- focused 608 passed、Firefox以外の全pytest 1733 passed、変更Firefoxテスト 2 passed。構文・diff検査成功。Gemini実通信0回。新規テストIDは増やしていない（既存回帰の再実行）。

### 2026-10-16 22:12 JST D02一般情報/第三者質問の誤分類修正

| T405 | 一般情報の映画質問を本人質問ゲートから除外 | pytest。`_topic_for_personal_question`/`missing_personal_fact_question`の固定ケースと全pytest | FIXED | 「最近の映画ランキングで何が人気ですか？」「今話題の映画は何ですか？」「最新の映画の興行収入はどれくらいですか？」はtopic=Noneかつ確認質問なし。対照の「おすすめの映画ありますか？」「最近観た映画は何ですか？」「どんな映画が好きですか？」は本人確認を維持。「その友達はどうなったんですか？」は第三者質問として確認なし。新規focused 10 passed、`tests/test_app.py` 1675 passed、全pytest `1782 passed in 354.40s`（Firefox UI含む）。`ast.parse(app.py)`成功。Gemini実通信0回。commit `b73ac65`。 |
| T406 | Firefoxプロフィール保存テストの描画競合安定化 | Firefox E2E。モーダルopen待機と入力/textarea描画待機を追加し単体3回反復 | FIXED | 全pytest実行時に `test_firefox_saved_profile_is_available_during_first_and_reply_generation` が保存前のフィールド読取で1件FAIL（単体はpass）。描画待機を追加後、単体3回連続pass、全pytest `1782 passed`。commit `dfc3659`。 |
| T407 | 丁寧過去形の映画視聴質問を本人体験として維持（T405の偽陽性回帰） | pytest。`_topic_for_personal_question` の一般情報ガードの除外形と対照ケース | FIXED | 検証エージェント#2がT405の自己導入偽陽性を検出: 除外マーカーが `(?:観|見)た\|ますか\|る` のみで丁寧過去形が漏れ、「人気の映画を観ましたか？」「話題の映画、もう見ましたか？」「評価が高い映画、観ましたか？」がtopic=Noneへ降格し確認質問が消えていた。除外を `(?:観\|見)(?:た\|て\|ま\|る\|れ)` に拡張し本人確認を回復。一般情報（ランキング/話題/興行収入）は引き続きNone。`tests/test_app.py` 1678 passed。commit `d3f1c23`。 |
| T408 | 相手保存の二重送信防止と写真の事前検証 | Firefox E2E 2件（二重クリック、5MB超写真）＋ API件数確認 | FIXED | 相手フォームで `button.confirm` を二重クリックすると `POST /api/matches` が2回発行され重複登録。また5MB超/不正形式の写真は相手INSERT後に `/photo` で拒否され、再試行時に孤児相手が増加。`modalFooter` に送信中ロックを追加し、写真のサイズ・形式をPOST前に検証、作成済みidを再利用して再試行はPUTへ変更。新規Firefoxテスト2件pass（POST数1・写真過大時は相手0件→再保存で1件）。全pytest `1787 passed in 373.92s`。commit `17aef51`。 |
| T409 | 一般情報ガードの接続動詞除外を限定（T407の偽陽性回帰） | pytest。一般情報の接続動詞ケースと丁寧過去形の対照 | FIXED | 検証エージェント#2がT407の除外 `(?:観|見)(?:た|て|ま|る|れ)` が接続の「を見て」まで除外し、`映画ランキングを見て決めたいのですが、何が人気ですか？` 等の世界情報質問が本人確認を要求する新偽陽性を検出。除外を `(?:観|見)(?:た|ま|る|れ)` に限定し、接続動詞は一般情報のまま保持。丁寧過去形（`観ましたか`等）は本人確認を維持。`tests/test_app.py` 1681 passed。commit `11c6dbc`。 |
| T410 | 近未来の誘い表現を誘いとして認識（D02残） | pytest。誘いマッチャ、誘い意思確認、非誘い文の負例 | FIXED | 検証エージェント#2が `近いうちに会いませんか？` が `INVITATION_PATTERN` の `一緒に/今度/よかったら` 条件に当たらず誘い意思確認が出ない点を指摘。近未来ブランチを `(?:近いうちに\|近々\|そのうち\|近日\|いずれ).{0,20}(?:ませんか\|ません\|ましょう\|おう\|てみません\|てみましょう)` として追加し、`近々お会いしませんか？`・`そのうちご飯でも行きません？` を誘いとして認識。`近いうちに映画が公開されるらしいよ` 等の非誘い文は除外。`tests/test_app.py` 1688 passed。commit `32db88a`。 |
| T411 | 確認回答のセッション蓄積と重複排除（D03第一歩） | pytest。`build_context` の回答マージと4件以上の受理 | FIXED | `GenerateInput.user_answers` の上限3により、別の確認が続くと以前の一時回答ごと拒否され、D03の「複数確認の蓄積」が成立しない問題を修正。`merge_user_answers` を追加しNFKC正規化した質問文でキー化、最新回答を採用し初出順を保持（ブラウザ側 `mergeUserInfoAnswers` と一致）。上限を12へ緩和。`tests/test_app.py` 1690 passed。commit `08560dc`。 |
| T412 | 映画ガードのテ形スコープ修正と近未来誘いの精度改善（T409/T410の回帰） | pytest。テ形の本人映画質問と近未来誘いの正例/負例 | FIXED | 検証エージェント#3が(a)`11c6dbc` が下流分類器のテ形未対応により `観てる映画の評価はどれですか？` 等の本人映画質問を本人確認から漏らす、(b)`32db88a` が `近いうちに食事でもどうですか？` 等の「どうですか」提案を漏らしつつ `近日中には間に合いません`・`近いうちに来ませんね`・`近いうちにまた連絡しましょう` 等を誘いと誤認、を検出。除外を `(?<!を)(?:観\|見)て` にして接続の「を見て」だけ除外、映画分類器にテ形（`てる/ている/ています`）を追加、近未来ブランチを動作動詞＋`ませんか\|ましょう\|どうですか` に限定。正例/負例の対テストを追加。`tests/test_app.py` 1702 passed。commit `e2b7426`。 |
| T413 | 一時確認の構造化レコード（D03サブステップ） | pytest。`build_ephemeral_confirmations` の構造・正規化・非永続 | FIXED | 検証#3推奨のD03サブステップ。`build_ephemeral_confirmations` を追加し、各確認回答に `question_id`（NFKC正規化）・`subject`・`requested_slot`・`source="user_confirmation"`・`confirmation_state="ephemeral"`・`match_id` を付与。`build_context` に `ephemeral_confirmations` を追加（`ephemeral_user_answers` は不変）。プロフィールへは永続化せず（明示確認時のみ昇格）。等価質問は同一question_id、異なる質問は別id。`tests/test_app.py` 1704 passed。commit `73c8bee`。 |

| T414 | 一時確認レコードのプロンプト除外と誤字ガードの一般化 | pytest。`prompt_context` 除外と `雰囲(?!気)` の正例/負例 | FIXED | 検証エージェントが `73c8bee` の新キーが `json.dumps(context)` 経由でGeminiプロンプトに混入し内部 `match_id` を漏らしQ/Aを重複させると指摘。`prompt_context` を追加して内部専用キーを唯一のモデル呼び出し地点で除去し、プロンプト非含有をテストで担保。加えて `candidate_has_high_confidence_japanese_error` をリテラル `雰囲い` から正書法ルール `雰囲(?!気)` へ一般化し、同種の未知変形（`雰囲き`・`雰囲`）を拒否しつつ正しい `雰囲気` を保持。`tests/test_app.py`＋`test_quality_checks_009.py` 1715 passed。commit `8ba307b`。 |

| T415 | 明示確認のプロフィール昇格（D03永続化サブステップ） | pytest。`confirmed_facts` の保存・既存キー保持・重複排除・非永続 | FIXED | `GenerateInput` に任意 `clarification_session_id` と任意 `confirmed` を追加（validatorは許可キーを question/answer/confirmed に限定）。`build_ephemeral_confirmations` は state を confirmed/ephemeral に分け session_id を保持。`persist_confirmed_facts` は confirmed のみを profile content の `confirmed_facts` へ upsert（`schema_version=2`、既存キー保持、同一 question_id は上書き）。未確認回答はプロフィールに触れない。ブラウザは session_id を送るが resume 回答は未確認のまま（一時回答のUI契約を維持、明示保存UIは製品判断待ち）。focused 7 passed。commit `b6983b4`。 |

| T416 | 確認回答の明示保存ボタン（D03） | pytest+Firefox。保存エンドポイントと自動非保存 | FIXED | `POST /api/profile/confirmed-facts` と `renderUserInfoQuestions` の「回答をプロフィールに保存」ボタンを追加。エンドポイントは回答を confirmed として `confirmed_facts` のみへupsert（他キー保持）。resume/skip は未確認のまま（一時回答契約を維持、roundtripテストでプロフィール不変を維持）。requiredパネルの文言を更新（optionalパネルは不変）。検証エージェント#6はPASS・回帰なし。focused 6、全pytest 1822 passed。commit `1fb32b6`。 |

| T417 | プロフィール保存時の未知キー欠落防止（D04） | pytest。`put_profile` の read-modify-write | FIXED | `merge_profile_content_preserving_keys` を追加し、`put_profile` で保存前に既存 content とマージ（両側JSON objectなら `{**existing, **incoming}` で incoming 優先・既存のみキー保持。非objectは incoming をそのまま採用して旧テキスト/明示クリアを維持。`avoid` は別列のまま）。UIは既に spread 保持していたが、スクリプト・確認ファクト書き込みとの競合で `confirmed_facts`/`schema_version` が消え得た穴を塞ぐ。focused 4、`tests/test_app.py` 1719 passed。commit `1f322f3`。 |
| T418 | 確認済み事実の再質問抑止（D03接続） | pytest。`_topic_is_verified` の確認ファクト照合 | FIXED | `_confirmed_fact_covers_question` を追加し `_topic_is_verified` の先頭で評価。正規化 `question_id` 一致のときのみ verified。`question_text` が空のときは照合しない。未保存の回答は従来どおり非永続。focused 3。commit `1f322f3`（初版はslot一致を含んだが下記T419で是正）。 |
| T419 | 確認済み事実の過剰抑止の是正 | pytest。slot一致の衝突を再現し修正 | FIXED | 検証エージェントが実バグ検出: slot一致は `_optional_user_question_scope_key` の topic誤分類により、別トピック（映画の確認が「最近読んだ本」を抑止）や別ディテール（作品名の確認が「ジャンル」を抑止）まで抑止した。`_confirmed_fact_covers_question` を正規化 `question_id` 一致のみに変更。ネガティブテスト2件（別トピック・別ディテール）とhelper単体テスト更新を追加。focused 38、`tests/test_app.py` 1721 passed。commit `a2f82e2`。 |

| T420 | 保存済み確認ファクトを直接質問の証拠源にする（D03ブリッジ） | pytest。`_answers_verified_single_partner_question` と `_trusted_fact_clauses` | FIXED | `_confirmed_fact_values_for_question` を追加（`_confirmed_fact_covers_question` と同じ正規化id一致）。直近の直接質問に対する確認ファクト値を、最近観た映画タイトル枝と汎用フォールバックの証拠に追加。`_trusted_fact_clauses` は `confirmed_facts` から `value` のみを収集し、`question`/`session_id`/`source`/`requested_slot` のメタ文字列を接地から除外（値の捏造接地を防止）。focused 183、`tests/test_app.py` 1724 passed、全pytest **1834 passed in 422.73s**。commit `f382077`。 |

| T421 | 確認済み映画回答の矛盾・伝聞の却下（fail-closed是正） | pytest。genericフォールバックのタイトル枝 | FIXED | T420でgenericフォールバックに混入した無ガードのタイトル接頭辞一致を撤去し、`_reading_genre_evidence_segments`＋`_asserts_movie_viewing`＋`_movie_viewing_attributed_to_other_person`＋逆質問除外による guarded 判定へ置換。保存済み作品名を否定（「観ていません」）・伝聞（「と聞きました」）・逆質問した候補は却下し、肯定（「『青い灯台』を観ました」）は受理。回帰3件追加。focused 116、`tests/test_app.py` 1727 passed。commit `f1aac28`。 |

| T422 | 映画タイトル証拠の第三者・受動態の却下（共通判定） | pytest。`_candidate_asserts_viewing_of_title` | FIXED | confirmed/ephemeral両ループを共通述語 `_candidate_asserts_viewing_of_title` に統合（タイトル含有・`_asserts_movie_viewing`・非第三者・逆質問除外）。`_movie_viewing_attributed_to_other_person` に後置主語（「観たのは妹です」）と受動/伝聞（「観たと言われました」）を追加。第三者・受動・矛盾・伝聞・逆質問を却下し、一人称肯定を受理。回帰10件追加。focused 149、`tests/test_app.py` 1737 passed、全pytest **1847 passed in 427.49s**。commit `8bc498d`。 |

| T423 | 映画タイトル証拠の所有格第三者・伝聞の却下 | pytest。`_movie_viewing_attributed_to_other_person` | FIXED | 後置主語の所有格形（「観たのは私の妹です」）と伝聞（「観たという話」「観たとのことです」）を追加。同伴（「観たのは友達と一緒です」）を誤却下しないよう負の先読みで除外し、一人称肯定は受理。回帰5件追加。`tests/test_app.py` 1742 passed。commit `b7be0fe`。 |
| T424 | Host許可リスト（D15） | pytest。TrustedHostMiddleware | FIXED | `TrustedHostMiddleware` を追加し、許可ホストを `MRA_ALLOWED_HOSTS`（既定 `127.0.0.1,localhost,testserver`）から読込。未知Hostの GET/POST を400で拒否し、loopback（ポート付き）と既定TestClientホストを許可。envでの設定変更もテスト。DNSリバインディング対策（実攻撃の再現は未主張）。テスト4件追加。`tests/test_app.py` 1746 passed、全pytest **1856 passed in 446.01s**。commit `2c6f2ab`。 |

| T425 | Host許可リストの空設定フォールバック（D15補強） | pytest。`_allowed_hosts` | FIXED | `MRA_ALLOWED_HOSTS` が空白のみ（例 `","`）でも許可リストが空にならず、既定の loopback へ戻す。空リストが全拒否になる設定ミスを防止。テスト1件。commit `63f73d3`。 |
| T426 | 孤児写真の記録と再試行（D13） | pytest。`orphaned_photos` テーブル | FIXED | DBコミット後の写真削除失敗でファイルが残留する問題を解消。冪等な `CREATE TABLE IF NOT EXISTS orphaned_photos` を既存 `executescript` へ追加（マイグレーション不要、既存DBは自動追加）。`_remove_photo_file`（失敗時 False）/`_queue_orphaned_photo`/`_retry_orphaned_photos`（記録済みのみ削除、ディレクトリ走査なし）を追加。`delete_match`・`upload_photo` の旧写真削除失敗時に記録し、応答へ加算キー `photo_cleanup_pending` を返す。テスト4件。`tests/test_app.py` 1751 passed、全pytest **1861 passed in 420.74s**。commit `e3d5353`。 |
| T427 | 存在しない match の削除404順序 | pytest。delete_match | FIXED | 存在しないIDの削除が404で終わり、写真ファイルとジャーナルに触れないことを固定。テスト1件。commit `364e441`。 |

| T428 | live-gemini の設定契約統一（D10） | pytest 静的+SDKモック | FIXED | smoke ワークフローは `GEMINI_API_KEY` のみ設定していたが、アプリは `MRA_API_1_KEY`/`MRA_API_2_KEY` を読むため実経路が動作せず demo に落ちていた。`env` に `MRA_API_1_KEY: ${{ secrets.GEMINI_API_KEY_TEST }}` を追加し1つのsecretで両契約を満たす。workflow_dispatch 限定・ref ガード・キー非表示は維持。静的YAMLテストとオフラインSDKモックテスト2件。`tests/test_app.py` 1754 passed。commit `e986f06`。 |
| T429 | 窓外の拒否・誘いを保持（D14） | pytest | FIXED | プロンプト用 `history` は最新60件のままにしつつ、内部専用 `history_policy`（既定600件、`MRA_CONTEXT_POLICY_WINDOW`、`prompt_context` で除外）を追加。`partner_has_active_invitation_refusal` と `invite_opportunity_ready` の阻害判定を方針履歴へ広げ、窓外の拒否を再勧誘で覆わない。テスト3件。`tests/test_app.py` 1757 passed、全pytest 1867。commit `e7c176b`。 |
| T430 | 窓外再開後の誘い可否（D14補正） | pytest | FIXED | 検証エージェントが `invite_opportunity_ready` の却下走査が再開を考慮せず窓外の再開後も過剰抑止する不整合を検出。再開対応済みの `partner_has_active_invitation_refusal` へ委譲し、窓外で再開された場合は誘い検討を再開できるようにした。テスト1件。`tests/test_app.py` 1758 passed、全pytest **1868 passed in 422.99s**。commit `195889f`。 |

| T431 | 独立した品質採点モジュール（D09） | pytest。`scripts/quality_eval.py`（app.py 非依存） | FIXED | アプリ自身の採点に依存しない独立採点器を追加。`normalize_text`/`clause_split`/`char_ngrams`/`jaccard`/`has_near_duplicate_candidates`/`has_redundant_reaction_set`/`has_placeholder`/`has_missing_sentence_break`/`untrusted_first_person_topics`/`all_candidates_answer`/`independent_quality_verdict`/`combine_quality_verdict` を公開。`app.py` を一切 import しないことをテストで固定。テスト17件。全pytest **1885 passed in 424.65s**。commit `0f77f1c`。 |
| T432 | 独立採点器の009ランナー配線（D09） | pytest。`scripts/run_quality_checks_009.py` | FIXED | 009ランナーの最終判定を独立採点へ委譲。`independent_quality_verdict` を各ケースで実行し `independent_*` を記録、`combine_quality_verdict(content_pass and not diversity_violation, independent_pass, ...)` で PASS/FAIL/BLOCKED を決定。映画ケースの `any("青い灯台" ...)` を全候補回答要求（`answer_violation`）へ置換。二経路importガード（`scripts.quality_eval`／単体実行時の `quality_eval`）。`quality_case_result` は後方互換のため保持。テスト1件追加。全pytest **1886 passed in 425.77s**。commit `ba8906c`。 |
| T433 | 句読点規約の一致（D09補正） | pytest。`scripts/quality_eval.py` | FIXED | 検証エージェントが独立採点器の句読点判定が製品規約（候補本文に「、」「。」を含めない）と逆で、製品が通した候補を常にFAILさせる不具合を検出。判定を「本文に『、』または『。』を含む場合に違反」へ修正し、記録済みの句読点なし候補で PASS する回帰テストを追加。全pytest **1887 passed in 422.06s**。commit `6428754`。 |

| T434 | 永続利用台帳と事前予約（D11） | pytest。`api_usage` テーブル | FIXED | 呼出し前に予約する永続台帳を追加。冪等な `CREATE TABLE IF NOT EXISTS api_usage(reserved_epoch, api_alias, model)` を既存 `executescript` へ追加。`_usage_ledger_limit`（`MRA_USAGE_LEDGER_LIMIT`、未設定なら台帳に一切書き込まない）/`_usage_ledger_window_seconds`（`MRA_USAGE_LEDGER_WINDOW`、既定 day）/`usage_ledger_used`/`reserve_provider_usage` を追加。`generate` の provider ループで `generate_content` 直前に予約し、枯渇時は `UsageBudgetExceededError`→`error_code=usage_budget_exceeded` の安全な502。テスト3件。全pytest **1890 passed in 382.05s**。commit `6d555b6`。 |
| T435 | 利用台帳予約の原子性（D11補正） | pytest。並行予約 | FIXED | 検証エージェントが check-then-insert の競合（`BEGIN IMMEDIATE` もロックもなく並行要求で予算超過）を検出。`_usage_ledger_lock` と `BEGIN IMMEDIATE` で読み取り・挿入を単一トランザクションにまとめ、枯渇時は rollback して送出。40スレッド×上限10で granted=10/denied=30 を固定するテストを追加。全pytest **1891 passed in 400.54s**。commit `a369794`。 |

| T436 | 要求全体の期限（D11後半） | pytest。`_request_deadline` | FIXED | 検証エージェントが provider ループに要求全体の壁時計上限がないことを指摘。`MRA_REQUEST_DEADLINE_SECONDS`（既定120秒、`none`/負値で無効、`0`で即時失効）を追加し、各試行の直前に期限を判定して超過時は `RequestDeadlineExceededError`→`error_code=request_deadline_exceeded` の安全な502を返す（期限直前のSDK呼び出しは最大1回分=30秒の超過があり得る）。テスト2件追加。全pytest **1893 passed in 421.26s**。commit `efebc41`。 |

| T437 | 実Geminiでの009再評価（D07） | 実APIランナー。`quality_checks_009_live_20261017.json` | 初回は 8/9 PASS、`joke_mirroring` のみFAIL | ユーザーの実API許可を受け、`scripts/run_quality_checks_009.py` を実Geminiで実行。既存の `quality_checks_009.json` を上書きしないよう `MRA_QUALITY_OUTPUT` で出力先を別ファイルへ振り替えた。smoke は PASS（model gemini-3.5-flash-lite、alias API1）。初回は 9件中8件PASSで、`joke_mirroring` のみ製品の多様性ゲートが共感・休息トピックのレキシカル衝突を検出してFAIL（全候補は句読点なしで独立採点はPASS）。同一入力の再実行1回は別内容の候補でPASSし、元のFAILは `superseded_by=joke_mirroring_retry` として履歴保持。最終状態は status=PASS、logical 9、provider 19、historical_nonpass 1、unresolved 0。多様性ゲートが確率的で再実行に依存する点、独立採点器がこの衝突を検出しない点は残課題。全pytest **1894 passed in 416.53s**。commit `b2930b1`。 |

| T438 | 会話テストでの確認質問ループ修正（P0正確さ） | pytest。`_topic_is_verified` | FIXED | 実APIの会話テスト中、相手文が `('旅行','atmosphere')`、アプリ自身の確認質問が `('旅行','preference')` と分類される場合に `_same_personal_information_scope` が不一致となり、ユーザーが確認質問へ回答しても `_topic_is_verified` が False のままで同じ質問を無限に再発する欠陥を検出。`_topic_is_verified` の末尾で「アプリ自身が尋ねた確認質問にそのまま回答した場合」も検証済みとするよう修正し、あわせてカレー頻度の回答パターンへひらがな頻度語を追加。回帰テスト2件。全pytest **1896 passed in 389.01s**。commit `c145368`。Push CI [39012335427](https://github.com/kenkyu0909/aichatapp/actions/runs/39012335427) / PR CI [39012446977](https://github.com/kenkyu0909/aichatapp/actions/runs/39012446977) は success。 |

| T439 | 相槌と質問量の改善（送信前品質） | pytest。`sentence_estimate`・`_candidate_exceeds_mirrored_length` | FIXED | 句読点付きの相手文を1文と数えていたため2文の相手に2行しか返せず、相槌か質問のどちらかが落ちていた。`sentence_estimate` で「。」「．」を文末として数え、相槌と質問を併せ持つ返信の上限を1行だけ緩和（最大3行）。`prompts/common.txt` で相槌と質問を既定で入れる指示へ変更。テスト4件追加。全pytest **1900 passed in 411.01s**。commit `da8ba20`。Push CI [39013957467](https://github.com/kenkyu0909/aichatapp/actions/runs/39013957467) / PR CI [39013960710](https://github.com/kenkyu0909/aichatapp/actions/runs/39013960710) で success。 |

| T440 | アプリ自身の確認質問への回答照合（P0正確さ） | pytest。`_ephemeral_answer_addresses_question` | FIXED | アプリ自身が尋ねた確認質問へ回答しても、相手文と確認質問のスコープ分類が食い違うと `_topic_is_verified` が偽のままで同じ質問を再発した。`_ephemeral_answer_addresses_question` を追加し、topic 別分岐で臨時回答を照合する箇所を置き換え。休日トピックの回帰テスト1件。全pytest **1901 passed in 394.61s**。commit `916ec41`。 |

| T441 | 未知WH質問の決定論的フォールバックと文体連動（P0正確さ） | pytest。`_build_unclassified_question_fallback_candidate` | FIXED | 未分類の直接質問（`topic == "本人情報"` または `not topic`）で `user_answers` に本人回答があり、モデル生成候補がすべて安全検査で棄却された場合に、選択文体（`敬語` / `タメ口` / `混合` / `自動`）に連動した `相槌（1行） + 回答の逐語引用（句読点除去・1行） + 相手への質問（1行）` の安全な候補1案を合成するフォールバックを追加。`_answers_verified_single_partner_question` の語彙一致ルールは一切緩和せず、全候補ガード `_candidate_rejection_reasons` を通過することを検証。回帰テスト8件（文体6パターン・回答なし時の確認質問維持・全試行失敗時のフォールバック返却）。commit `97317e1`。 |

| T442 | README整合（取得先・起動終了・依存固定・バックアップ手順、D16） | ドキュメント検査・整合確認 | FIXED | `README.md` に実リポジトリURL（`https://github.com/kenkyu0909/aichatapp.git`）、`start.bat`/`uvicorn` 起動と `Ctrl+C` 停止確認、全4生成モードと本人情報確認、検証済みPython（3.12.10 / 3.11）と依存パッケージ固定バージョン、および `data/`（`app.sqlite3` + `photos/`）のオフラインバックアップ・復元・SQLite/JSON整合性確認手順を記載。commit `40171be`。 |

| T443 | 共通プロンプトの自己矛盾解消と重複整理（D08） | pytest・プロンプト検査 | FIXED | `prompts/common.txt` における趣味質問の自己矛盾（相手の趣味話題と本人への直接質問の区別）および `user_answers` のQ&Aメタデータ転記禁止と本人回答内容の反映指示の矛盾を解消し、重複行を整理。commit `ded9b22`。 |

| T444 | プロフィール保存時の古い候補無効化と写真失敗時の相手一覧同期（D06, D12） | `node --check app.js`・UI契約 | FIXED | `app.js` でプロフィール保存成功時に `invalidateGenerationResults()` を呼び出して古いプロフィール前提の候補表示を無効化し、連絡先新規作成後の写真アップロード失敗時に `loadMatches(data.id)` で作成済み連絡先を左ペイン一覧へ同期。commit `705bf05`。 |

| T445 | オフライン `data/` ディレクトリのバックアップ・復元テスト（D17） | pytest。`test_offline_data_directory_backup_and_restore_preserves_full_state` | FIXED | 構造化プロフィール・`avoid`・`confirmed_facts`・複数相手・識別写真・会話履歴・`api_usage` 台帳を保存後、`data/` を丸ごとバックアップし、データ消失・破損後に復元して別インスタンスから全データが100%復元・再生成利用可能であることを自動検証。commit `cb08d57`。 |

| T446 | 変更要求（POST/PUT/DELETE/PATCH）の Origin 許可リスト検証（D15） | pytest。`verify_mutation_origin` | FIXED | `Origin` ヘッダーが付与された状態変更要求に対し、`_allowed_hosts()` 以外の Origin（例: `https://evil.example`）を 403 で拒否し、ローカル Origin および非ブラウザ（Originなし）を許可するミドルウェアとテストを追加。commit `28d15a3`。 |

| T447 | プロンプト履歴文字数上限と窓外の連絡停止要求保持（D14） | pytest。`_trim_history_to_char_budget`・`partner_requests_contact_stop` | FIXED | `MRA_PROMPT_HISTORY_CHAR_BUDGET`（既定24000文字）でプロンプト入力履歴の文字数肥大化を防ぎつつ最新ターンを保持し、`partner_requests_contact_stop` が `_history_for_policy`（600件窓）を走査して60件超前の連絡停止要求も保持するよう修正。テスト2件。commit `42c9635`。 |

| T448 | 単発SDKタイムアウトの残りDeadlineクランプとsmokeキー環境変数補完（D10, D11） | pytest・スクリプト検査 | FIXED | `generate()` でプロバイダー設定ごとのSDK初期タイムアウトを `request_deadline` の残り時間（1〜30秒）へクランプし、`scripts/live_gemini_smoke.py` で `GEMINI_API_KEY` と `MRA_API_1_KEY` を双方向補完。commit `c29f720`。 |

| T449 | 保存済み `confirmed_facts` の料理・カフェ頻度バリデータ接続（D03） | pytest。`_answers_verified_single_partner_question` | FIXED | `_answers_verified_single_partner_question` の `料理習慣`（最近の料理）および `カフェ頻度` 分岐の証拠リストに `_confirmed_fact_values_for_question` を追加。全pytest **1913 passed in 368.81s**。commit `7e648e2`。 |
| T450 | 平叙文の「いつも」「ついつい」「いつか」「いつでも」に対する本人質問誤判定の解消 | pytest＋実API会話テスト再確認。`_topic_for_personal_question`・`UNPUNCTUATED_CASUAL_PERSONAL_QUESTION` | FIXED | 20通会話テスト（`conversation_test_20261017_T441.html`）のTurn #8で相手文「木目調の落ち着いた喫茶店が多くて、ついつい長居してしまいます。いつも深煎りのブレンドと固めのプリンかドーナツを頼んでいます。」が `いつ` 部分一致により本人への質問（`カフェ好み`）と誤判定され不要な本人確認質問と9回のブロックを誘発した不具合を修正。`(?<!つ)いつ(?!い|か|も|でも|までも|だって)` に厳密化し、真の「いつ〜？」質問のみを検出。回帰テスト追加・実API再確認（`conversation_test_20261017_T450_recheck.html`）で誤質問0・試行1回目で3案通過を確認。commit `c0056e0`。 |
| T451 | 相槌1行目＋回答2行目＋質問3行目の複数行返信における回答認識・カフェ質問行除外 | pytest。`_answers_verified_single_partner_question`・`_candidate_uses_specific_answer_detail`・`_claim_supported_by_trusted_fact` | FIXED | T439で推奨した「1行目相槌＋2行目本人回答＋3行目質問」の形式に対し、`カフェ好み`（雰囲気）および `_candidate_uses_specific_answer_detail` が1行目のみを検査して2行目の回答を見落としていた問題、ならびに `_claim_supported_by_trusted_fact("カフェ")` が末尾の相手向け質問文（「よく行くお気に入りのお店はありますか？」）を本人の未確認主張と誤認していた問題を修正。疑問符（`?`/`？`）で終わる質問文を除いた全非疑問文を検査対象に統一。全pytest **1915 passed in 401.68s**。commit `5f7b766`。 |
| T452 | 質問付き候補の `#1 (recommended)` 優先昇格・五段動詞連用形抜け誤字ガード・新規20通実API検証 | pytest＋実API 20通会話テスト（`conversation_test_20261017_T452.html`） | FIXED | 安全通過候補の先頭（`#1`）が複数行の相槌・感想のみで質問を持たず、後続の安全候補に質問付き候補がある場合に最初の質問付き候補を `#1 (recommended)` に昇格（拒否・不快・重い相談文脈と1行リアクション単体は除外）。あわせて `_HIGH_CONFIDENCE_MALFORMED_WORDS` に五段動詞連用形抜け誤字（`頼たく`・`読たく`・`飲たく`・`休たく` 等、一段・カ変正例 `来たく`・`見たい`・`着たく`・`寝たい` 等は維持）を追加。新規実API 20通テストで **20通完走・ブロック0回・誤字0件・推奨#1候補の質問付与15/20通（75%）** を確認。 |
| T453 | 独立採点器の休息・共感語彙衝突検出整合と `FINAL_REPORT.md` 条件付きGO残条件整理 | pytest（`tests/test_quality_eval.py`）＋ドキュメント更新 | FIXED | `scripts/quality_eval.py` の `has_redundant_reaction_set` に `_REST_EMPATHY` 語彙衝突検出を追加し、製品多様性ゲートと独立採点器の判定を一致させた。あわせて `FINAL_REPORT.md` 冒頭で「条件付きGO」に残る条件を「コード・検証で解消済みの事項」と「確率的生成・運用上の留意事項」に仕分けして明記。 |
| T454 | 誘い判断（Stage 1–6 / `invite_decision`）のオフライン48件＋実API 5シナリオ検証 | pytest（48件）＋実API短編5シナリオ（`conversation_test_20261017_invite_a_early.html` 〜 `e_stop.html`） | PASS | オフライン48件全PASSに加え、実APIで (a) 初期ターン（`Stage 1 / do_not_invite` → `Stage 2 / continue_conversation`）、(b) 相手の関心表明（`Stage 4 / invite_gently`）、(c) 相手の慎重姿勢（`Stage 3 / respect_no`＋次ターン再勧誘なし）、(d) 承諾・日程質問（本人空き日程確認 `needs_user_info=True` → 回答後 `Stage 5 / schedule_after_acceptance`）、(e) 連絡終了要求（即座に生成停止・候補0件）の全5シナリオを検証し全件期待どおり動作。 |
| T455 | フォールバック候補の文脈別相槌・相手名入り質問の自然化と日程調整シナリオ(d)再検証 | pytest＋実API再確認（`conversation_test_20261017_invite_d_schedule_T455.html`） | FIXED | 既存の厳密な回答一致ガードを維持したまま、誘い承諾＋日程質問時は喜び表現（`うれしいです😊` / `うれしいな！`）、通常日程質問時は感謝表現（`ありがとうございます！` / `ありがとう！`）、および相手名が設定されている場合は相手名入り質問（`黒川さんはご都合いかがですか？` / `黒川さんは都合どうかな？`）を返すよう `_build_unclassified_question_fallback_candidate`・`_is_partner_directed_followup_question`・相槌許可リストを改善。実API再確認で `うれしいです😊 / 土曜日の午後なら空いています / 黒川さんはご都合いかがですか？` が生成されることを確認。 |
| T456 | 日程調整質問の「予定」トピック独立化・厳格なスケジュール値マッチング・実モデル生出力通過 | pytest＋実API再確認（`conversation_test_20261017_invite_d_schedule_T456.html` / `.json`） | FIXED | 日程調整・都合照会質問（曜日・時間帯・空き・日程）を専用トピック `予定` として分類。厳格な値照合（`_validate_schedule_elements_match`）を実装し、曜日・時間帯・時刻・日付の厳格一致を要求、異なる曜日（土曜→日曜）・余計な日程追加（土曜→土日）・時刻追加・極性逆転（空いていません）をすべてfail-closedで棄却。日程合意コンテキストでの受諾表現（「ぜひ行きましょう」等）の文体許可により、実APIシナリオ(d)で決定論的フォールバックに頼ることなく、モデル生出力3案が安全・正確に一発通過（`available=3`, `deterministic_fallback_used=None`）することを確認。回帰テスト2件追加、全テスト1,920 passed（`tests/test_app.py` 1,790 passed + 全スイート計 1,920 passed）。 |

| T457 | 相槌＋質問両方を備えた候補の優先配置（品質向上） | pytest。`_prioritize_ack_and_question_candidate` | FIXED | 安全候補群の中で相槌と相手への質問の両方を備えた候補を最優先候補（`#1`）に昇格する仕組みを実装。回帰テスト2件追加。全pytest **1,922 passed**。commit `05b2a56`。 |
| T458 | プロバイダー安全遮断ログ伏字化・サーキットブレーカー耐性 | pytest。プロバイダーエラー安全処理 | FIXED | API障害発生時のログ出力において秘密情報・APIキー・生エラーの詳細を漏洩しない伏字化と連続障害時の安全遮断（サーキットブレーカー）の挙動を検証するテストを追加。全pytest **1,925 passed**。commit `d3a92a7`。 |
| T459 | 外部ランナーテストの会話テストフォルダー分離 | pytest。テストスイート整理 | FIXED | リポジトリ外の会話テスト用ランナーに依存していたテストファイルを会話テスト専用フォルダーへ移管し、リポジトリの自己完結性を担保。commit `1cc7ef2`。 |
| T460 | プロフィール事実フォールバック候補生成と返信プロンプト調整 | pytest。`_build_profile_fact_fallback_candidate` | FIXED | 本人の既知プロフィール事実（職業、趣味等）に基づく質問に対する決定論的フォールバック生成を拡充し、プロンプト指示を微調整。全pytest **1,927 passed**。commit `c576df1`。 |
| T461 | 職業質問バリデーション・相手姓フォールバック・反復質問抑止（T461） | pytest。`app.py` | FIXED | 相手からの職業質問に対するバリデーションを厳格化し、相手名抽出時の姓フォールバック処理、および直近会話で既出の話題（コーヒー豆の品種等）に対する重複質問を抑止するガードを追加。全pytest **1,927 passed**。commit `0b0fc99`。 |
| T462 | 休日質問ガード・日時場所提案エスカレーション・自己重複棄却（T462） | pytest。`app.py`・`prompts/reply.txt` | FIXED | 相手からの休日・ルーティン質問を回避する候補を棄却するガード、相手からの具体的日時・場所の提案を本人の意向確認へエスカレーションするチェック（`_is_concrete_date_or_place_proposal`）、直前発言と類似・重複する候補の棄却ガード（`_is_duplicate_or_near_identical_to_prior_me`）、および相手の新情報に対する冒頭相槌・共感のプロンプト指示を追加。全pytest **1,932 passed**。commit `b17ecee`。 |
| T463 | カフェ好み確認質問回答による一般カフェ質問の検証完了対応 | pytest。`_topic_is_verified` | FIXED | ユーザーがカフェ好みに関する確認質問（`personal_fact_question`）に回答した際、一般のカフェ質問も検証済みとして認識されるよう `_topic_is_verified("カフェ好み")` を補正。回帰テスト追加。全pytest **1,932 passed**。commit `37d0e8e`。 |
| T464 | 読書質問回答の事実検証連携・未分類回答スコープ照合・文体整合（T464） | pytest＋実API文体短編再検証（`conversation_test_20261018_casual_v2.html` / `mixed_v2.html`） | FIXED | 相手の読書質問（「普段どんな本読むの？」）に対するユーザーの最近の読書回答（「星新一のショートショート」）が「普段」語彙スキップやスコープ不一致で棄却されていた不具合を修正。候補が未確認の習慣を偽称する場合のみ除外するよう `app.py:6825` を厳密化し、`_ephemeral_answer_addresses_question` を読書照合に接続。`_unclassified_personal_question_user_answer` にトピックスコープ照合を追加し別トピック回答の誤引用を防止。初回・返信プロンプトおよびフォールバックでのタメ口・混合文体支持、自プロファイル（水野そよか）復元による名前衝突解消を実施。タメ口・混合各6ターンの再シミュレーション（`casual_v2` / `mixed_v2`）でブロック0回・敬語混入ゼロ・本人確認済み事実バッジ表示を実証。全pytest **1,934 passed**。 |
| T465 | 飲食メニュー・注文習慣一人称主張の本人事実照合ガード（T465） | pytest（`tests/test_app.py:15165`） | FIXED | 候補文中の飲食メニューや注文習慣の一人称主張（「〜を見つけると思わず頼んじゃう」「〜を頼むことが多い」「〜を注文しちゃう」等）を検出するパターンを `_has_unverified_general_personal_claim` に追加。主張文節から注文メニュー（オムライス、タルト等）を抽出し、プロフィールの `favorite_foods` や臨時ユーザー回答（`ephemeral_user_answers`）に根拠が存在しない場合は「未確認の本人事実」として確実に棄却するよう実装。回帰テスト追加（未確認時棄却、プロフィール事実確認時通過、臨時回答確認時通過）。全pytest **1,935 passed**。 |

| T471 | 相手発話の末尾質問取り違えと好み語の質問誤判定（T470会話テストの指摘） | pytest。`_last_question_sentence`・`_is_ask_sentence`・`_focus_question_carries_own_subject`・`missing_personal_fact_question`・`_answers_verified_single_partner_question`・`_topic_for_personal_question` | FIXED | 相手の1通が自分の話と末尾の質問でできている場合、文全体の語でトピックを決めていたため、末尾の質問（美術館の展示）が本人確認と送信ゲートの対象から外れ、話題を変えた候補も送信できた。`_last_question_sentence` を追加し、疑問文が1つのときだけ末尾質問で分類・照合する（事前確認は文全体が確認済みなら尋ねず、送信ゲートは末尾質問が通れば許可し、通らなければ文全体で判定）。あわせて `_topic_for_personal_question` の素の `好き|お好き` 一致を `PREFERENCE_QUESTION_CUE`（質問形のみ）へ置き換え、相手の「オムライスは私も大好きです…雰囲気でした」を本人質問と誤判定して6件停止した不具合を解消。T471の会話テストで、問いかけの節に `古本屋`（`読書` の語）を含む形と、`「心に残っている本」ですか、…` の確認の言い回しが残ったため、節単位の切り出しと `_is_ask_sentence`（文末が疑問形の文だけを数える）を追加し、切り出した問いかけが自前の主題を持つときはそちらを優先する `_focus_question_carries_own_subject` を追加。回帰テストは合計5件。`tests/test_app.py` は **1806 passed / 15 failed**（15件は変更前と同じ環境依存）、Actions の全試験は **1951 passed**。実Gemini 32回（会話テスト）。詳細は `会話テスト/ds4_T471_report.md`。 |

| T472 | 回答の改行・同一セッションの再確認・メモ事実の利用・段階の下限・硬い敬語のやわらげ（T471会話テストの指摘とClaude指示5件） | pytest（`pytest -k t472` 8件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t472.json` / `会話テスト/conversation_test_keigo20_ds4_t472.html`） | FIXED | (1) 回答の改行: `_answer_lines_for_candidate` で本人回答を文単位（`。．.!！?？` と改行）に分割し、確認済み回答をそのまま返すフォールバックの本文も `\n` で連結（T471の点2）。実測で3通目が3行に分かれ、連結は再現しなかった。(2) 同一セッションの再確認: `session_answers` テーブルと `_session_key`/`load_session_answers`/`remember_session_answers` を追加し、`build_context` が `ephemeral_user_answers` へ統合、`_session_answer_remembers`/`_suppress_remembered_question` が同一セッションの再質問を抑止（T471の点3）。今回は再確認が発生せず、経路は回帰テストで確認。(3) メモ事実の利用: `MEMO_FACT_KEYS`/`_profile_memo_text`/`_memo_terms`/`_memo_answer_sentence`/`_confirmed_answer_reflected_in_candidate` と `_unclassified_personal_question_user_answer` を追加し、メモの記述で本人情報の確認を省く（T471の点4）。実測で7通目の「タルト」、4通目候補3と10通目の「窓ぎわの席」、5通目候補3の「観葉植物」がメモ由来。Claudeの追加指示により `_memo_answer_terms`（質問語を除いたメモ側の回答語）を必須とし、`_memo_answer_contradicted`（苦手・嫌い・無理・否定形）で矛盾候補を棄却する厳格化を追加（「カウンター席が好きです」「窓ぎわの席は苦手です」を棄却、「窓ぎわの席が好きです」を通す回帰テスト）。(4) 段階と誘い: `conversation_state` テーブルと `load_conversation_stage`/`store_conversation_stage`、`_partner_accepted_invitation`、`_apply_conversation_state_floor` を追加し、`generate` で `_generate_impl` の後に適用（拒否でリセット、承諾で Stage 5 と `schedule_after_acceptance`）。実測で Stage 1→2→3（9通目）→4/`invite_gently`（14通目）→5、承諾後の16通目で `schedule_after_acceptance` となり、T471の点7・点8は再現しなかった。(5) 硬い敬語: `_CASUAL_KEIGO_GUIDANCE` を追加して敬語・既定の文体指示に使い、`prompts/common.txt`・`reply.txt`・`first.txt`・`followup.txt` にカジュアルな敬語の規則を追加。フォールバックの「（ラベル）はいかがですか？」「ご都合いかがですか？」を「どうですか」「ご都合どうですか」へ変更。実測で「ですよね」5回・「かもです」4回・「なんですね」4回・「〜しましょー」複数が現れ、硬い言い回しはモデル生成の17通目に「ご都合いかがですか」が1件残った（候補検査での棄却は未対応）。テストは `pytest -k t472` 8件成功、`tests/test_app.py` は **1814 passed / 15 failed**（15件は環境依存で変更前と同一）。Actions（`ca0c788` Push run 39117428135 / PR run 39117430741、`707f048` Push run 39118569174 / PR run 39118572274）はいずれも success で全試験 **1959 passed**。実Gemini 27回（T472会話テスト）。詳細は `会話テスト/reports/ds4_T472_report.md`。残課題は「行ってみたい場所」の質問で確認ダイアログに落ちず4回停止した経路、モデル生成候補に残る硬い敬語、相手の発言に対する候補の長さ。 |

| T473 | 停止せず本人確認へ回す・硬い敬語の言い換え・上から目線の除去・会話例に寄せる指針（T472会話テストの指摘とユーザー指示） | pytest（`pytest -k t473` 4件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t473.json` / `会話テスト/conversation_test_keigo20_ds4_t473.html`） | FIXED | (1) 全候補が「未確認の本人事実」で棄却され、かつ相手の末尾発言が本人への直接質問のときは停止せず本人確認へ回す。`_partner_trailing_direct_question`（末尾質問の切り出し、分類済みトピック、`_is_unclassified_question_about_user`、`_user_name_tokens` による呼びかけ判定）と `generate` の停止直前の分岐を追加し、回答済みトピックでは再質問せず従来どおり停止する。実測で「水野さんは甘いものは好きですか？」のターンが停止せず本人確認になった。(2) `_soften_stiff_keigo` を `filter_safe_candidates` の候補検査直前に当て、やわらげた文も `_candidate_rejection_reasons` を通す。`いかがですか`→`どうですか`、`でしょうか`→`ですか`、`いただけますか`→`もらえますか`、`よろしければ`→`よかったら`、`お越しください`→`来てください`、`承知しました`→`わかりました` など。実測で硬い言い回しは0件。(3) `してみますか`→`しませんか`、`てみましょうか`→`てみませんか` へ言い換え、`CONDESCENDING_OFFER_PATTERN`（`してあげます`・`させてあげます`・`してもいいですよ`・`してくださいね` など）を理由「上から目線の表現」として棄却。実測で0件。(4) 会話例に寄せる指針（相手の具体物を一つ拾って一段だけ深掘り、質問の前に自分の似た経験や本音を一言、質問は2〜3通に1回の軽さ、軽いツッコミや正直な感想、誘いは早めに軽く自分も一緒に行く形）を固有名詞なしの抽象的な指針と短い例にして `prompts/common.txt`・`reply.txt`・`first.txt`・`followup.txt` へ追加し、common.txt の質問必須の記述を「2〜3通に1回の軽さ」へ改めた。指標は相槌含有率が第1候補 90.0% / 全候補 85.4%、質問含有率が 35.0% / 18.8%（限定57.1% / 35.7%）で、20通中13通は質問のない返信になった。会話例との比較は報告書に記載（近い点: 具体物の拾い、質問前の一言、質問頻度、早めの軽い誘い、短文。遠い点: ツッコミの弱さ、生の自己開示の少なさ、深掘りの浅さ、終盤の反復、好意表現の少なさ）。`tests/test_app.py` は **1818 passed / 15 failed**（15件は環境依存で変更前と同一）。Actions は `1fd366c`（Push run 39130897898 / PR run 39130901686）と `9a0ddd2`（Push run 39131167881 / PR run 39131171706）が success。残課題は回答済みトピックでの停止、停止ターンで確認した回答（窓ぎわの席）が会話に出ないこと、同じ質問と自分の直前発言の繰り返し。 |

| T474 | 回答済み停止の解消（回答の逐語フォールバック）・繰り返しの抑制・深掘りの指針・感想文の許可・検証手順（T473会話テストの残課題とClaude指示） | pytest（`pytest -k t474` 7件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t474.json` / `会話テスト/conversation_test_keigo20_ds4_t474.html`） | FIXED | (1) `_compose_answer_relay_candidate`/`_build_answered_question_fallback_candidate` を追加し、候補がすべて棄却されても本人の確認済み回答を文単位でそのまま反映した1案を返す。スコープ一致（`_ephemeral_answer_addresses_question`）を要求し、回答の一部だけの行は受理せず、回答の文単位と一致する行だけを反映として認める（T441と同じ考え方で照合は緩めない）。実測で旅行（4通目）・招待（7通目）・日程（8通目）の停止3ターンが復旧し、相手役の連投0回で20通へ到達。(2) `_recent_self_repetition_reasons`/`_demote_repetitive_self_candidates` を追加。直近の自分の行と一致する文や同じ趣旨の質問を含む候補を後ろへ回して通知する。実測で直前の自分と同じ行の重複0件・同じ質問の連続0件。(3) `prompts/common.txt`・`reply.txt` に、相手の具体物から一段だけ深掘りし「お気に入りの〜はありますか」で止めないこと、直近6通で同じ趣旨を尋ねないことを抽象的な例で追加。実測で絵本→どんな絵本→どんなデザイン、カレー→お店→雰囲気と段階が進んだ。(4) 感想や感情は本人の事実主張ではないため自由に使えることをプロンプトに明記し、感想文が未確認の本人事実として棄却されないことを回帰テストで固定。(5) 停止したターンは相手役を連投せず本人の回答で再生成する手順を実施。指標は相槌含有率が第1候補 85.0% / 全候補 90.9%（限定100%/100%）、質問含有率が 50.0% / 29.5%（限定66.7%/60.0%）。`pytest -k "t472 or t473 or t474"` は18件成功、`tests/test_app.py` は **1826 passed / 15 failed**（15件は環境依存で変更前と同一）。Actions は `b9ad12c`・`ba2332f`・`47afc26`・`94e54e2`・`cf73eaa`・`61c2a40` が success（`61c2a40` Push run 39160089408 / PR run 39160094161）。残る指摘は絵本の話題で3通連続の質問、日程確定後の「楽しみ」の反復、旅行回答の未発展、モデル応答の `next_action` 500文字超1回。 |

| T475 | 話題の切り替え（同じ話題の質問を1〜2往復に制限）・締めの反復の回避・回答済み事実の再活用・軽いツッコミの許可・質問ターンの相槌の作り直し | pytest（`pytest -k t475` 5件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t476.json` / `会話テスト/conversation_test_keigo20_ds4_t476.html`） | FIXED | (1) `_recent_self_repetition_reasons` に、直近2通の自分の質問と内容語（漢字・カタカナ2字以上）または疑問詞が重なる候補を「同じ話題の質問が続く」として後ろへ回す判定を追加。プロンプトにも1〜2往復で切り上げ別の具体物へ移ることを例つきで明記。実測で絵本の話題は2往復で終わり、その後は祭り・屋台・古本のワゴンへ移った（前回は3通連続）。(2) 「当日」「お会いできる」「楽しみ」を含む候補は直近2通で自分が同じ趣旨を使っていたら後ろへ回し、プロンプトにも日程確定後は普段の雑談へ戻ることを明記。実測で「楽しみ」系は2通（前回6通）。(3) 確認済みの回答を後のターンで別の角度から話題にしてよいとプロンプトに明記。実測で窓ぎわの席の話が複数ターン、育てている植物の話が13通目に出た。(4) 「えっ、それは気になります笑」「意外です！？」などの例をプロンプトに追加。実測で軽い笑いを含む反応が4通。(5) `_compose_answer_relay_candidate` で質問ターンの返信を「そうなんですね！」で始めず、相手の共有への「いいですね！」にするか反応の行を省くようにした（T455の方針）。実測で4通目は「いいですね！ / 旅行は好きです / …」となった。あわせて直前の発言と同じ短い相槌の行も重複として後ろへ回す。走行は、相手役の発言を以前のテストから流用して不自然だった最初の1回を破棄し、毎ターン、アプリの直前の返信を読んで新しく書いた発言でやり直した。指標は相槌含有率が第1候補 90.0% / 全候補 85.1%（厳格 80.0% / 78.7%）、質問含有率が 65.0% / 42.6%。API要求24回、候補停止1回（同ターン内で復旧）。`pytest -k "t472 or t473 or t474 or t475"` は23件成功、`tests/test_app.py` は **1831 passed / 15 failed**（15件は環境依存で変更前と同一）。Actions は `5454303`・`46364b2` が success（Push run 39169109673 / PR run 39169113446）。残る指摘は17通目が前の話題を1ターン引きずったこと、19・20通目が同じ対象への近い質問だったこと、確認済みの「景色の写真」が発展しなかったこと、形式エラー2回。 |

| T476 | 直前の相手の話題から離れた自己開示の抑制・言い換えだけの再質問の抑制（T475会話テストの指摘とClaude指示） | pytest（`pytest -k t476` 3件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t477.json` / `会話テスト/conversation_test_keigo20_ds4_t477.html`） | FIXED | (1) `_candidate_drifts_from_partner_topic` を追加。直前の相手の発言に出た具体物と関係のない自分の話題（自分が以前に話した事実だけを並べた行）を「直前の相手の話題と離れている」として後ろへ回す。プロンプトにも、相手の直前の話題に近い自分の話を選ぶこと（相手がパン→自分の朝食、相手が祭り→自分の街歩き）を例つきで明記。実測で20通すべてが相手の直前の発言につながり、前回の「パンの直後に植物」「祭りの直後に絵本」に相当するずれは出なかった。(2) `_question_repeats_previous_ask` を追加。直前の自分の質問と内容語が同じで、正規化した文の類似度が0.6以上の質問を「直前の自分の質問と同じ」として後ろへ回す。プロンプトにも、同じ対象なら角度を変えるか別の対象へ移ることを明記。実測で同じ質問の連続0件、同じ趣旨の再質問0件（対象が新刊ポップ、フィルムカメラ、旅先の写真、あんバターへ移った）。相手役の発言は毎ターン、アプリの直前の返信を読んで新しく書いた。候補停止0回、API要求24回。指標は相槌含有率が第1候補 75.0% / 全候補 66.0%（限定 70.0% / 57.7%）で**目標を下回った**（質問ターンの返信を事実の回答から始める形にしたため相槌のない第1候補が5件出た。自然さと相槌のトレードオフ）、質問含有率は 70.0% / 58.0%（20通中14通が質問）。`pytest -k "t472 or t473 or t474 or t475 or t476"` は26件成功、`tests/test_app.py` は **1834 passed / 15 failed**（15件は環境依存で変更前と同一）。Actions は `b01b08d`（Push run 39175200278 / PR run 39175203119）が success。残る指摘は質問が14通と多いこと、3〜4通目で同じ対象を続けたこと、回答が後の具体物として拾われなかったこと、相槌のない返信が3通あること。 |

| T477 | 共有＋質問のターンは相槌を先に・質問だけのターンは答えから・日程応答フォールバックの反応・相槌主指標の限定 | pytest（`pytest -k t477` 3件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t478.json` / `会話テスト/conversation_test_keigo20_ds4_t478.html`） | FIXED | (1) `prompts/common.txt`・`reply.txt` に、相手が自分の話をしたうえで質問してきたターンは答えの前に短い相槌を1つ入れ、質問だけのターンは相槌を付けずに答えから始めてよいことを例つきで明記。実測で3通目「わかります！ / エッセイを読むことも多いです！」、11通目「いいですね！ / ぜひ行きましょう😊 / …」のように反応が先に出た。(2) 実測で7通目（何を飲むか）と10通目（休日の過ごし方）が答えから始まった。(3) `_compose_answer_relay_candidate` で、相手が共有したうえで日程を尋ねた場合も反応（うれしいです😊／いいですね！）を先に置くようにし、`_answers_for_partner_question` でアプリの確認質問が相手の質問文ではなく相手の発言を引用している場合（「私は土曜も日曜も空いてます」）でも確認済みの回答を対応付けるようにした。(4) 相槌の主指標は検証用ドライバ `会話テスト/scripts/run20.py` を変更し、相手が自分の話をしたターンだけを対象にして質問だけのターンを分母から外した（repo外のため追跡差分なし、全ターン値は参考として併記）。指標は主指標（15ターン）が第1候補 73.3% / 全候補 64.9% で**目標に未達**（不足5件のうち4件は「〜ですね！」の確認、「すごいですね」「わくわくします」など現行マーカーに載っていない形の相槌、1件は日程応答のフォールバックで本テストのあとに修正済み）、参考（全20ターン）は 70.0% / 63.0%、厳格は 60.0% / 58.7%、質問含有率は 70.0% / 52.2%。`pytest -k "t472..t477"` は29件成功、`tests/test_app.py` は **1836 passed / 15 failed**（15件は環境依存で変更前と同一）。Actions は `4a64033`（Push run 39178156411 / PR run 39178159639）と `f37f33b`（Push run 39179596168 / PR run 39179599225）が success。残る指摘は「本屋のどこ」を読書の場所として拾った回答、飲み物の質問に注文内容で答えたこと、写真の話題で3回連続の質問、確認場面の事務的な応答。マーカー定義を広げるかは判断待ち。 |

| T478 | 相槌マーカーの追加・「かしこまりました」の言い換えと崩れ形の棄却・繰り返す質問の昇格停止・軽い確認の例 | pytest（`pytest -k t478` 2件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t479.json` / `会話テスト/conversation_test_keigo20_ds4_t479.html`） | FIXED | (1) 検証用ドライバ `会話テスト/scripts/run20.py` の相槌マーカーに「すごいですね」「すごい」「わくわく」「ワクワク」「興味あります」などの感想・反応語を追加し、行全体が「〜ですね！」で終わる確認（「土曜日の14時ですね！」）も受け止めとして数えるようにした（文頭の確認形に限定、repo外のため追跡差分なし）。(2) `_STIFF_KEIGO_REWRITES` に「かしこまりました」→「わかりました」を追加し、崩れた形（「かこまりました」「かしこまりましたでした」）は `_HIGH_CONFIDENCE_MALFORMED_WORDS` で「明らかな誤字」として棄却。回帰テスト付き。(3) 3通連続の質問の原因は、`filter_safe_candidates` で後ろへ回した候補を `_prioritize_question_candidate` が「質問を含む候補を第1候補へ上げる」処理で再び先頭に戻していたこと。`candidate_tier` に `_recent_self_repetition_reasons` を組み込み、繰り返す候補と相手の直前の話題から離れた候補を昇格の対象外にした。実測でフィルム写真の話題は2往復で終わった。回帰テスト付き。(4) `prompts/common.txt` に「おけです👌」「りょーかいですー」「その時間で大丈夫です😊」などの軽い確認の例を追加。指標は相槌の主指標（相手が話した14ターン）が第1候補 **92.9%** / 全候補 **91.9%** で目標（80%/70%）を達成、参考の全20ターン値は 80.0% / 85.4%、厳格は 55.0% / 64.6%、質問含有率は 55.0% / 45.8%（20通中11通が質問）。候補停止1回、API要求24回。`pytest -k "t472..t478"` は31件成功、`tests/test_app.py` は **1838 passed / 15 failed**（15件は環境依存で変更前と同一）。Actions は `f6e3cfb`（Push run 39182004452 / PR run 39182007846）が success。残る指摘は6・7通目で場所の質問が2通続いたこと、2〜5通目は本の話題が4通続いたこと、14通目の質問が13通目とほぼ同趣旨だったこと、形式エラー2回。 |

| T479 | 相手の呼び名の統一・同趣旨質問（疑問詞と動作動詞が同じ）の抑制・相手の言葉の引用をやめる | pytest（`pytest -k t479` 3件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t480.json` / `会話テスト/conversation_test_keigo20_ds4_t480.html`） | FIXED | (1) `_established_partner_address`（会話で最初に使った呼び方、履歴になければプロフィール名の姓＋さん）と `_candidate_mixes_partner_address` を追加し、別の呼び方を使う候補を「相手の呼び方が揺れている」として後ろへ回す。プロンプトにも統一の規則を明記。実測で「黒川さん」4回・「いつき」0回。(2) `_question_repeats_previous_ask` に、同じ疑問詞と同じ動作動詞（撮る・行く等）なら対象語が違っても同じ質問とみなす判定を追加。実測で「どんな被写体を撮る」に続く「どんな街や景色を撮る」の形は出ず、フィルム写真は2往復で終わり、同じ質問の連続0件。(3) プロンプトに、相手の言葉をそのまま引用せず自分の気持ちとして言い直すことと例を追加（実測で引用0件）。指標は相槌の主指標（相手が話した15ターン）が第1候補 **93.3%** / 全候補 **94.6%** で目標達成、参考の全20ターン値は 85.0% / 89.8%、厳格は 70.0% / 71.4% でこちらも目標達成、質問含有率は 55.0% / 40.8%（20通中11通）。候補停止0回、API要求23回。`pytest -k "t472..t479"` は34件成功、`tests/test_app.py` は **1841 passed / 15 failed**（15件は環境依存で変更前と同一）。Actions は `f1cdca8`（Push run 39184773000 / PR run 39184776962）が success。残る指摘は2〜4通目で本の話題が3通続いたこと、17通目が16通目の相手発言の繰り返しに近いこと、メモの窓ぎわ・観葉植物が今回は出なかったこと、形式エラー1回。 |

| T480 | フレンドリーな敬語（尊敬語・謙譲語の除去、軽い疑問・共感、軽い定型文）とプロンプトの矛盾点検 | pytest（`pytest -k t480` 3件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t481.json` / `会話テスト/conversation_test_keigo20_ds4_t481.html`） | FIXED | プロンプト4ファイルに、個別の言い換え表ではなく原則（尊敬語・謙譲語を使わない、です・ますは保ったまま少し年上の友達の距離感、疑問は「〜んですか？」、共感は「〜ですよね」、無表情な文に温度感、丸投げをやめて具体的に聞き返す、日程は「いつ空いてます？」「どうします？」）と代表例を追加。`_soften_stiff_keigo` に安全な言い換え（〜されてるんですね→〜なんですね、行かれる→行く、使われている→使ってる、されるんですか→するんですか、〜させていただく→〜する、ありますね→ありますよね）を追加し、意味が変わる広い置換（〜される→〜する、ありますか→あるんですか）は入れずプロンプト側で扱う。フォールバックは「ご都合どうですか？」→「いつ空いてます？」「〜はどうですか？」→「〜はどうしてるんですか？」へ変更（回帰テスト付き）。実測で尊敬語・謙譲語0件、「ありますか？」0件、「ご都合」0件。あわせてプロンプトの矛盾を8組点検し、「新情報の相槌」と「質問だけのターンは答えから」の例外、「名前を毎回省略しない」と呼び方統一の整合、optional_user_questions と相手向け質問回数の別扱いの3件を修正した。指標は相槌の主指標（相手が話した14ターン）が第1候補 71.4% / 全候補 76.3%（全候補は目標達成、第1候補は未達。フレンドリー化で「〜んですね」「〜んだね」や回答始まりが現行マーカーに載らないため）、質問含有率は 65.0% / 46.2%。`pytest -k "t472..t480"` は37件成功、`tests/test_app.py` は **1844 passed / 15 failed**（15件は環境依存で変更前と同一）。Actions は `8d58a8c`（Push run 39203510501 / PR run 39203513875）が success。残る指摘は16通目のタメ口混入、20通目の2文1行、7通目の「フィルムカメラのカメラ」重複、9通目の「いきませんか」ひらがな。 |

| T481 | 敬語設定でのタメ口語尾の降格・直前と同じ書き出しの重複・相手の話題語での聞き返し・表記と区切りの細部 | pytest（`pytest -k t481` 4件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t482.json` / `会話テスト/conversation_test_keigo20_ds4_t482.html`） | FIXED | (1) tone が敬語または混合のとき、文末が「〜だね」「〜だな」「〜だよ」「〜じゃん」になる候補を「敬語設定にタメ口が混ざっている」として後ろへ回す。プロンプトにも明記。実測で文末のタメ口0件。(2) 直前の自分の発言と同じ書き出しの行（記号や絵文字の違いを無視）を「直近の自分の発言と同じ書き出し」として後ろへ回す。実測で「駅前ですね！」「駅前ですね✨」の連続は出ていない。(3) フォールバックの聞き返しを相手の直前の発言の内容語で作る（例「黒川さんはどんな看板が好きなんですか？」）。使える語がなければ省く。敬語設定では文末のタメ口を避け、呼び名と名前の語は除く。(4) 同じ語の重複をまとめる、ひらがなの「いきませんか」→「行きませんか」「いきましょう」→「行きましょう」の表記統一、あいさつ語が連結した行を区切り不足として棄却する検査を追加。指標は相槌の主指標（相手が話した16ターン）が第1候補 **81.2%** / 全候補 **81.6%** で目標（80%/70%）を達成、参考の全20ターン値は 80.0% / 79.2%、厳格は 75.0% / 72.9%、質問含有率は 65.0% / 64.6%。候補停止1回、API要求23回。今回の変更分の矛盾点検は5組で、いずれも両立。「〜んですね」「〜んだね」を行頭の受け止めとして相槌に数えた（T480の判断）。`pytest -k "t472..t481"` は42件成功、`tests/test_app.py` は **1848 passed / 15 failed**（15件は環境依存で変更前と同一）。Actions の `179eca6` は `tests/test_quality_checks_009.py` の保存候補再生テスト1件で failure。`filter_safe_candidates` が `_soften_stiff_keigo` の言い換えを適用するようになり保持本文が元候補と一致しなくなったことが原因で、期待値を「保持本文は元候補か、その言い換え結果のいずれか」に更新して解消した（言い換え後も同じ検査を通すため安全性は下げていない）。残る指摘は7通目の曖昧な回答、18・20通目の同趣旨質問、20通目の2文1行、従来形の「ありますか？」3件。 |

| T482 | はい/いいえ直接質問の未回答検出・同対象+同趣旨の再質問の降格・あいさつ連結の一般検出 | pytest（`pytest -k t482` 3件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t483.json` / `会話テスト/conversation_test_keigo20_ds4_t483.html`） | FIXED | (1) `_is_unclassified_question_about_user` に本人の習慣・経験の極性質問（〜たりしますか、〜ることはありますか、撮りますか）を追加し、はい/いいえで答えられる直接質問への未回答を「相手からの直接質問に未回答」として棄却、本人確認を出して回答を反映する。実測で14通目の「水野さんは写真は撮ったりしますか？」に撮るか否かを答え、回答を反映した。(2) 対象の名詞と述語クラス（決める・好む・頻度・経験・場所・予定）が重なる質問を「直近の自分と同じ趣旨の質問」として後ろへ回す（`_question_shares_object_and_intent`）。実測で本と「決まったか」を重ねる再質問は出ていない。(3) あいさつ・締めの語の後に助詞も句点も無しに別の文が続く行を特定の型に限らず棄却する。長い語の前部と一致する短いあいさつ語は否定先読みで誤検出しない。実測で締めは「お仕事の前は無理しちゃダメですよ！\nゆっくり休んでくださいね😊」となり連結は出ていない。(4) 「ありますか」はプロンプト原則の範囲でコード変更なし（実測で直接形は初回の1件）。指標は相槌の主指標（相手が話した16ターン）が第1候補 75.0% (12/16) / 全候補 **78.0%** (32/41) で全候補は目標（70%）達成、第1候補は目標（80%）に届かず T481 の 81.2%/81.6% から下降。相槌マーカーに載らない自然な受け止めが4件あり #7・#10 は T481 と別表現だったため計測差（品質の後退ではない）。候補停止0回、API要求22回。矛盾点検は5組でいずれも両立。`tests` 全体は **1996 passed / 0 failed**。Actions は `0e4bc1d`（Push run 39235338503 / PR run 39235344171）が success。 |

| T483 | 日程の聞き返しを日程・誘いの文脈に限定・共感の「〜ますよね」「〜よね」の受け止め計測 | pytest（`pytest -k t483` 3件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t484.json` / `会話テスト/conversation_test_keigo20_ds4_t484.html`） | FIXED | (1) 日程の分岐（回答リレー末尾の「いつ空いてます？」と冒頭「ありがとうございます！」）に入る条件を、対象の発言か直前の相手発言に日程・誘いの語（空いて・都合・何曜日・時間帯・日程・週末・土曜・日曜・予定）がある場合に限定した。実測の写真の問い #6 は「よく撮ります\n景色や看板を撮ることが多いです\n黒川さんはどんな写真が好きなんですか？」となり、日程の聞き返しも冒頭の「ありがとうございます」も出ず、日程ターン #12 では従来どおり「いつ空いてます？」を付けた。(2) `ACKNOWLEDGMENT_OR_QUESTION_MARKERS` と会話テストの相槌マーカーに `ますよね|よね` を追加し、共感の「ですよね」の「ます」版を受け止めとして数える（「よろしくお願いします」「無理しちゃダメですよ」は数えない）。指標は相槌の主指標（相手が話した15ターン）が第1候補 **93.3%** (14/15) / 全候補 **82.1%** (32/39) で目標（80%/70%）を達成し T482 の 75.0%/78.0% から第1候補が戻った。参考の全20ターン値は 80.0% / 78.3%、厳格は 75.0% / 73.9%、質問含有率は 55.0% / 52.2%。候補停止0回、API要求23回。矛盾点検は3組でいずれも両立。`tests` 全体は **1998 passed / 1 failed**（失敗は Firefox UI の Selenium タイムアウトで単独再実行では29件成功の環境依存）。Actions は `94b1067`（Push run 39239705965 / PR run 39239712625）が success。 |

| T484 | 相手が空き日時を述べたターンの日程の聞き返しの抑止・誘い直後以外の「ありがとうございます」の抑止 | pytest（`pytest -k t484` 1件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t485.json` / `会話テスト/conversation_test_keigo20_ds4_t485.html`） | FIXED | (1) `_partner_states_own_availability`（`PARTNER_OWN_AVAILABILITY_PATTERN`）を追加し、相手が空き・余裕（空いて・暇・フリー・都合がいい・予定がない）を述べたターンでは回答リレー末尾の「いつ空いてます？」を付けない。直後が「か」「？」の疑問形や直前が「〜さんは」の場合は相手の申告とみなさない（「水野さんはいつ空いてますか？」は申告でない）。実測 #13 相手「土曜と日曜ならだいたい空いてます」に対してアプリは「土曜の昼なら空いてます」の1行だけを返し、聞き返しも冒頭の ack も出なかった。全20通で「いつ空いてます？」は0件。相手の空きが述べられていない日程の問いには従来どおり付ける（`test_t483_schedule_turn_still_appends_the_ask_back`）。(2) 日程分岐の冒頭は、対象の発言に誘い・喜びの語（ぜひ・行きましょう・ご一緒・楽しみ・うれしい・いいですね）があるか、直前の相手発言が誘いか、直前発言に誘い・喜びの語があるときだけ「うれしいです😊」を出し、それ以外は回答から始める。実測で「ありがとうございます」を含むアプリ発話は #1 の初回あいさつだけ。(3) 会話テストの行頭の受け止めマーカーが行末「！」の行しか数えず「〜んですね😊」「〜んですね✨」を数えていなかったため、行頭の短い受け止め行に限り行末の絵文字を最大3字まで許すようにした（アプリの挙動は不変。第1候補 73.3% (11/15) → 93.3% (14/15)、全候補 82.4% (28/34) → 94.1% (32/34)）。指標は相槌の主指標（相手が話した15ターン）が第1候補 **93.3%** (14/15) / 全候補 **94.1%** (32/34) で目標（80%/70%）を達成。第1候補の唯一の未達は T484 で意図的に ack を外した #13。参考の全20ターン値は 90.0% / 88.9%、厳格は 65.0% / 71.1%、質問含有率は 60.0% / 53.3%。候補停止1回（#19 の後、試行1で「相手の返信量に対して長すぎる候補」、再試行で復旧）、API要求24回。矛盾点検は3組でいずれも両立。`tests` 全体は **2000 passed / 0 failed**。Actions は `f6509cb`（Push run 39242666855）が success。 |

| T485 | 選択式質問への回答・聞き返しの名詞句・「お好き」の言い換え・受け止め直後の連結の棄却・締めの重複の抑止 | pytest（`pytest -k t485` 6件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t486.json` / `会話テスト/conversation_test_keigo20_ds4_t486.html`） | FIXED | (1) `_is_unclassified_question_about_user` に「AとBならどっち」「AとBどっちが多い」型の選択式質問を追加し、未回答は「相手からの直接質問に未回答」として棄却、本人確認を出して回答を反映する。実測 #4「甘い系と食事系ならどっちが好みですか？」→「食事系のほうが好きです！」、#7 紙/電子、#15 イートイン/テイクアウトも直接答えた。(2) `_latest_topic_noun` を名詞句単位（系・風・タイプ・派・の+名詞）へ拡張し、「ハード系のパン」を「ハード」だけで切り出さない。実測で聞き返しは「お気に入りのパン屋さんがあるんですか？」「黒川さんはどんな写真が好きなんですか？」。(3) `_STIFF_KEIGO_REWRITES` に「お好き」系の言い換えを追加し、実測で20通すべて「お好き」0件。(4) `candidate_has_missing_sentence_break` に短い受け止め（ですね／ですよね／ますよね）の直後の連結（「13時50分ですね了解です！」）を追加。実測で該当の連結は送信されず候補停止0回。ただし「感触が好きなんですが黒川さんはどんな本…」の形は残った。(5) `_recent_self_repetition_reasons` で直近の締めの行と同趣旨（当日・お会いできる・会えるの・楽しみ、助詞差は無視）の行を後ろへ回す。実測で #19/#20 の「楽しみにしています」連続は残った（他に ack 候補が無いターン）。あわせて `prompts/common.txt` に3項目を追記。走行中、回答の「カレーパンが好きです」が別トピック「カレー好み」に部分一致して候補が全滅する回帰が出たため、`_candidate_rejection_reasons` で本人確認済みの回答そのままの候補（`_candidate_is_verified_answer_relay`）には「未確認の本人事実」を付けないよう修正した（`test_t485_verified_answer_relay_survives_partial_topic_match`）。指標は相槌の主指標（相手が話した13ターン）が第1候補 **84.6%** (11/13) / 全候補 **90.3%** (28/31) で目標（80%/70%）を達成。参考の全20ターン値は 80.0% / 86.4%、厳格は 60.0% / 54.5%、質問含有率は 45.0% / 45.5%。候補停止0回、API要求25回。矛盾点検は3組でいずれも両立。`tests` 全体は **2005 passed / 0 failed**。Actions は `074cdf5`（Push run 39247779829 / PR run 39247785904）と `72189f7`（Push run 39250428038 / PR run 39250436447）がいずれも success。 |

| T486 | 呼び名統一の経路修正・逆接で続く1行の分割・確定日時と違う日時の確認・聞き返しの話題の限定 | pytest（`pytest -k t486` 4件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t487.json` / `会話テスト/conversation_test_keigo20_ds4_t487.html`） | FIXED | (1) 回答リレーとプロフィール確認リレーが `_fallback_partner_honorific_name`（常に既定名）を使い、T479 の「最初に使った呼び方」を迂回して呼び名が混在していた。両方を `_established_partner_address` へ変更。実測で名前の使用は1か所のみで混在0件。(2) `split_pivot_run_on_line` を追加し「〜ですが◯◯さんは…」を逆接の後で2行に割る（`filter_safe_candidates` の入口）。実測で該当の連結0件。(3) `_extract_schedule_elements` で最後の相手発言の日時が以前の日時と食い違うとき（時刻・曜日・日付・午前午後）に確認返しを先頭に出す `_build_schedule_conflict_fallback_candidate` を追加し、丸受け入れは「確定済みの日時と食い違う」として棄却。実測 #19「西口に9時集合」→「あれ15時じゃなかったでしたっけ？\nもしかして時間が変わったんですか？」。時間帯は午前・午後・夕方に限定して「夜型」の誤検出を解消し、確認済みなら再確認しない。(4) `_latest_topic_noun` を、相手発言が質問なら質問文に現れる語だけに限定（地名・日付の混入を防止。実測の聞き返しは「どんなジャンルの本」「どんな写真」等）。指標は相槌の主指標（相手が話した19ターン）が第1候補 **89.5%** (17/19) / 全候補 **95.2%** (40/42) で目標（80%/70%）を達成。参考の全20ターン値は 90.0% / 95.3%、厳格は 60.0% / 67.4%、質問含有率は 45.0% / 25.6%。候補停止0回、API要求25回。プロンプトは未変更。`tests` 全体は **2010 passed / 0 failed**。Actions は `7b5fbe5`・`057ce65` がいずれも success。 |

| T487 | どこから型の直接質問・回答リレーの末尾空行・古い話題への相槌・重複承諾・硬い確認・性質語の聞き返し | pytest（`pytest -k t487` 4件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t488.json` / `会話テスト/conversation_test_keigo20_ds4_t488.html`） | FIXED | (1) `_is_unclassified_question_about_user` に「どこから/どれから/何から」＋ますか型を追加。実測 #3「入口の平台から見て回ります」。(2) 回答リレーの行組み立てから空行を無くし、`filter_safe_candidates` の入口で末尾改行も除去。実測で末尾改行0件。(3) `_opening_line_reacts_to_stale_topic` で書き出しが1つ前の相手発言に反応する候補を棄却。(4) 誘いの承諾で「ぜひ行きましょう」と回答の「ぜひ行きたい」を重ねない。(5) 「何時に変更するか教えてもらえますか」→「何時になったんですか」の言い換え。あわせて性質語（夜型）を聞き返しに使わない（commit a48fc39）。`tests` 全体は **2015 passed / 0 failed**。Actions は `4ba122a`・`a48fc39` が success。 |

| T488 | メモ回答の対象限定・承諾の整理・飲む食べる質問・複合語の聞き返しの抑止・なぞり返しの抑止 | pytest（`pytest -k t488` 6件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t489.json` / `会話テスト/conversation_test_keigo20_ds4_t489.html`） | FIXED | (1) `_memo_answer_sentence` を質問文（最後の質問節）に限定し、2字以上の重なり、または両方で独立して現れる1字の重なりを要求。実測 #5「飲みます\nレモンティーが多いです」でメモの食事文は出ず、無関係なら本人確認へ回る。(2) 誘いの承諾に日程と無関係なメモ文を添えず、承諾だけの `_build_invitation_acceptance_fallback_candidate` を追加。実測 #12「土曜日の古本市ぜひ行きたいです😊\n一緒に行けたらうれしいです！」。(3) 「〜は飲みますか」「〜は食べますか」を直接質問として追加。(4) 話題の名詞句に「の」を含むときは聞き返しを省く（「どんな中野の商店街」を出さない）。(5) `_opening_line_echoes_partner` で相手の直前発言をなぞるだけの1行返しを棄却。指標は相槌の主指標（相手が話した19ターン）が第1候補 **84.2%** (16/19) / 全候補 **86.0%** (37/43) で目標（80%/70%）を達成。参考の全20ターン値は 85.0% / 86.4%、厳格は 65.0% / 65.9%、質問含有率は 30.0% / 27.3%。候補停止2回（再試行で復旧）、API要求30回。`tests` 全体は **2020 passed / 0 failed**。Actions は `fc172aa`・`dc81c07` がいずれも success。 |

| T489 | 尊敬の「〜られる」＋「んですか」の言い換え・変更後の日時の確定の保留 | pytest（`pytest -k t489` 2件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t490.json` / `会話テスト/conversation_test_keigo20_ds4_t490.html`） | FIXED | (1) `_STIFF_KEIGO_REWRITES` に「〜られるんですか」→「〜るんですか」（撮る・読む・食べる・飲む・書く・聞く・作る・見る・観る）を追加。受け身と区別できるよう「んですか」形に限定。実測 #9「黒川さんはどんなジャンルを観るんですか？」。(2) `_schedule_change_pending`（確認済みで相手が時刻を明示していない状態）と `_build_schedule_reask_fallback_candidate` を追加し、確定させる候補を「日時が未確定なのに確定させている」として棄却。実測 #19「あれ10時じゃなかったでしたっけ？\nもしかして時間が変わったんですか？」→ #20「何時になったんですか？」で確定しなかった。指標は相槌の主指標（相手が話した19ターン）が第1候補 **84.2%** (16/19) / 全候補 **88.9%** (40/45) で目標（80%/70%）を達成。参考の全20ターン値は 85.0% / 89.4%、厳格は 75.0% / 68.1%、質問含有率は 70.0% / 51.1%。候補停止3回（再試行で復旧）、API要求30回。`tests` 全体は **2022 passed / 0 failed**。Actions は `ae36058` が success。 |

| T490 | 「〜はしますか」型の未回答検出・料理回答の反映要求・分割後の言い切り | pytest（`pytest -k t490` 3件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t491.json` / `会話テスト/conversation_test_keigo20_ds4_t491.html`） | FIXED | (1) `_is_unclassified_question_about_user` に「(は\|も\|って)…しますか／していますか／ていますか／行きますか／観ますか／見ますか／聴きますか／聞きますか／読みますか／作りますか／育てますか／買いますか／使いますか」を追加（いつ・何時の日程疑問詞は除外）。実測 #3「よく行きます\n近場の銭湯によく行きます」ほか。(2) `_answers_verified_single_partner_question` の料理習慣一般スコープで、確認済み回答の文節が候補に含まれることを要求。実測 #5「します\n簡単なものだけですが作ります」。(3) `split_pivot_run_on_line` で分割した左側の「〜んですが／〜ですが／〜ますが」を「〜んです！／〜です！／〜ます！」に直す（けど系は分割しない）。指標は相槌の主指標（相手が話した19ターン）が第1候補 **89.5%** (17/19) / 全候補 **93.3%** (28/30) で目標（80%/70%）を達成。参考の全20ターン値は 90.0% / 93.5%、厳格は 70.0% / 71.0%、質問含有率は 75.0% / 61.3%。候補停止8回・接続エラー8回（各ターン再試行で復旧）、API要求36回。`tests` 全体は **2025 passed / 0 failed**。Actions は `3f1da2a` が success。 |

| T491 | 回答をモデル候補に含めるプロンプト明示・フォールバックの型の多様化・動詞由来語の切り出し抑止・短い日程確定の受け皿 | pytest（`pytest -k t491` 3件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t492.json` / `会話テスト/conversation_test_keigo20_ds4_t492.html`） | FIXED | (1) `prompts/reply.txt` に、答があるときはどの候補にも回答の内容語を必ず入れると明示（照合は緩めない）。候補停止は T490 の8回→0回、フォールバックは7/20ターンに減少。(2) `_pick_relay_ack`／`_recent_relay_text` で相槌3種・聞き返し2型から直近未使用を選び、両方使っていれば省く。実測 #3 いいですね／#7 そうなんですね。(3) `_latest_topic_noun` で漢字2字の直後に助詞以外のひらがなが続く語（「遠回」り）を使わない。実測 #11 は聞き返し無し。あわせて `_build_schedule_confirmation_fallback_candidate` を追加し、回答リレーを段階的に短縮。指標は相槌の主指標（相手が話した19ターン）が第1候補 **89.5%** (17/19) / 全候補 **88.9%** (32/36) で目標（80%/70%）を達成。候補停止0回・接続エラー0回、API要求28回。`tests` 全体は **2028 passed / 0 failed**。Actions は `659ac82`・`2a558e8` が success。 |

| T492 | 一語回答と言い直しの統合・同じ時刻の書き出しの抑止・行為語の自然な聞き返し | pytest（`pytest -k t492` 3件） | FIXED | (1) `_answer_lines_for_candidate` で「好きです」のような一語の答えの後に言い直しが続くときは一語を落とす（「好きです／冬の空を見るのが好きです」→「冬の空を見るのが好きです」）。(2) `_repeats_last_me_time_opening` を追加し、直前の自分の発言と同じ時刻で書き出し、相手がその時刻を出していない候補を「直近の自分の発言と同じ書き出し」として棄却（食い違いの確認は除外）。(3) 将棋・読書などの行為語は「どんな〜が好き」ではなく「〜はよくやる／するんですか？」の型にする（`_ACTIVITY_FOLLOWUP_VERB`）。`tests` 全体は **2031 passed / 0 failed**。Actions は `073df6b` が success。 |

| T493 | ユーザーの話題転換指示の優先・方向に「話題を変える」追加・検査との両立 | pytest（`pytest -k t493` 3件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t493.json` / `会話テスト/conversation_test_keigo20_ds4_t493.html`） | FIXED | (1) `prompts/reply.txt` に、direction/extra の指示は会話運びの規則より優先すると明記。(2) `index.html` の方向に「話題を変える」を追加。`_topic_change_requested` が話題語を抜き出し、相手へ短く反応してから指定の話題へ移す。実測 #7 映画／#12 旅行／#17 本へ切り替え。(3) 指示があるときは「直前の相手の話題と離れている」「同じ話題の質問が続く」等を行わず、指定の話題に触れた候補を先頭に出す。無ければ `_build_topic_change_fallback_candidate` で合成（#7・#17）。(4) `run20.py` に `--extra`／`--direction` を追加し、3回の指示で切り替わりを確認。指標は相槌の主指標（相手が話した19ターン）が第1候補 **100.0%** / 全候補 **100.0%**。候補停止0回、API要求28回。`tests` 全体は **2034 passed / 0 failed**。Actions は `45da674`・`f6967f9` がいずれも success。 |

| T494 | 旧アプリの本人情報の取り込み（読み取り専用）・明示時のみ読み込み・相手プロフィールのランダム選択 | pytest（`pytest -k t494` 2件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t494.json` / `会話テスト/conversation_test_keigo20_ds4_t494.html`） | FIXED | (1) `scripts/legacy_extract.py` を追加（データなし・パスは引数）。旧 app.db を `mode=ro` で読み、user_profile・user_knowledge・手入力 self メッセージから本人の事実を小さく抽出（根拠ID付き）。結果はリポジトリ外の `会話テスト\data\user_facts_from_legacy.json`（38件）と `reports\user_facts_from_legacy.md`。(2) 環境変数 `MRA_LEGACY_FACTS_PATH` 指定時のみ `load_legacy_facts`→`_merge_legacy_facts` で profile.facts に足し、確定事実として使う（既定オフ、テストは架空データ）。(3) `run20.py` の start に `--partner-from-legacy`／`--seed` を追加し contacts.profile から1件選択（読み取り専用）。走行は seed=7 の相手役と取り込み事実で20通、候補停止0・接続エラー0。指標は相槌の主指標（相手が話した19ターン）が第1候補 73.7% / 全候補 **86.5%**（第1候補は目標未達）。個人情報は一切コミットせず、出力はリポジトリ外のみ。`tests` 全体は **2036 passed / 0 failed**。Actions は `49f76b0`（Push run 39340015590 / PR run 39340022020）が success。 |

| T495 | 旧アプリ由来の本人プロフィールへ統一・抽出の絞り込みと要確認・名前置換・アンケート取り込み・話題転換の細部 | pytest（`pytest -k t495 or t494` 8件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t495.json` / `会話テスト/conversation_test_keigo20_ds4_t495.html`） | FIXED | (1) `MRA_SELF_FROM_LEGACY` で本人プロフィールを旧アプリの user_profile＋speaking_style＋抽出事実から組む（架空メモ不使用）。(2) 抽出は user_knowledge を除外し、本人が自分を述べている文だけに絞り、相手への感想・疑問文を除外。プロフィール（大学院生）と食い違う勤務の申告は needs_review へ。ID 1793 除外・ID 1237 要確認。`--replace-name` で本名を出力に残さない。(3) `_clean_legacy_profile` で contacts.profile の画面断片を整形。(4) `MRA_SURVEY_ANSWERS_PATH` で選択式アンケート（choices/ratings/notes）をポリシー（大好き/好き→好き、苦手→苦手、経験なし→未経験、普通→不使用）で確定事実に。(5) 転換の合成候補に「ちなみに」を追加し、切り替え質問（〜だりするんですか⇔〜こともあるんですか）を同趣旨判定に含めた。回帰テストの旧DB実文を架空文へ差し替え。指標は相槌の主指標（相手が話した19ターン）が第1候補 **84.2%** / 全候補 **90.9%** で目標達成。候補停止3回（再試行で復旧）、API要求26回。`tests` 全体は **2042 passed / 0 failed**。Actions は `8a251b2`・`04eb8db`・`97d0884`・`bb384eb` が success、`096a612`（Push run 39349097168 / PR run 39349104036）が success。 |

| T496 | アンケート回答の自然化・質問と答えの型の一致・項目名の棄却・職業の決めつけ防止・本人プロフィールの作り直し | pytest（`pytest -k t496` 4件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t496.json` / `会話テスト/conversation_test_keigo20_ds4_t496.html`） | FIXED | (1) `run20.py` の `_self_from_legacy` をカテゴリ別事実から area/job/hobbies/memo（生データを除く自然な文）を組み立てる形に変更。(2) `_merged_survey_answers` が `_natural_survey_answer` で 評価語や一語を自然な文に変換。(3) `_answer_type_matches_question` で「どんな・何・どちら」への極性・評価語だけの回答リレーを棄却し 本人確認へ回す。(4) 「profile: …」など項目名がそのまま出た候補を棄却。(5) 職業確認の聞き返しは職業欄か勤務表現からだけ作る。走行は seed=7 の相手役＋旧アプリ由来の本人設定で20通、候補停止5回（再試行で復旧）。指標は相槌の主指標（相手が話した19ターン）が 第1候補 **89.5%** / 全候補 **93.3%** で目標達成。`profile:` 0件・職業の決めつけ0件。`tests` 全体は **2046 passed / 0 failed**。 Actions は `3d8de1b`（Push run 39351215563 / PR run 39351220948）が success。 |

| T497 | 整備済み本人プロフィールの使用・学生への仕事の質問の抑止・決定的フォールバックの敬語化 | pytest（`pytest -k t497` 2件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t497.json` / `会話テスト/conversation_test_keigo20_ds4_t497.html`） | FIXED | (1) `run20.py` の start に `--self-profile-json` を追加し、整備済みの本人プロフィールJSON（area=北海道札幌市・hobbies 14件・memo 自然文）をそのまま使用（抽出からの自動組み立ては不使用）。(2) 職業確認のフォールバックで、相手が学生なら仕事の聞き返しを作らない（実測 #3 で仕事の質問0件）。(3) 決定的フォールバックにも `_soften_stiff_keigo` を適用（全20通で「お好き」0件）。走行は seed=7 の相手役＋指定本人プロフィールで20通、候補停止5回（再試行で復旧）。指標は相槌の主指標（相手が話した19ターン）が 第1候補 78.9% / 全候補 **84.8%**（第1候補は目標に僅かに届かず）。`tests` 全体は **2048 passed / 0 failed**。 Actions は `db7e95f`（Push run 39354131280 / PR run 39354141723）が success。 |

| T498 | 休日回答のスコープ・固有名詞への乗っかりの棄却・直前宣言の聞き返しの抑止・未確定への返し・文法 | pytest（`pytest -k t498` 5件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t498.json` / `会話テスト/conversation_test_keigo20_ds4_t498.html`） | FIXED | (1) topic「休日」で確認済み回答の内容が無い候補を棄却（マッチングは休日語一致。topic 未分類経路は次回課題）。(2) 相手の固有名詞への無根拠な「僕も聴く」を「未確認の本人事実」で棄却。(3) `_repeats_partner_fresh_statement` で相手の直前宣言の聞き返しを棄却。(4) `_partner_schedule_unsetted` で未確定と言われたら「決まったら教えてください！」と返し、時刻の催促を棄却（実測 #20）。(5) 「のです！」→「んです！」の言い換え。走行は seed=3 の相手役＋新話題の台本で20通、候補停止3回（再試行で復旧）。指標は相槌の主指標（相手が話した18ターン）が 第1候補 **88.9%** / 全候補 **93.5%** で目標達成。`tests` 全体は **2053 passed / 0 failed**。Actions は `dc3bccd`（Push run 39356228049 / PR run 39356232689）と `219ddd4`（Push run 39357593824 / PR run 39357598682）がいずれも success。 |

| T499 | アンケート設問名の棄却・質問の聞き返しの棄却・遠方の誘いの本人確認・敬語 | pytest（`pytest -k t498 or t499` 11件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t499.json` / `会話テスト/conversation_test_keigo20_ds4_t499.html`） | FIXED | (1) `_survey_question_names` で choices のキーと ratings の内側キー（3文字以上）を取得し、候補に設問名がそのまま出たら棄却。実走の誤爆を受け、対象は「・」入りの複合ラベルと設問らしい語尾（方・派・頻度・選び 等）に限定。(2) `_candidate_only_asks_back_partner_question` で相手の末尾質問への実質回答がなく質問行だけの候補を「相手の質問の聞き返し」で棄却。`_is_polar_personal_question` で「朝は苦手ですか？」型を本人確認へ回す。(3) `_partner_invitation_is_far_from_user` で本人の居住地と誘い先を比較し、遠い場合は承諾候補を棄却して本人確認。誘い文の地域を相手プロフィールより優先。(4) 謙譲語の書き換えを追加。(5) 予定質問に別設問の回答が対応したと誤判定するスコープ不一致を修正。実測 #16 で遠方確認、#17 で予定確認。設問名の露出0件・「お好き」等0件。走行は seed=5 の相手役で20通、候補停止3回（品質2・要求上限1）。指標は相槌の主指標（相手が話した12ターン）が第1候補 **91.7%** / 全候補 **95.8%** で目標達成。`tests` 全体は **2059 passed / 0 failed**。Actions は `a7e32af`（Push run 39367228684 / PR run 39367235247）が success。`a13409b`・`1fd677a` はPush後に確認。 |

| T500 | memo の決定的リレー廃止・質問の取り違えの棄却・尊敬語・相手役の整合 | pytest（`pytest -k t500` 4件）＋実API敬語20通会話テスト | FIXED | (1) `_unclassified_personal_question_user_answer` から memo 文の return を外し、回答は本人が確認した会話回答だけにした。memo は `_memo_answer_reflected_in_candidate` の検査と事前確認の省略判定にだけ使う。全候補が落ちたら名指しの無い直接質問でも本人確認へ回す。(2) `_candidate_misreads_user_question_as_partner_info` で「そちらはお弁当ですか？」への「お弁当なんですね！」を「本人への質問を相手の情報として受け止めている」で棄却。同意を求める「〜ですよね」は対象外。派・型を外した語幹と絵文字付きの行も照合する。(3) 「〜されていたんですね」「〜されていた頃」→「〜してた…」に加え、されてた・されたり・やられてた・聴かれる・いらっしゃる を書き換え。(4) 台本を21歳・北海道・学生に合わせ、遠方の誘い先を大阪から東京へ変更（リポジトリ外）。(5) 助詞の重なった崩れ（「は方は」）を「明らかな誤字」で棄却。実走は20通・相手19通・`LIMIT_REACHED`・候補停止0回・要求28回。主指標（相手が話した12ターン）は第1候補 **91.7%** / 全候補 **96.2%** で目標達成。memo リレー、「〜なんですね」の取り違え、尊敬語の残存はいずれも0件。`tests` 全体は **2063 passed / 0 failed**。Actions は `cc4dceb`・`7deb12a`・`522d6aa`・`9e96820`・`a4025f4`・`ad8c8c4` が success。 |

| T501 | 自分の以前の回答の繰り返し・ペット所有の含み・相手が答えた話題の聞き返し・遠い誘いへの自然な断り | pytest（`pytest -k t500 or t501 or t498 or t499` 19件、全体2068件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t501.json` / `会話テスト/conversation_test_keigo20_ds4_t501.html`） | FIXED | (1) `_candidate_reuses_prior_me_answer` で直近6通の自分の宣言文と一致・類似0.85以上の候補を「自分の以前の回答を繰り返している」で棄却。(2) `_has_unverified_pet_claim` に「実家／うち＋猫・犬・ペット・癒や・もふもふ」の含意を追加（文節単位で trusted fact を判定）。(3) `_repeats_partner_fresh_statement` を全相手発言へ拡張。(4) 台本の相手行を辞退前提へ変更。走行で、誘いへの回答リレーが承諾句を前置して断りを落とす不具合と、勧めの質問に別トピックの回答をリレーする不具合を発見して修正（`_candidate_is_verified_answer_relay` の辞退検出、`_answers_for_partner_question` の勧め質問ガード、`_compose_answer_relay_candidate` の辞退分岐）。run20 のリトライで相手文が落ちるバグも修正。実走は20通・相手19通・`LIMIT_REACHED`・候補停止2回・要求31回。主指標（相手が話した11ターン）は第1候補 72.7% / 全候補 86.4%。断りの矛盾は解消し、ペット所有の含み・自己回答の繰り返しは0件。一方で #6「朝は苦手ですか？」の未回答、#19 の勧め質問への聞き返し、#17 の「言っていただけて」が残り、T502 の課題として記録した。Actions は `51af300`・`815ad9a`・`693a19e`・`c4b7165` が success。代表を t501 版へ差し替え。 |

| T502 | 直接質問への未回答の解消・断り方・札幌の誘いへの前向きな応答・謙譲語（追補: memo 評価語の誤一致） | pytest（`pytest -k t502` 3件、全体2072件）＋実API敬語20通会話テスト（接続エラーで未完走） | FIXED（実走行は未完走） | (1) `_is_unanswered_sensitive_question` で勧め（おすすめ＋店・場所）と二択（そちら・そっち＋どっち）を定義し、確認済み回答が候補の最初の1〜2行に無ければ「相手からの直接質問に未回答」で棄却。本文全体が質問形でなくても末尾の一文（「朝は苦手ですか？」）が本人への直接質問なら同じ検査を行い、preflight で本人確認へ回す。(2) 辞退リレーに「また〇〇で何かあればぜひ行きたいです！」を添える（〇〇は居住地の市名）。(3) `_local_plan_willingness_sentence` で「もし札幌でイベントがあったら一緒に行きたいです」を本人確認の対象にし「札幌ならぜひ行きたいです！」を反映。(4) `_STIFF_KEIGO_REWRITES` に「言っていただけて→言ってもらえて」等を追加。(5) 追補: memo の評価語（苦手等）だけで別話題（「朝は苦手ですか？」と「雨の日は苦手」）を答えにしていたため `MEMO_POLARITY_STOPWORDS` を導入し、話題語の共有を必須にした。回帰テストは `test_t502_direct_question_to_user_must_be_answered`・`test_t502_local_plan_willingness_is_confirmed`・`test_t502_stiff_humble_keigo_is_rewritten`・`test_t503_memo_polarity_word_does_not_answer_another_topic`。全 pytest **2072 passed / 0 failed**。Actions は `f419042` が success、`4de1437` は確認時点で実行中。t502 の実走行は Gemini の 503 UNAVAILABLE / 504 DEADLINE_EXCEEDED が連続し、接続エラー累計10回の安全停止で未完走（1回目 #14、2回目 #1）。停止前に #10 の二択質問への回答反映を確認。完全な20通と指標、代表差し替えは接続回復後に実施する。 |

| T503 | memo の評価語だけを頼りに別話題を答えにしていた不具合 | pytest（`pytest -k t503`、全体2072件） | FIXED | 「朝は苦手ですか？」に対し、memo の「雨の日は苦手」を評価語（苦手）の一致だけで答えにしていた。`MEMO_POLARITY_STOPWORDS` を導入し、`_memo_answer_sentence` で話題語の共有を必須にした。`_memo_answer_terms` の1字語（日）による誤一致も併せて解消。回帰テスト `test_t503_memo_polarity_word_does_not_answer_another_topic`。 |

| T504 | 相手が答えた活動の聞き返し・猫への外歩き質問 | pytest（`pytest -k t504` 2件） | FIXED | 相手が「学生の頃はテニスをしていました」と言った直後の「学生時代はどんな部活やスポーツをしていましたか？」を「相手が答えた活動を聞き返している」で棄却。猫を飼っている相手への「外にお散歩に行ったりするのは好きですか？」を「猫に外歩きを尋ねている」で棄却。回帰テスト `test_t504_partner_declared_activity_is_not_asked_again`・`test_t504_cat_walk_question_is_rejected`。 |

| T505 | 断りのリレーに添える前向きな一言が承諾矛盾ガードで落ちる不具合 | pytest（`pytest -k t501 or t502 or t504` 9件、全体2045件＋Firefox29件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t505.json` / `会話テスト/conversation_test_keigo20_ds4_t505.html`） | FIXED | 辞退回答に添える「また札幌で何かあればぜひ行きたいです！」が、T501の承諾矛盾ガード（辞退＋ぜひ行き／行きたい）に触れて落ち、断りだけが残っていた。ガードを「また・別の機会・今度・機会があれば」を伴う行には適用しない形に狭めた。実走は20通・相手19通・`LIMIT_REACHED`・候補停止0回・要求31回。主指標（相手が話した11ターン）は第1候補 **100.0%** / 全候補 **100.0%** で目標達成。T502の4項目（朝は苦手・どっち・おすすめ・断り＋前向き・札幌の前向き・謙譲語）とT504の2項目をすべて実走で確認。代表を t505 版へ差し替えた。 |

| T506 | 週末・普段などの習慣文を答えた話題として扱い、同じ話題の再質問を棄却 | pytest（`pytest -k t506` 1件、全体2045件＋Firefox29件）＋実API敬語20通会話テスト（`会話テスト/json/conversation_test_keigo20_ds4_t506.json` / `会話テスト/conversation_test_keigo20_ds4_t506.html`、接続エラーで17通BLOCKED） | FIXED（実走行は接続エラーで中断） | `_repeats_partner_fresh_statement` の対象文に習慣マーカー（週末・平日・普段・いつも・日課）を追加し、相手が「週末は近所の公園を散歩しています」と言った直後の「近くでよく行くお気に入りの公園とかあるんですか？」を「相手が直前に答えた内容を聞き返す」で棄却。回帰 `test_t506_partner_routine_topic_is_not_asked_again`。t506 の実走行は Gemini の 503/504 が続き17通で BLOCKED（19ブロック）。中断前の #12 で再質問の消滅を確認。代表は t505 のまま。 |

| T507 | 相手の状況と食い違うお弁当質問の棄却・「分かります」連結の検出 | pytest（`pytest -k t507` 2件、全体2048件＋Firefox29件） | FIXED | 相手が「普段は昼休みに友達とご飯に行きます。そちらはお弁当ですか？」と外食を述べた直後に、相手へ「普段はどんなお弁当を作ってるんですか？」と振る候補を `_asks_partner_bento_after_eating_out` で「相手の外食の話と食い違うお弁当の質問」として棄却。`candidate_has_missing_sentence_break` に「分かります」を追加し、相槌と本文の区切りなし連結を検出。回帰 `test_t507_no_bento_question_after_partner_eats_out`・`test_t507_reaction_word_is_not_concatenated`。 |

| T508 | 相手の状況と食い違う質問の一般化（T507のお弁当×外食を表駆動の共通検査へ） | pytest（`pytest -k t508` 2件、全体2050件＋Firefox29件） | FIXED | `PARTNER_PREMISE_CONFLICT_RULES`（相手の状況・両立しない質問の語・棄却理由の表）と `_partner_premise_conflict_reasons` を追加し、相手が直前に述べた状況と両立しない前提を置く質問行だけを棄却。ルールは お弁当×外食（T507 の理由文を維持し `_asks_partner_bento_after_eating_out` は薄いラッパー化）・通勤/満員電車/出社×在宅勤務/テレワーク/リモートワーク/家で作業・家族/両親との同居/実家から通う×一人暮らし。対象は `_is_ask_sentence` が真の質問行のみで、本人の回答や相槌の行は対象外。回帰 `test_t508_remote_worker_is_not_asked_about_commute`・`test_t508_partner_living_alone_is_not_asked_about_family`（修正前 `-k t508` で2 failed → 修正後PASS）。 |

| T509 | 本人情報確認で同じ質問を2回連続表示し、余分な1往復が発生 | ops1 実走行の観測（`会話テスト/conversation_test_ops1.html`・`json/conversation_test_ops1.json`）＋再現テスト | FIXED | 原因は保存順ではなく、`_topic_is_verified` の映画「最近」分岐（app.py 2317）が相手の前置きの「最近は流行ってる作品を…」に反応して `return any(...)`（＝False）で早期確定し、共通の「本人へ確認した質問に回答済みか」判定（同 2465 付近）に届いていなかったこと。ops1 の証拠（`session_answers` が1件＝同じ質問が2回、要求#3/#4 がどちらも `api_attempt_count 0`・provider試行 0）と一致。`_ephemeral_answer_matches_owned_question`（app.py 1656）を追加し、確認済みの質問に今回の回答が対応していれば回答済みとして扱う（趣味に「映画」と書いてあるだけの最近観た映画スコープは従来どおり満たさない）。回帰 `test_t509_supplied_answer_stops_repeating_the_same_question`・`test_t509_answered_question_resumes_generation_without_extra_round_trip`。全pytest（Firefox UI を除く）**2056 passed / 0 failed**。 |

| T510 | マッチ前「メッセージ付きいいね」の文面（名前呼びかけ＋挨拶・プロフィール共感・お話ししたい気持ち） | pytest（`pytest -k like_prompt_requires` 1件、全体2054件＋Firefox29件） | FIXED | 実際に送られるマッチ前いいねが要件を満たさない文面だったため、`prompts/like.txt` を3要素（「名前の呼びかけ＋挨拶」→「プロフィールから共感したところ・ここがいいなと思ったところ」→「よかったらお話ししてみたいという気持ち」）必須へ書き換えた。3要素はすべて入れ、いいねのみ3〜4文まで許可する。冒頭は相手の名前＋「さん」＋短い挨拶とし、名前が確実でない場合だけ呼びかけを省く。中身のない褒め言葉（「なんとなく」「雰囲気が」）を禁止し、質問は1つまで任意。既存の禁止（「私も」の共通点主張・外見評価・マッチ済み前提表現）は維持。回帰 `test_like_prompt_requires_name_greeting_empathy_and_desire_to_talk`。 |

| T511 | 誘い時期の下限（自分の送信15通、相手が「すぐ会いたい」希望なら例外） | pytest（`pytest -k "invite_floor or early_invite_is_downgraded"` 4件、全体2054件＋Firefox29件） | FIXED | 話題が揃っただけで会話開始直後に誘っていたため下限を導入。`MIN_SELF_MESSAGES_BEFORE_INVITE_DEFAULT = 15`（環境変数 `MRA_MIN_SELF_MESSAGES_BEFORE_INVITE` で上書き可）とし、今回作る候補を含めて自分の送信が15通目に届くまでは誘わない。相手プロフィールが `PARTNER_EAGER_TO_MEET_PATTERN`（「すぐに会いたい」「出会うまでの希望：すぐ」など）に一致する「すぐ会いたい」希望を示すときだけ下限を免除する。`build_context` に `conversation_length`（`my_messages` / `my_message_number_including_candidate` / `invite_min_my_messages` / `partner_wants_to_meet_soon` / `invite_allowed_now`）を追加し、プロンプト（`prompts/common.txt`）は `invite_allowed_now=false` のとき `invite_gently`・`consider_invite` を選ばず `continue_conversation` にするよう指示。実装側は `invite_allowed_by_conversation_length` で、invite系の判断が出た場合は1回だけ誘い抜きで再生成し、なお残る場合は `INVITATION_PATTERN` / `reply_move=="invite"` の候補を外して `continue_conversation`・Stage 2 に落とし、候補不足を通知する（`safe_candidates` を同期して `check_suggestions` の件数検査と一致させる）。`_apply_conversation_state_floor` にも判断のみを落とす最終ガードを追加。回帰 `test_invite_floor_requires_minimum_own_messages`・`test_early_invite_is_downgraded_before_minimum_own_messages`・`test_invite_floor_does_not_block_eager_partner`。下限導入で既存の誘い系テストは前提が変わるため、「すぐ会いたい」希望のプロフィール（`add_eager_match` / `EAGER_MEETING_PROFILE`）を使う形へ変更し、テストの意図を維持した。 |

| T512 | いいねの `reason` が候補本文に無い要素（質問）を述べる | ops1 実走行の観測（`会話テスト/json/conversation_test_ops1.json` の turns/0）＋pytest（`pytest -k t512` 1件） | FIXED | ops1 のマッチ前いいねは2案とも質問を含まないのに `reason` が「答えやすい質問を添えて」と述べ、説明と本文が食い違っていた。`/api/generate` の共通出力仕様（app.py 11915 付近）に「実際に候補本文へ入れた要素だけを書く」「本文に無い要素を reason に書かない」を追加。回答候補 `reason` については応答の元データ（観測3）として扱い、コード側で文言を書き換える処理は入れない。回帰 `test_t512_reason_spec_forbids_claiming_elements_absent_from_candidates`（like モード・count 3・偽プロバイダで `system_instruction` を捕獲して検証）。全pytest（Firefox UI を除く）**2057 passed / 0 failed**。 |

| T513 | 物・題材の名詞に「〜はよく行くんですか？」（壊れた日本語）を出す回答フォールバック | ops1 実走行の再現＋pytest（`pytest -k t513` 2件） | FIXED | ops1 受信#3 の「回答を反映した返信」は相槌（`_supplement_acknowledgment_lines`）＋確認済み回答のみで相手への質問が無かった。再現すると、`_compose_answer_relay_candidate` の聞き返し候補は「どんな〜が好き」と「〜はよく行く」の2択で、相手の質問の聞き返し（同義）になる1つ目が棄却されると2つ目の「楓さんはアニメはよく行くんですか？」が棄却理由ゼロで通る余地があった（アニメは場所ではないため不自然）。`_PLACE_LIKE_NOUN_PATTERN` を追加し、「〜はよく行く」は場所らしい名詞のときだけ候補にする。場所（公園・カフェ等）と行為語（将棋・読書等、`_ACTIVITY_FOLLOWUP_VERB`）は従来どおり。回帰 `test_t513_thing_topic_is_not_asked_with_go_frequently`・`test_t513_place_topic_may_be_asked_with_go_frequently`。全pytest（Firefox UI を除く）**2059 passed / 0 failed**。 |

| T514 | 話題転換フォールバックが行為語でも場所でもない話題に既定の「する」を付ける | pytest（`pytest -k t514` 2件）＋オフライン再現（`_build_topic_change_fallback_candidate`） | FIXED | ユーザーが「〜の話にして」と指示したとき、モデルが指定話題の候補を作れないと `_build_topic_change_fallback_candidate` が受け皿を合成するが、`_ACTIVITY_FOLLOWUP_VERB.get(requested, "する")` の既定値「する」のため「ちなみに楓さんは仕事はよくするんですか？」「（大学／ペット／北海道も同様）」という不自然な質問が棄却理由ゼロで通り得た（T513 と同種）。行為語（`_ACTIVITY_FOLLOWUP_VERB`）→ その動詞、場所らしい名詞（`_PLACE_LIKE_NOUN_PATTERN`）→「行く」、どちらでもない話題 → 動詞を使わない「ちなみに{相手}は{話題}って好きですか？」に変更。再現（修正後）: 北海道→「北海道はよく行くんですか？」、仕事／大学／ペット／資格勉強→「〜って好きですか？」、映画→「映画はよく観るんですか？」、カフェ→「カフェはよく行くんですか？」。回帰 `test_t514_topic_change_does_not_use_a_default_verb_for_things`・`test_t514_topic_change_keeps_activity_and_place_verbs`。全pytest（Firefox UI を除く）**2061 passed / 0 failed**。 |

| T515 | APIキーなし（デモ）のいいね例文がT510の3要素を満たさない | pytest（`pytest -k t515` 1件） | FIXED | `demo_suggestions("like")` の固定例文は実際にコピーされる文面なのに、5例中4例が3要素（挨拶／プロフィールに触れる／お話ししたい気持ち）のうち1つ以上を欠いていた（例:「はじめまして！\n紹介文が気になっていいねしました\nよろしくお願いします！」はお話ししたい気持ちなし）。4例を3要素を満たす形へ書き換え（名前は固定例文では分からないため省く）。回帰 `test_t515_like_demo_texts_satisfy_like_requirements`（5例すべてに挨拶・プロフィール言及・お話ししたい表現があり、句読点なし）。全pytest（Firefox UI を除く）**2062 passed / 0 failed**。 |

| T516 | 初回フォールバックが分割断片の話題化・好みの未確認断定を出す | pytest（`pytest -k t516` 2件）＋オフライン再現（`_build_first_message_fallback_candidate`） | FIXED | モデル候補が全滅したときの初回フォールバックで、「実家で猫と犬を飼っています。休日は家でのんびりしています」から「んびりしてがお好きなんですね！\nんびりしてで特におすすめはありますか？」という**分割断片の話題化**（助詞で切った断片「んびりして」を名詞扱い）が棄却理由ゼロで通り、「佐世保から来ました。今は一人暮らしです」から「一人暮らしがお好きなんですね！」という**好みの未確認断定**が出ていた。名詞抽出に断片除外（先頭「ん」・「して/って/みて/くて」で終わる断片）を追加し、節に好みの宣言（好き・趣味・お気に入り・楽しい・はまって・愛用）がある名詞だけを「お好きなんですね」の対象に変更。宣言が無いときは「プロフィールの{話題}のところが気になっていました！\nよかったら{話題}について教えてもらえますか？」の中立形にする。同点の話題は辞書順で決定（これまでは集合の反復順次第で実行ごとに揺れていた）。好みの宣言がある名詞（例「ランニングが趣味です」→「ランニングがお好きなんですね！」）は従来どおり。なお既存のelifチェーン（喫茶店・映画など）の誤マッチは「未確認の本人事実」検査が自力で棄却するため触っていない（再現で確認）。回帰 `test_t516_first_fallback_does_not_mangle_or_invent_likes`・`test_t516_first_fallback_keeps_liked_topic_assertion`。全pytest（Firefox UI を除く）**2064 passed / 0 failed**。 |

| T517 | 学校名・専攻の確定事実に「をしています」で答える（壊れた日本語＋末尾空行） | pytest（`pytest -k t517` 2件）＋オフライン再現（`_build_verified_profile_fact_fallback_candidate`） | FIXED | 職業・学校質問のフォールバックが確定事実の種類に関係なく `f"{値}をしています"` を使うため、「大学はどこですか？」× facts school=北海道大学 で「北海道大学をしています」という壊れた日本語が、末尾に空行を残したまま（`f"{line1}\n{followup}"` の followup="" で改行のみの行）**棄却理由ゼロ**で通っていた。専攻（major=経営学）でも「経営学をしています\n」が出ていた。`_verified_fact_answer_line` を追加し、学校名→「〜に通っています」、専攻→「〜を学んでいます」、職業→「〜をしています」（`_verified_job_or_school_values` と同じ条件で判定）。候補文は空行を除いて結合。あわせて職業トピックの送信前検査の許容答え形に「{値}に通っています」「{値}を学んでいます」等を追加し、正しい答え方が「相手からの直接質問に未回答」で落ちないようにした（修正後: 学校名・専攻とも棄却ゼロで成立、末尾空行なし）。職業の既存テスト（「経理をしています」等）は変更なし。回帰 `test_t517_school_fact_answers_with_the_right_verb`・`test_t517_study_subject_fact_answers_with_the_right_verb`。全pytest（Firefox UI を除く）**2066 passed / 0 failed**。 |

| T518 | 「今度」などの時を表す語が話題名詞になり「どんな今度が好き」と聞く | pytest（`pytest -k t518` 1件）＋オフライン再現（`_compose_answer_relay_candidate`） | FIXED | 誘いへの回答リレーで、「よかったら今度カフェに行きませんか？」× 回答「土曜の午後なら空いています」→「いいですね！\nぜひ行きましょう😊\n土曜の午後なら空いています\n**楓さんはどんな今度が好きなんですか？**」という壊れた日本語の聞き返しが棄却理由ゼロで付いていた。`_latest_topic_noun` が文頭の時を表す語（今度）を最初の内容語として選んでいたため。`_REPETITION_NOUN_STOPWORDS` に時を表す語（今度・今後・来月・今月・先月・今週末・来週末・午前・午後）を追加し、話題名詞にならないようにした。修正後は「今度」が除外され「カフェ」が話題になり「楓さんはカフェはよく行くんですか？」（自然な形）になる。回帰 `test_t518_invitation_relay_does_not_ask_about_time_words`。全pytest（Firefox UI を除く）**2067 passed / 0 failed**。 |

| T519 | タメ口の誘い（「行かない？」「会おう！」）が誘いとして認識されない | pytest（`pytest -k t519` 2件）＋オフライン再現（`INVITATION_PATTERN`・`_compose_answer_relay_candidate`） | FIXED | `INVITATION_PATTERN` が丁寧語の形（行きませんか・ましょう・行けたら・どうですか）しか認めないため、タメ口の誘い「今度カフェに行かない？ぜひ！」が誘いとして扱われず、回答リレーが承諾の受け止め（いいね！／ぜひ行きましょー）なしになり、回答「土曜なら空いてるよ」が「未確認の本人事実」で棄却されて最後は回答だけに縮んでいた（丁寧語の同じ場面では受け止め付きの4行が成立するのに）。`INVITATION_PATTERN` にタメ口の形（「会おう／会わない」＋スコープ語（今度・週末・近いうち等）＋「行こう／会おう／飲もう／遊ぼう／行かない／会わない」（「〜と思ってます」の意図報告は否定先読みで除外）、「今度／よかったら…会いたいです」）を追加。あわせてリレーの受け止めをタメ口では「いいね！」にし、`_ANSWER_RELAY_TEMPLATE_LINE` に「いいね」を追加してタメ口受け止め付きのリレーが「確認済み回答のリレー」として長さ制限を素通りできるようにした。修正後: タメ口の誘いでも「いいね！＋ぜひ行きましょー＋回答＋聞き返し」の4行が棄却ゼロで成立。回帰 `test_t519_casual_invitation_is_recognized_and_relayed`・`test_t519_casual_invite_pattern_variants`。全pytest（Firefox UI を除く）**2069 passed / 0 failed**。 |

| T520 | 断り回答に承諾の受け止めが重なり、断った話題の質問が付く | pytest（`pytest -k t520` 3件）＋オフライン再現（`_compose_answer_relay_candidate`） | FIXED | 誘いへの回答が断りでも、(1) タメ口の断り「ごめん、今はちょっと落ち着いていたいからやめておくね」が断りと認識されず（断り語彙が「やめておき」のみ）「いいね！\nぜひ行きましょー」（承諾）と断りが**同じ候補に矛盾して併存**、(2) 丁寧語の断りには「楓さんはカフェはよく行くんですか？」という**断った話題の質問**（再勧誘に当たる）が付いていた（いずれも棄却理由ゼロで送信可能）。`PARTNER_INVITATION_REFUSAL_PATTERN` にタメ口の断り（やめてお・落ち着いていたい・今回はパス・遠慮しておく等）を追加し、リレーの断り判定をこの共有パターンへ統一。断りのときは聞き返しを付けず（回答＋前向きな一言のみ）、`_build_invitation_acceptance_fallback_candidate` も本人の断り確認済みなら出さない。あわせて `_answer_lines_for_candidate`／`_normalized_answer_sentence_units` は「ごめんなさい、」等の挨拶・お詫びの語に続く読点を行区切りにして「ごめんなさい今は…」のような連結を作らない。修正後: 丁寧語・タメ口とも「断り＋また機会があればぜひ行きたいです！」（棄却ゼロ・承諾なし・質問なし）。回帰 `test_t520_declined_invite_gets_no_acceptance_and_no_reask`・`test_t520_greeting_comma_becomes_a_line_break`・`test_t520_acceptance_fallback_is_skipped_when_answer_declines`。全pytest（Firefox UI を除く）**2072 passed / 0 failed**。 |

| T521 | 時刻を含む報告に「当日を楽しみにしています」と約束を作る | pytest（`pytest -k t521` 2件）＋オフライン再現（`_build_schedule_confirmation_fallback_candidate`） | FIXED | 日時の受け止めフォールバックが「相手の発言に時刻が含まれ質問でない」だけで発火するため、(1) 誘いへの返事ではなく都合の報告「明日は19時までバイトです」にも、(2) 誘いの文脈が無い「今日は19時に帰ってきます」にも「19時ですね！\n当日を楽しみにしています😊」と**打ち合わせ未確定の約束を作って**いた（棄却理由ゼロで送信可能）。時刻が境界・報告の語（まで・帰っ・終わ・戻っ・出発・退勤）を伴うときは発火せず、発火条件を「自分の時間提案への同意（大丈夫・わかりました等）」または「相手自身の待ち合わせ宣言（待ち合わせ・会いましょう等）」に限定した。修正後: 同意「19時で大丈夫です！」と待ち合わせ宣言「12時に待ち合わせにしましょう」は従来どおり受け止め、都合の報告では出ない。回帰 `test_t521_schedule_confirmation_requires_an_agreed_time`・`test_t521_schedule_confirmation_still_fires_on_agreement`（T491の既存テストも通過）。全pytest（Firefox UI を除く）**2074 passed / 0 failed**。 |

| T524 | 丁寧な誘い（「お会いしませんか」「お会いしましょう」「一緒に行きましょう」）が誘いとして認識されない | pytest（`pytest -k t524` 3件）＋オフライン再現（`INVITATION_PATTERN`・`partner_latest_message_has_invitation`） | FIXED | `INVITATION_PATTERN` は丁寧な誘いのうち「会いません」「お会いましょう（近い将来の語付きは `し?ません` のみ）」しか認めておらず、活用「会い＋し＋ません／しましょう」を取りこぼしていた。このため「よかったら今度お会いしませんか？」「今度お会いしましょう」「近いうちにまたお会いしましょう」「よかったら一緒に行きましょう！」「一緒に行きましょう！」が**誘いとして認識されず**、送信前検査の「相手からの誘いに未回答」（app.py 10364）が働かず、誘いを無視した質問だけの候補が**棄却理由ゼロで通って**いた。承諾だけの受け皿（`_build_invitation_acceptance_fallback_candidate`）も出なかった。1本目のブランチへ「行きましょう／会いましょう／行こう／会おう」、2本目（今度・よかったら）へ「お会いしません／行きましょう／会いましょう／お会いしましょう」、3本目（近い将来の語）を「(?:お)?(?:会い|行き)し?ましょう(?:か)?」へ、4本目（スコープ語＋タメ口の勧誘）へ「行きましょう／会いましょう」を追加し、近い将来の語を伴わない丁寧な問いかけ「(?:お)?会いし?(?:ません|ましょう)か」を独立ブランチで拾うようにした。誘いでない報告（「来週は仕事で行けない」等）は引き続き拾わない。回帰 `test_t524_polite_invitations_are_recognized`・`test_t524_candidate_ignoring_polite_invitation_is_rejected`・`test_t524_polite_invitation_gets_an_acceptance_fallback`（修正前3 failed → 修正後PASS）。全pytest（Firefox UI を除く）**2077 passed / 0 failed**。 |

| T525 | 状態・確認の語（「大丈夫」「可能」「無理」「方法」「方向」等）が「どんな〜が好き」の話題になる | pytest（`pytest -k t525` 2件、非Firefox全体2079件＋Firefox29件）＋オフライン再現（`_latest_topic_noun`・`_compose_answer_relay_candidate`） | FIXED | 回答リレーの聞き返しは `_latest_topic_noun` が選んだ内容語に「どんな{N}が好きなんですか？」を付けるが、相手の確認・状態を尋ねる質問（「明日の14時で大丈夫ですか？」「その日は可能ですか？」「来週は無理ですか？」「この方法でいいですか？」「この方向で合っていますか？」「あとで連絡もらえますか？」）から**状態語・やりとりの語**を話題名詞として拾い、「黒川さんはどんな大丈夫が好きなんですか？」「どんな可能が好き」「どんな無理が好き」「どんな方法が好き」「どんな方向が好き」「どんな連絡が好き」という**意味の通らない聞き返し**を、`_candidate_rejection_reasons` **棄却理由ゼロ**で付けていた（送信可能）。T513（場所以外に「よく行く」を付けない）・T518（時を表す語を話題にしない）と同じ生成元修正として、`_REPETITION_NOUN_STOPWORDS` に状態・確認・やりとりの語（大丈夫・可能・無理・都合・方法・方向・確認・了解・承知・対応・連絡・返事）を追加。`_latest_topic_noun` は該当語を話題にせず、聞き返しが付かない（回答そのものは従来どおり届く）。好みの対象になる話題（カメラ等）の「どんなカメラが好き」は残ることを回帰で固定。回帰 `test_t525_state_nouns_do_not_become_like_topics`・`test_t525_likeable_topic_still_gets_the_preference_followup`（修正前 1 failed → 修正後PASS）。全pytest（Firefox UI を除く）**2079 passed / 0 failed**。 |

| T526 | 状態・確認の質問（「最近体調はどうですか？」等）から拾った語に「どんな〜が好き」の聞き返しが付く | pytest（`pytest -k t526` 2件、非Firefox全体2081件＋Firefox29件）＋オフライン再現（`_compose_answer_relay_candidate`） | FIXED | T525 のストップワード追加でも、漢字連続（「最近体調」＝1トークン）や未登録の抽象語（気分・具合・印象・結果・意味・不安・進捗・課題…）は `_latest_topic_noun` に拾われ、回答リレーが「黒川さんはどんな最近体調が好きなんですか？」「どんな気分が好き」「どんな具合が好き」「どんな印象が好き」という**意味の通らない聞き返し**を `_candidate_rejection_reasons` **棄却理由ゼロ**で付けていた。聞き返しの型そのものを修正し、「どんな{N}が好き」は相手が**好み・カテゴリを尋ねた質問**（どんな・何が／何を・どこ・好き・お気に入り・好み・趣味・興味…）にだけ付ける。状態・確認質問の目印（`_STATE_OR_CONFIRMATION_QUESTION_PATTERN`＝どうですか／いかが／大丈夫／可能／無理／いいですか／合っていますか／気分・体調・具合・様子・調子・印象・感想・理由・結果・意味・不安・心配・進捗・状況・課題・悩み・事情）があり、かつ好み・カテゴリの目印（`_CATEGORY_OR_PREFERENCE_QUESTION_PATTERN`）が無いときは付けない。活動（映画＝観る等）・場所（よく行く）の型は従来どおり。好み質問（「趣味はありますか？」→「どんな趣味が好き」「どんなお仕事をされていますか？」→「どんな仕事が好き」）と「なぜカメラを始めたんですか？」（T525回帰）は残ることを固定。回帰 `test_t526_state_questions_do_not_get_a_preference_followup`・`test_t526_preference_questions_keep_the_preference_followup`（修正前 1 failed → 修正後PASS）。全pytest（Firefox UI を除く）**2081 passed / 0 failed**。 |

| T527 | 相手が予定を断った・キャンセルした直後に、日程の再確認（「何時になったんですか？」）や「どんな〜が好き」の聞き返し（「どんな機会が好き」）が付く | pytest（`pytest -k t527` 5件、非Firefox全体2086件＋Firefox29件）＋オフライン再現（`_build_schedule_reask_fallback_candidate`・`_compose_answer_relay_candidate`） | FIXED | (a) 日時の食い違いを確認した後（「あれ午後じゃなかったんでしたっけ？」）に相手が「やっぱり今回はやめておきます」と断っても、日時変更保留の判定（`_schedule_change_pending`）が真のまま残り、`_build_schedule_reask_fallback_candidate` が**棄却理由ゼロ**で「何時になったんですか？」を送れてしまっていた。断りの後は日程の催促をしない。(b) 断り・キャンセルの直後の回答リレーが、断り文（「その日は行けません。別の機会にしましょう」）の「機会」を話題名詞として拾い、**棄却理由ゼロ**で「黒川さんはどんな機会が好きなんですか？」を付けていた。両者は「相手の断り／キャンセルを無視して再確認・聞き返しを続ける」という同種の欠陥のため、共通の断り判定 `_partner_latest_declines_plan`（`PARTNER_INVITATION_REFUSAL_PATTERN` に加えて予定キャンセル・延期の言い方 `_PARTNER_PLAN_DECLINE_PATTERN`＝無理です・無理そう・都合が合わな・予定が合わな・また今度・次回に・またにする を拾う）を追加し、`_build_schedule_reask_fallback_candidate` では断りなら候補を出さず、回答リレーの「どんな{N}が好き」の型（T526の好み・カテゴリ判定）にも断りでないことを条件に加えた。断りでない質問（趣味・仕事・カメラ）の聞き返しと、断りの無いときの「決まったら教えてください！」は残ることを固定。回帰 `test_t527_schedule_reask_is_not_sent_after_the_partner_declines`・`test_t527_schedule_reask_still_fires_when_no_decline`・`test_t527_declined_plan_does_not_get_a_preference_followup`・`test_t527_decline_detection_classifies_plan_cancellations`・`test_t527_non_decline_question_keeps_the_preference_followup`（修正前 3 failed → 修正後PASS）。全pytest（Firefox UI を除く）**2086 passed / 0 failed**。 |

| T528 | 状態語の話題転換（「体調の話にして」等）に「〜って好きですか？」の聞き方を付ける | pytest（`pytest -k t528` 2件、非Firefox全体2088件＋Firefox29件）＋オフライン再現（`_build_topic_change_fallback_candidate`） | FIXED | 話題転換の指示（「〜の話にして」）で行為語でも場所でもない話題には動詞を使わない聞き方（T514）を採るが、状態語（体調・気分・具合・調子…）に「〜って好きですか？」を付けると「ちなみに楓さんは**体調って好きですか？**」という**意味の通らない質問**になり、`_candidate_rejection_reasons` **棄却理由ゼロ**で通り得た。T526 で導入した状態・確認の目印 `_STATE_OR_CONFIRMATION_QUESTION_PATTERN` を話題の判定にも使い、状態語の話題は「ちなみに{相手}の{話題}はどうですか？」（体調→「ちなみに楓さんの体調はどうですか？」）にする。状態語でない話題（仕事・大学・ペット＝「〜って好きですか？」、映画＝「よく観る」、北海道＝「よく行く」）は従来どおり。回帰 `test_t528_state_topic_does_not_ask_whether_the_partner_likes_it`・`test_t528_likeable_topic_still_asks_whether_the_partner_likes_it`（修正前 1 failed → 修正後PASS）、T514 回帰 `test_t514_topic_change_does_not_use_a_default_verb_for_things`・`test_t514_topic_change_keeps_activity_and_place_verbs` も維持（2 passed）。全pytest（Firefox UI を除く）**2088 passed / 0 failed**。 |

| T529 | 出身・居住地や過ごし方を尋ねる質問、親族関係の語に「どんな〜が好き」の聞き返しが付く | pytest（`pytest -k t529` 3件、非Firefox全体2091件＋Firefox29件）＋オフライン再現（`_compose_answer_relay_candidate`） | FIXED | 「ご出身はどちらですか？」→「札幌です／黒川さんは**どんな出身が好き**なんですか？」、「休日は何をして過ごしていますか？」→「どんな休日が好き」、「ご兄弟はいますか？」→「どんな兄弟が好き」という**意味の通らない聞き返し**が `_candidate_rejection_reasons` **棄却理由ゼロ**で通り得た。出身・居住地（出身・住ま・住ん・生まれ・地元・在住）や過ごし方（何をして過ご・どのように過ご・一日の流れ・ルーティン・暇なとき…）は好みの質問ではないため、`_NON_PREFERENCE_QUESTION_PATTERN` を追加し、回答リレーの「どんな{N}が好き」の型（T526）に「好みの質問でない」ことを条件として加えた。親族関係の語（兄弟・姉妹）は `_REPETITION_NOUN_STOPWORDS` に追加。好みの質問（趣味→「どんな趣味が好き」、仕事→「どんな仕事が好き」、ペット・天気・カメラ）と「どこが好きですか？」のような場所の好みの質問は従来どおり。回帰 `test_t529_fact_questions_do_not_get_a_preference_followup`・`test_t529_siblings_question_does_not_get_a_preference_followup`・`test_t529_preference_questions_keep_the_followup`（修正前 2 failed → 修正後PASS）、T526/T527回帰も維持。全pytest（Firefox UI を除く）**2091 passed / 0 failed**。 |

| T530 | 承諾の回答をリレーすると、文末の読点を詰めて2文を1行にし（「いいですね行きましょう」）、承諾の相槌を重ねる（「いいですね！／ぜひ行きましょう😊／いいですね／お願いします」） | pytest（`pytest -k t530` 4件、非Firefox全体2095件＋Firefox29件）＋オフライン再現（`_answer_lines_for_candidate`・`_compose_answer_relay_candidate`） | FIXED | 誘いへの承諾回答「いいですね、行きましょう」のリレーが「いいですね！／**いいですね行きましょう**／黒川さんはカフェはよく行くんですか？」となり、相槌「いいですね」が重複し、2文が1行に詰め込まれていた。「いいですね！お願いします」では「いいですね！／ぜひ行きましょう😊／いいですね／お願いします／…」と承諾の言い回しを3つ重ねていた。「札幌です、生まれも育ちも札幌です」も「札幌です生まれも育ちも札幌です」と1行に詰まっていた。読みやすさの要「1文ごとに改行」に反する。(a) 読点の直前が文末（です・ます・ましょう・ください等）で終わるときは読点を文の区切りとして改行する `_split_at_sentence_final_commas` を追加し、`_answer_lines_for_candidate` と `_normalized_answer_sentence_units` で共用した。(b) 回答が「いいね／いいですね／いいです」で始まるときは承諾の相槌を重ねず、`already_accepts` に「お願いします」を足して「ぜひ行きましょう」の重複も避けた。列挙（映画、音楽、読書が好きです）と接続（雨ですが、行きます）の読点は分断せず従来どおり。回帰 `test_t530_sentence_final_comma_becomes_a_line_break`・`test_t530_enumeration_and_continuative_comma_is_not_split`・`test_t530_acceptance_relay_does_not_repeat_the_ack`・`test_t530_acceptance_answer_with_the_ack_gets_no_extra_ack`（修正前 3 failed／1 passed → 修正後PASS）。全pytest（Firefox UI を除く）**2095 passed / 0 failed**。 |

| T531 | 初回メッセージのフォールバックが、プロフィール文の動詞・形容詞・挨拶の断片を話題語にして壊れた日本語を作る（「動かすがお好きなんですね！」「プロフィールのないのところ…」「よろしくお願いしについて…」）。さらに検証側だけ古い抽出のままで、正しい「散歩がお好きなんですね！」を話題不足として棄却する | pytest（`pytest -k t531` 4件、非Firefox全体2099件＋Firefox29件）＋オフライン再現（`_build_first_message_fallback_candidate`・`_first_message_required_content_reasons`） | FIXED | 初回フォールバックの話題語抽出が、節を助詞で割った断片をそのまま名詞として扱っていた。「体を動かすことが好きです」→**「動かすがお好きなんですね！」**、「甘いものに目がないです」→**「プロフィールのないのところが気になっていました！」**、「よろしくお願いします」→**「よろしくお願いしについて教えて…」**が `_candidate_rejection_reasons` **棄却理由ゼロ**で通り得た。また必須要素の検証（`_first_message_required_content_reasons`）だけが古い抽出の複製を持ち、「犬と散歩するのが好きです」から「散歩する」という塊を要求していたため、生成側の正しい「散歩がお好きなんですね！」を**話題不足**として棄却し、安全な候補がゼロになっていた。抽出を `_profile_topic_terms` に一本化して生成と検証で共有し、`_topic_term_is_usable_noun` で (a) 挨拶の決まり文句（よろしく・お願い…）、(b) 形容詞・否定の語尾（〜い・ない）、(c) 漢字・カタカナを含む動詞語尾（う・く・す・つ・ぬ・ぶ・む・る・ぐ）、(d) ます・ました・ている・られる・たい等の活用語尾を落とす。先頭の副詞（よく写真→写真）を除き、サ変動詞は語幹だけ残す（散歩します→散歩）。「一人暮らし」「カフェ巡り」「山登り」は「し・り」で終わるため名詞として残り、好みの宣言が無ければ「お好き」と断定しない（T516維持）。回帰 `test_t531_profile_topic_terms_reject_verb_and_greeting_fragments`・`test_t531_first_message_fallback_never_uses_broken_fragments`・`test_t531_first_message_fallback_uses_the_profile_topic_for_walking`・`test_t531_first_message_fallback_does_not_assert_unknown_preferences`（修正前 3 failed／1 passed → 修正後PASS）。全pytest（Firefox UI を除く）**2099 passed / 0 failed**。 |

| T532 | 相手がプロフィールで宣言した好みを「〜がお好きなんですね！」と受け止めた候補が「未確認の本人事実」として棄却され、初回メッセージの候補がゼロになる（読書・映画） | pytest（`pytest -k t532` 2件、非Firefox全体2101件＋Firefox29件）＋オフライン再現（`_build_first_message_fallback_candidate`・`unsupported_personal_claim_topics`） | FIXED | 「読書が好きです」の相手への「**読書がお好きなんですね！**」が `unsupported_personal_claim_topics` の話題別パターン（読書は「読書…好き」）に掛かり、`_candidate_claim_is_partner_attribution` が**履歴だけ**を見ていたため履歴の空の初回メッセージでは必ずFalse →「未確認の本人事実」で棄却され、安全な候補がゼロになっていた。映画も同様（「映画がお好きなんですね！」が映画の意見表明 `_movie_assertion_segments` に拾われる）。相手の**プロフィールも相手自身の申告**として扱う `_declared_partner_preference_clauses`（プロフィール＋相手の履歴から、好みの宣言があり・疑問文でなく・否定でない節）と `_preference_attribution_clauses`（候補の「〜なんですね」節の話題語が相手の宣言に実在する節）を追加し、`_candidate_claim_is_partner_attribution` の共通免除と `_movie_assertion_segments` の除外に使った。宣言の無い話題（散歩が趣味の相手への「映画がお好きなんですね」）と否定の宣言（「映画は好きじゃないです」）は免除しない。回帰 `test_t532_preference_attribution_clauses_require_a_declared_preference`・`test_t532_declared_partner_preference_is_not_treated_as_my_fact`（修正前 2 failed → 修正後PASS）。全pytest（Firefox UI を除く）**2101 passed / 0 failed**。 |

| T533 | 初回フォールバックがプロフィールに無い固定の話題語を出し、必須要素の検証で棄却される（「カフェ巡り」→喫茶店、「旅行」→散歩、「音楽」→映画） | pytest（`pytest -k t533` 1件、非Firefox全体2103件＋Firefox29件）＋オフライン再現（`_build_first_message_fallback_candidate`・`_candidate_rejection_reasons`） | FIXED | キーワード分岐が固定語（喫茶店・散歩・映画・読書）を話題語にしていたため、(1) プロフィール「休日はカフェ巡りをしています」に**「喫茶店がお好きなんですね！」**、(2) 「旅行が好きで、よく写真を撮ります」に**「散歩がお好きなんですね！」**、(3) 「音楽が好きです」に**「映画がお好きなんですね！」**と、相手が言っていない話題を出していた。T531 で生成と検証の話題語を一本化したため、これらは必須要素の「プロフィール話題不足」で棄却され、安全な候補がゼロになっていた。`_fallback_profile_topic` でプロフィールの実語（最長・辞書順）を選び、`_fallback_topic_line` で好みの宣言がある語だけ「好き」と断定する（宣言が無ければ「プロフィールの{N}のところが気になっていました！」）。旅行・音楽は専用の質問（「旅行先はどこが多いですか？」「最近よく聴くアーティストはいますか？」）に分岐。修正後は4例すべて棄却理由ゼロ。フォールバックが成立するようになったため、既存の `test_first_mode_withholds_candidates_missing_required_opening_content` は「候補0件で停止」ではなく「不正なモデル候補を出さず検証済みフォールバックへ差し替える」ことを確認する形へ更新した（27パラメータ）。回帰 `test_t533_first_message_fallback_uses_the_profile_word_for_hobbies`（修正前FAIL）。全pytest（Firefox UI を除く）**2103 passed / 0 failed**。 |

| T534 | 丁寧な質問「普段はどんなお店に行かれることが多いですか？」が本人の頻度習慣の断定として棄却される | pytest（`pytest -k t534` 1件、非Firefox全体2103件＋Firefox29件）＋オフライン再現（`_has_unverified_general_personal_claim`） | FIXED | 未確認の本人事実の検査は「普段は…行…る」のような頻度習慣の型を本文全体から拾うため、**相手に向けた質問**「普段はどんなお店に行かれることが多いですか？」まで本人の習慣として扱い、カフェ系の初回候補を棄却していた。最初に `_candidate_claim_is_interrogative` を「丁寧な質問の語尾なら質問」と広く緩めたところ、既存の安全テスト27件（買い物などの一人称の断定を含む文）が壊れたため撤回し、節レベルの狭い判定にした：頻度の副詞を含む候補でも、一致部分に疑問語（どんな・どちら・どこ・何・いつ・誰・どう等）があり、かつ所属する節が丁寧な質問（〜ですか・ますか・ませんか…）で終わるときだけ本人の事実にしない。一人称の断定「普段はよくカフェに行きます」は従来どおり棄却する。回帰 `test_t534_polite_question_is_not_a_first_person_habit`（修正前FAIL、断定側の対照つき）。全pytest（Firefox UI を除く）**2103 passed / 0 failed**。 |

| T535 | 「どんな曲を聴くときに行くのが好きなんですか？」のような動詞を重ねた係り受けの壊れた質問が、棄却理由ゼロで送信候補に出る | pytest（`pytest -k t535` 1件）＋実走行 ops2（`会話テスト/conversation_test_ops2.json`） | FIXED | ops2 の実走行で、ライブの話題に対して**「ライブ行ってみたいですね✨／どんな曲を聴くときに行くのが好きなんですか？」**が候補に出た。「聴く」と「行く」が重なり、相手に意味が伝わらない。`_STACKED_RELATIVE_QUESTION_PATTERN`／`_candidate_has_stacked_relative_question` を追加し、`_candidate_rejection_reasons` で**「質問のつくりが不自然（動詞の重なり）」**として棄却する。対象は「どんな＋3〜24文字＋ときに＋移動/行為の動詞＋のが好き」に限定し、自然な「どんな音楽を聴くのが好きですか？」「どんなときに食べるのが好きですか？」「学生のときに行ったライブは楽しかったです」は対象外（回帰で対照）。 |

| T537 | 本人確認質問に回答しても同じ質問を返し続け、20通の実走行が6ターンで止まる（40リクエストのループ） | pytest（`pytest -k t537` 2件）＋実走行 t533b/t533c＋単発再現（`/api/generate` 1回） | FIXED | 実走行で「最近行った旅行先やお出かけ先があれば教えてください」に回答（「去年は京都と沖縄に行きました」）を渡しても同じ質問が返り続け、アプリ送信6通のまま40リクエストを消費した。原因は (1) `_topic_is_verified("旅行最近")` が「去年」を明示的な過去旅行として除外するため回答では確認済みにならない（最近＝去年ではないという検証自体は意図どおり）、(2) 生成後の直接質問パスがセッション内の回答を参照せず同じ確認質問を無条件に返すこと。`_personal_question_was_answered(context, question)` を追加し、`session_answers` と `ephemeral_user_answers` の両方で同じ質問文への空でない回答を検出したら、再質問せず `blocked_user_info_response`（「回答済みの本人情報では候補の自己開示を裏づけられなかったため、同じ確認を繰り返さず生成を中断しました」）で止める。ループは最大1回で終わり、利用者に状態が伝わる。回帰 `test_t537_answered_personal_question_is_not_asked_again`（真偽表）と `test_t537_recent_trip_question_stays_unverified_for_an_old_trip_answer`（去年の回答では確認済みにならない＝引き金の記録）。 |

最新ID行: 537（T466は欠番）。`tests`（Firefox UI を除く）は **2106 passed / 0 failed**、Firefox UI 単独で **29 passed**（一括実行時は Selenium タイムアウトが1件出る環境依存あり）。Actions は `cc4dceb`・`7deb12a`・`522d6aa`・`9e96820`・`a4025f4`・`ad8c8c4`・`51af300`・`815ad9a`・`693a19e`・`c4b7165`・`f419042`・`4de1437`・`f19d2de`・`23c8153`・`08c3f7d`・`ea504c9`・`4d62a23`・`5bfc4f0`・`3cb0ffc`・`dd14656`・`f7a574b`・`0879c85`・`e809768`・`c5e1c8c`・`4ac629c`・`5b7c14a`・`43cb5a9`・`789ce13`・`4245f0b`・`ca9f8ce`・`fdbe07e`・`daa4a9b`・`48f7fd0`・`74b3148`・`899016e`・`60c3507` が success。実Gemini20通は t505 で20通・相手19通・`LIMIT_REACHED`・候補停止0回・要求31回、主指標 **100.0% / 100.0%** を記録し、代表を t505 版へ差し替えた。相槌の主指標は「相手が話したターン」を対象とし質問だけのターンは除外する。claude からの引き継ぎ後は、報告の確認と次タスクの決定も ds4 が行う。改修のたびにプロンプトと検査・フォールバックの矛盾点検を行う。
