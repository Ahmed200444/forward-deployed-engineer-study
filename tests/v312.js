// v31.2 acceptance: the fixes from the v31.1 audit, through the page's own buttons.
// node v312.js   (server: node server.js .. 8820)
const { chromium } = require('playwright');
const B = 'https://localhost:8820/';
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
const out = []; const ok = (n, c, i) => out.push((c ? 'PASS ' : 'FAIL ') + n + (!c && i !== undefined ? ' — ' + String(i).slice(0, 400) : ''));
const gh = async () => (await fetch(B + '__test/gh')).json();
async function idle(p, sel) { await p.waitForFunction(s => { const b = document.querySelector(s); return b && !b.disabled; }, sel, { timeout: 180000 }); }
async function rvIdle(p) { await p.waitForFunction(() => { const s = document.querySelector('[data-gh-rv-status]'); return s && !/^Checking/.test(s.textContent); }, null, { timeout: 20000 }); }
async function fresh(c) { const p = await c.newPage(); p.on('dialog', d => d.accept()); await p.goto(B + '#/home'); await p.evaluate(async () => { localStorage.clear(); sessionStorage.clear(); for (const d of (await indexedDB.databases())) indexedDB.deleteDatabase(d.name); }); await p.reload(); return p; }
async function runEx(p) {
  await p.evaluate(() => { const r = document.querySelector('#result'); if (r) r.innerHTML = ''; });
  await p.click('[data-act="run"]'); await p.waitForTimeout(100); await idle(p, '[data-act="run"]');
  await p.waitForFunction(() => ((document.querySelector('#result') || {}).innerText || '').length > 0, null, { timeout: 120000 });
  return p.innerText('#result');
}
async function runQ(p, qid, code) {
  return p.evaluate(async ({ qid, code }) => {
    const box = [...document.querySelectorAll('.pq')].find(b => (b.querySelector('h3') || {}).textContent.includes(': ' + qid)) || null;
    const ta = box ? box.querySelector('textarea[id^="pq-code-"]') : null; if (!ta) return { missing: true };
    if (code != null) { ta.value = code === 'SOL' ? box.querySelector('textarea[id^="pq-solcode-"]').value : code; ta.dispatchEvent(new Event('input', { bubbles: true })); }
    const run = box.querySelector('[data-pq="run"]'); box.querySelectorAll('[data-pq-result]').forEach(x => { x.innerHTML = ''; }); run.click();
    const t0 = Date.now(); await new Promise(r => setTimeout(r, 80));
    while ((run.disabled || !(box.querySelector('[data-pq-result]') || {}).innerText) && Date.now() - t0 < 180000) await new Promise(r => setTimeout(r, 100));
    await new Promise(r => setTimeout(r, 300));
    return { res: box.querySelector('[data-pq-result]').innerText };
  }, { qid, code });
}
(async () => {
  await fetch(B + '__test/reset');
  const b = await chromium.launch(); const c = await b.newContext({ ignoreHTTPSErrors: true });
  let p = await fresh(c); const errs = []; p.on('pageerror', e => errs.push(String(e)));

  // 1. ph9-e12: model solution passes twice in a row through the Run button
  await p.goto(B + '#/ex/ph9-e12'); await p.waitForSelector('[data-act="run"]');
  await p.click('[data-act="solution"]'); const sol = await p.inputValue('#sol-code');
  await p.evaluate(v => { const t = document.querySelector('#code'); t.value = v; t.dispatchEvent(new Event('input', { bubbles: true })); }, sol);
  const r1 = await runEx(p), r2 = await runEx(p);
  ok('ph9-e12: solution passes on the first Run', /All \d+ tests? passed/.test(r1), r1.slice(0, 200));
  ok('ph9-e12: solution passes again on the second Run', /All \d+ tests? passed/.test(r2) && !/already exists/.test(r2), r2.slice(0, 200));

  // 2. weak checkers: a wrong answer fails, the model solution passes (fresh profile per lesson)
  const TITLE = { 'q:ph5-l12-3': 'Accept the job, answer 202', 'q:ph6-l15-3': 'Cache answers by image hash', 'q:ph9-l4-3': 'Write once, not twice', 'q:ph9-l9-3': 'Parse a stdio stream', 'q:ph9-l13-2': 'A valid order to run', 'q:ph9-l14-2': 'A task with a lifecycle', 'q:ph9-l16-1': 'Resume from saved state' };
  const WEAK = { 'ph5-l12': ['q:ph5-l12-3', 'def submit(queue, payload):\n    queue.append({"id": f"job-{len(queue) + 1}", "payload": payload})\n    return None\n'],
    'ph6-l15': ['q:ph6-l15-3', 'import hashlib\ndef cached_describe(image_bytes, prompt, cache, describe):\n    key = hashlib.sha256(image_bytes).hexdigest() + "|" + prompt\n    if key not in cache:\n        cache[key] = describe(image_bytes, prompt)\n    return None\n'],
    'ph9-l4': ['q:ph9-l4-3', 'def once(journal, request_id, action, args, do):\n    return do(**args)\n'],
    'ph9-l9': ['q:ph9-l9-3', 'import json\ndef read_messages(text):\n    for line in text.splitlines():\n        if line.strip():\n            json.loads(line)\n    return []\n'],
    'ph9-l13': ['q:ph9-l13-2', 'def run_order(plan):\n    ids = [s["id"] for s in plan]\n    if any(a not in ids for s in plan for a in s["after"]) or len(plan) == 2 and plan[0]["after"] and plan[1]["after"]:\n        raise ValueError("cycle")\n    return ids\n'],
    'ph9-l14': ['q:ph9-l14-2', 'def next_state(state, event):\n    if state in ("completed", "failed", "canceled"):\n        raise ValueError((state, event))\n    return "working"\n'],
    'ph9-l16': ['q:ph9-l16-1', 'def resume(checkpoints, thread_id, answer):\n    s = checkpoints[thread_id]\n    if s["waiting_for"] is None:\n        raise KeyError(thread_id)\n    s[s["waiting_for"]] = answer\n    return s\n'] };
  for (const [lid, [qid, bad]] of Object.entries(WEAK)) {
    await p.goto(B + '#/lesson/' + lid); await p.waitForTimeout(300);
    const w = await runQ(p, TITLE[qid], bad), s = await runQ(p, TITLE[qid], 'SOL');
    if (w.missing || s.missing) { ok(qid + ': box found', false); continue; }
    ok(qid + ': a wrong answer now fails', !/All \d+ tests? passed/.test(w.res), w.res.slice(0, 160));
    ok(qid + ': the model solution passes', /All \d+ tests? passed/.test(s.res), s.res.slice(0, 160));
  }

  // 3. every question box shows a level chip; hand-set levels kept
  for (const lid of ['l1', 'l3', 'ph5-l12', 'ph9-l11', 'fde-l8']) {
    await p.goto(B + '#/lesson/' + lid); await p.waitForTimeout(250);
    const m = await p.evaluate(() => ({ n: document.querySelectorAll('.pq').length, lv: document.querySelectorAll('.pq .pq-level').length }));
    ok(lid + ': every question has a level (' + m.lv + '/' + m.n + ')', m.n > 0 && m.n === m.lv, JSON.stringify(m));
  }
  await p.goto(B + '#/lesson/l1'); await p.waitForTimeout(250);
  ok('l1 Q1 keeps its hand-set Guided level', /Guided/i.test(await p.evaluate(() => (document.querySelector('.pq .pq-level') || {}).textContent || '')));

  // 4. New here notes: l1 Q2 (split/join/append), an exercise (ph3-e7 np.clip)
  await p.goto(B + '#/lesson/l1'); await p.waitForTimeout(250);
  const l1 = await p.evaluate(() => { const b = [...document.querySelectorAll('.pq')].find(x => /Where does cd take you\?/.test((x.querySelector('h3') || {}).textContent)); return b ? (b.querySelector('.pq-before') || {}).textContent || '' : 'NOBOX'; });
  ok('l1 Q2 has a New here note for split, join and append, with worked examples', /New here/.test(l1) && /split/.test(l1) && /join/.test(l1) && /append/.test(l1) && />>>/.test(l1), l1.slice(0, 300));
  await p.goto(B + '#/ex/ph3-e7'); await p.waitForTimeout(250);
  const e7 = await p.evaluate(() => (document.querySelector('.ex-task .pq-before') || {}).innerText || '');
  ok('ph3-e7 exercise page explains np.clip and np.log before the task', /np\.clip/.test(e7) && /np\.log/.test(e7) && />>>/.test(e7), e7.slice(0, 300));
  ok('ph3-e7 still has its optional hint', await p.$('.pq-hint, [data-act="hint"], details.hint') !== null || /Hint/.test(await p.innerText('#view')));

  // 5. Hint target size on a phone
  const m = await b.newContext({ ignoreHTTPSErrors: true, viewport: { width: 375, height: 800 }, hasTouch: true, isMobile: true });
  const pm = await m.newPage(); await pm.goto(B + '#/lesson/l2'); await pm.waitForTimeout(400);
  const hh = await pm.evaluate(() => [...document.querySelectorAll('.pq-hint > summary')].filter(s => s.offsetParent).map(s => s.getBoundingClientRect().height));
  ok('Hint summaries are at least 44 px tall on a 375 px phone', hh.length > 0 && hh.every(h => h >= 44), hh.slice(0, 5).join(','));
  await m.close();

  // 6. Page not found
  await p.goto(B + '#/ph0/project'); await p.waitForTimeout(250);
  ok('An unknown address says Page not found', /Page not found/.test(await p.innerText('#view')));
  await p.goto(B + '#/home'); await p.waitForTimeout(250);
  ok('Home itself shows no Page not found note', !/Page not found/.test(await p.innerText('#view')));
  await p.goto(B + '#/lesson/l2'); await p.waitForTimeout(250);
  ok('A real address shows no Page not found note', !/Page not found/.test(await p.innerText('#view')));

  // 7. README for an untouched starter does not claim a solution; publish to an empty repo says Published, in 2 commits
  p = await fresh(c); p.on('pageerror', e => errs.push(String(e)));
  const route = '#/project';
  await p.goto(B + route); await p.waitForTimeout(600);
  const readme = await p.evaluate(() => { const t = document.querySelector('#gh-readme'); return t ? t.value : ''; });
  if (readme) {
    ok('Starter README does not say "my solution"', !/my solution/i.test(readme), readme.slice(0, 300));
    ok('Starter README says it is not solved yet', /not solved yet|starting template/.test(readme), readme.slice(0, 300));
    ok('Starter README has no Key ideas from the model solution', !/## Key ideas/.test(readme));
    const sum = (readme.match(/^> (.*)$/m) || [])[1] || '';
    ok('README summary ends with a full stop or ellipsis', /[.!?…]$/.test(sum), sum);
  } else ok('README preview found on ' + route, false, route);
  // publish this project to the empty mock repo through the review screen
  const pb = await p.$('[data-act="gh-publish"]');
  if (pb) {
    await pb.click(); await p.waitForSelector('[data-gh-review]:not([hidden])', { timeout: 20000 }); await rvIdle(p);
    await p.selectOption('#gh-rv-repo', 'Ahmed200444/empty-test'); await p.fill('#gh-rv-branch', ''); await p.click('[data-act="gh-rv-check"]'); await rvIdle(p);
    const ack = await p.$('#gh-rv-ack'); if (ack && await ack.isVisible()) await ack.check();
    const before = (await gh()).log.filter(x => x.op === 'commit').length;
    await p.click('[data-act="gh-confirm"]');
    await p.waitForFunction(() => /Published to GitHub|Not published|Already on GitHub/.test((document.querySelector('#gh-status') || {}).textContent || ''), null, { timeout: 30000 }).catch(() => {});
    const st = await p.innerText('#gh-status');
    const after = (await gh()).log.filter(x => x.op === 'commit').length;
    ok('Publish shows a clear "Published to GitHub" message', /✓ Published to GitHub/.test(st), st);
    ok('The message links to the files on GitHub', await p.$('#gh-status a[href*="github.com"]') !== null);
    ok('An empty repo gets 2 commits, not one per file', after - before === 2, after - before);
    ok('The message states the commit count', /in 2 commits/.test(st), st);
    const e = (await gh()).repos['ahmed200444/empty-test'];
    const files = Object.keys(e.trees[e.commits[e.branches.main].tree]);
    ok('All files reached the empty repo', files.some(f => /README\.md$/.test(f)) && files.length >= 3, files.join(','));
  } else ok('Publish button on the Phase 0 project', false, route);

  ok('No page errors', errs.length === 0, errs.join(' | '));
  await b.close();
  console.log(out.join('\n')); const f = out.filter(x => !x.startsWith('PASS')).length; console.log('\n' + (out.length - f) + ' passed, ' + f + ' failed');
  process.exit(f ? 1 : 0);
})();
