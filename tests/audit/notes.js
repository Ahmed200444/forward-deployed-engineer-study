// Audit helper: dump, for every inline question and exercise, the "New here" note and hint text the learner sees.
const { chromium } = require('playwright');
const B = process.env.B || 'https://localhost:8820/';
(async () => {
  const b = await chromium.launch(); const c = await b.newContext({ ignoreHTTPSErrors: true }); const p = await c.newPage();
  await p.goto(B + '#/projects'); await p.waitForTimeout(600);
  const ids = await p.evaluate(() => ({ l: [...document.querySelectorAll('.lesson-src')].map(x => x.dataset.id), e: [...document.querySelectorAll('.ex-src')].map(x => x.dataset.id) }));
  for (const id of ids.l) {
    await p.goto(B + '#/lesson/' + id); await p.waitForTimeout(250);
    const qs = await p.evaluate(() => [...document.querySelectorAll('.pq')].map(q => ({ title: (q.querySelector('.pq-h') || {}).textContent, before: ((q.querySelector('.pq-before') || {}).innerText || ''), hint: ((q.querySelector('.pq-hint') || {}).innerText || '') })));
    console.log(JSON.stringify({ kind: 'lesson', id, qs }));
  }
  for (const id of ids.e) {
    await p.goto(B + '#/ex/' + id); await p.waitForTimeout(200);
    const r = await p.evaluate(() => { const v = document.querySelector('#view'); const nb = [...v.querySelectorAll('.pq-before,.newhere,.new-here')].map(x => x.innerText).join('\n'); const t = v.innerText; const i = t.indexOf('New here'); return { before: nb || (i >= 0 ? t.slice(i, i + 900) : ''), label: (t.match(/EXERCISE E\d+/i) || [''])[0] }; });
    console.log(JSON.stringify({ kind: 'ex', id, ...r }));
  }
  await b.close();
})();
