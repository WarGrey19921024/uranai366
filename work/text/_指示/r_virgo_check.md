占いサイト「人生予報」2027年版 誕生日占いの**乙女座の文章の仕上げ（検査と直し）**の担当です。リポジトリ /home/user/uranai366。

前の担当3人が、乙女座31日分（`work/text/virgo/0824.json`〜`0923.json`）を書き終えたあと、検査の途中で止まりました。

## 最初に読む
`work/text/_書き方.md`、`docs/04_本人の決定.md`（確認2・中間チェック・確認3）、`work/text/_指示/w_virgo_1.md`（書いたときの指示。特に「短い事実だけの文を単独で置かない」）。

## やること
1. `cd /home/user/uranai366/work/scripts && /tmp/claude-0/venv/bin/python merge_text.py && /tmp/claude-0/venv/bin/python check_dup.py virgo` を実行し、`work/reports/dup_check_virgo.md` の表がすべて ✅ になるまで、乙女座の日のファイルを直す。
2. 全体の検査 `/tmp/claude-0/venv/bin/python check_dup.py`（引数なし）も実行し（全体の検査は数分かかるので、Bash の timeout を 600000 にする）、`work/reports/dup_check.md` の「同じ文（4ページ以上）」「セクションの類似度0.40以上」に**乙女座の日**が入っていれば、乙女座の側を書き換える（ほかの星座のファイルは変えない）。
3. 直し方：その文を、その日の材料（`work/data/materials_366.json`）を使った別の言い方にする。月の名前・字数の目安・度数を出さない、などの決まりは崩さない。

## ルール
- 乙女座以外のファイルは変更しない。JSONは元の字下げのまま、UTF-8・ensure_ascii なし。
- git commit はしない。最後に、直したページ数と検査の結果（乙女座の表がすべて✅か、全体の一覧に乙女座の日が残っていないか）を4行以内で報告。
