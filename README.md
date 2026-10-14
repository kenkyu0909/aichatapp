# Matching Reply Assistant — UI-only v1

マッチングアプリの返信を支援する、Windows PC向けUIプロトタイプです。ご提供いただいた参考画像をもとに、**左側の相手一覧＋会話画面＋画面下部の返信操作**というレイアウトにしました。

## ブラウザでURLから操作する（GitHub Pages）

このブランチは、HTML/CSS/JavaScriptのみで構成されています。**Cloneせず**に、GitHub PagesのURLから操作できます。ただし最初に、リポジトリ管理者がGitHub上で次の初期設定を一度行う必要があります。

1. [リポジトリのPages設定](https://github.com/kenkyu0909/aichatapp/settings/pages) を開く。
2. **Build and deployment → Source** で **Deploy from a branch** を選ぶ。
3. **Branch** を `design/ui-only-v1`、フォルダを **/(root)** にして **Save** を押す。
4. 公開処理が成功すると、[https://kenkyu0909.github.io/aichatapp/](https://kenkyu0909.github.io/aichatapp/) でUIを操作できます。URLが有効になるのはGitHub Pagesのデプロイ成功後です。

これ以降、`design/ui-only-v1` へUI変更をプッシュすれば、自動的に反映される構成です。Pagesに公開される内容は一般公開されるため、架空データとUIコード以外をこのブランチへコミットしないでください。

## 表示方法

1. `design/ui-only-v1` ブランチを ZIP でダウンロード（GitHub の **Code → Download ZIP**）
2. 展開したフォルダの `index.html` をダブルクリック
3. Chrome / Edge 等のブラウザで表示されます。Python、サーバー、APIキーは不要です。

## UI上で試せること

- 架空の相手12人の切り替えと名前検索
- 相手の登録・編集・削除、識別用写真（画面上だけ）
- 会話を「相手として送信」「自分として送信」で追加
- 文体切り替え（自動／敬語／混合／タメ口）
- 返信方向と候補数（1・3・5）選択
- 固定サンプルの返信候補・追いメッセージ候補とコピー
- メッセージ付きいいねBOT（架空のサンプル文章）
- 自分のプロフィール入力、履歴表示、架空データのJSONエクスポート

**重要：UI-onlyデモです。** JavaScript内の仮サンプル文を表示します。生成AIは接続されていません。入力した情報はブラウザの一時メモリだけに保持され、ページを再読み込みすると消えます。バックエンド、データベース、保存、認証、自動送信はありません。

すべての初期データは架空の内容です。相手の写真を選んだ場合もブラウザ内の一時プレビューだけに使用し、外部にアップロードしません。

## 構成

- `index.html` — 画面構造
- `style.css` — PC向けのレイアウト・デザイン
- `app.js` — UI-onlyの操作デモ

このブランチは `main` から作成しており、`arena/072200f4-aichatapp` および `feat/local-matching-ai-mvp` には依存しません。