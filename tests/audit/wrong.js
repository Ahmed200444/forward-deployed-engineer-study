// Audit: every exercise and inline question is run three ways through the visible controls:
//   starter  = the editor as the learner first sees it (must not pass)
//   wrong    = the model solution with its last `return` (or first print) broken (must not pass)
//   correct  = the model solution (must pass)
// usage: node wrong.js <shard> <nshards> > out.jsonl
const { chromium } = require('playwright');
const B = process.env.B || 'https://localhost:8820/'; const [shard, n] = [+process.argv[2] || 0, +process.argv[3] || 1];
function classify(status, result) {
  const s = (status || '') + ' ' + (result || '');
  if (/Could not start Python|Python could not start|did not start within|worker startup/.test(s)) return 'startup';
  if (/libraries this code needs could not be loaded/.test(s)) return 'libload';
  const m = (result || '').match(/(\d+) of (\d+) tests? passed/); if (m) return +m[1] === +m[2] ? 'pass' : 'assert';
  if (/All \d+ tests? passed|All \d+ checks? pass/.test(result || '') || /Marked as passed/.test(status || '')) return 'pass';
  if (/Traceback|Error|Stopped after/.test(result || '')) return 'error';
  return 'other';
}
function mutate(src, js) {
  const lines = src.split('\n');
  for (let i = lines.length - 1; i >= 0; i--) {
    const m = lines[i].match(/^(\s*)return\b\s*(.*)$/);
    if (m && m[2].trim() !== '' && !/^None\b/.test(m[2])) { lines[i] = m[1] + 'return ' + (js ? 'null' : 'None'); return lines.join('\n'); }
  }
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^(\s*)(print|console\.log)\(.*\)\s*$/);
    if (m) { lines[i] = m[1] + m[2] + '("WRONG")'; return lines.join('\n'); }
  }
  return null;
}
async function idle(p, sel) { await p.waitForFunction(s => { const b = document.querySelector(s); return b && !b.disabled; }, sel, { timeout: 180000 }); }
(async () => {
  const b = await chromium.launch(); const c = await b.newContext({ ignoreHTTPSErrors: true }); const p = await c.newPage();
  p.on('dialog', d => d.accept());
  await p.goto(B + '#/projects'); await p.waitForTimeout(500);
  const phases = await p.evaluate(() => [...document.querySelectorAll('.phase-src')].map(s => JSON.parse(s.querySelector('script.phase-meta').textContent).id));
  const routes = [];
  for (const ph of phases) { await p.goto(B + '#/' + ph); await p.waitForTimeout(120); for (const h of await p.evaluate(() => [...document.querySelectorAll('a[href^="#/ex/"]')].map(a => a.getAttribute('href').slice(2)))) routes.push(h); }
  const lessons = await p.evaluate(() => [...document.querySelectorAll('.lesson-src')].map(l => l.dataset.id));
  const items = [...new Set(routes)].map(r => ({ r, kind: 'ex' })).concat(lessons.map(l => ({ r: 'lesson/' + l, kind: 'lesson' }))).filter((_, i) => i % n === shard).filter(it => !process.env.ONLY || process.env.ONLY.split(',').includes(it.r));
  const run = async (code) => {
    await p.evaluate(v => { const t = document.querySelector('#code'); t.value = v; t.dispatchEvent(new Event('input', { bubbles: true })); }, code);
    await p.evaluate(() => { const r = document.querySelector('#result'); if (r) r.innerHTML = ''; });
    await p.click('[data-act="run"]'); await p.waitForTimeout(100); await idle(p, '[data-act="run"]');
    await p.waitForFunction(() => ((document.querySelector('#result') || {}).innerText || '').length > 0, null, { timeout: 60000 }).catch(() => {});
    return p.evaluate(() => ({ st: [...document.querySelectorAll('#view .status')].map(x => x.textContent).join(' | '), res: (document.querySelector('#result') || {}).innerText || '' }));
  };
  for (const it of items) {
    if (process.env.FRESH) { await p.context().clearCookies(); await p.goto(B + '#/home'); await p.evaluate(async () => { localStorage.clear(); sessionStorage.clear(); for (const d of (await indexedDB.databases())) indexedDB.deleteDatabase(d.name); }); await p.reload(); await p.waitForTimeout(400); }
    await p.goto(B + '#/' + it.r); await p.waitForTimeout(150);
    if (it.kind === 'ex') {
      if (!(await p.$('[data-act="run"]'))) { console.log(JSON.stringify({ route: it.r, kind: 'skip', why: 'no run button' })); continue; }
      const js = /^ex\/(fde-e12|fde-e13)$/.test(it.r);
      const start = await p.inputValue('#code').catch(() => '');
      let r = await run(start);
      console.log(JSON.stringify({ route: it.r, mode: 'starter', cls: classify(r.st, r.res), head: r.res.split('\n').slice(0, 3).join(' / ').slice(0, 240), startLen: start.length }));
      if (!(await p.$('[data-act="solution"]'))) { console.log(JSON.stringify({ route: it.r, kind: 'skip', why: 'no solution button' })); continue; }
      await p.click('[data-act="solution"]'); await p.waitForTimeout(50);
      const sol = await p.inputValue('#sol-code').catch(() => null);
      if (sol == null) continue;
      const bad = mutate(sol, js);
      if (bad == null) console.log(JSON.stringify({ route: it.r, mode: 'wrong', cls: 'unmutatable' }));
      else { r = await run(bad); console.log(JSON.stringify({ route: it.r, mode: 'wrong', cls: classify(r.st, r.res), head: r.res.split('\n').slice(0, 3).join(' / ').slice(0, 240) })); }
      r = await run(sol); console.log(JSON.stringify({ route: it.r, mode: 'correct', cls: classify(r.st, r.res), head: r.res.split('\n').slice(0, 2).join(' / ').slice(0, 200) }));
    } else {
      const ids = await p.evaluate(() => [...document.querySelectorAll('textarea[id^="pq-code-"]')].map(t => t.id.replace('pq-code-', '')));
      for (const k of ids) {
        for (const mode of ['starter', 'wrong', 'correct']) {
          const res = await p.evaluate(async ({ k, mode, mutSrc }) => {
            const ta = document.getElementById('pq-code-' + k), sol = document.getElementById('pq-solcode-' + k);
            let code = ta.value;
            if (mode === 'correct') code = sol.value;
            if (mode === 'wrong') { code = mutSrc ? (new Function('src', mutSrc))(sol.value) : null; if (code == null) return { none: true }; }
            if (mode !== 'starter') { ta.value = code; ta.dispatchEvent(new Event('input', { bubbles: true })); }
            let run = null, el = ta; while (el && !run) { el = el.parentElement; run = el && el.querySelector('[data-pq="run"]'); }
            el.querySelectorAll('[data-pq-result]').forEach(x => { x.innerHTML = ''; }); run.click(); const t0 = Date.now(); await new Promise(r => setTimeout(r, 80));
            while ((run.disabled || !(el.querySelector('[data-pq-result]') || {}).innerText) && Date.now() - t0 < 180000) await new Promise(r => setTimeout(r, 100));
            await new Promise(r => setTimeout(r, 300));
            return { st: [...el.querySelectorAll('[data-pq-status]')].map(x => x.textContent).join(' | '), res: [...el.querySelectorAll('[data-pq-result]')].map(x => x.innerText).join('\n') };
          }, { k, mode, mutSrc: mode === 'wrong' ? 'return (' + mutate.toString() + ')(src,false)' : null });
          if (res.none) { console.log(JSON.stringify({ route: it.r, q: +k, mode, cls: 'unmutatable' })); continue; }
          console.log(JSON.stringify({ route: it.r, q: +k, mode, cls: classify(res.st, res.res), head: res.res.split('\n').slice(0, 3).join(' / ').slice(0, 240) }));
        }
      }
    }
  }
  await b.close();
})().catch(e => { console.error('CRASH', e); process.exit(1); });
