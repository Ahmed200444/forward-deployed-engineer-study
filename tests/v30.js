// v30 acceptance: the rewritten lessons (l1 bridge, l2, l4, l5, ph2-l6, ph3-l1) and the "new here" notes.
// Checks, through the visible buttons against tests/server.js:
//  - every block's live output equals the output printed in the lesson (which build.py recorded in CPython)
//  - SQL steps render as tables with the same rows; the chart block draws an image
//  - question levels, Optional practice (closed, after the core questions, opens when it holds a draft)
//  - old snippet drafts and question drafts and passes still load under their old keys
//  - guided starters fail and reference solutions pass when run through Run and check
//  - New here notes on questions and on an exercise page; Playground shows a bare expression; ax.hist prints no tuple
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path');
const B = 'https://localhost:8820/', KEY = 'ai-study-phase0-v1';
const out = []; const ok = (n, c, i) => out.push((c ? 'PASS ' : 'FAIL ') + n + (i !== undefined && !c ? ' — ' + String(i).slice(0, 400) : ''));
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const IQ = (() => { const i = html.indexOf('var INLINE_Q = ') + 15; let d = 0, j = i, s = false, e = false; for (; j < html.length; j++) { const c = html[j]; if (s) { if (e) e = false; else if (c === '\\') e = true; else if (c === '"') s = false; continue; } if (c === '"') s = true; else if (c === '{') d++; else if (c === '}') { d--; if (!d) break; } } return JSON.parse(html.slice(i, j + 1)); })();
const LESSONS = ['l1', 'l2', 'l4', 'l5', 'ph2-l6', 'ph3-l1', 'ph2-l7', 'ph3-l2'];
function emptyState(extra) { return Object.assign({ lessons: {}, ex: {}, quiz: {}, drafts: {}, tried: {}, check: {}, review: {}, notes: {}, log: {}, hints: {}, gh: {}, qpass: {} }, extra || {}); }
async function ready(p) { await p.waitForFunction(() => window.__FDE_STORE__ && window.__FDE_STORE__.store.mode !== 'starting'); await p.evaluate(() => window.__FDE_STORE__.store.ready); }
async function ctx(b, fixture) { const c = await b.newContext({ ignoreHTTPSErrors: true });
  if (fixture) await c.addInitScript(([k, f]) => { if (!sessionStorage.getItem('seeded')) { localStorage.setItem(k, JSON.stringify(f)); sessionStorage.setItem('seeded', '1'); } }, [KEY, fixture]);
  return c; }
async function page(c, route) { const p = await c.newPage(); p.on('pageerror', e => out.push('FAIL pageerror ' + e)); await p.goto(B + '#/' + route); await ready(p); await p.waitForTimeout(200); return p; }
const norm = t => t.replace(/\r/g, '').replace(/\s+$/g, '').split('\n').map(l => l.replace(/\s+$/, '')).join('\n');

