# uranai366（人生予報 366日誕生日占い 2027年版）

翔太さん向けのメモです。**2026-10-13 から、パソコン上の Claude Code（ローカル）で使う前提に切り替えました。**

## はじめての準備（パソコンで1回だけ）
1. 必要なものを入れる（入っていれば不要）
   - Git for Windows … https://git-scm.com/
   - Python 3.11 以上 … https://www.python.org/ （インストール時に「Add python.exe to PATH」にチェック）
   - Node.js 20 以上 … https://nodejs.org/
2. このリポジトリをパソコンに置く。Obsidian の外に置くのがおすすめ（ファイル数が多く、Obsidian の検索が重くなるため）
   ```
   cd D:\
   mkdir Projects
   cd Projects
   git clone https://github.com/WarGrey19921024/uranai366.git
   ```
3. Claude デスクトップアプリの Code を開き、作業フォルダに `D:\Projects\uranai366` を選んで新しいセッションを始める
4. 最初のセッションで次の一文を送る（Python と Node の部品を Claude Code が入れます）

   > CLAUDE.md の「ローカルでの準備」をやって

## ふだんの始め方
Code で `D:\Projects\uranai366` を開いて、次の一文を送る

> CLAUDE.md の手順で始めて

途中で止まっても、次のセッションで同じ一文を送れば `work/00_進捗.md` を見て続きから進みます。
🛑 の確認ポイントでは Claude が止まって質問してくるので、返事をしてください。

## 中身
- `docs/01_作業指示書.md` … 作業の流れ（Claude Code はこれに従う）
- `docs/02_実装仕様.md` … 何を作るか
- `docs/prototype/` … 1月1日の試作ページ（ブラウザで開ける）
- `work/` … Claude Code が作ったものが入る
- `work/00_進捗.md` … 今どこまで進んだか

## 成果物を Obsidian に戻すには
ローカルなら Claude Code に「work を Obsidian にコピーして」と頼めば、
`D:\Obsidian\Obsidian\30_Areas\副業\10_Webメディア\12_占いサイト\記事\2027誕生日占い\work\` にコピーします（ZIP のダウンロードは不要）。

## 注意：このリポジトリは「公開」です
GitHub 上で誰でも読めます。公開前の原稿やサーバーの情報を置かないでください。非公開にするなら、GitHub のリポジトリ画面 → Settings → 一番下の「Change repository visibility」→ Private。
