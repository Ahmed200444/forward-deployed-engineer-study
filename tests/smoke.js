// Final-build smoke: one model solution per phase + every phase project, in compatibility (main-thread) mode,
// and a JavaScript task with a wrong and a right answer. Runs through the visible buttons.
const { chromium } = require('playwright');
const B='https://localhost:8820/';
const out=[]; const ok=(n,c,i)=>out.push((c?'PASS ':'FAIL ')+n+(!c&&i!==undefined?' — '+String(i).slice(0,300):''));
async function idle(p){ await p.waitForFunction(()=>{ const b=document.querySelector('[data-act="run"]'); return b && !b.disabled; },null,{timeout:180000}); }
(async()=>{
 const b=await chromium.launch(); const c=await b.newContext({ignoreHTTPSErrors:true}); await c.addInitScript(()=>{ window.__PY_MODE__='main'; });
 const p=await c.newPage(); p.on('dialog',d=>d.accept());
 await p.goto(B+'#/home'); await p.waitForTimeout(300);
 const phases=await p.evaluate(()=>[...document.querySelectorAll('.phase-src')].map(s=>JSON.parse(s.querySelector('script.phase-meta').textContent).id));
 const routes=[];
 for (const ph of phases){ await p.goto(B+'#/'+ph); await p.waitForTimeout(100);
   const ex=await p.evaluate(()=>{ const a=document.querySelector('a[href^="#/ex/"]'); return a&&a.getAttribute('href').slice(2); }); if (ex) routes.push(ex);
   const pr=await p.evaluate(()=>{ const a=[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href').slice(2)).find(h=>h==='project'||/^[\w-]+\/project$/.test(h)); return a; }); if (pr) routes.push(pr); }
 for (const r of [...new Set(routes)]){
   await p.goto(B+'#/'+r); await p.waitForTimeout(100);
   await p.click('[data-act="solution"]'); const sol=await p.inputValue('#sol-code');
   await p.evaluate(v=>{ const t=document.querySelector('#code'); t.value=v; t.dispatchEvent(new Event('input',{bubbles:true})); }, sol);
   await p.click('[data-act="run"]'); await p.waitForTimeout(100); await idle(p);
   const res=await p.innerText('#result'); ok('main mode '+r+' model solution passes', /^All \d+ tests? passed/.test(res), res.split('\n')[0]);
 }
 ok('ran in compatibility mode', await p.evaluate(()=>document.documentElement.dataset.pyMode)==='main');
 // JavaScript task: wrong then right
 await p.goto(B+'#/ex/fde-e12'); await p.waitForTimeout(200);
 await p.fill('#code','// wrong on purpose\n'); await p.click('[data-act="run"]'); await p.waitForTimeout(100); await idle(p);
 let res=await p.innerText('#result'); ok('JS fde-e12 wrong answer fails', /^0 of \d+ tests passed/.test(res), res.split('\n')[0]);
 await p.click('[data-act="solution"]'); const sol=await p.inputValue('#sol-code'); await p.fill('#code', sol); await p.click('[data-act="run"]'); await p.waitForTimeout(100); await idle(p);
 res=await p.innerText('#result'); ok('JS fde-e12 model solution passes', /^All \d+ tests? passed/.test(res), res.split('\n')[0]);
 await b.close(); console.log(out.join('\n')); console.log(out.filter(x=>!x.startsWith('PASS')).length+' not passing of '+out.length);
})().catch(e=>{ console.log(out.join('\n')); console.error('CRASH',e); process.exit(1); });
