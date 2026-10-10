"""フェーズ4-2 検査：scores_366.json → work/reports/score_check.md と グラフ画像 work/reports/img/score_*.png"""
import json, os, statistics as st, collections
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
REP = os.path.join(HERE, "..", "reports")
IMG = os.path.join(REP, "img")
os.makedirs(IMG, exist_ok=True)
for f in ["/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"]:
    if os.path.exists(f):
        font_manager.fontManager.addfont(f)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=f).get_name()
C = {"bg": "#fcfcfb", "ink": "#0b0b0b", "ink2": "#52514e", "s1": "#2a78d6", "s2": "#eb6834", "s3": "#1baf7a", "s4": "#eda100"}
plt.rcParams.update({"axes.facecolor": C["bg"], "figure.facecolor": C["bg"], "axes.edgecolor": C["ink2"],
                     "axes.labelcolor": C["ink"], "xtick.color": C["ink2"], "ytick.color": C["ink2"],
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e6e5e0"})

S = json.load(open(os.path.join(HERE, "..", "data", "scores_366.json"), encoding="utf-8"))
B = json.load(open(os.path.join(HERE, "..", "data", "base_366.json"), encoding="utf-8"))
meta = S.pop("_meta")
keys = list(B)
md = lambda k: f"{int(k[:2])}/{int(k[2:])}"
L, ng = [], collections.defaultdict(list)

alltot = [t for k in keys for t in S[k]["total"]]
pagemean = {k: st.mean(S[k]["total"]) for k in keys}
L.append(f"""# フェーズ4 検査：月別スコア（scores_366.json）

`python work/scripts/build_scores.py && python work/scripts/check_scores.py` で再生成。計算規則は `work/knowledge/12_スコアと相性の規則.md`。**数字は手で直していない。**

## 全体
| 項目 | 星座 | 数秘 | 暦の五行 | 総合 |
|---|---|---|---|---|""")
for lab, f in [("平均", st.mean), ("ばらつき（標準偏差）", st.pstdev), ("最小", min), ("最大", max)]:
    row = [f([v for k in keys for v in S[k][x]]) for x in ("astro", "num", "gogyo", "total")]
    L.append(f"| {lab} | " + " | ".join(f"{x:.1f}" for x in row) + " |")
L.append(f"\n- ◎の境目：総合 {meta['q_top']} 以上（全体の上位25%）／△の境目：{meta['q_bottom']} 未満（下位25%）")
L.append(f"- 星座スコアの基準 S＝{meta['S']:.3f}（366日×12か月の値の大きさの99パーセンタイル）")
L.append(f"- 2027年の月柱：" + "・".join(f"{m}月{v}" for m, v in meta["month_kanshi"].items()))

# 星座別
L.append("\n## 星座別の平均（総合）\n\n| 星座 | 日数 | 総合の平均 | ページ平均の最小〜最大 | ◎の月の数（平均） | △の月の数（平均） |\n|---|---|---|---|---|---|")
bysign = collections.OrderedDict()
for k in keys:
    bysign.setdefault(B[k]["sign"], []).append(k)
for s, ks in bysign.items():
    L.append(f"| {s} | {len(ks)} | {st.mean(pagemean[k] for k in ks):.1f} | {min(pagemean[k] for k in ks):.1f}〜{max(pagemean[k] for k in ks):.1f} | "
             f"{st.mean(S[k]['marks'].count('◎') for k in ks):.1f} | {st.mean(S[k]['marks'].count('△') for k in ks):.1f} |")

# チェック
forced = 0
for k in keys:
    v = S[k]
    if v["marks"].count("◎") < 2: ng["◎が2つ未満"].append(k)
    if v["marks"].count("△") < 1: ng["△が無い"].append(k)
    if set(v["marks"]) == {"◎"} or set(v["marks"]) == {"△"} or "△" not in v["marks"] or "◎" not in v["marks"]:
        ng["全部良い／全部悪い"].append(k)
    hi = [t for t in v["total"] if t >= meta["q_top"]]
    lo = [t for t in v["total"] if t < meta["q_bottom"]]
    if len(hi) < 2 or len(lo) < 1: forced += 1
for a, b in zip(keys, keys[1:] + keys[:1]):
    if S[a]["total"] == S[b]["total"]: ng["隣の日と12か月の推移が同じ"].append(f"{a}-{b}")
    if S[a]["marks"] == S[b]["marks"]: ng["(参考)隣の日と◎○△の並びが同じ"].append(f"{a}-{b}")
low40 = sum(1 for t in alltot if t < 40)
L.append(f"""
## チェックリスト
| 検査 | 結果 |
|---|---|
| 1ページに◎が2つ以上 | {'✅ 全ページ' if not ng['◎が2つ未満'] else '⚠ ' + str(len(ng['◎が2つ未満'])) + 'ページ'} |
| 1ページに△が1つ以上 | {'✅ 全ページ' if not ng['△が無い'] else '⚠ ' + str(len(ng['△が無い'])) + 'ページ'} |
| 全部良い・全部悪いページがない | {'✅ なし' if not ng['全部良い／全部悪い'] else '⚠ ' + str(len(ng['全部良い／全部悪い']))} |
| 隣り合う日の12か月の推移が完全に同じ | {'✅ なし' if not ng['隣の日と12か月の推移が同じ'] else '⚠ ' + ' '.join(ng['隣の日と12か月の推移が同じ'][:10])} |
| （参考）隣り合う日で◎○△の並びまで同じ | {len(ng['(参考)隣の日と◎○△の並びが同じ'])} 組 |
| 総合が40を下回る月 | {low40} か所（全{len(alltot)}か月中）。すべて計算どおり（手で作っていない） |
| 全体の基準だけでは◎2つ・△1つに届かず、「その人の上位2か月を◎・最下位を△」の規則で補ったページ | {forced} ページ |
""")

# 山・谷の月の分布
pk = collections.Counter(S[k]["peak_months"][0] for k in keys)
lw = collections.Counter(S[k]["low_months"][0] for k in keys)
L.append("## いちばん良い月・いちばん慎重な月の分布（ページ数）\n\n| 月 | " + " | ".join(f"{m}月" for m in range(1, 13)) + " |\n|---|" + "---|" * 12)
L.append("| 山の月 | " + " | ".join(str(pk[m]) for m in range(1, 13)) + " |")
L.append("| 谷の月 | " + " | ".join(str(lw[m]) for m in range(1, 13)) + " |")
fp = {f: collections.Counter(S[k]["field_peak"][f] for k in keys) for f in S[keys[0]]["fields"]}
L.append("\n## 分野別：山の月の分布（ページ数）\n\n| 分野 | " + " | ".join(f"{m}月" for m in range(1, 13)) + " |\n|---|" + "---|" * 12)
for f, c in fp.items():
    L.append(f"| {f} | " + " | ".join(str(c[m]) for m in range(1, 13)) + " |")

# グラフ1：総合の分布
fig, ax = plt.subplots(figsize=(8, 3.6))
ax.hist(alltot, bins=range(0, 101, 4), color=C["s1"], edgecolor=C["bg"], linewidth=2)
ax.axvline(meta["q_top"], color=C["ink2"], ls="--", lw=1); ax.axvline(meta["q_bottom"], color=C["ink2"], ls="--", lw=1)
ax.text(meta["q_top"] + 1, ax.get_ylim()[1] * .9, "◎の境目", color=C["ink2"]); ax.text(meta["q_bottom"] - 15, ax.get_ylim()[1] * .9, "△の境目", color=C["ink2"])
ax.set_title("総合スコアの分布（366日×12か月）", color=C["ink"], loc="left"); ax.set_xlabel("総合スコア"); ax.set_ylabel("か月の数")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "score_hist.png"), dpi=120); plt.close(fig)
# グラフ2：3本それぞれの分布
fig, axs = plt.subplots(1, 3, figsize=(10, 3), sharey=True)
for ax, (x, lab, c) in zip(axs, [("astro", "星座", C["s1"]), ("num", "数秘", C["s2"]), ("gogyo", "暦の五行", C["s3"])]):
    ax.hist([v for k in keys for v in S[k][x]], bins=range(0, 101, 5), color=c, edgecolor=C["bg"], linewidth=2)
    ax.set_title(lab, loc="left", color=C["ink"])
