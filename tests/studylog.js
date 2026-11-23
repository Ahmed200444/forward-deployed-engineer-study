// v31: two tabs finish different lessons on a day with no Study Log entry yet. Both lessons, both log counts and
// both lessonIds must survive reload. Run several rounds with the clicks fired together, with and without the
// other tab's broadcast arriving first.
const { chromium } = require('playwright');
const B='https://localhost:8820/';
const out=[]; const ok=(n,c,i)=>out.push((c?'PASS ':'FAIL ')+n+(i!==undefined&&!c?' — '+String(i).slice(0,300):''));
const today=(()=>{const d=new Date();const p=n=>(n<10?'0':'')+n;return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate());})();
async function ready(p){ await p.waitForFunction(()=>window.__FDE_STORE__ && window.__FDE_STORE__.store.mode!=='starting'); await p.evaluate(()=>window.__FDE_STORE__.store.ready); }
async function open(c, route){ const p=await c.newPage(); p.on('pageerror',e=>out.push('PAGEERROR '+e)); await p.goto(B+'#/'+route); await ready(p); return p; }
async function flush(...ps){ for (const p of ps) await p.evaluate(()=>window.__FDE_STORE__.flush()); await ps[0].waitForTimeout(200); for (const p of ps) await p.evaluate(()=>window.__FDE_STORE__.flush()); }
(async()=>{
  const b=await chromium.launch();
  const cases=[['l5','l6','together'],['ph1-l1','ph1-l2','together'],['l7','l8','no-broadcast'],['ph2-l1','ph2-l2','together, after a lessonIds map exists'],['l2','l3','lessonIds created by both']];
  for (const [la,lb,how] of cases){
    const c=await b.newContext({ignoreHTTPSErrors:true});
    if (how.startsWith('together, after')) await c.addInitScript(t=>{ if(!localStorage.getItem('seeded')){ localStorage.setItem('seeded','1'); localStorage.setItem('ai-study-phase0-v1', JSON.stringify({log:{[t]:{runs:3}}})); } }, today);
    const A=await open(c,'lesson/'+la), Bt=await open(c,'lesson/'+lb);
    if (how==='no-broadcast') for (const p of [A,Bt]) await p.evaluate(()=>{ window.__FDE_STORE__.store.onRemote=null; });
    await Promise.all([A.click('[data-act="read"]'), Bt.click('[data-act="read"]')]);
    await flush(A,Bt);
    const R=await c.newPage(); await R.goto(B+'#/activity'); await ready(R);
    const s=await R.evaluate(()=>window.__FDE_STORE__.state || null) || await R.evaluate(k=>JSON.parse(localStorage.getItem(k)),'ai-study-phase0-v1');
    const st=await R.evaluate(()=>new Promise(res=>{ const r=indexedDB.open('fde-study',1); r.onsuccess=()=>{ const tx=r.result.transaction('kv'); const g=tx.objectStore('kv').get('state'); tx.oncomplete=()=>res(g.result.state); }; }));
    const e=(st.log||{})[today]||{};
    const nm=la+'+'+lb+' ('+how+')';
    ok('SL '+nm+': both lessons marked read', st.lessons[la]===true && st.lessons[lb]===true, JSON.stringify(st.lessons));
    ok('SL '+nm+': both lesson ids in today\'s log', !!(e.lessonIds&&e.lessonIds[la]&&e.lessonIds[lb]), JSON.stringify(e));
    if (how.startsWith('together, after')) ok('SL '+nm+': earlier counter kept', e.runs===3, JSON.stringify(e));
    const txt=await R.innerText('#view'); const shown=(txt.match(/(\d+)\s*\n\s*lessons read/)||[])[1];
    ok('SL '+nm+': Study log page counts 2 lessons read this week', shown==='2', shown);
    // reload both tabs: still there
    await A.reload(); await ready(A);
    ok('SL '+nm+': tab A after reload shows its lesson read', !!(await A.$('[data-act="unread"]')));
    await Bt.reload(); await ready(Bt);
    ok('SL '+nm+': tab B after reload shows its lesson read', !!(await Bt.$('[data-act="unread"]')));
    await c.close();
  }
  // the merge itself: both tabs start from a day with no entry and add counters and lesson ids
  { const c=await b.newContext({ignoreHTTPSErrors:true}); const p=await open(c,'home');
    const r=await p.evaluate(()=>{ const S=window.__FDE_STORE__, base={log:{}};
      const a={log:{d:{quizzes:1,runs:2,lessonIds:{l1:1}}}}, bb={log:{d:{quizzes:1,exercises:1,lessonIds:{l2:1}}}};
      const saved=S.applyOps(S.applyOps(JSON.parse(JSON.stringify(base)), S.diffState(base,a)), S.diffState(base,bb)); return saved.log.d; });
    ok('SL merge: counters added from both tabs with no parent record', r.quizzes===2 && r.runs===2 && r.exercises===1, JSON.stringify(r));
    ok('SL merge: lesson ids merged one by one', r.lessonIds.l1===1 && r.lessonIds.l2===1, JSON.stringify(r));
    await c.close(); }
  await b.close(); console.log(out.join('\n')); console.log(out.filter(x=>!x.startsWith('PASS')).length+' not passing of '+out.length);
})().catch(e=>{ console.log(out.join('\n')); console.error('CRASH',e); process.exit(1); });
