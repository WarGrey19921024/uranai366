// 確認用：work/out/sample/MMDD.html をスマホ幅（390px）とPC幅（1280px）で撮り、JSエラー・横はみ出しを調べる。
// 使い方: NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node work/scripts/screenshot_sample.js 0101 [0229 ...]
// 生まれ年を選んだ状態（1990年、0229は1988年）でもう1枚撮り、生まれ年パネルとグラフが描けるかも確かめる。
const path = require('path');
const { chromium } = require('playwright');
const SAMPLE = path.join(__dirname, '..', 'out', 'sample');

(async () => {
  const days = process.argv.slice(2);
  if (!days.length) { console.error('MMDD を指定してください'); process.exit(2); }
  const browser = await chromium.launch();
  let bad = 0;
  for (const mmdd of days) {
    for (const [name, vp] of [['sp', { width: 390, height: 844 }], ['pc', { width: 1280, height: 900 }]]) {
      const page = await browser.newPage({ viewport: vp, deviceScaleFactor: 1 });
      const errors = [];
      page.on('pageerror', e => errors.push('pageerror: ' + e.message));
      page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
      page.on('requestfailed', r => { if (!r.url().startsWith('https://fonts.')) errors.push('requestfailed: ' + r.url()); });
      await page.goto('file://' + path.join(SAMPLE, mmdd + '.html'), { waitUntil: 'load' });
      await page.waitForTimeout(300);
      const before = await page.evaluate(() => ({
        overflow: document.documentElement.scrollWidth - window.innerWidth,
        chart: !!document.querySelector('#fh-b27-chart svg'),
        legend: document.querySelectorAll('#fh-b27-leg button').length,
      }));
      await page.screenshot({ path: path.join(SAMPLE, `${mmdd}_${name}.png`), fullPage: true });
      const year = mmdd === '0229' ? '1988' : '1990';
      await page.selectOption('#fh-b27-y', year);
      await page.waitForTimeout(200);
      const after = await page.evaluate(() => ({
        overflow: document.documentElement.scrollWidth - window.innerWidth,
        legend: document.querySelectorAll('#fh-b27-leg button').length,
        star: document.getElementById('fh-b27-star').textContent,
        pillars: document.getElementById('fh-b27-pillars').textContent,
        shuku: document.getElementById('fh-b27-shuku').textContent,
        kin: document.getElementById('fh-b27-kin').textContent + ' ' + document.getElementById('fh-b27-kin-n').textContent,
        lp: document.getElementById('fh-b27-lp').textContent,
        animal: document.getElementById('fh-b27-animal').textContent,
        bioRows: document.querySelectorAll('#fh-b27-btable tbody tr').length,
        bio: document.getElementById('fh-b27-bio').textContent.slice(0, 60),
      }));
      const panel = await page.$('#b27-year');
      await panel.screenshot({ path: path.join(SAMPLE, `${mmdd}_${name}_year${year}.png`) });
      const bio = await page.$('#b27-bio');
      await bio.screenshot({ path: path.join(SAMPLE, `${mmdd}_${name}_bio${year}.png`) });
      const ok = !errors.length && before.overflow <= 0 && after.overflow <= 0 && before.chart && after.legend === before.legend + 2 && after.bioRows >= 28;
      if (!ok) bad++;
      console.log(JSON.stringify({ mmdd, name, ok, errors, before, after }, null, 0));
      await page.close();
    }
  }
  await browser.close();
  process.exit(bad ? 1 : 0);
})();
