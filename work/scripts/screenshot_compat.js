// 確認用：誕生日相性診断（work/out/sample/compatibility.html）を、1990年1月25日 × 1992年7月7日 を入れた状態で
// スマホ幅（390px）とPC幅（1280px）で撮り、JSエラー・横はみ出しを調べる。
// 使い方: NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node work/scripts/screenshot_compat.js
const path = require('path');
const { chromium } = require('playwright');
const SAMPLE = path.join(__dirname, '..', 'out', 'sample');
(async () => {
  const browser = await chromium.launch();
  let bad = 0;
  for (const [name, vp] of [['sp', { width: 390, height: 844 }], ['pc', { width: 1280, height: 900 }]]) {
    const page = await browser.newPage({ viewport: vp, deviceScaleFactor: 1 });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto('file://' + path.join(SAMPLE, 'compatibility.html'), { waitUntil: 'load' });
    for (const [id, v] of [['am', '1'], ['ad', '25'], ['ay', '1990'], ['bm', '7'], ['bd', '7'], ['by', '1992']]) await page.selectOption('#fh-b27-cp-' + id, v);
    await page.click('#fh-b27-cp-go');
    await page.waitForTimeout(300);
    const r = await page.evaluate(() => ({ overflow: document.documentElement.scrollWidth - window.innerWidth,
      type: (document.getElementById('fh-b27-cp-type') || {}).textContent, a: (document.getElementById('fh-b27-cp-da') || {}).getAttribute && document.getElementById('fh-b27-cp-da').getAttribute('href'),
      b: document.getElementById('fh-b27-cp-db') && document.getElementById('fh-b27-cp-db').getAttribute('href') }));
    await page.screenshot({ path: path.join(SAMPLE, `compatibility_${name}.png`), fullPage: true });
    const ok = !errors.length && r.overflow <= 0 && r.a === '/366uranai/01-25/' && r.b === '/366uranai/07-07/';
    if (!ok) bad++;
    console.log(JSON.stringify({ name, ok, errors, r }));
    await page.close();
  }
  await browser.close();
  process.exit(bad ? 1 : 0);
})();
