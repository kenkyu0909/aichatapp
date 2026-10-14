# テストマトリクス

結果は実際に確認できるまで`NOT_TESTED`とする。

| ID | テスト項目 | 実施方法 | 結果 | 証拠・備考 |
|---|---|---|---|---|
| T01 | アプリ起動（Python） | uvicorn起動 | NOT_TESTED | |
| T02 | `start.bat`起動 | Windows実行 | NOT_TESTED | |
| T03 | ローカルURL HTTP 200 | HTTP確認 | NOT_TESTED | |
| T04 | HTML・CSS・JavaScript配信 | ブラウザーとHTTP確認 | NOT_TESTED | |
| T05 | ブラウザーConsole | UI操作 | NOT_TESTED | |
| T06 | 自分のプロフィール新規保存・再読込・更新 | UI操作とAPI/SQLite確認 | NOT_TESTED | |
| T07 | 相手3人の登録・表示・検索・切替 | UI操作 | NOT_TESTED | 架空データ |
| T08 | 相手プロフィール編集・削除 | UI操作 | NOT_TESTED | |
| T09 | 写真追加・表示・更新 | UI操作 | NOT_TESTED | 架空の識別用画像 |
| T10 | 不正画像と5MB超画像の拒否 | UI/API異常系 | NOT_TESTED | |
| T11 | 相手別メッセージ追加・時系列・発言者表示 | UI操作 | NOT_TESTED | |
| T12 | メッセージ編集・削除 | UI操作 | NOT_TESTED | |
| T13 | 相手切替時の履歴分離 | UI操作 | NOT_TESTED | |
| T14 | 再読み込み・再起動後のSQLite永続化 | UI操作後にアプリ再起動 | NOT_TESTED | |
| T15 | 相手削除時の履歴・写真削除 | UIとSQLite/ファイル確認 | NOT_TESTED | |
| T16 | 返信生成1案・3案・5案 | UI/API | NOT_TESTED | |
| T17 | 敬語・混合・タメ口・自動 | UIとプロンプト確認 | NOT_TESTED | |
| T18 | 返信方向・追加指示 | UI/API | NOT_TESTED | |
| T19 | 会話方針の表示切替 | UI操作 | NOT_TESTED | |
| T20 | 候補コピーと送信済み記録の分離 | UI操作・DB確認 | NOT_TESTED | |
| T21 | 追いメッセージ生成と用途 | UI/API | NOT_TESTED | |
| T22 | メッセージ付きいいね3案 | UI/API | NOT_TESTED | |
| T23 | 会話履歴画面・設定画面 | UI操作 | NOT_TESTED | |
| T24 | JSONエクスポート | UI操作 | NOT_TESTED | |
| T25 | キーボード操作 | UI操作 | NOT_TESTED | |
| T26 | Gemini返信実通信・日本語品質 | 実API 1リクエスト | NOT_TESTED | APIキー有無を確認 |
| T27 | Geminiいいね実通信・品質 | 実API 1リクエスト | NOT_TESTED | APIキー有無を確認 |
| T28 | Gemini候補数と重複検証 | 実APIまたはモック | NOT_TESTED | |
| T29 | APIキー未設定時の表示と生成 | ローカル起動/UI | NOT_TESTED | 固定デモの明示を確認 |
| T30 | 無効キー・未使用モデル・429処理 | モック/局所確認 | NOT_TESTED | |
| T31 | ネットワーク切断・不正JSON処理 | モック | NOT_TESTED | |
| T32 | 空入力・空プロフィール | UI/API異常系 | NOT_TESTED | |
| T33 | 存在しない相手ID | API異常系 | NOT_TESTED | |
| T34 | 長い会話履歴 | API/SQLite | NOT_TESTED | 最大60件の文脈制限を確認 |
| T35 | 保存先へのアクセス失敗 | モック/局所確認 | NOT_TESTED | |
| T36 | サーバー停止中のUIエラー | UI操作 | NOT_TESTED | |
| T37 | 起動ホストが127.0.0.1 | プロセス/ソース確認 | NOT_TESTED | |
| T38 | 写真がGeminiへ送られない | 送信文脈/コード確認 | NOT_TESTED | |
| T39 | 他の相手の履歴がGeminiへ送られない | 送信文脈確認 | NOT_TESTED | |
| T40 | APIキーがリクエスト本文やログに出ない | 文脈・ログ確認 | NOT_TESTED | 値は出力しない |
| T41 | `.env`、DB、写真がGit追跡されない | git確認 | NOT_TESTED | |
| T42 | XSS・パストラバーサル | コードと異常入力確認 | NOT_TESTED | |
| T43 | プロフィール内の命令文への耐性 | 架空プロンプト入力 | NOT_TESTED | |
| T44 | APIエラー時に会話履歴が保全される | 異常系前後比較 | NOT_TESTED | |
| T45 | 無料枠プライバシー条件の公式確認 | Google公式資料確認 | NOT_TESTED | |
| T46 | Windows利用手順 | `start.bat`とREADME確認 | NOT_TESTED | |
