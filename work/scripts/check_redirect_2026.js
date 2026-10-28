// 2027-01-01 の転送確認（人生予報のページを開いたタブで実行。結果は window._rc に入る）
// /2026-MMDD/ が /366uranai/MM-DD/ に転送され、200 で開けるかを366本すべて確かめる。1.2秒間隔（サーバーに負担をかけない）。
(async () => {
  const R = (window._rc = { done: 0, ok: 0, bad: [], state: 'run' });
  const days = [];
  for (let i = 0; i < 366; i++) {
    const d = new Date(2024, 0, 1 + i);
    days.push([String(d.getMonth() + 1).padStart(2, '0'), String(d.getDate()).padStart(2, '0')]);
  }
  const extra = [['/366uranai/2026y/', '/366uranai/'], ['/2026-0101/feed/', '/366uranai/01-01/']];
  const list = days.map(([m, d]) => [`/2026-${m}${d}/`, `/366uranai/${m}-${d}/`]).concat(extra);
  for (const [from, to] of list) {
    try {
      const r = await fetch(from + '?rc=' + Date.now(), { cache: 'no-store' });
      const fin = new URL(r.url).pathname;
      if (r.status === 200 && r.redirected && fin === to) R.ok++;
      else R.bad.push(`${from} -> ${fin} (${r.status}${r.redirected ? '' : ' 転送なし'})`);
    } catch (e) {
      R.bad.push(`${from} エラー`);
    }
    R.done++;
    await new Promise((z) => setTimeout(z, 1200));
  }
  R.state = 'done';
  console.log('転送確認', R.ok, '/', list.length, R.bad);
})();
