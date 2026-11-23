// Offline copy acceptance: node bundle.js http://localhost:8765/ /path/to/extracted/fde-study-offline
// Run it against a freshly extracted zip served by the bundle's own start.sh. Every request that leaves
// localhost is blocked, so a pass means the copy works with no internet.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const B = process.argv[2] || 'http://localhost:8765/';
const DIR = process.argv[3];
const out = []; const ok = (n, c, i) => out.push((c ? 'PASS ' : 'FAIL ') + n + (i !== undefined && !c ? ' — ' + String(i).slice(0, 300) : ''));
async function idle(p) { await p.waitForFunction(() => ![...document.querySelectorAll('#view button')].some(b => b.disabled && /Run/.test(b.textContent)), null, { timeout: 240000 }); }
async function play(p, lang, code) {
  await p.goto(B + '#/playground'); await p.waitForTimeout(300);
  await p.getByRole('button', { name: lang, exact: true }).click();
  await p.fill('#code', code); await p.click('[data-act="run"]'); await p.waitForTimeout(200); await idle(p);
  return p.evaluate(() => { const o = document.querySelector('#view .out:last-of-type, #view #result, #view .run-out'); return document.querySelector('#view').innerText; });
}
(async () => {
  // files in the extracted folder
  if (DIR) {
    for (const f of ['index.html', 'py/pyodide.js', 'py/pyodide.asm.wasm', 'py/pyodide-lock.json', 'Start FDE Study.cmd', 'serve.ps1', 'start.sh', 'HOW-TO-START.txt'])
      ok('bundle has ' + f, fs.existsSync(path.join(DIR, f)));
    ok('start.sh is executable after extracting', (fs.statSync(path.join(DIR, 'start.sh')).mode & 0o111) !== 0);
    ok('Windows launcher uses CRLF line endings', /\r\n/.test(fs.readFileSync(path.join(DIR, 'Start FDE Study.cmd'), 'utf8')));
    const lock = JSON.parse(fs.readFileSync(path.join(DIR, 'py/pyodide-lock.json'), 'utf8'));
    const missing = Object.values(lock.packages).map(x => x.file_name).filter(f => !fs.existsSync(path.join(DIR, 'py', f)));
    const need = ['numpy', 'pandas', 'matplotlib', 'scikit-learn', 'scipy', 'pytest', 'sqlite3'];
    ok('runtime lists numpy, pandas, matplotlib, scikit-learn, scipy, pytest, sqlite3', need.every(n => lock.packages[n]), need.filter(n => !lock.packages[n]).join(','));
    ok('every package file named in the lock that the site loads is present (' + missing.length + ' absent of ' + Object.keys(lock.packages).length + ')', need.every(n => fs.existsSync(path.join(DIR, 'py', lock.packages[n].file_name))), missing.slice(0, 8).join(', '));
    const html = fs.readFileSync(path.join(DIR, 'index.html'), 'utf8');
    ok('index.html points at the relative py/ folder, not /py/', /window\.__PY_BASE__="py\/"/.test(html) && !/__PY_BASE__="\/py\/"/.test(html));
  }
  const b = await chromium.launch();
  const c = await b.newContext();
  const outside = [];
  await c.route('**/*', r => { const u = new URL(r.request().url()); if (['localhost', '127.0.0.1'].includes(u.hostname) || ['data:', 'blob:', 'file:'].includes(u.protocol)) return r.continue(); outside.push(u.href); return r.abort(); });
  const p = await c.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e)));
  await p.goto(B); await p.waitForTimeout(800);
  ok('home page loads from the launcher address', /FDE Study/.test(await p.title()) || /FDE Study/.test(await p.innerText('body')));
  ok('file notice hidden when served', !(await p.isVisible('.file-notice')));
  let t = await play(p, 'Python', 'import sys\nprint(6 * 7, sys.version_info[:2])');
  ok('Python runs: print(6 * 7)', /42 \(3, 12\)/.test(t), t.slice(-300));
  t = await play(p, 'Python', 'import pandas as pd\ndf = pd.DataFrame({"agency": ["DOT", "DEP", "DOT"], "hours": [12, 2, 48]})\nprint(df.groupby("agency")["hours"].mean())');
  ok('pandas runs: groupby mean', /DEP\s+2\.0[\s\S]*DOT\s+30\.0/.test(t), t.slice(-300));
  t = await play(p, 'Python', 'import matplotlib.pyplot as plt\nfig, ax = plt.subplots()\nax.plot([1, 2, 3], [1, 4, 9])\nax.set_title("offline chart")\nplt.show()\nprint("drawn")');
  const fig = await p.evaluate(() => !!document.querySelector('#view .out img, #view .out svg, #view .fig img, #view .fig svg, #view figure img, #view figure svg'));
  ok('Matplotlib draws a chart', /drawn/.test(t) && fig, t.slice(-200) + ' fig=' + fig);
  t = await play(p, 'Python', 'import numpy as np, sklearn, scipy\nprint(np.arange(3) @ np.arange(3), sklearn.__version__, scipy.__version__)');
  ok('NumPy, scikit-learn and SciPy import', /\b5 1\.\d/.test(t), t.slice(-200));
  t = await play(p, 'SQL', "CREATE TABLE r (agency TEXT, hours REAL);\nINSERT INTO r VALUES ('DOT', 12), ('DEP', 2), ('DOT', 48);\nSELECT agency, AVG(hours) AS avg_hours FROM r GROUP BY agency ORDER BY agency;");
  ok('SQL runs: grouped average', /avg_hours[\s\S]*DEP[\s\S]*2[\s\S]*DOT[\s\S]*30/.test(t), t.slice(-300));
  // grading through the real buttons
  await p.goto(B + '#/ex/e1'); await p.waitForTimeout(300);
  await p.click('[data-act="solution"]'); const sol = await p.inputValue('#sol-code');
  await p.fill('#code', sol); await p.click('[data-act="run"]'); await p.waitForTimeout(200); await idle(p);
  const r = await p.innerText('#result'); ok('an exercise is graded (model solution passes)', /2 of 2 tests passed|All 2/.test(r), r.split('\n')[0]);
  await p.goto(B + '#/lesson/ph2-l7'); await p.waitForTimeout(500);
  ok('a lesson SQL table shows offline', await p.evaluate(() => document.querySelectorAll('#view table.sql-rows').length) > 5);
  // The only outside request is the optional Google Fonts stylesheet; when it is blocked the page uses system fonts.
  const other = outside.filter(u => !u.startsWith('https://fonts.googleapis.com/') && !u.startsWith('https://fonts.gstatic.com/'));
  ok('nothing but the optional font stylesheet asked for the internet (' + (outside.length - other.length) + ' font request, blocked)', other.length === 0, other.slice(0, 5).join(' '));
  ok('no page errors', errs.length === 0, errs.join('; '));
  // the same file opened straight from disk: lessons readable, a clear message instead of a broken Run
  if (DIR) {
    const f = await c.newPage();
    await f.goto('file://' + path.join(DIR, 'index.html') + '#/playground'); await f.waitForTimeout(800);
    ok('file:// shows the "Opened as a file" notice', await f.isVisible('.file-notice'), await f.innerText('body').then(x => x.slice(0, 200)));
    await f.fill('#code', 'print(1)'); await f.click('[data-act="run"]'); await f.waitForTimeout(1500);
    const st = await f.innerText('#view');
    ok('file:// Run explains how to start it instead of failing silently', /opened straight from a file[\s\S]*Start FDE Study/.test(st), st.slice(-300));
    await f.goto('file://' + path.join(DIR, 'index.html') + '#/lesson/l2'); await f.waitForTimeout(600);
    ok('file:// lessons are still readable', /Values, names and strings/.test(await f.innerText('#view')));
  }
  await b.close();
  console.log(out.join('\n')); console.log(out.filter(x => x.startsWith('FAIL')).length + ' failed of ' + out.length);
})();