(async () => {
  const b = await chromium.launch();
  try {
    // ---------- blocks: live output equals the printed output ----------
    { const c = await ctx(b); const p = await page(c, 'home');
      for (const lid of LESSONS) {
        await p.evaluate(r => { location.hash = '#/lesson/' + r; }, lid); await p.waitForTimeout(300);
        const blocks = await p.$$eval('#view pre[data-snip]', ps => ps.map(pre => {
          let n = pre.nextElementSibling, exp = null;
          while (n && !n.matches('pre, h2')) { if (n.matches('.lesson-out')) { exp = n; break; } n = n.nextElementSibling; }
          let bb = pre.nextElementSibling; while (bb && !bb.matches('pre,h2,.snip-bar')) bb = bb.nextElementSibling;
          return { key: pre.dataset.snip, hasBar: !!(bb && bb.matches('.snip-bar')),
            text: exp ? [...exp.querySelectorAll('pre.lesson-out-text:not(.lesson-out-err)')].map(x => x.textContent).join('\n') : null,
            err: exp ? [...exp.querySelectorAll('pre.lesson-out-err')].map(x => x.textContent).join('') : '',
            rows: exp && exp.querySelector('table.sql-rows') ? [...exp.querySelectorAll('table.sql-rows tr')].map(tr => [...tr.children].map(td => td.textContent)) : null,
            fig: !!(exp && exp.querySelector('.lesson-out-fig img')) }; }));
        ok(lid + ': every code block carries data-snip', await p.$$eval('#view > pre', ps => ps.filter(x => !x.closest('.rec-out,.lesson-out,.pq,.snip-panel,.line-notes,.pq-optional')).every(x => x.hasAttribute('data-snip'))));
        for (let bi = 0; bi < blocks.length; bi++) {
          const bl = blocks[bi]; if (!bl.hasBar || (bl.text === null && !bl.rows)) continue;
          const pre = (await p.$$('#view pre[data-snip]'))[bi];
          const bar = await pre.evaluateHandle(e => { let n = e.nextElementSibling; while (n && !n.matches('.snip-bar')) n = n.nextElementSibling; return n; });
          const panel = await bar.evaluateHandle(e => { let n = e.nextElementSibling; while (n && !n.matches('.snip-panel')) n = n.nextElementSibling; return n; });
          await (await panel.$('[data-act="snip-run"]')).click();
          await p.waitForFunction(pn => /Finished|error|could not/i.test(pn.querySelector('.status').textContent), panel, { timeout: 120000 });
          const live = await panel.evaluate(pn => ({ heads: [...pn.querySelectorAll('.snip-result .out-head')].map(h => h.textContent),
            printed: [...pn.querySelectorAll('.snip-result .out')].filter(o => /Printed output/.test(o.querySelector('.out-head').textContent)).map(o => o.querySelector('pre').textContent).join(''),
            error: [...pn.querySelectorAll('.snip-result .out-head.fail')].map(h => h.parentElement.querySelector('pre').textContent).join(''),
            rows: pn.querySelector('.snip-result table') ? [...pn.querySelectorAll('.snip-result table tr')].map(tr => [...tr.children].map(td => td.textContent)) : null,
            img: !!pn.querySelector('.snip-result .charts img') }));
          const name = lid + '#' + bl.key;
          if (bl.rows) ok(name + ': SQL table matches the lesson rows (' + (bl.rows.length - 1) + ')', JSON.stringify(live.rows) === JSON.stringify(bl.rows), JSON.stringify(live.rows) + ' vs ' + JSON.stringify(bl.rows));
          else ok(name + ': live output equals the lesson output', norm(live.printed) === norm(bl.text), JSON.stringify(live.printed) + ' vs ' + JSON.stringify(bl.text));
          if (bl.err) ok(name + ': the expected error appears', live.error.includes(bl.err.split(': ').slice(-1)[0]), live.error);
          if (bl.fig) ok(name + ': the chart is drawn live', live.img);
        }
      }
      await c.close(); }

    // ---------- question structure ----------
    { const c = await ctx(b); const p = await page(c, 'home');
      for (const lid of LESSONS) {
        await p.evaluate(r => { location.hash = '#/lesson/' + r; }, lid); await p.waitForTimeout(250);
        const qs = IQ[lid];
        const dom = await p.$$eval('.pq-inline .pq', ps => ps.map(x => ({ t: x.querySelector('.pq-h').textContent, lvl: (x.querySelector('.pq-level') || {}).textContent || '', opt: !!x.closest('.pq-optional'), before: !!x.querySelector('.pq-before') })));
        const core = qs.filter(q => !q.optional), opt = qs.filter(q => q.optional);
        ok(lid + ': ' + qs.length + ' questions shown', dom.length === qs.length, dom.length);
        ok(lid + ': core questions first, in the planned order', core.every((q, i) => dom[i] && dom[i].t.includes(q.title) && !dom[i].opt), JSON.stringify(dom.map(d => d.t)));
        ok(lid + ': optional questions inside Optional practice', opt.every((q, i) => dom[core.length + i] && dom[core.length + i].opt && dom[core.length + i].t.includes(q.title)));
        ok(lid + ': level chips match', qs.every((q, i) => { const d = dom.find(x => x.t.includes(': ' + q.title)); return d && d.lvl.toLowerCase() === (q.level || ''); }));
        ok(lid + ': the first core question is Guided', (core[0] || {}).level === 'guided');
        if (opt.length) { const g = await p.$eval('.pq-optional', d => ({ open: d.open, sum: d.querySelector('summary').textContent, next: (d.nextElementSibling || {}).textContent }));
          ok(lid + ': Optional practice is closed and before Check yourself', !g.open && /Optional practice/.test(g.sum) && /Check yourself/.test(g.next), JSON.stringify(g)); }
        ok(lid + ': the core questions are numbered 1..' + core.length, await p.$$eval('.pq-inline .pq', ps => ps.every((x, i) => x.id === 'pq-' + (i + 1))));
      }
      await c.close(); }

    // ---------- saved work under old keys ----------
    { const fx = emptyState({ drafts: { 'snip:l2#2': 'print("my edit of the card")\n', 'snip:l5#0': 'print("my file edit")\n', 'q:l2-6': '# my draft for count_after\n', 'q:l2-4': '# draft in optional\n', 'snip:ph2-l6#0': 'SELECT 42 AS answer;\n' }, qpass: { 'q:l2-7': true }, lessons: { l2: true } });
      const c = await ctx(b, fx); const p = await page(c, 'lesson/l2');
      const card = await p.$('pre[data-snip="2"]'); const bar = await card.evaluateHandle(e => { let n = e.nextElementSibling; while (n && !n.matches('.snip-bar')) n = n.nextElementSibling; return n; });
      ok('old snippet draft l2#2 still marked as saved', /your edits are saved/.test(await bar.evaluate(e => e.textContent)));
      ok('old snippet draft l2#2 loads into the right block', (await bar.evaluate(e => e.nextElementSibling.querySelector('textarea').value)).includes('my edit of the card'));
      ok('line notes still attached to l2#2', await card.evaluate(e => { let n = e.nextElementSibling; while (n && !n.matches('pre,h2')) { if (n.matches('details.line-notes')) return n.querySelectorAll('li').length === 9; n = n.nextElementSibling; } return false; }));
      const qd = await p.evaluate(() => { const h = [...document.querySelectorAll('.pq')].find(x => x.querySelector('.pq-h').textContent.includes('Update a variable')); return h && h.querySelector('textarea').value; });
      ok('question draft q:l2-6 loads', (qd || '').includes('my draft for count_after'), qd);
      ok('question pass q:l2-7 still shows Passed', await p.evaluate(() => [...document.querySelectorAll('.pq')].some(x => x.querySelector('.pq-h').textContent.includes('A price tag') && x.querySelector('.done-badge'))));
      ok('Optional practice opens when it holds a draft', await p.$eval('.pq-optional', d => d.open));
      ok('lesson l2 still marked as read', /Marked as read/.test(await p.innerText('#view')));
      await p.evaluate(() => { location.hash = '#/lesson/l5'; }); await p.waitForTimeout(250);
      ok('old snippet draft l5#0 attached to the first block', await p.$eval('pre[data-snip="0"]', e => { let n = e.nextElementSibling; while (n && !n.matches('.snip-bar')) n = n.nextElementSibling; return /your edits are saved/.test(n.textContent); }));
      await p.evaluate(() => { location.hash = '#/lesson/ph2-l6'; }); await p.waitForTimeout(250);
      ok('old snippet draft ph2-l6#0 attached to the shape-of-a-query block', await p.$eval('pre[data-snip="0"]', e => { let n = e.nextElementSibling; while (n && !n.matches('.snip-bar')) n = n.nextElementSibling; return /your edits are saved/.test(n.textContent) && /SELECT complaint/.test(e.textContent); }));
      await c.close(); }

    // ---------- guided starters fail, solutions pass, through Run and check ----------
    { const c = await ctx(b); const p = await page(c, 'home'); let n = 0;
      for (const lid of LESSONS) {
        await p.evaluate(r => { location.hash = '#/lesson/' + r; }, lid); await p.waitForTimeout(250);
        await p.evaluate(() => document.querySelectorAll('.pq-optional').forEach(d => d.open = true));
        const boxes = await p.$$('.pq-inline .pq');
        for (const box of boxes) {
          const title = await box.$eval('.pq-h', h => h.textContent);
          const q = IQ[lid].find(x => title.includes(': ' + x.title));
          await (await box.$('[data-pq="run"]')).click();
          await box.waitForSelector('[data-pq-result] .out-head', { timeout: 120000 });
          const starter = await box.$eval('[data-pq-result] .out-head', h => h.textContent);
          await (await box.$('[data-pq="sol"]')).click();
          await (await box.$('[data-pq="sol-run"]')).click();
          await box.waitForSelector('[data-pq-solresult] .out-head', { timeout: 120000 });
          const sol = await box.$eval('[data-pq-solresult] .out-head', h => h.textContent);
          ok(q.id + ': starter does not pass, solution passes', !/^All \d+ tests passed/.test(starter) && /^All \d+ tests passed/.test(sol), starter + ' | ' + sol);
          n++;
        }
      }
      ok('ran ' + n + ' questions through the buttons', n === LESSONS.reduce((a, l) => a + IQ[l].length, 0));
      await c.close(); }

    // ---------- new here notes, Playground echo, histogram ----------
    { const c = await ctx(b); const p = await page(c, 'lesson/ph3-l7');
      ok('ph3-l7: a New here note explains np.clip', await p.$$eval('.pq-before', bs => bs.some(x => /New here/.test(x.textContent) && /np\.clip/.test(x.textContent) && /array\(\[0, 3, 5\]\)/.test(x.textContent))));
      await p.evaluate(() => { location.hash = '#/ex/ph1-e7'; }); await p.waitForTimeout(250);
      ok('exercise page ph1-e7 shows its New here note (re.sub)', await p.$eval('.ex-task', e => /New here/.test(e.textContent) && /re\.sub/.test(e.textContent)));
      await p.evaluate(() => { location.hash = '#/lesson/l3'; }); await p.waitForTimeout(250);
      ok('an unchanged lesson (l3) still has no levels or optional group', await p.evaluate(() => !document.querySelector('#view .pq-optional') && !document.querySelector('#view .pq-level')));
      await p.evaluate(() => { location.hash = '#/playground'; }); await p.waitForTimeout(300);
      await p.fill('textarea', 'import pandas as pd\ndf = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})\ndf\n');
      await p.click('[data-act="run"]'); await p.waitForSelector('#result .out', { timeout: 120000 });
      const pg = await p.innerText('#result');
      ok('Playground: a bare DataFrame shows its table', /a\s+b/.test(pg) && !/nothing was printed/.test(pg), pg);
      await p.fill('textarea', 'import numpy as np\nimport matplotlib.pyplot as plt\nfig, ax = plt.subplots()\nax.hist(np.arange(10), bins=3)\n');
      await p.click('[data-act="run"]'); await p.waitForFunction(() => document.querySelector('#result .charts img'), null, { timeout: 120000 });
      const hg = await p.innerText('#result');
      ok('Playground: ax.hist draws the chart and prints no object tuple', !/BarContainer|array\(/.test(hg), hg);
      await p.evaluate(() => { location.hash = '#/lesson/ph3-l4'; }); await p.waitForTimeout(300);
      const pre = (await p.$$('#view > pre'))[1]; const bar = await pre.evaluateHandle(e => { let n = e.nextElementSibling; while (n && !n.matches('.snip-bar')) n = n.nextElementSibling; return n; });
      const panel = await bar.evaluateHandle(e => { let n = e.nextElementSibling; while (n && !n.matches('.snip-panel')) n = n.nextElementSibling; return n; }); await (await panel.$('[data-act="snip-run"]')).click();
      await p.waitForFunction(pn => pn.querySelector('.snip-result .charts img') || /error/i.test(pn.querySelector('.status').textContent), panel, { timeout: 120000 });
      const t = await panel.evaluate(pn => pn.querySelector('.snip-result').innerText);
      ok('ph3-l4 histogram: chart shown, no object representation printed', !/BarContainer|array\(/.test(t) && await panel.evaluate(pn => !!pn.querySelector('.snip-result .charts img')), t);
      await c.close(); }
  } catch (e) { out.push('FAIL crashed: ' + (e.stack || e)); }
  await b.close();
  console.log(out.join('\n'));
  const f = out.filter(x => x.startsWith('FAIL')).length; console.log('\n' + (out.length - f) + ' passed, ' + f + ' failed');
  process.exit(f ? 1 : 0);
})();
