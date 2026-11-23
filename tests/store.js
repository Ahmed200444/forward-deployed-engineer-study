// Progress storage acceptance: two tabs, migration, interrupted migration, unread, restore with a stale tab.
const { chromium } = require('playwright'); const fs=require('fs');
const B='https://localhost:8820/', KEY='ai-study-phase0-v1';
const out=[]; const ok=(n,c,i)=>out.push((c?'PASS ':'FAIL ')+n+(i!==undefined&&!c?' — '+String(i).slice(0,300):''));
const today=(()=>{const d=new Date();const p=n=>(n<10?'0':'')+n;return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate());})();
async function rec(p){ return p.evaluate(()=>new Promise(res=>{ const r=indexedDB.open('fde-study',1); r.onsuccess=()=>{ const db=r.result; if(!db.objectStoreNames.contains('kv')){res(null);return;} const tx=db.transaction('kv'); const a=tx.objectStore('kv').get('state'), b=tx.objectStore('kv').get('legacy-localStorage'); tx.oncomplete=()=>{res({state:a.result,legacy:b.result}); db.close();}; }; r.onerror=()=>res(null); })); }
async function settle(...ps){ for (const p of ps) await p.evaluate(()=>window.__FDE_STORE__.flush()); await ps[0].waitForTimeout(150); for (const p of ps) await p.evaluate(()=>window.__FDE_STORE__.flush()); }
async function ready(p){ await p.waitForFunction(()=>window.__FDE_STORE__ && window.__FDE_STORE__.store.mode!=='starting'); await p.evaluate(()=>window.__FDE_STORE__.store.ready); }
async function open(c, route){ const p=await c.newPage(); p.on('dialog',d=>d.accept()); p.on('pageerror',e=>out.push('PAGEERROR '+e)); await p.goto(B+'#/'+route); await ready(p); return p; }
const FIX = { lessons:{l1:true,l2:true,l3:false}, ex:{e1:true}, quiz:{l1:{best:3,last:2}}, drafts:{e2:'def f():\n    return 2\n', 'q:l2-1':'x = 1\n'}, tried:{e2:true},
  check:{}, review:{'l1:1':{step:1,due:1700000000000}}, notes:{'lesson/l1':{text:'my note',at:1700000000000}}, log:{'2026-11-20':{lessons:2,runs:5}},
  hints:{e2:2}, gh:{repo:'Ahmed200444/ai-engineer-portfolio',items:{}}, qpass:{'q:l2-1':true}, theme:'dark' };
