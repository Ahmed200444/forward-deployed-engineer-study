// v31 acceptance: sidebar Projects/Review split (same destinations as v30), file notice hidden when served.
// node v31.js [path/to/v30/index.html]  (the v30 file is optional; with it, every route id is compared)
const { chromium } = require('playwright');
const fs = require('fs');
const B = 'https://localhost:8820/';
const OLD = process.argv[2];
const out = []; const ok = (n, c, i) => out.push((c ? 'PASS ' : 'FAIL ') + n + (i !== undefined && !c ? ' — ' + String(i).slice(0, 400) : ''));
const sidebar = () => {
  // group headings and the links under each, in page order
  const res = []; let cur = null;
  for (const el of document.querySelectorAll('.np-body p.nav-label, .np-body a[href^="#/"]')) {
    if (el.matches('p.nav-label')) { cur = { h: el.textContent.trim(), links: [] }; res.push(cur); }
    else if (el.matches('a[href^="#/"]') && cur) cur.links.push([el.textContent.replace(/\s+/g, ' ').trim(), el.getAttribute('href')]);
  }
  return res;
};
(async () => {
  const b = await chromium.launch();
  const c = await b.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1440, height: 900 } });
  if (OLD) await c.route('**/__v30.html', r => r.fulfill({ status: 200, contentType: 'text/html', body: fs.readFileSync(OLD) }));
  const p = await c.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e)));
  await p.goto(B + '#/ph0'); await p.waitForTimeout(800);
  ok('served over https: file notice hidden', !(await p.isVisible('.file-notice')));
  const sb = await p.evaluate(sidebar);
  const heads = sb.map(g => g.h);
  ok('no "Practice" group left in the sidebar', !heads.some(h => /^Practice$/i.test(h)), heads.join(' | '));
  const proj = sb.find(g => /^Projects$/i.test(g.h) && g.links.length);
  const rev = sb.find(g => /^Review$/i.test(g.h) && g.links.length);
  ok('Phase 0 has a Projects group', !!proj, heads.join(' | '));
  ok('Phase 0 has a Review group', !!rev, heads.join(' | '));
  if (proj) {
    ok('Projects shows "Text-tools analyzer" without the "Project:" prefix', proj.links.some(l => /Text-tools analyzer/.test(l[0])) && !proj.links.some(l => /Project:/.test(l[0])), JSON.stringify(proj.links));
    ok('Projects holds only projects', proj.links.every(l => !/Interview prep|checkpoint/i.test(l[0])), JSON.stringify(proj.links));
  }
  if (rev) ok('Review holds Interview prep and the Phase 0 checkpoint', rev.links.some(l => /Interview prep/.test(l[0])) && rev.links.some(l => /Phase 0 checkpoint/.test(l[0])), JSON.stringify(rev.links));
  // the project link still opens the project page
  if (proj) {
    const href = proj.links.find(l => /Text-tools analyzer/.test(l[0]))[1];
    await p.click('a[href="' + href + '"] >> nth=0'); await p.waitForTimeout(500);
    ok('Text-tools analyzer link opens the project (' + href + ')', /text-tools|Text tools|analyzer/i.test(await p.innerText('#view')));
  }
  // every phase: the same route ids as v30, in Projects/Review instead of Practice
  if (OLD) {
    const q = await c.newPage(); await q.goto(B + '__v30.html#/ph0'); await q.waitForTimeout(800);
    const old = await q.evaluate(() => [...document.querySelectorAll('a[href^="#/"]')].map(a => a.getAttribute('href')));
    const now = await p.evaluate(() => [...document.querySelectorAll('a[href^="#/"]')].map(a => a.getAttribute('href')));
    const so = new Set(old), sn = new Set(now);
    const lost = [...so].filter(h => !sn.has(h)), added = [...sn].filter(h => !so.has(h));
    ok('Phase 0 page: every v30 link destination still present (' + so.size + ')', lost.length === 0, 'lost ' + lost.join(' '));
    ok('Phase 0 page: no new destinations', added.length === 0, 'added ' + added.join(' '));
    for (let ph = 0; ph <= 10; ph++) {
      await q.goto(B + '__v30.html#/ph' + ph); await p.goto(B + '#/ph' + ph); await q.waitForTimeout(300); await p.waitForTimeout(300);
      const a = await q.evaluate(() => [...document.querySelectorAll('.np-body a[href^="#/"]')].map(x => x.getAttribute('href')).sort().join(','));
      const z = await p.evaluate(() => [...document.querySelectorAll('.np-body a[href^="#/"]')].map(x => x.getAttribute('href')).sort().join(','));
      ok('phase ' + ph + ' sidebar: same destinations as v30', a === z && a.length > 0, a.slice(0, 120) + ' vs ' + z.slice(0, 120));
    }
  }
  ok('no page errors', errs.length === 0, errs.join('; '));
  await b.close();
  console.log(out.join('\n')); console.log(out.filter(x => x.startsWith('FAIL')).length + ' failed of ' + out.length);
})();
