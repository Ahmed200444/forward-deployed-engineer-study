// Audit: every quiz, through the real form. For each lesson quiz: pick every correct answer -> check -> all marked right,
// the explanation shown equals the data's `why`; then pick a wrong answer for each question -> marked wrong, explanation shown.
// usage: node quiz.js > quiz.jsonl
const { chromium } = require('playwright');
const B = process.env.B || 'https://localhost:8820/';
(async () => {
  const b = await chromium.launch(); const c = await b.newContext({ ignoreHTTPSErrors: true }); const p = await c.newPage();
  p.on('dialog', d => d.accept());
  const errs = []; p.on('pageerror', e => errs.push(String(e)));
  await p.goto(B + '#/projects'); await p.waitForTimeout(600);
  const data = await p.evaluate(() => { const o = {}; document.querySelectorAll('script.quiz-data').forEach(s => Object.assign(o, JSON.parse(s.textContent))); return o; });
  for (const [lid, qs] of Object.entries(data)) {
    for (const mode of ['right', 'wrong']) {
      await p.goto(B + '#/quiz/' + lid); await p.waitForTimeout(150);
      if (await p.$('#quiz-form [data-act="retry"]:not([hidden])')) { await p.click('#quiz-form [data-act="retry"]'); await p.waitForTimeout(100); }
      const info = await p.evaluate(({ qs, mode }) => {
        const fs = [...document.querySelectorAll('#quiz-form fieldset.q')];
        const out = { n: fs.length, expected: qs.length, picked: [] };
        fs.forEach((f, i) => {
          const q = qs[i]; const radios = [...f.querySelectorAll('input[type=radio]')];
          const texts = radios.map(r => r.nextElementSibling.textContent);
          const want = mode === 'right' ? [q.o[q.a]] : q.o.filter((_, j) => j !== q.a);
          const r = radios.find((r, k) => texts[k] === want[0]);
          out.picked.push(!!r); if (r) r.click();
        });
        return out;
      }, { qs, mode });
      await p.click('#quiz-form button[type=submit]'); await p.waitForTimeout(150);
      const res = await p.evaluate(({ qs }) => {
        const fs = [...document.querySelectorAll('#quiz-form fieldset.q')];
        return { status: (document.querySelector('#quiz-status') || {}).textContent, items: fs.map((f, i) => ({ why: (f.querySelector('.why') || {}).textContent, whyHidden: (f.querySelector('.why') || {}).hidden, cls: f.className, mark: f.innerText.replace(/\s+/g,' ').slice(-90), nOk: f.querySelectorAll('.ok,.right,.correct,[data-ok]').length, nBad: f.querySelectorAll('.bad,.wrong,.incorrect').length })) };
      }, { qs });
      const whyOk = res.items.every((it, i) => !it.whyHidden && (it.why || '').includes(qs[i].why.slice(0, 25)));
      console.log(JSON.stringify({ lesson: lid, mode, n: info.n, expected: info.expected, allPicked: info.picked.every(Boolean), status: (res.status || '').slice(0, 80), whyShownAndEqual: whyOk, classes: [...new Set(res.items.map(i => i.cls))].join('|'), sample: res.items[0].mark, nOk: res.items.reduce((a,i)=>a+i.nOk,0), nBad: res.items.reduce((a,i)=>a+i.nBad,0) }));
    }
  }
  console.log(JSON.stringify({ pageerrors: errs }));
  await b.close();
})().catch(e => { console.error('CRASH', e); process.exit(1); });
