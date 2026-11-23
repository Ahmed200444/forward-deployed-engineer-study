// Audit: mobile navigation and editor controls with touch emulation at 320/375/390/430/768.
// For each width: Course contents opens and navigates; an inline question and an exercise can be edited by typing,
// run and graded with taps; Run/Show solution/Reset/Hint buttons are fully on screen and at least 40px tall;
// the page never scrolls sideways; the playground runs and switches language.
const { chromium } = require('playwright');
const B = process.env.B || 'https://localhost:8820/';
const out = []; const ok = (n, c, i) => out.push((c ? 'PASS ' : 'FAIL ') + n + (!c && i !== undefined ? ' — ' + String(i).slice(0, 300) : ''));
async function idle(p, sel) { await p.waitForFunction(s => { const b = document.querySelector(s); return b && !b.disabled; }, sel, { timeout: 120000 }); }
(async () => {
  const b = await chromium.launch();
  for (const w of [320, 375, 390, 430, 768]) {
    const c = await b.newContext({ ignoreHTTPSErrors: true, viewport: { width: w, height: 800 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
    const p = await c.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e))); p.on('dialog', d => d.accept());
    const T = n => `${w}px ${n}`;
    const noSide = async () => p.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1);
    await p.goto(B + '#/ph0'); await p.waitForTimeout(500);
    // Course contents
    const det = await p.$('#mobile-details summary');
    ok(T('Course contents control exists'), !!det);
    if (det) {
      await p.tap('#mobile-details summary'); await p.waitForTimeout(250);
      const links = await p.evaluate(() => [...document.querySelectorAll('#mobile-details[open] a[href^="#/lesson/"]')].filter(a => a.getBoundingClientRect().width > 0).length);
      ok(T('Course contents lists lessons when opened (' + links + ')'), links >= 5, links);
      const target = await p.$('#mobile-details[open] a[href="#/lesson/l3"]');
      if (target) { await target.tap(); await p.waitForTimeout(500); ok(T('tapping a lesson in Course contents opens it'), /Functions/.test(await p.innerText('#view h1'))); }
      else ok(T('lesson link in Course contents'), false, 'no link');
    }
    ok(T('lesson page does not scroll sideways'), await noSide());
    // inline question: type and run
    await p.goto(B + '#/lesson/l3'); await p.waitForTimeout(500);
    const ta = '#pq-code-1';
    const box = await p.evaluate(() => { const r = [...document.querySelectorAll('#pq-1 .btn-row button, #pq-1 summary')].map(b => { const q = b.getBoundingClientRect(); return { t: b.textContent.trim().slice(0, 20), x: q.x, r: q.right, h: q.height, w: q.width }; }); return r; });
    ok(T('question buttons fit on screen (' + box.map(x => x.t).join(', ') + ')'), box.length >= 3 && box.every(x => x.x >= -1 && x.r <= w + 1), JSON.stringify(box));
    ok(T('visible question buttons are at least 40px tall'), box.filter(x => x.h > 0).every(x => x.h >= 40), JSON.stringify(box.filter(x => x.h > 0 && x.h < 40)));
    await p.tap(ta); await p.keyboard.press('Control+A'); await p.keyboard.type('def double(n):\n    return n * 2\n\nprint(double(4))\n');
    ok(T('typing in the editor changes it'), /double/.test(await p.inputValue(ta)));
    await p.tap('#pq-1 [data-pq="run"]'); await p.waitForTimeout(200); await p.waitForFunction(() => !document.querySelector('#pq-1 [data-pq="run"]').disabled, null, { timeout: 120000 }); await p.waitForTimeout(300);
    const res = await p.innerText('#pq-1 [data-pq-result]');
    ok(T('tap on Run shows a graded result'), /tests? passed/.test(res), res.slice(0, 100));
    await p.tap('#pq-1 summary'); await p.waitForTimeout(150);
    ok(T('hint opens by tap'), await p.evaluate(() => document.querySelector('#pq-1 .pq-hint').open));
    await p.tap('#pq-1 [data-pq="sol"]'); await p.waitForTimeout(250);
    ok(T('Show solution reveals the solution'), await p.evaluate(() => !document.querySelector('#pq-sol-1').hidden));
    ok(T('question page does not scroll sideways'), await noSide());
    // exercise page
    await p.goto(B + '#/ex/e1'); await p.waitForTimeout(500);
    const eb = await p.evaluate(() => [...document.querySelectorAll('[data-act="run"],[data-act="solution"],[data-act="reset"],[data-act="hint"],[data-act="wex-run"]')].map(b => { const q = b.getBoundingClientRect(); return { t: b.textContent.trim().slice(0, 18), x: q.x, r: q.right, h: q.height }; }));
    ok(T('exercise buttons fit and are 40px tall (' + eb.map(x => x.t).join(', ') + ')'), eb.length >= 3 && eb.every(x => x.x >= -1 && x.r <= w + 1 && x.h >= 40), JSON.stringify(eb.filter(x => x.x < -1 || x.r > w + 1 || x.h < 40)));
    await p.tap('#code'); await p.keyboard.press('Control+A'); await p.keyboard.type('def x(): pass');
    await p.tap('[data-act="run"]'); await p.waitForTimeout(200); await idle(p, '[data-act="run"]');
    ok(T('exercise: wrong code shows failed tests by tap'), /\d+ of \d+ tests? passed|error/.test(await p.innerText('#result')));
    ok(T('exercise page does not scroll sideways'), await noSide());
    // long code scrolls inside, not the page
    await p.goto(B + '#/lesson/ph3-l2'); await p.waitForTimeout(600);
    ok(T('lesson with tables/charts does not scroll sideways'), await noSide());
    // playground
    await p.goto(B + '#/playground'); await p.waitForTimeout(400);
    await p.tap('#code'); await p.keyboard.press('Control+A'); await p.keyboard.type('print(6*7)');
    await p.tap('[data-act="run"]'); await p.waitForTimeout(200); await idle(p, '[data-act="run"]');
    ok(T('playground runs on touch'), /42/.test(await p.innerText('#view')));
    const lang = await p.$('button:text-is("SQL")'); ok(T('playground language buttons visible'), !!lang && (await lang.boundingBox()).x + (await lang.boundingBox()).width <= w + 1);
    ok(T('no page errors'), errs.length === 0, errs.join(';'));
    await c.close();
  }
  await b.close();
  console.log(out.join('\n')); console.log(out.filter(x => x.startsWith('FAIL')).length + ' failed of ' + out.length);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
