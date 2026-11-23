// Audit: stronger wrong submission. Every `return <value>` in the model solution becomes `return None`; the learner-facing
// checker must reject it. Reads the route list from WP (json array of [route, q]). Fresh profile per item.
const { chromium } = require('playwright'); const fs = require('fs');
const B = process.env.B || 'https://localhost:8820/'; const wp = JSON.parse(fs.readFileSync(process.env.WP));
function mutAll(src, js) { let n = 0; const out = src.split('\n').map(l => { const m = l.match(/^(\s*)return\b\s*(.*)$/); if (m && m[2].trim() && !/^(None|null)\b/.test(m[2].trim())) { n++; return m[1] + 'return ' + (js ? 'null' : 'None'); } return l; }); return n ? out.join('\n') : null; }
function cls(s) { const m = (s || '').match(/(\d+) of (\d+) tests? passed/); if (m) return +m[1] === +m[2] ? 'pass' : 'assert'; if (/All \d+ tests? passed/.test(s)) return 'pass'; if (/Traceback|Error/.test(s)) return 'error'; return 'other'; }
(async () => {
  const b = await chromium.launch(); const c = await b.newContext({ ignoreHTTPSErrors: true }); const p = await c.newPage();
  for (const [route, q] of wp) {
    await p.goto(B + '#/' + route); await p.waitForTimeout(350);
    const js = /fde-e1[23]|fde-l8/.test(route);
    if (q != null) {
      const sol = await p.evaluate(q => document.getElementById('pq-solcode-' + q).value, q); const bad = mutAll(sol, js);
      if (!bad) { console.log(JSON.stringify({ route, q, cls: 'no-return' })); continue; }
      const r = await p.evaluate(async ({ q, bad }) => { const ta = document.getElementById('pq-code-' + q); ta.value = bad; ta.dispatchEvent(new Event('input', { bubbles: true })); const box = document.getElementById('pq-' + q); const run = box.querySelector('[data-pq="run"]'), res = box.querySelector('[data-pq-result]'); res.innerHTML = ''; run.click(); const t0 = Date.now(); await new Promise(r => setTimeout(r, 100)); while ((run.disabled || !res.innerText) && Date.now() - t0 < 120000) await new Promise(r => setTimeout(r, 100)); await new Promise(r => setTimeout(r, 300)); return res.innerText.split('\n').slice(0, 3).join(' | '); }, { q, bad });
      console.log(JSON.stringify({ route, q, cls: cls(r), head: r.slice(0, 160) }));
    } else {
      await p.click('[data-act="solution"]'); await p.waitForTimeout(60);
      const sol = await p.inputValue('#sol-code'); const bad = mutAll(sol, js);
      if (!bad) { console.log(JSON.stringify({ route, cls: 'no-return' })); continue; }
      await p.evaluate(v => { const t = document.querySelector('#code'); t.value = v; t.dispatchEvent(new Event('input', { bubbles: true })); document.querySelector('#result').innerHTML = ''; }, bad);
      await p.click('[data-act="run"]'); await p.waitForTimeout(150); await p.waitForFunction(() => !document.querySelector('[data-act="run"]').disabled && (document.querySelector('#result').innerText || '').length, null, { timeout: 120000 }); await p.waitForTimeout(200);
      const r = await p.innerText('#result'); console.log(JSON.stringify({ route, cls: cls(r), head: r.split('\n').slice(0, 3).join(' | ').slice(0, 160) }));
    }
  }
  await b.close();
})().catch(e => { console.error('CRASH', e); process.exit(1); });
