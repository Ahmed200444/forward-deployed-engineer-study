// Layout: no page-wide horizontal overflow, review panel inside the viewport, both themes, 7 widths; duplicate ids.
const { chromium } = require('playwright');
const B='https://localhost:8820/'; const W=[320,375,390,430,768,1024,1440];
const out=[]; const ok=(n,c,i)=>out.push((c?'PASS ':'FAIL ')+n+(!c&&i!==undefined?' — '+String(i).slice(0,300):''));
(async()=>{
 const b=await chromium.launch();
 for (const theme of ['light','dark']){
  const c=await b.newContext({ignoreHTTPSErrors:true}); await c.addInitScript(t=>{ if(!localStorage.getItem('ai-study-phase0-v1')) localStorage.setItem('ai-study-phase0-v1', JSON.stringify({theme:t})); }, theme);
  const p=await c.newPage(); p.on('dialog',d=>d.accept());
  for (const w of W){
   await p.setViewportSize({width:w,height:800});
   for (const r of ['home','ex/e1','lesson/l5','playground','local/ai-backend','ph3/project','backup']){
     await p.goto(B+'#/'+r); await p.waitForTimeout(200);
     if (r==='local/ai-backend' || r==='ph3/project'){
       await p.click('[data-act="gh-publish"]'); await p.waitForSelector('[data-gh-review]:not([hidden])');
       await p.waitForFunction(()=>!/^Checking/.test(document.querySelector('[data-gh-rv-status]').textContent),null,{timeout:20000});
       await p.selectOption('#gh-rv-repo','Ahmed200444/ai-engineer-portfolio').catch(()=>{}); await p.waitForTimeout(400);
     }
     const m=await p.evaluate(()=>{ const d=document.documentElement; const rv=document.querySelector('[data-gh-review]:not([hidden])'); const rr=rv&&rv.getBoundingClientRect();
       const ids={}; document.querySelectorAll('[id]').forEach(e=>ids[e.id]=(ids[e.id]||0)+1);
       return { sw:d.scrollWidth, cw:d.clientWidth, theme:d.getAttribute('data-theme'), rv: rr?{l:rr.left,r:rr.right}:null, dup:Object.keys(ids).filter(k=>ids[k]>1) }; });
     ok(theme+' '+w+' '+r+': no page overflow', m.sw<=m.cw, m.sw+'>'+m.cw);
     if (m.rv) ok(theme+' '+w+' '+r+': review panel fits', m.rv.l>=0 && m.rv.r<=m.cw+0.5, JSON.stringify(m.rv));
     if (w===390) ok(theme+' '+r+': no duplicate ids', m.dup.length===0, m.dup.join(','));
     if (w===1440 && r==='home') ok(theme+': theme applied', m.theme===theme, m.theme);
     if ((w===390||w===1440) && m.rv) await p.screenshot({path:`${require('os').tmpdir()}/review-${theme}-${w}-${r.replace('/','_')}.png`, fullPage:false, clip: undefined}).catch(()=>{});
   }
  }
  await c.close();
 }
 await b.close(); console.log(out.filter(x=>!x.startsWith('PASS')).join('\n')); console.log(out.filter(x=>!x.startsWith('PASS')).length+' not passing of '+out.length);
})().catch(e=>{ console.log(out.join('\n')); console.error('CRASH',e); process.exit(1); });
