// Audit: open every lesson and report structure: headings, questions (hint / New-here note / level), figures that load,
// tables with column headers, recorded outputs, broken internal links, console errors.
const { chromium } = require('playwright');
const B = process.env.B || 'https://localhost:8820/';
(async () => {
  const b = await chromium.launch(); const c = await b.newContext({ ignoreHTTPSErrors: true }); const p = await c.newPage();
  const errs = []; p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
  await p.goto(B + '#/projects'); await p.waitForTimeout(600);
  const lessons = await p.evaluate(() => [...document.querySelectorAll('.lesson-src')].map(l => l.dataset.id));
  const routes = new Set(await p.evaluate(() => { const r = []; document.querySelectorAll('.lesson-src,.ex-src').forEach(x => r.push((x.classList.contains('ex-src') ? 'ex/' : 'lesson/') + x.dataset.id)); return r; }));
  for (const id of lessons) {
    errs.length = 0;
    await p.goto(B + '#/lesson/' + id); await p.waitForTimeout(350);
    const r = await p.evaluate(async () => {
      const v = document.querySelector('#view');
      const text = s => (s || '').replace(/\s+/g, ' ').trim();
      const qs = [...v.querySelectorAll('.pq')].map(q => ({
        id: q.id, level: (q.querySelector('.pq-level') || {}).textContent || '', hint: !!q.querySelector('.pq-hint'),
        newHere: !!q.querySelector('.pq-before'), problem: text((q.querySelector('.qbox-problem') || {}).textContent).length,
        hasEditor: !!q.querySelector('textarea[id^="pq-code-"]'), hasSolBtn: !!q.querySelector('[data-pq="sol"]')
      }));
      const figs = [...v.querySelectorAll('img')].map(i => ({ ok: i.complete && i.naturalWidth > 0, alt: !!i.alt && i.alt.length > 3 }));
      const tables = [...v.querySelectorAll('table')].map(t => ({ th: t.querySelectorAll('th').length, rows: t.querySelectorAll('tr').length, sql: t.classList.contains('sql-rows') }));
      const outs = [...v.querySelectorAll('.lesson-out')].map(o => ({ fig: !!o.querySelector('img,svg'), text: text((o.querySelector('.lesson-out-text') || {}).textContent).length }));
      const hrefs = [...v.querySelectorAll('a[href^="#/"]')].map(a => a.getAttribute('href').slice(2));
      return { h1: text((v.querySelector('h1') || {}).textContent), h2: v.querySelectorAll('h2').length, qs, figs, tables, outs,
        snips: v.querySelectorAll('[data-act="snip-run"]').length, hrefs, len: text(v.textContent).length, hasQuizLink: !!v.querySelector('a[href^="#/quiz/"]') };
    });
    const bad = r.hrefs.filter(h => !(/^(home|projects|playground|search|log|backup|checkpoint|interview|capstone|portfolio|review|notes|ph\d+|fde|ph\d+\/project|[\w-]+\/project|projects\/[\w-]+)$/.test(h) || /^(lesson|ex|quiz)\//.test(h) && routes.has(h.replace(/^quiz\//, 'lesson/'))));
    console.log(JSON.stringify({ lesson: id, ...r, hrefs: undefined, badLinks: bad, errors: errs.slice() }));
  }
  await b.close();
})().catch(e => { console.error('CRASH', e); process.exit(1); });
