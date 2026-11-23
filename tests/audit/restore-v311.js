const { chromium } = require('playwright'); const fs=require('fs');
const B='https://localhost:8820/', KEY='ai-study-phase0-v1'; const out=[]; const ok=(n,c,i)=>out.push((c?'PASS ':'FAIL ')+n+(!c&&i!==undefined?' — '+String(i).slice(0,400):''));
async function ready(p){ await p.waitForFunction(()=>window.__FDE_STORE__ && window.__FDE_STORE__.store.mode!=='starting'); await p.evaluate(()=>window.__FDE_STORE__.store.ready); }
async function flush(p){ await p.evaluate(()=>window.__FDE_STORE__.flush()); await p.waitForTimeout(200); }
(async()=>{ const b=await chromium.launch();
  // 1. v31.1 session: make progress through the real UI
  const c1=await b.newContext({ignoreHTTPSErrors:true, acceptDownloads:true}); const p=await c1.newPage(); p.on('pageerror',e=>out.push('PAGEERROR v311 '+e));
  await p.goto(B+(process.env.OLD||'v311-tmp.html')+'#/lesson/l1'); await ready(p); await p.click('[data-act="read"]');
  await p.goto(B+(process.env.OLD||'v311-tmp.html')+'#/ex/e1'); await ready(p); await p.fill('#code','# my v31.1 draft\nprint("hi")\n'); await flush(p);
  await p.goto(B+(process.env.OLD||'v311-tmp.html')+'#/quiz/l1'); await ready(p); await p.evaluate(()=>document.querySelectorAll('fieldset.q').forEach(f=>f.querySelector('input').checked=true));
  const sub=await p.$('[data-act="submit-quiz"], button[type="submit"]'); if (sub) await sub.click(); await flush(p);
  const before=await p.evaluate(k=>JSON.parse(localStorage.getItem(k)),KEY);
  ok('v31.1 progress made', before.lessons.l1===true && before.drafts.e1==='# my v31.1 draft\nprint("hi")\n' && !!before.quiz.l1, JSON.stringify(before).slice(0,300));
  await p.goto(B+(process.env.OLD||'v311-tmp.html')+'#/backup'); await ready(p);
  const [dl]=await Promise.all([p.waitForEvent('download'), p.click('[data-act="backup"]')]); const file='/tmp/claude-0/v311-backup.json'; await dl.saveAs(file);
  const bk=JSON.parse(fs.readFileSync(file,'utf8')); ok('backup file written by v31.1', bk.key===KEY && bk.state.drafts.e1, JSON.stringify(bk).slice(0,200));
  // 2. fresh isolated session on v31.2: restore through the UI
  const c2=await b.newContext({ignoreHTTPSErrors:true}); const q=await c2.newPage(); q.on('pageerror',e=>out.push('PAGEERROR v312 '+e)); q.on('dialog',d=>d.accept());
  await q.goto(B+'index.html#/backup'); await ready(q);
  const empty=await q.evaluate(k=>localStorage.getItem(k),KEY); ok('v31.2 session starts empty', !empty || !JSON.parse(empty).lessons.l1, empty&&empty.slice(0,200));
  await q.setInputFiles('#restore-file', file); await q.waitForSelector('[data-act="restore-go"]'); await q.click('[data-act="restore-go"]'); await q.waitForTimeout(400); await flush(q);
  await q.reload(); await ready(q);
  const after=await q.evaluate(k=>JSON.parse(localStorage.getItem(k)),KEY);
  for (const k of ['lessons','ex','quiz','drafts','tried','qpass','notes','review']) ok('restored '+k+' equal', JSON.stringify(after[k]||{})===JSON.stringify(before[k]||{}), JSON.stringify(after[k]));
  await q.goto(B+'index.html#/lesson/l1'); await ready(q); ok('lesson l1 shows read on v31.2', !!(await q.$('[data-act="unread"]')));
  await q.goto(B+'index.html#/ex/e1'); await ready(q); ok('draft in editor on v31.2', (await q.inputValue('#code'))==='# my v31.1 draft\nprint("hi")\n', await q.inputValue('#code'));
  await q.goto(B+'index.html#/quiz/l1'); await ready(q); ok('quiz score shown on v31.2', /best|score|\d+\s*\/\s*\d+/i.test(await q.innerText('#view')));
  console.log(out.join('\n')); await b.close(); })().catch(e=>{console.log(out.join('\n')); console.log('ERR',e); process.exit(1);});
