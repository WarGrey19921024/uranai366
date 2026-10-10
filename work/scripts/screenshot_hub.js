// 確認用：一覧ページ（work/out/sample/hub.html）と生年月日まるごと診断（work/out/sample/seinengappi.html）を
// スマホ幅（390px）とPC幅（1280px）で撮り、JSエラー・横はみ出しを調べる。まるごと診断は 1990年1月1日を入れた状態で撮る。
// 使い方: NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node work/scripts/screenshot_hub.js [出力JSON]
// 出力JSON（省略時は書かない）：まるごと診断に何件かの生年月日を入れたときのカードの表示。test_seinengappi.py が Python の計算と突き合わせる。
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const SAMPLE = path.join(__dirname, '..', 'out', 'sample');
const DATES = [[1990, 1, 1], [1988, 2, 29], [1930, 1, 1], [2030, 12, 31], [1964, 10, 10], [2000, 2, 4], [2025, 2, 3], [1975, 7, 23], [2012, 12, 21], [1945, 8, 15]];

async function open(browser, file, vp, errors) {
  const page = await browser.newPage({ viewport: vp, deviceScaleFactor: 1, acceptDownloads: true });
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  page.on('requestfailed', r => { if (!r.url().startsWith('https://fonts.')) errors.push('requestfailed: ' + r.url()); });
  await page.goto('file://' + path.join(SAMPLE, file), { waitUntil: 'load' });
  await page.waitForTimeout(300);
  return page;
}
const overflow = page => page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);

async function pick(page, [y, m, d]) {
  await page.selectOption('#fh-b27-sg-y', String(y));
  await page.selectOption('#fh-b27-sg-m', String(m));
  await page.selectOption('#fh-b27-sg-d', String(d));
  await page.click('#fh-b27-sg-go');
  await page.waitForTimeout(150);
  return page.evaluate(() => {
    const t = id => (document.getElementById('fh-b27-sg-' + id) || {}).textContent;
    const o = {};
    for (const k of ['date', 'sub', 'c-sign', 'c-star', 'c-eto', 'c-pillars', 'c-nikkan', 'c-shuku', 'c-kin', 'c-seal', 'c-lp', 'c-animal',
      'sign-n', 'star-n', 'eto-n', 'pillars-n', 'shuku-n', 'kin-n', 'lp-n']) o[k] = t(k);
    o.dayHref = document.getElementById('fh-b27-sg-day').getAttribute('href');
    o.signHref = document.getElementById('fh-b27-sg-sign-a').getAttribute('href');
    o.hidden = document.getElementById('fh-b27-sg-out').hidden;
    return o;
  });
}

(async () => {
  const browser = await chromium.launch();
  let bad = 0;
  const results = [];
  for (const [name, vp] of [['sp', { width: 390, height: 844 }], ['pc', { width: 1280, height: 900 }]]) {
    // 一覧ページ
    let errors = [];
    let page = await open(browser, 'hub.html', vp, errors);
    const hub = await page.evaluate(() => ({
      dayLinks: document.querySelectorAll('.fh-b27-days a[href^="/366uranai/"]').length,
      borderDays: document.querySelectorAll('.fh-b27-days a.fh-b27-bd').length,
      h1: document.querySelectorAll('.fh-b27 h1').length,
    }));
    hub.overflow = await overflow(page);
    await page.screenshot({ path: path.join(SAMPLE, `hub_${name}.png`), fullPage: true });
    let ok = !errors.length && hub.overflow <= 0 && hub.dayLinks === 366 && hub.h1 === 1;
    if (!ok) bad++;
    console.log(JSON.stringify({ page: 'hub', name, ok, errors, hub }));
    await page.close();

    // まるごと診断
    errors = [];
    page = await open(browser, 'seinengappi.html', vp, errors);
    const before = { overflow: await overflow(page), hidden: await page.evaluate(() => document.getElementById('fh-b27-sg-out').hidden),
      years: await page.evaluate(() => [...document.querySelectorAll('#fh-b27-sg-y option')].filter(o => o.value).map(o => +o.value)) };
    const yr = [Math.min(...before.years), Math.max(...before.years), before.years.length];
    // 2月の日数（うるう年・平年）
    await page.selectOption('#fh-b27-sg-y', '1989'); await page.selectOption('#fh-b27-sg-m', '2');
    const feb1989 = await page.evaluate(() => document.querySelectorAll('#fh-b27-sg-d option[value]:not([value=""])').length);
    await page.selectOption('#fh-b27-sg-y', '1988');
    const feb1988 = await page.evaluate(() => document.querySelectorAll('#fh-b27-sg-d option[value]:not([value=""])').length);
    if (name === 'sp') for (const dte of DATES) results.push({ date: dte, shown: await pick(page, dte) });
    const r1990 = await pick(page, [1990, 1, 1]);
    // 画像で保存（PNG がダウンロードされるか）
    const [dl] = await Promise.all([page.waitForEvent('download', { timeout: 10000 }), page.click('[data-fh-action="save-sg"]')]);
    const dlName = dl.suggestedFilename();
    const dlPath = path.join(require('os').tmpdir(), dlName); await dl.saveAs(dlPath);
    const dlSize = fs.statSync(dlPath).size;
    if (name === 'sp') fs.copyFileSync(dlPath, path.join(SAMPLE, 'seinengappi_card1990.png'));
    await page.evaluate(() => window.scrollTo(0, 0));
    const after = { overflow: await overflow(page), h1: await page.evaluate(() => document.querySelectorAll('.fh-b27 h1').length) };
    await page.screenshot({ path: path.join(SAMPLE, `seinengappi_${name}.png`), fullPage: true });
    ok = !errors.length && before.overflow <= 0 && after.overflow <= 0 && before.hidden && !r1990.hidden && after.h1 === 0 &&
      yr[0] === 1930 && yr[1] === 2030 && yr[2] === 101 && feb1989 === 28 && feb1988 === 29 && dlName === 'seinengappi-19900101.png' && dlSize > 20000;
    if (!ok) bad++;
    console.log(JSON.stringify({ page: 'seinengappi', name, ok, errors, before: { overflow: before.overflow, hidden: before.hidden, years: yr, feb1989, feb1988 }, after, download: [dlName, dlSize], r1990 }));
    await page.close();
  }
  await browser.close();
  if (process.argv[2]) fs.writeFileSync(process.argv[2], JSON.stringify(results));
  process.exit(bad ? 1 : 0);
})();
