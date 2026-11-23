// GitHub publish acceptance against the local mock of GitHub (no real repository is touched).
const { chromium } = require('playwright');
const B='https://localhost:8820/';
const out=[]; const ok=(n,c,i)=>out.push((c?'PASS ':'FAIL ')+n+(!c&&i!==undefined?' — '+String(i).slice(0,300):''));
const gh=async()=> (await fetch(B+'__test/gh')).json();
const commits=async()=> (await gh()).log.filter(x=>x.op==='commit');
process.env.NODE_TLS_REJECT_UNAUTHORIZED='0';
async function rvIdle(p){ await p.waitForFunction(()=>{ const s=document.querySelector('[data-gh-rv-status]'); return s && !/^Checking/.test(s.textContent); }, null, {timeout:20000}); }
(async()=>{
  await fetch(B+'__test/reset');
  const b=await chromium.launch();
  const c=await b.newContext({ignoreHTTPSErrors:true}); const p=await c.newPage(); p.on('dialog',d=>d.accept()); p.on('pageerror',e=>out.push('PAGEERROR '+e));
  // P1 signed out -> sign in -> review screen, nothing written
  await p.goto(B+'#/local/ai-backend'); await p.waitForSelector('[data-act="gh-publish"]:visible');
  await p.click('[data-act="gh-publish"]');
  await p.waitForURL(/github=connected|#\/local\/ai-backend/); await p.waitForSelector('[data-gh-review]:not([hidden])', {timeout:20000}); await rvIdle(p);
  ok('P1 signed-out: sign-in returns to the review screen', await p.isVisible('[data-gh-review]'));
  ok('P1 signed-out: still on the same project', /#\/local\/ai-backend$/.test(p.url()), p.url());
  ok('P1 signed-out: zero commits after sign-in', (await commits()).length===0);
  const facts=await p.innerText('[data-gh-rv-facts]');
  ok('P1 review shows account, repo, visibility, branch, folder', /Ahmed200444/.test(facts) && /ai-engineer-portfolio/.test(facts) && /Public/.test(facts) && /main/.test(facts) && /Project folder/.test(facts), facts);
  ok('P1 public portfolio: warning shown', /is public/.test(await p.innerText('[data-gh-rv-warn]')) && /existing portfolio/.test(await p.innerText('[data-gh-rv-warn]')));
  ok('P1 public portfolio: Publish now disabled until confirmed', await p.isDisabled('[data-act="gh-confirm"]'));
  const nfiles=await p.$$eval('[data-gh-rv-files] li',l=>l.length);
  ok('P1 file list shown', nfiles>=10, nfiles);
  await p.click('[data-act="gh-cancel"]');
  ok('P1 cancel hides review and says nothing was published', !(await p.isVisible('[data-gh-review]')) && /Nothing was published/.test(await p.innerText('#gh-status')));
  ok('P1 zero commits after cancel', (await commits()).length===0);
  // P2 signed in: first click opens review, cancel, zero commits
  await p.reload(); await p.waitForSelector('[data-act="gh-publish"]:visible'); await p.waitForTimeout(300);
  await p.click('[data-act="gh-publish"]'); await rvIdle(p);
  ok('P2 signed-in: first click opens the review, no write', await p.isVisible('[data-gh-review]') && (await commits()).length===0);
  await p.click('[data-act="gh-cancel"]'); ok('P2 signed-in: zero commits after cancel', (await commits()).length===0);
  // P3 publish to a private disposable repository
  await p.click('[data-act="gh-publish"]'); await rvIdle(p);
  await p.selectOption('#gh-rv-repo','Ahmed200444/fde-publish-test'); await rvIdle(p);
  const f3=await p.innerText('[data-gh-rv-facts]');
  ok('P3 private repo shows Private', /fde-publish-test/.test(f3) && /Private/.test(f3), f3);
  ok('P3 new folder on private repo needs no extra tick', await p.isHidden('[data-gh-rv-ack]') && !(await p.isDisabled('[data-act="gh-confirm"]')));
  const listed=await p.$$eval('[data-gh-rv-files] li code',l=>l.map(x=>x.textContent));
  await p.click('[data-act="gh-confirm"]'); await p.waitForFunction(()=>/Published|already has/.test(document.querySelector('#gh-status').textContent), null, {timeout:20000});
  const g3=await gh(), r3=g3.repos['ahmed200444/fde-publish-test'], c3=await commits();
  const tree3=r3.trees[r3.commits[r3.branches.main].tree];
  ok('P3 exactly one commit, in the private test repo', c3.length===1 && c3[0].repo==='Ahmed200444/fde-publish-test', JSON.stringify(c3));
  ok('P3 committed files are exactly the reviewed list', JSON.stringify(Object.keys(tree3).filter(x=>x!=='README.md').sort())===JSON.stringify(listed.slice().sort()), JSON.stringify(Object.keys(tree3)));
  ok('P3 portfolio untouched', g3.repos['ahmed200444/ai-engineer-portfolio'].branches.main && Object.keys(g3.repos['ahmed200444/ai-engineer-portfolio'].commits).length===1);
  const st3=await p.innerText('[data-gh-state]'); ok('P3 page links the published folder', /Published/.test(st3) && /fde-publish-test/.test(st3), st3);
  // P4 re-publish after changing one file: review shows Replace / No change, needs a tick
  const ta=await p.$('textarea.local-edit'); const tid=await ta.getAttribute('id');
  await p.evaluate(id=>{ const t=document.getElementById(id); t.value=t.value+'\n# changed for the update test\n'; t.dispatchEvent(new Event('input',{bubbles:true})); }, tid);
  await p.click('[data-act="gh-publish"]'); await rvIdle(p);
  const acts=await p.$$eval('[data-gh-rv-files] li .gh-act',l=>l.map(x=>x.textContent));
  ok('P4 update preview: one Replace, rest No change', acts.filter(a=>a==='Replace').length>=1 && acts.filter(a=>a==='No change').length>=5, JSON.stringify(acts));
  ok('P4 update needs explicit tick', await p.isVisible('[data-gh-rv-ack]') && await p.isDisabled('[data-act="gh-confirm"]'));
  await p.check('#gh-rv-ack'); await p.click('[data-act="gh-confirm"]'); await p.waitForFunction(()=>/Published/.test(document.querySelector('#gh-status').textContent), null, {timeout:20000});
  const c4=await commits(); ok('P4 one more commit for the update', c4.length===2 && c4[1].repo==='Ahmed200444/fde-publish-test', JSON.stringify(c4));
  // P5 branch moved after the review -> refused, re-reviewed, no commit from us
  await p.evaluate(id=>{ const t=document.getElementById(id); t.value=t.value+'# second change\n'; t.dispatchEvent(new Event('input',{bubbles:true})); }, tid);
  await p.click('[data-act="gh-publish"]'); await rvIdle(p);
  await fetch(B+'__test/move?repo=Ahmed200444/fde-publish-test');
  await p.check('#gh-rv-ack'); await p.click('[data-act="gh-confirm"]'); await p.waitForTimeout(800); await rvIdle(p);
  const c5=await commits(); ok('P5 moved branch: publish refused, nothing written', c5.length===2, JSON.stringify(c5));
  ok('P5 moved branch: page re-checked and explains', /changed on GitHub after you reviewed/.test(await p.innerText('[data-gh-rv-status]')), await p.innerText('[data-gh-rv-status]'));
  await p.click('[data-act="gh-cancel"]');
  // P6 publish request without a review token is refused by the server
  const r6=await p.evaluate(async()=>{ const s=await (await fetch('/api/github/status')).json(); const r=await fetch('/api/github/publish',{method:'POST',headers:{'Content-Type':'application/json','X-FDE-CSRF':s.csrf},body:JSON.stringify({repository:'Ahmed200444/ai-engineer-portfolio',folder:'projects/x',files:{'README.md':'# x','a.py':'print(1)'}})}); return {s:r.status, d:await r.json()}; });
  ok('P6 server refuses a write with no review (428)', r6.s===428 && (await commits()).length===2, JSON.stringify(r6));
  // P7 test branch on the public portfolio: main stays untouched
  await p.click('[data-act="gh-publish"]'); await rvIdle(p);
  await p.selectOption('#gh-rv-repo','Ahmed200444/ai-engineer-portfolio'); await rvIdle(p);
  await p.click('[data-act="gh-rv-testbranch"]'); await rvIdle(p);
  ok('P7 test branch shown as new', /new: it will be created/.test(await p.innerText('[data-gh-rv-facts]')), await p.innerText('[data-gh-rv-facts]'));
  await p.check('#gh-rv-ack'); await p.click('[data-act="gh-confirm"]'); await p.waitForFunction(()=>/Published/.test(document.querySelector('#gh-status').textContent), null, {timeout:20000});
  const g7=await gh(), pr=g7.repos['ahmed200444/ai-engineer-portfolio'];
  ok('P7 commit went to the test branch, main unchanged', Object.keys(pr.branches).length===2 && Object.keys(pr.commits).length===2 && pr.commits[pr.branches.main].message==='init', JSON.stringify(pr.branches));
  // P8 empty repository: first commit
  await p.click('[data-act="gh-publish"]'); await rvIdle(p);
  await p.selectOption('#gh-rv-repo','Ahmed200444/empty-test'); await p.fill('#gh-rv-branch',''); await p.click('[data-act="gh-rv-check"]'); await rvIdle(p);
  ok('P8 empty repo explained', /empty/.test(await p.innerText('[data-gh-rv-facts]')), await p.innerText('[data-gh-rv-facts]'));
  await p.click('[data-act="gh-confirm"]'); await p.waitForFunction(()=>/Published/.test(document.querySelector('#gh-status').textContent), null, {timeout:20000});
  const e8=(await gh()).repos['ahmed200444/empty-test']; ok('P8 empty repo got the files', Object.keys(e8.trees[e8.commits[e8.branches.main].tree]).length>=10);
  // P9 exercise-style project (phase project) opens the same review
  await p.goto(B+'#/ph3/project'); await p.waitForSelector('[data-act="gh-publish"]:visible'); const before=(await commits()).length;
  await p.click('[data-act="gh-publish"]'); await rvIdle(p);
  ok('P9 phase project: review opens, nothing written', await p.isVisible('[data-gh-review]') && (await commits()).length===before);
  await p.click('[data-act="gh-cancel"]');
  await b.close(); console.log(out.join('\n')); console.log(out.filter(x=>!x.startsWith('PASS')).length+' not passing of '+out.length);
})().catch(e=>{ console.log(out.join('\n')); console.error('CRASH',e); process.exit(1); });
