# uranai366 — 人生予報「366日誕生日占い 2027年版」制作リポジトリ

占いサイト「人生予報」（https://www.uranai.epoch-compass.com/）の誕生日占い366ページを、2027年版として一から作り直すためのリポジトリ。サイト運営者は翔太（本人）。

## 始め方・再開のしかた（毎回これ）
1. `work/00_進捗.md` を読む
   - 「未着手」なら → `docs/01_作業指示書.md` を最初から読み、フェーズ1から始める
   - 途中なら → 書いてある「次にやること」から再開する。必要な部分だけ `docs/01_作業指示書.md` を読み直す
2. 何を作るかは `docs/02_実装仕様.md`、見た目と分量の見本は `docs/prototype/birthday-0101-2027_試作.html`
3. 本人がこれまでに決めたことは `docs/04_本人の決定.md`（🛑で返事をもらったら、ここに追記する）
4. **始める前に `git pull`（main）で最新にする。** 作業ブランチで始めた場合は `git merge origin/main` で main の更新を取り込む。フェーズ（または星座）が終わるたびに、push したうえで **main にもマージして push** する（次のセッションは main から始まるため）

## 動かす場所（2026-10-13〜：本人のパソコン＝Windows のローカルが基本）
- 作業フォルダは本人のパソコン上のクローン（例：`D:\Projects\uranai366`）。クラウドのセッションは基本使わない（枠がないため）
- ローカルでは外部サイトの取得もできる。ただし「サイト（WordPress）は変更しない」は同じ
- Obsidian（`D:\Obsidian\Obsidian\...`）は同じパソコンにあるので直接読み書きできる。成果物を戻すときは `work/` を `D:\Obsidian\Obsidian\30_Areas\副業\10_Webメディア\12_占いサイト\記事\2027誕生日占い\work\` にコピー（Obsidian 側の他のファイルは消さない）
- このリポジトリは**公開**。公開前の原稿・パスワード・サーバーのパスや接続情報・個人情報をコミットしない

### ローカルでの準備（初回だけ。「ローカルでの準備をやって」と言われたらこれ）
1. `python --version`（3.11以上）・`node --version`（20以上）・`git --version` を確認。足りなければ本人に入れてもらう（README の手順）
2. Python の仮想環境：`python -m venv .venv` → `.venv\Scripts\python -m pip install -U pip setuptools wheel` → `.venv\Scripts\python -m pip install -r work\scripts\requirements.txt`（pyswisseph のビルドに失敗したら、エラー内容を本人に伝えて「Microsoft C++ Build Tools」を入れてもらう）
3. Node の部品：リポジトリ直下で `npm install` → `npx playwright install chromium`（画面確認用。`node_modules/` は git に入れない）
4. 文字コード：Windows では Python の既定が UTF-8 ではないので、Python は **`.venv\Scripts\python -X utf8 ...`** で動かす（または環境変数 `PYTHONUTF8=1`）
5. 動作確認：`.venv\Scripts\python -X utf8 work\scripts\check_pages.py` などが通ること。結果を本人に一言で報告

### コマンドの読み替え（作業指示書・進捗メモはクラウド時代の書き方が残っている）
| 書いてあるもの | ローカル（Windows）では |
|---|---|
| `python3 work/scripts/xxx.py`／`.venv/bin/python ...` | `.venv\Scripts\python -X utf8 work\scripts\xxx.py` |
| `NODE_PATH=/opt/node22/... PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node work/scripts/xxx.js` | `node work\scripts\xxx.js`（`npm install` 済みなら環境変数は不要） |
| `/tmp/...` | `%TEMP%\...`（または `work\tmp\`。`work/tmp/` は git に入れない） |
- 担当（サブエージェント）を同時にたくさん動かすと利用上限に当たる。同時は6人までが目安

## 必ず守ること
- 🛑 の確認ポイント（作業指示書に4か所）では必ず止まり、本人の返事を待つ
- 占いの値（天体・節気・干支・旧暦・宿・九星）は**計算で出す**。記憶や推測で書かない。計算できないものは出典を1つ決めて記録
- **別の日で同じようなことを書かない**：366日を表で一括作成 → 日ごとの材料を必ず使う → 重複を機械で検査（基準は作業指示書フェーズ8）
- 現行ページの文章・相性・ラッキー情報はコピーしない（有名人だけは `source/famous/` を使う）
- サイト（WordPress）は変更しない。投入用ファイルと手順書を作るまで
- 六星占術は使わない。「動物占い」という名前は使わない（自前の「動物×色占い」）
- 成果物はすべて `work/` に。フェーズや星座が1つ終わるたびに `work/00_進捗.md` を更新してコミット・push
- 本人への報告は日本語で、専門用語を避けて短く

## 自分で決めて進めてよいこと（止まらない）
本人は「Claude Code だけで進められる」ことを望んでいる。🛑 以外では止まらず、次のルールで自分で決めて進める。
- **出典が開けない・見つからない** → 代わりの信頼できる出典を探す。無ければ「このサイト独自の決め方」を作り、決め方をページの注記と `work/reports/` に書いて進める
- **計算方式や流派が複数ある** → 日本で一般的なものを選び、`work/knowledge/` に「なぜそれを選んだか」を書いて進める
- **本人にしかできないこと**（ファイルの提供、アフィリエイトのリンクなど） → `work/00_進捗.md` の「お願いリスト」に追記し、**作業は止めずに**それを使わない部分を先に進める。お願いリストは次の🛑でまとめて聞く
- 🛑で聞くのは「方向を決める判断」だけ。細かい確認は、決めた内容を報告するだけでよい（本人は後から直せる）
- 本人への報告は、結果 → 決めたこと → お願い（あれば）の順で短く
