// Runtime acceptance: Python + SQL in worker and compatibility modes, wrong vs right answer, startup failure handling.
const { chromium } = require('playwright');
const B='https://localhost:8820/';
const out=[]; const ok=(name,cond,info)=>{ out.push((cond?'PASS ':'FAIL ')+name+(info?' — '+info:'')); };
async function idle(p){ await p.waitForFunction(()=>![...document.querySelectorAll('#view button')].some(b=>b.disabled && /Run/.test(b.textContent)),null,{timeout:180000}); }
async function play(p, lang, code){
  await p.goto(B+'#/playground'); await p.waitForTimeout(300);
  await p.getByRole('button',{name:lang,exact:true}).click();
  await p.fill('#code', code); await p.click('[data-act="run"]'); await p.waitForTimeout(200); await idle(p);
  return p.evaluate(()=>document.querySelector('#view').innerText);
}
(async()=>{
 const b=await chromium.launch();
 for (const mode of ['worker','main']){
  const c=await b.newContext({ignoreHTTPSErrors:true}); await c.addInitScript(m=>{ window.__PY_MODE__=m; }, mode);
  const p=await c.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(String(e)));
  let t=await play(p,'Python','print(6 * 7)');
  ok(mode+': Python print(6 * 7) -> 42', /\n42\n|^42$|\b42\b/.test(t.split('Run')[t.split('Run').length-1]) , JSON.stringify(t.slice(-200)));
  ok(mode+': runtime mode used', await p.evaluate(()=>document.documentElement.dataset.pyMode)===mode, await p.evaluate(()=>document.documentElement.dataset.pyMode));
  t=await play(p,'SQL','SELECT 6 * 7 AS answer;');
  ok(mode+': SQL SELECT 6 * 7 AS answer -> 42', /answer[\s\S]*42/.test(t), JSON.stringify(t.slice(-200)));
  // wrong and right answer on e1 through the real buttons
  await p.goto(B+'#/ex/e1'); await p.waitForTimeout(300);
  await p.fill('#code','def make_greeting(name):\n    return "Hello"\n'); await p.click('[data-act="run"]'); await p.waitForTimeout(200); await idle(p);
  let r=await p.innerText('#result'); ok(mode+': e1 wrong answer fails', /0 of 2 tests passed/.test(r), r.split('\n')[0]);
  await p.click('[data-act="solution"]'); const sol=await p.inputValue('#sol-code');
  await p.fill('#code', sol); await p.click('[data-act="run"]'); await p.waitForTimeout(200); await idle(p);
  r=await p.innerText('#result'); ok(mode+': e1 model solution passes', /2 of 2 tests passed|All 2/.test(r), r.split('\n')[0]);
  ok(mode+': no page errors', errs.length===0, errs.join('; ').slice(0,200));
  await c.close();
 }
 // startup failure: runtime file missing -> deployment message, draft kept, button usable, retry works
 for (const mode of ['worker','main']){
  const c=await b.newContext({ignoreHTTPSErrors:true}); await c.addInitScript(m=>{ window.__PY_MODE__=m; }, mode);
  const p=await c.newPage();
  await c.route('**/py/pyodide.js', r=>r.fulfill({status:404, contentType:'text/html', body:'<h1>Page not found</h1>'}));
  await p.goto(B+'#/ex/e1'); await p.waitForTimeout(300);
  const draft='def make_greeting(name):\n    return "draft-kept"\n';
  await p.fill('#code', draft); await p.waitForTimeout(100); await p.click('[data-act="run"]'); await p.waitForTimeout(300); await idle(p);
  const st=await p.evaluate(()=>[...document.querySelectorAll('#view .status')].map(x=>x.textContent).join(' | '));
  ok(mode+' missing runtime: deployment-specific message', /missing its Python runtime: py\/pyodide\.js returned HTTP 404/.test(st) && !/Check your internet connection/.test(st), st.slice(0,260));
  ok(mode+' missing runtime: Run button enabled again', !(await p.isDisabled('[data-act="run"]')));
  ok(mode+' missing runtime: stage not left running', (await p.evaluate(()=>document.documentElement.dataset.pyStage))!=='running', await p.evaluate(()=>document.documentElement.dataset.pyStage));
  await p.reload(); await p.waitForTimeout(500);
  ok(mode+' missing runtime: draft intact after reload', (await p.inputValue('#code'))===draft);
  await c.unroute('**/py/pyodide.js');
  await p.click('[data-act="run"]'); await p.waitForTimeout(300); await idle(p);
  const r=await p.innerText('#result').catch(()=>''); ok(mode+' retry after the file is back runs the checks', /0 of 2 tests passed/.test(r), r.split('\n')[0]);
  await c.close();
 }
 await b.close(); console.log(out.join('\n')); console.log(out.filter(x=>x.startsWith('FAIL')).length+' failed of '+out.length);
})();
