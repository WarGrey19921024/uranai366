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
      // アフィリエイトの表示計測の画像（もしも・A8）は確認用の環境では読めない（file:// では //i.moshimo.com が開けず、外へもつながらない）ので数えない
      const adPixel = u => /^(https?|file):\/\/([^/]*\.)?(moshimo\.com|a8\.net)\//.test(u || '');
      page.on('console', m => { if (m.type() === 'error' && !(m.text().startsWith('Failed to load resource') && adPixel(m.location().url))) errors.push('console: ' + m.text()); });
      page.on('requestfailed', r => { if (!r.url().startsWith('https://fonts.') && !adPixel(r.url())) errors.push('requestfailed: ' + r.url()); });
      await page.goto('file://' + path.join(SAMPLE, mmdd + '.html'), { waitUntil: 'load' });
      await page.waitForTimeout(300);
      const before = await page.evaluate(() => ({
        overflow: document.documentElement.scrollWidth - window.innerWidth,
        chart: !!document.querySelector('#fh-b27-chart svg'),
        calDays: document.querySelectorAll('#fh-b27-cal .fh-b27-cday').length,
        dayout: (document.getElementById('fh-b27-dayout') || {}).textContent || '',
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
      // カレンダーの日付を押す → その日のひとこと／グラフ表示に切り替え
      await page.click('#fh-b27-cal .fh-b27-cday[data-d="15"]');
      await page.waitForTimeout(100);
      const day = await page.evaluate(() => document.getElementById('fh-b27-dayout').textContent);
      // 改善第2弾：カレンダーの印と「その日のひとこと」の5段階が同じか（その月の全部の日を押して確かめる）
      const mismatch = await page.evaluate(async () => {
        let bad = 0; const n = document.querySelectorAll('#fh-b27-cal .fh-b27-cday').length;
        for (let d = 1; d <= n; d++) { const c = document.querySelector('#fh-b27-cal .fh-b27-cday[data-d="' + d + '"]'); const mk = c.querySelector('.fh-b27-cmk').textContent;
          c.click(); const v = document.querySelector('#fh-b27-dayout .fh-b27-verd').textContent.charAt(0); if (v !== mk) bad++; }
        return bad; });
      await page.click('[data-fh-view="graph"]');
      await page.waitForTimeout(100);
      const graph = await page.evaluate(() => !!document.querySelector('#fh-b27-bchart svg') && !document.getElementById('fh-b27-bchart').hidden);
      await page.click('[data-fh-view="cal"]');
      // 2029年生まれ（赤ちゃん）：生まれる前の2027年はバイオリズムを出さない
      const baby = mmdd === '0229' ? '2028' : '2029';
      await page.selectOption('#fh-b27-y', baby);
      await page.waitForTimeout(150);
      const babyRes = await page.evaluate(() => ({ star: document.getElementById('fh-b27-star').textContent,
        before: document.querySelectorAll('#fh-b27-btable td[colspan]').length, overflow: document.documentElement.scrollWidth - window.innerWidth }));
      const okDay = /日の数 \d/.test(day) && /日の干支/.test(day) && /バイオリズム/.test(day) && /おみくじ/.test(day);
      const ok = !errors.length && before.overflow <= 0 && after.overflow <= 0 && before.chart && after.legend === before.legend + 2 && after.bioRows >= 28
        && before.calDays >= 28 && /日の数/.test(before.dayout) && okDay && graph && mismatch === 0 && babyRes.star !== '—' && babyRes.before >= 28 && babyRes.overflow <= 0;
      Object.assign(after, { day: day.slice(0, 80), graph, baby, babyRes, mismatch });
      if (!ok) bad++;
      console.log(JSON.stringify({ mmdd, name, ok, errors, before, after }, null, 0));
      await page.close();
    }
  }
  await browser.close();
  process.exit(bad ? 1 : 0);
})();
