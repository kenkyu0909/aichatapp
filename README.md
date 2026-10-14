# Matching Reply Assistant — Windows ローカルアプリ

確認いただいたPC向けのUIに、Python (FastAPI)・SQLite・Gemini APIを接続した本人専用アプリです。通常の会話データはPC内に保存します。ログイン機能・外部サーバー・自動送信はありません。

## 1. Windowsで起動する

1. Python 3.11以降をインストールします。インストーラーで Add Python to PATH をオンにしてください。
2. GitHubのブランチ feat/ui-local-backend-v1 を開き、Code → Download ZIPで取得し、展開します。
3. フォルダ内の **start.bat** をダブルクリックします。初回はライブラリのインストールがあるため、インターネット接続が必要です。
4. ブラウザで **http://127.0.0.1:8765/** を開きます。通常は起動時にブラウザが開きます。
5. 右上の「⚙ 設定」から「架空の相手を2人追加して試す」を押すと、実際の個人情報なしで操作確認できます。
6. 終了時は起動用の黒い画面で Ctrl+C を押してください。

## 2. Gemini APIを使う

APIキーがない状態でも、相手の登録・写真・会話履歴・候補表示の操作はできます。ただし生成候補は**会話を解析しない固定サンプル**です。

1. [Google AI Studio](https://aistudio.google.com/apikey) でAPIキーを作ります。
2. 初回起動時に自動作成された **.env** ファイルをメモ帳で開き、GEMINI_API_KEY= の右側にキーを記入します。
3. start.bat を一度停止して起動し直します。
4. 標準モデルは **gemini-3.5-flash-lite** です。変更するときは .env の GEMINI_MODEL= を編集します。

無料枠のモデル・プロジェクト・レート制限は [公式料金表](https://ai.google.dev/gemini-api/docs/pricing) と [AI Studio](https://aistudio.google.com/rate-limit) で確認してください。1日1000回は固定保証ではありません。**すでに課金が有効なプロジェクトの料金上限や請求状態を、このアプリは自動的に管理しません。** 無料運用なら、課金していないGoogleプロジェクトを使用してください。

## 3. 主な機能

- 自分のプロフィールの登録と保存（名前・年齢・職業・性格・趣味・話し方など）
- 相手の名前・プロフィール・識別用写真の登録・編集・削除
- 相手ごとの会話履歴の保存、履歴の編集・削除
- Geminiによる返信候補1・3・5案、文体や方向性・追加指示の反映
- 追いメッセージ案と会話方針の提案
- 相手のプロフィールからマッチ前の「メッセージ付きいいね」3案を生成
- 候補のコピーと、**送った文章だけを手動で履歴に記録**
- 架空データを使った動作確認と会話JSONのエクスポート

## 4. 保存とプライバシー

- アプリのサーバーは 127.0.0.1 にのみ接続します。GitHub PagesのURLから動くアプリではありません。
- 自分・相手のプロフィールと会話履歴は data/app.sqlite3 に、写真は data/photos/ に保存します。Git追跡から除外しています。
- Gemini生成時には本人・対象の相手のプロフィール、相手の名前、対象の直近最大60件の会話と生成オプションをGoogleに送信します。**写真、ファイルパス、他の相手の会話は送信しません。**
- **Gemini APIの無料枠へ送る入力データは、Googleの製品改善に使用される場合があります。** 必要なら匿名化・個人情報の削除をしてください。
- APIキーを保存した .env や個人データの data/ をGitHubにコミットしないでください。リポジトリがPublicでも、これらは公開しないでください。
- バックアップ時はアプリを停止してから data/ をコピーしてください。
- 写真はJPEG・PNG・WebPの最大5MBを受け付けます。AI画像認識は行いません。

## 5. 開発・テスト

主なファイル：

- index.html / style.css / app.js：画面とUI操作
- app.py：FastAPIとSQLiteとGeminiへの接続
- prompts/reply.txt / prompts/like.txt：生成時のAIへの指示
- start.bat：Windows用の起動ファイル
- .env.example：設定例
- tests/test_app.py：架空データだけを使うローカルAPIテスト

架空データによるテスト：

    python -m pip install -r requirements.txt pytest httpx
    python -m pytest -q

外部Geminiとの実通信・AI生成品質は、APIキーをPC内で設定してから確認してください。

## 6. GitHub PagesのUIと区別してください

[既存のUIデモ](https://kenkyu0909.github.io/aichatapp/) は design/ui-only-v1 の静的デモです。バックエンドへ接続されません。**今回のシステムはPCで start.bat を起動した http://127.0.0.1:8765/ から使用します。**
