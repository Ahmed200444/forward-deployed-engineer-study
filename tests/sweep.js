// Runs every coding surface through its visible controls with the reference solution.
// usage: node sweep.js <shard> <nshards> > out.jsonl
const { chromium } = require('playwright');
const B='https://localhost:8820/'; const [shard,n]=[+process.argv[2]||0,+process.argv[3]||1];
function classify(status, result){
  const s=(status||'')+' '+(result||'');
  if (/Could not start Python|Python could not start|did not start within|worker startup/.test(s)) return 'startup';
  if (/libraries this code needs could not be loaded/.test(s)) return 'libload';
  const m=(result||'').match(/(\d+) of (\d+) tests? passed/); if (m) return +m[1]===+m[2]?'pass':'assert';
  if (/All \d+ tests? passed|All \d+ checks? pass/.test(result||'')) return 'pass';
  if (/Traceback|Error|Stopped after/.test(result||'')) return 'error';
  return 'other';
}
async function waitIdle(p, sel){
  await p.waitForFunction(s=>{ const b=document.querySelector(s); return b && !b.disabled; }, sel, {timeout:180000});
}
(async()=>{
  const b=await chromium.launch(); const c=await b.newContext({ignoreHTTPSErrors:true}); const p=await c.newPage();
  p.on('dialog',d=>d.accept());
  await p.goto(B+'#/projects'); await p.waitForTimeout(500);
  const routes=await p.evaluate(()=>{
    const r=[]; document.querySelectorAll('.phase-src').forEach(src=>{
      const ph=JSON.parse(src.querySelector('script.phase-meta').textContent);
      src.querySelectorAll('.lesson-src').forEach(l=>r.push('lesson/'+l.dataset.id));
    });
    document.querySelectorAll('#view a[href^="#/"]').forEach(a=>{ const h=a.getAttribute('href').slice(2); if (h==="project" || /^(projects\/[\w-]+|[\w-]+\/project)$/.test(h)) r.push(h); });
    return [...new Set(r)];
  });
  // exercises: from every phase overview
  const exr=[];
  for (const ph of await p.evaluate(()=>[...document.querySelectorAll('.phase-src')].map(s=>JSON.parse(s.querySelector('script.phase-meta').textContent).id))){
    await p.goto(B+'#/'+ph); await p.waitForTimeout(150);
    for (const h of await p.evaluate(()=>[...document.querySelectorAll('a[href^="#/ex/"]')].map(a=>a.getAttribute('href').slice(2)))) exr.push(h);
  }
  const all=[...new Set([...exr, ...routes])].filter((_,i)=>i%n===shard);
  if (shard===0) console.error('total routes in shard', all.length);
  for (const r of all){
    await p.goto(B+'#/'+r); await p.waitForTimeout(150);
    const isLesson=r.startsWith('lesson/');
    if (!isLesson){
      // worked example
      if (await p.$('[data-act="wex-run"]')){
        await p.click('[data-act="wex-run"]'); await p.waitForTimeout(100); await waitIdle(p,'[data-act="wex-run"]');
        const t=await p.evaluate(()=>{ const box=document.querySelector('[data-act="wex-run"]').closest('section,div.card,div'); return box? box.innerText.slice(-600):''; });
        console.log(JSON.stringify({route:r, kind:'example', cls: /Could not start Python|Python could not start/.test(t)?'startup':/Traceback|Error:/.test(t)?'error':'ran', tail:t.slice(-200)}));
      }
      if (!(await p.$('[data-act="run"]'))) { console.log(JSON.stringify({route:r, kind:'skip', why:'no run button'})); continue; }
      const hasSol=await p.$('[data-act="solution"]');
      if (!hasSol){ console.log(JSON.stringify({route:r, kind:'skip', why:'no solution button'})); continue; }
      await p.click('[data-act="solution"]'); await p.waitForTimeout(50);
      const sol=await p.inputValue('#sol-code').catch(()=>null);
      if (sol==null){ console.log(JSON.stringify({route:r, kind:'skip', why:'no solution editor'})); continue; }
      await p.evaluate(v=>{ const t=document.querySelector('#code'); t.value=v; t.dispatchEvent(new Event('input',{bubbles:true})); }, sol);
      await p.click('[data-act="run"]'); await p.waitForTimeout(100); await waitIdle(p,'[data-act="run"]');
      const res=await p.evaluate(()=>({st:[...document.querySelectorAll('#view .status')].map(x=>x.textContent).join(' | '), res:(document.querySelector('#result')||{}).innerText||''}));
      console.log(JSON.stringify({route:r, kind:r.includes('project')?'project':'exercise', cls:classify(res.st,res.res), head:res.res.split('\n').slice(0,4).join(' / ').slice(0,300), st:res.st.slice(0,300)}));
    } else {
      const boxes=await p.evaluate(()=>[...document.querySelectorAll('textarea[id^="pq-code-"]')].map(t=>t.id.replace('pq-code-','')));
      for (const k of boxes){
        const res=await p.evaluate(async k=>{
          const ta=document.getElementById('pq-code-'+k), sol=document.getElementById('pq-solcode-'+k);
          const box=ta.closest('[data-pq-box], .pq, section, .qbox-wrap') || ta.parentElement.parentElement;
          ta.value=sol.value; ta.dispatchEvent(new Event('input',{bubbles:true}));
          let run=null; let el=ta; while(el && !run){ el=el.parentElement; run=el && el.querySelector('[data-pq="run"]'); }
          run.click(); const t0=Date.now();
          await new Promise(r=>setTimeout(r,80));
          while(run.disabled && Date.now()-t0<180000) await new Promise(r=>setTimeout(r,100));
          return { st:[...el.querySelectorAll('.status')].map(x=>x.textContent).join(' | '), res:[...el.querySelectorAll('.result, [class*="result"]')].map(x=>x.innerText).join('\n') };
        }, k);
        console.log(JSON.stringify({route:r, kind:'inline', q:+k, cls:classify(res.st,res.res), head:res.res.split('\n').slice(0,3).join(' / ').slice(0,300), st:res.st.slice(0,300)}));
      }
      const snips=await p.evaluate(()=>[...document.querySelectorAll('textarea[id^="snip-"]')].map(t=>t.id));
      for (const id of snips){
        const res=await p.evaluate(async id=>{
          const ta=document.getElementById(id); let el=ta, run=null; while(el && !run){ el=el.parentElement; run=el && el.querySelector('[data-act="snip-run"]'); }
          if (!run) return {none:true};
          run.click(); const t0=Date.now(); await new Promise(r=>setTimeout(r,80));
          while(run.disabled && Date.now()-t0<180000) await new Promise(r=>setTimeout(r,100));
          return { st:[...el.querySelectorAll('.status')].map(x=>x.textContent).join(' | '), res:[...el.querySelectorAll('[class*="result"]')].map(x=>x.innerText).join('\n') };
        }, id);
        if (res.none) continue;
        const t=res.st+' '+res.res;
        console.log(JSON.stringify({route:r, kind:'snippet', id, cls:/Could not start Python|Python could not start/.test(t)?'startup':/Traceback|Error:|Stopped after/.test(res.res)?'error':'ran', tail:t.slice(-200)}));
      }
    }
  }
  await b.close();
})().catch(e=>{ console.error('CRASH',e); process.exit(1); });