fig.suptitle("占いごとのスコアの分布", x=.02, ha="left"); fig.tight_layout(); fig.savefig(os.path.join(IMG, "score_parts.png"), dpi=120); plt.close(fig)
# グラフ3：日付ごとのページ平均（星座で色分けせず1本）
fig, ax = plt.subplots(figsize=(10, 3.2))
ax.plot(range(366), [pagemean[k] for k in keys], color=C["s1"], lw=2)
ticks = [i for i, k in enumerate(keys) if k.endswith("01")]
ax.set_xticks(ticks, [f"{int(keys[i][:2])}月" for i in ticks]); ax.set_ylim(30, 80)
ax.set_title("誕生日ごとの総合スコアの年平均", loc="left", color=C["ink"]); ax.set_ylabel("12か月の平均")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "score_by_day.png"), dpi=120); plt.close(fig)
# グラフ4：例 1/1・1/2・1/10 の総合の推移（隣の日でも違うことの確認）
fig, ax = plt.subplots(figsize=(8, 3.4))
for k, c in [("0101", C["s1"]), ("0102", C["s2"]), ("0110", C["s3"])]:
    ax.plot(range(1, 13), S[k]["total"], color=c, lw=2, marker="o", ms=5, label=md(k))
    ax.annotate(md(k), (12, S[k]["total"][-1]), xytext=(5, 0), textcoords="offset points", color=C["ink2"], va="center")
ax.set_xticks(range(1, 13), [f"{m}月" for m in range(1, 13)]); ax.set_ylim(20, 100); ax.legend(frameon=False, loc="upper left", ncol=3)
ax.set_title("例：1/1・1/2・1/10 の総合スコアの推移", loc="left", color=C["ink"])
fig.tight_layout(); fig.savefig(os.path.join(IMG, "score_examples.png"), dpi=120); plt.close(fig)

L.append("\n## グラフ\n\n![総合の分布](img/score_hist.png)\n\n![占いごとの分布](img/score_parts.png)\n\n![誕生日ごとの平均](img/score_by_day.png)\n\n![例](img/score_examples.png)\n")
open(os.path.join(REP, "score_check.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L)[:4000])