(async()=>{
  const b=await chromium.launch();
  // ---- S1-S4: two tabs from the same state ----
  { const c=await b.newContext({ignoreHTTPSErrors:true});
    const A=await open(c,'lesson/l5'), Bt=await open(c,'lesson/l6');
    await A.click('[data-act="read"]'); await Bt.click('[data-act="read"]'); await settle(A,Bt);
    // drafts and quiz interleaved
    await A.goto(B+'#/ex/e1'); await Bt.goto(B+'#/ex/e2'); await ready(A); await ready(Bt);
    await A.fill('#code','# draft A1\n'); await Bt.fill('#code','# draft B1\n'); await A.fill('#code','# draft A2\n'); await settle(A,Bt);
    for (const [p,q] of [[A,'l1'],[Bt,'l2']]){ await p.goto(B+'#/quiz/'+q); await ready(p); await p.evaluate(()=>document.querySelectorAll('fieldset.q').forEach(f=>f.querySelector('input').checked=true)); await p.click('#quiz-form button[type=submit]'); }
    await settle(A,Bt);
    // B sees A's lesson without reloading (BroadcastChannel)
    await Bt.goto(B+'#/lesson/l5'); await Bt.waitForTimeout(100);
    ok('S4 tab B shows tab A\'s lesson as read without reload', !!(await Bt.$('[data-act="unread"]')));
    await A.reload(); await Bt.reload(); await ready(A); await ready(Bt);
    for (const [nm,p] of [['A',A],['B',Bt]]){
      const st=await p.evaluate(k=>JSON.parse(localStorage.getItem(k)),KEY), r=(await rec(p)).state.state;
      ok('S1 '+nm+': both lessons read after reload', r.lessons.l5===true && r.lessons.l6===true, JSON.stringify(r.lessons));
      ok('S1 '+nm+': study log counts both lessons', r.log[today].lessons===2, JSON.stringify(r.log));
      ok('S2 '+nm+': both drafts kept (A latest, B)', r.drafts.e1==='# draft A2\n' && r.drafts.e2==='# draft B1\n', JSON.stringify(r.drafts));
      ok('S3 '+nm+': both quiz results kept', !!(r.quiz.l1 && r.quiz.l2) && r.log[today].quizzes===2, JSON.stringify(r.quiz)+JSON.stringify(r.log[today]));
      ok('S1 '+nm+': localStorage mirror matches IndexedDB', JSON.stringify(st)===JSON.stringify(r));
    }
    await A.goto(B+'#/lesson/l5'); await ready(A);
    ok('S1 lesson page shows read after reload', !!(await A.$('[data-act="unread"]')));
    // S7 Mark as not read in A, unrelated change in B afterwards must not bring it back
    await A.click('[data-act="unread"]'); await settle(A,Bt);
    await Bt.goto(B+'#/lesson/l7'); await ready(Bt); await Bt.click('[data-act="read"]'); await settle(A,Bt);
    await A.reload(); await ready(A); const r7=(await rec(A)).state.state;
    ok('S7 Mark as not read sticks while another tab saves', r7.lessons.l5===false && r7.lessons.l7===true && r7.lessons.l6===true, JSON.stringify(r7.lessons));
    await c.close(); }
  // ---- S5: migration of pre-upgrade progress in two tabs ----
  { const c=await b.newContext({ignoreHTTPSErrors:true});
    await c.addInitScript(([k,f])=>{ if (!sessionStorage.getItem('seeded') && !localStorage.getItem(k)){ localStorage.setItem(k, JSON.stringify(f)); } sessionStorage.setItem('seeded','1'); }, [KEY, FIX]);
    const A=await open(c,'home'), Bt=await open(c,'review');
    const r=await rec(A);
    const exp=JSON.parse(JSON.stringify(FIX)); exp.check=exp.check||{};
    ok('S5 migrated state equals the pre-upgrade progress', JSON.stringify(r.state.state)===JSON.stringify(Object.assign({},FIX,{})) || ['lessons','ex','quiz','drafts','tried','check','review','notes','log','hints','gh','qpass','theme'].every(k=>JSON.stringify(r.state.state[k])===JSON.stringify(FIX[k])), JSON.stringify(r.state.state).slice(0,300));
    ok('S5 original localStorage text kept as a copy', r.legacy===JSON.stringify(FIX));
    ok('S5 migrated exactly once (rev 1, epoch 1)', r.state.rev===1 && r.state.epoch===1, JSON.stringify({rev:r.state.rev,epoch:r.state.epoch}));
    ok('S5 theme preference applied', await A.evaluate(()=>document.documentElement.getAttribute('data-theme'))==='dark');
    const m1=r.state.migratedAt; await A.reload(); await ready(A); const r2=await rec(A);
    ok('S5 no second migration on reload', r2.state.migratedAt===m1);
    await A.goto(B+'#/ex/e2'); await ready(A);
    ok('S5 code draft shown from migrated data', (await A.inputValue('#code'))===FIX.drafts.e2);
    await A.goto(B+'#/lesson/l1'); await ready(A);
    ok('S5 lesson read state shown', !!(await A.$('[data-act="unread"]')));
    ok('S5 note shown', (await A.inputValue('#notes').catch(()=>''))==='my note');
    await c.close(); }
  // ---- S6: interrupted migration ----
  { const c=await b.newContext({ignoreHTTPSErrors:true});
    await c.addInitScript(([k,f])=>{ if (!localStorage.getItem(k)) localStorage.setItem(k, JSON.stringify(f)); if (!localStorage.getItem('aborted-once')){ localStorage.setItem('aborted-once','1'); window.__STORE_TEST__={abortMigration:true}; } }, [KEY, FIX]);
    const A=await open(c,'home');
    const r=await rec(A);
    ok('S6 interrupted migration wrote nothing to IndexedDB', !r || !r.state, String(JSON.stringify(r&&r.state)).slice(0,100));
    ok('S6 old data untouched in localStorage', await A.evaluate(k=>localStorage.getItem(k),KEY)===JSON.stringify(FIX));
    ok('S6 page fell back to localStorage', await A.evaluate(()=>window.__FDE_STORE__.store.mode)==='local');
    await A.reload(); await ready(A); const r2=await rec(A);
    ok('S6 next load migrates the same data', r2 && r2.state && JSON.stringify(r2.state.state.lessons)===JSON.stringify(FIX.lessons) && r2.legacy===JSON.stringify(FIX), String(JSON.stringify(r2&&r2.state&&r2.state.state)).slice(0,200));
    await c.close(); }
  // ---- S8: restore a version 1 backup while another tab is open; that tab must not write its old snapshot ----
  for (const variant of ['with-broadcast','missed-broadcast']){
    const c=await b.newContext({ignoreHTTPSErrors:true});
    await c.addInitScript(([k,f])=>{ if (!localStorage.getItem(k)) localStorage.setItem(k, JSON.stringify(f)); }, [KEY, FIX]);
    const A=await c.newPage(); A.on('dialog',d=>d.accept());
    if (variant==='missed-broadcast') await A.addInitScript(()=>{ delete window.BroadcastChannel; const add=window.addEventListener.bind(window), dadd=document.addEventListener.bind(document); window.addEventListener=(t,...a)=>t==='storage'?undefined:add(t,...a); document.addEventListener=(t,...a)=>t==='visibilitychange'?undefined:dadd(t,...a); });
    await A.goto(B+'#/lesson/l8'); await ready(A);
    const Bt=await open(c,'backup');
    const R={ lessons:{'ph1-l1':true}, ex:{}, quiz:{}, drafts:{e3:'restored\n'}, tried:{}, check:{}, review:{}, notes:{}, log:{}, hints:{}, gh:{}, qpass:{}, theme:'light' };
    const file=require('os').tmpdir() + '/backup-v1.json'; fs.writeFileSync(file, JSON.stringify({app:'ai-engineer-study',version:1,key:KEY,exportedAt:'2026-11-01T10:00:00.000Z',state:R}));
    await Bt.setInputFiles('#restore-file', file); await Bt.waitForTimeout(300); await settle(Bt);
    // tab A, opened before the restore, now marks its lesson read
    await A.click('[data-act="read"]'); await settle(A); await A.waitForTimeout(200); await settle(A,Bt);
    await Bt.reload(); await ready(Bt); const r=(await rec(Bt)).state;
    const s=r.state;
    ok('S8 '+variant+': restored progress not overwritten by the stale tab', s.lessons['ph1-l1']===true && !s.lessons.l1 && !s.ex.e1 && s.drafts.e3==='restored\n' && !s.drafts.e2 && s.theme==='light', JSON.stringify(s).slice(0,300));
    if (variant==='with-broadcast') ok('S8 with-broadcast: the action taken after the restore is kept', s.lessons.l8===true, JSON.stringify(s.lessons));
    else ok('S8 missed-broadcast: stale tab dropped its change and showed a notice', !s.lessons.l8 && /restored from a backup in another tab/.test(await A.innerText('#view')), JSON.stringify(s.lessons));
    ok('S8 '+variant+': restore started a new epoch', r.epoch===2, r.epoch);
    await A.reload(); await ready(A); await A.goto(B+'#/lesson/ph1-l1'); await ready(A);
    ok('S8 '+variant+': tab A shows the restored progress after reload', !!(await A.$('[data-act="unread"]')));
    await c.close();
  }
  await b.close(); console.log(out.join('\n')); console.log(out.filter(x=>!x.startsWith('PASS')).length+' not passing of '+out.length);
})().catch(e=>{ console.error(out.join('\n')); console.error('CRASH',e); process.exit(1); });
