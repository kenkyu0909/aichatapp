# 検証進捗

最終更新: 2026-10-14 13:36 JST

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
- UI実操作: `PASS`（Firefox）
- 不具合修正後のpytest: `PASS`（15件成功、警告1件）
- GitHub push・Draft PR: `BLOCKED`（GitHub認証ユーザー `utyujin51` に対象リポジトリへの書込権限がなく、pushがHTTP 403。PR作成・Draft解除も未実施）

## 完了した作業

- 指定ブランチをクローンし、作業ブランチを作成。
- README、FastAPI、UI、起動バッチ、依存関係、既存テスト、Gemini smoke testを確認。
- Python仮想環境を作成し、依存関係を導入。
- `start.bat` と直接のUvicorn起動を実行。`127.0.0.1`のローカルURL、HTML、CSS、JavaScriptがHTTP 200を返すことを確認。バッチがWindows既定ブラウザーを起動しないようFirefox専用に修正し、再実行でFirefox表示を確認。
- Firefoxでプロフィール保存、相手3人、写真表示、会話分離、検索、切替、再読込、返信生成、いいね生成、コピー、送信記録、履歴・設定・使い方、JSON export、キーボード操作、相手削除を実施。
- サーバー再起動後も架空プロフィール、相手、会話がSQLiteに残ることを確認。
- API1・API2の指定キーのみでGemini実通信。API1 3.5の割当制限応答後、API2 3.5へ切替。
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
- 指定フォルダー由来の実API試行は合計12回（API1 3.5が1回、API2 3.5が11回）。API1 3.5は割当上限応答後にAPI2へ切替。API2 3.5は10回応答成功し、1回は誤ったローカルキー抽出で認証/モデル権限エラー。
- プロンプトを修正する品質再試験とUI/smoke test確認で追加実通信。API1/2の3.1は未使用。
- APIキーを読み取った際、秘密値を伏せる処理が失敗し、この会話のツール出力に両キーが露出した。Gitには保存していないが、両キーを失効し、新しいキーへ交換する必要がある。作業後の無効化判断もユーザーに案内する。
- APIフォルダー指定前に、既存の環境変数キーで失敗リクエストを1回行った。指定後は当該キーを使っていない。環境変数キーの出所・状態は要確認。
- Google公式の料金・利用規約で無料枠と入力データ取扱条件を確認。無料枠への入力は製品改善に使われる場合がある。プロジェクト固有の課金状態は確認できない。

## GitHub・ブロッカー

- push実行結果: `403 Permission to kenkyu0909/aichatapp.git denied to utyujin51`。
- GitHub Secret一覧の参照も403。Secretの有無は未確認。
- 作業ブランチのremote作成、Draft PR、PR更新・Draft解除はできていない。
- 初期コミットと最終変更はローカルブランチに記録する。GitHubへの反映には書込権限を持つアカウントまたは権限付与が必要。

## 残作業

1. 最終テストとGit差分を確認し、意味のある単位でローカルコミット。
2. pushを再試行し、403ならブロッカーとして最終報告に残す。
3. API1・API2キーを失効・再発行し、露出した環境変数キーの有無も確認する。

## GitHub

- 最終実装コミットSHA: `ae042ea41b3b1439abc6c8c27c8945a1fd915682`
- 検証報告コミット: 作成後のGitHub ActionsでなくローカルGitログを参照
- Pull Request URL: 未作成（push権限なし）
