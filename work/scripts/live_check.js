// 本番の点検（改善ループの事前・事後に使う）。人生予報のページを開いたタブで実行する。
// 1) window.FHCHK.pages(urls)  … 各URLを取得して：200か・h1が1つか・禁止語（動物占い/六星占術）・題名・説明文・画像切れ候補・同じサイト内リンクの数
//    結果は window._lc に入る（長いので非同期。state が 'done' になるまで待つ）
// 2) window.FHCHK.view()       … いま表示しているページの見え方：淡い背景に白っぽい文字／濃い背景に黒っぽい文字（コントラスト3未満）と横はみ出し
// 3) window.FHCHK.links(url)   … そのページの同じサイト内リンクがすべて200か（0.5秒間隔）。結果は window._ll
(() => {
  const sleep = (ms) => new Promise((z) => setTimeout(z, ms));
  const BAN = [/動物占い/, /六星占術/];
  async function pages(urls) {
    const R = (window._lc = { state: 'run', rows: [], bad: [] });
    for (const u of urls) {
      try {
        const r = await fetch(u + (u.includes('?') ? '&' : '?') + 'lc=' + Date.now(), { cache: 'no-store' });
        const t = await r.text();
        const d = new DOMParser().parseFromString(t, 'text/html');
        const main = d.querySelector('article, main, #main') || d.body;
        const row = {
          u, s: r.status, h1: d.querySelectorAll('h1').length,
          title: (d.title || '').slice(0, 60),
          desc: (d.querySelector('meta[name=description]') || {}).content ? 1 : 0,
          ban: BAN.filter((b) => b.test(main.textContent)).map(String),
          rawWp: /<!-- \/?wp:/.test(t) ? 1 : 0, // 本文に wp のコメントが漏れていないか
          len: main.textContent.replace(/\s+/g, '').length,
        };
        R.rows.push(row);
        if (row.s !== 200 || row.h1 !== 1 || !row.desc || row.ban.length || row.rawWp) R.bad.push(row);
      } catch (e) { R.bad.push({ u, err: String(e) }); }
      await sleep(600);
    }
    R.state = 'done';
    return R;
  }
  function view() {
    const parse = (c) => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const v = m[1].split(',').map(Number); return { r: v[0], g: v[1], b: v[2], a: v.length > 3 ? v[3] : 1 }; };
    const lum = (c) => { const f = (x) => { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
    const bg = (e) => { while (e) { const s = getComputedStyle(e); if (s.backgroundImage && s.backgroundImage !== 'none') return 'img'; const c = parse(s.backgroundColor); if (c && c.a > 0.5) return c; e = e.parentElement; } return { r: 255, g: 255, b: 255, a: 1 }; };
    const bad = []; const seen = new Set();
    document.querySelectorAll('body *').forEach((e) => {
      const t = [...e.childNodes].filter((x) => x.nodeType === 3).map((x) => x.textContent.trim()).join('');
      if (!t) return; const s = getComputedStyle(e);
      if (s.display === 'none' || s.visibility === 'hidden' || +s.opacity === 0) return;
      if (!e.getBoundingClientRect().width) return;
      const fg = parse(s.color); const B = bg(e); if (B === 'img' || !fg) return;
      const L1 = lum(fg), L2 = lum(B); const cr = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
      if (cr < 3) { const k = s.color + JSON.stringify(B); if (!seen.has(k)) { seen.add(k); bad.push(cr.toFixed(2) + ' ' + s.color + ' on rgb(' + B.r + ',' + B.g + ',' + B.b + ') "' + t.slice(0, 20) + '" ' + e.tagName + '.' + String(e.className).slice(0, 40)); } }
    });
    return { lowContrast: bad.slice(0, 20), overflow: document.documentElement.scrollWidth - innerWidth, h1: document.querySelectorAll('h1').length };
  }
  async function links(url) {
    const R = (window._ll = { state: 'run', n: 0, bad: [] });
    url = new URL(url, location.href).href; // 相対URLでも動くように（2026-10-29 修正）
    const t = await (await fetch(url, { cache: 'no-store' })).text();
    const d = new DOMParser().parseFromString(t, 'text/html');
    const set = new Set();
    d.querySelectorAll('a[href]').forEach((a) => { try { const x = new URL(a.getAttribute('href'), url); if (x.host === location.host && !x.pathname.startsWith('/wp-')) set.add(x.origin + x.pathname); } catch (e) {} });
    for (const u of set) { try { const r = await fetch(u, { cache: 'no-store' }); if (r.status !== 200) R.bad.push(u + ' ' + r.status); } catch (e) { R.bad.push(u + ' err'); } R.n++; await sleep(500); }
    R.state = 'done';
    return R;
  }
  window.FHCHK = { pages, view, links };
  return 'FHCHK ready';
})();
