占いサイト「人生予報」2027年版 誕生日占いの**獅子座の文章の仕上げ（検査と直し）**の担当です。リポジトリ /home/user/uranai366。

前の担当3人が、獅子座32日分（`work/text/leo/0723.json`〜`0823.json`）を書き終えたあと、検査の途中で止まりました。

## 最初に読む
`work/text/_書き方.md`、`docs/04_本人の決定.md`（確認2・中間チェック・確認3）、`work/text/_指示/w_leo_1.md`（書いたときの指示。特に「短い事実だけの文を単独で置かない」）。

## やること
1. `cd /home/user/uranai366/work/scripts && /tmp/claude-0/venv/bin/python merge_text.py && /tmp/claude-0/venv/bin/python check_dup.py leo` を実行し、`work/reports/dup_check_leo.md` の表がすべて ✅ になるまで、獅子座の日のファイルを直す。
2. 全体の検査 `/tmp/claude-0/venv/bin/python check_dup.py`（引数なし）も実行し、`work/reports/dup_check.md` の「同じ文（4ページ以上）」「セクションの類似度0.40以上」に**獅子座の日**が入っていれば、獅子座の側を書き換える（ほかの星座のファイルは変えない）。
3. 直し方：その文を、その日の材料（`work/data/materials_366.json`）を使った別の言い方にする。月の名前・字数の目安・度数を出さない、などの決まりは崩さない。

## ルール
- 獅子座以外のファイルは変更しない。JSONは元の字下げのまま、UTF-8・ensure_ascii なし。
- git commit はしない。最後に、直したページ数と検査の結果（獅子座の表がすべて✅か、全体の一覧に獅子座の日が残っていないか）を4行以内で報告。
