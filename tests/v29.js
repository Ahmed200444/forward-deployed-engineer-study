// v29 acceptance: quiz shuffle and grading, Review, Study log distinct lessons, Playground undo clear, search paging and
// return position, backup preview/restore/undo, PowerShell download name, project counts, breadcrumb, phase navigation,
// Continue card, theme switch kept across navigation and reload, local ZIP contents, SQL empty result, checker messages.
// Runs through the visible buttons against tests/server.js.
const { chromium } = require('playwright'); const fs=require('fs'), os=require('os'), path=require('path'), cp=require('child_process');
const B='https://localhost:8820/', KEY='ai-study-phase0-v1', ROOT=path.join(__dirname,'..');
const out=[]; const ok=(n,c,i)=>out.push((c?'PASS ':'FAIL ')+n+(i!==undefined&&!c?' — '+String(i).slice(0,300):''));
const today=(()=>{const d=new Date();const p=n=>(n<10?'0':'')+n;return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate());})();
const TMP=fs.mkdtempSync(path.join(os.tmpdir(),'v29-'));
async function rec(p){ return p.evaluate(()=>new Promise(res=>{ const r=indexedDB.open('fde-study',1); r.onsuccess=()=>{ const db=r.result; if(!db.objectStoreNames.contains('kv')){res(null);return;} const tx=db.transaction('kv'); const a=tx.objectStore('kv').get('state'); tx.oncomplete=()=>{res(a.result); db.close();}; }; r.onerror=()=>res(null); })); }
async function ready(p){ await p.waitForFunction(()=>window.__FDE_STORE__ && window.__FDE_STORE__.store.mode!=='starting'); await p.evaluate(()=>window.__FDE_STORE__.store.ready); }
async function flush(p){ await p.evaluate(()=>window.__FDE_STORE__.flush()); await p.waitForTimeout(200); await p.evaluate(()=>window.__FDE_STORE__.flush()); }
async function st(p){ await flush(p); const r=await rec(p); return r && r.state; }
async function ctx(b, fixture, opts={}){ const c=await b.newContext({ignoreHTTPSErrors:true, acceptDownloads:true, ...opts});
  if (fixture) await c.addInitScript(([k,f])=>{ if (!localStorage.getItem(k) && !sessionStorage.getItem('seeded')){ localStorage.setItem(k, JSON.stringify(f)); sessionStorage.setItem('seeded','1'); } }, [KEY, fixture]);
  return c; }
async function page(c, route){ const p=await c.newPage(); p.on('pageerror',e=>out.push('PAGEERROR '+e)); await p.goto(B+'#/'+route); await ready(p); await p.waitForTimeout(150); return p; }
async function go(p, route){ await p.evaluate(r=>{ location.hash='#/'+r; }, route); await p.waitForTimeout(200); }
async function download(p, click){ const [d]=await Promise.all([p.waitForEvent('download',{timeout:20000}), click()]); const f=path.join(TMP, d.suggestedFilename()); await d.saveAs(f); return { name:d.suggestedFilename(), file:f }; }
function emptyState(extra){ return Object.assign({ lessons:{}, ex:{}, quiz:{}, drafts:{}, tried:{}, check:{}, review:{}, notes:{}, log:{}, hints:{}, gh:{}, qpass:{} }, extra||{}); }

(async()=>{
  const b=await chromium.launch();
  try {
  // ---------- Q: quiz shuffle and grading by choice ID ----------
  { const c=await ctx(b); const p=await page(c,'quiz/l1');
    const qs=await p.evaluate(()=>{ for (const s of document.querySelectorAll('script.quiz-data')){ const q=JSON.parse(s.textContent); if (q.l1) return q.l1; } });
    const orders=[]; let wrongDone=false;
    for (let attempt=0; attempt<4; attempt++){
      const texts=await p.$$eval('#quiz-form fieldset', fss=>fss.map(fs=>[...fs.querySelectorAll('label span')].map(s=>s.textContent)));
      orders.push(JSON.stringify(texts));
      for (let i=0;i<qs.length;i++){
        const want = (!wrongDone && i===0) ? qs[i].o.findIndex((_,j)=>j!==qs[i].a) : qs[i].a;
        await p.check(`#quiz-form input[name="q${i}"][value="${want}"]`);
        const shown=await p.$eval(`#quiz-form input[name="q${i}"][value="${want}"]`, el=>el.parentElement.textContent);
        if (shown!==qs[i].o[want]) ok('Q choice value matches its text', false, shown+' vs '+qs[i].o[want]);
      }
      await p.click('#quiz-form [type="submit"]'); await p.waitForTimeout(100);
      const status=await p.innerText('#quiz-status');
      const exp = (!wrongDone) ? qs.length-1 : qs.length;
      ok('Q attempt '+(attempt+1)+': graded by choice ID ('+exp+' / '+qs.length+')', status.includes('You scored '+exp+' / '+qs.length), status);
      const rightOk=await p.$$eval('#quiz-form fieldset', (fss,qs)=>fss.every((fs,i)=>{ const r=fs.querySelector('label.right'); return r && r.querySelector('span').textContent===qs[i].o[qs[i].a]; }), qs);
      ok('Q attempt '+(attempt+1)+': the marked right answer is the right text', rightOk);
      if (!wrongDone){ const s=await st(p); ok('Q wrong answer goes to Review', !!s.review['l1:0'] && s.quiz.l1.last===qs.length-1, JSON.stringify(s.review)); wrongDone=true; }
      await p.click('#quiz-form [data-act="retry"]'); await p.waitForTimeout(100);
    }
    ok('Q choices are shown in a new order on a new attempt', new Set(orders).size>1, orders.length);
    const s=await st(p); ok('Q best score saved as full marks', s.quiz.l1.best===qs.length, JSON.stringify(s.quiz.l1));
    // questions whose options refer to each other keep the written order
    const dep=await p.evaluate(()=>{ const re=/\b(?:all|none|both|neither) of the (?:above|below)\b/i; for (const sc of document.querySelectorAll('script.quiz-data')){ const q=JSON.parse(sc.textContent); for (const k in q) for (let i=0;i<q[k].length;i++) if (q[k][i].o.some(o=>re.test(o))) return {k,i,o:q[k][i].o}; } return null; });
    if (dep){ let same=true; for (let n=0;n<3;n++){ await go(p,'quiz/'+dep.k); const t=await p.$$eval(`#quiz-form fieldset:nth-of-type(${dep.i+1}) label span`, l=>l.map(x=>x.textContent)); if (JSON.stringify(t)!==JSON.stringify(dep.o)) same=false; await go(p,'home'); }
      ok('Q "all of the above" question keeps its written order', same, dep.k+'#'+dep.i); }
    else ok('Q no order-dependent question found (nothing to check)', true);
    await c.close(); }

  // ---------- R: Review grades by choice ID ----------
  { const c=await ctx(b, emptyState({ review:{ 'l1:1':{ step:0, due:1 } } })); const p=await page(c,'review');
    const q=await p.evaluate(()=>{ for (const s of document.querySelectorAll('script.quiz-data')){ const q=JSON.parse(s.textContent); if (q.l1) return q.l1[1]; } });
    await p.check(`#review-form input[name="r0"][value="${q.a}"]`); await p.click('#review-form [type="submit"]'); await p.waitForTimeout(100);
    const t=await p.innerText('#review-status'); const s=await st(p);
    ok('R review: right answer counted and moved to the 3-day step', /1 of 1 right/.test(t) && s.review['l1:1'].step===1, t+' '+JSON.stringify(s.review));
    await c.close(); }

  // ---------- L: Study log counts distinct lessons ----------
  { const c=await ctx(b, emptyState({ log:{ '2026-11-20':{ lessons:2, runs:5 } } })); const p=await page(c,'lesson/l5');
    await p.click('[data-act="read"]'); await p.click('[data-act="unread"]'); await p.click('[data-act="read"]');
    await go(p,'lesson/l6'); await p.click('[data-act="read"]');
    let s=await st(p); const ids=Object.keys((s.log[today]||{}).lessonIds||{});
    ok('L read, unread, read counts the lesson once', JSON.stringify(ids.sort())==='["l5","l6"]', JSON.stringify(s.log[today]));
    ok('L legacy counter kept', s.log['2026-11-20'] && s.log['2026-11-20'].lessons===2);
    await go(p,'lesson/l6'); await p.click('[data-act="unread"]'); s=await st(p);
    ok('L unread today removes it from today', !((s.log[today].lessonIds||{}).l6), JSON.stringify(s.log[today]));
    await p.reload(); await ready(p); await go(p,'activity'); const txt=await p.innerText('#view');
    ok('L Study log page renders after reload', /Study log/.test(txt));
    await go(p,'backup'); const d=await download(p, ()=>p.click('[data-act="backup"]')); const bk=JSON.parse(fs.readFileSync(d.file,'utf8'));
    ok('L backup keeps the distinct lesson ids', bk.state.log[today] && bk.state.log[today].lessonIds && bk.state.log[today].lessonIds.l5, JSON.stringify(bk.state.log));
    await c.close(); }

  // ---------- P: Playground Clear and Undo clear, per language ----------
  { const c=await ctx(b); const p=await page(c,'playground'); p.on('dialog',d=>d.accept());
    await p.fill('#code','print("python draft")\n'); await p.click('[data-act="clear"]');
    ok('P clear empties the editor and offers Undo', (await p.inputValue('#code'))==='' && await p.isVisible('[data-act="undo-clear"]'));
    await p.reload(); await ready(p); await p.waitForTimeout(150);
    ok('P undo still offered after reload', await p.isVisible('[data-act="undo-clear"]'));
    await p.click('[data-lang="sql"]'); await p.waitForTimeout(150);
    ok('P SQL has its own undo (none yet)', await p.isHidden('[data-act="undo-clear"]'));
    await p.fill('#code','SELECT * FROM requests WHERE 1 = 0;\n'); await p.click('[data-act="run"]');
    await p.waitForSelector('#result .out-head', {timeout:180000});
    const head=await p.innerText('#result .out-head'), cols=await p.$$eval('#result th', l=>l.length);
    ok('P SQL empty result shows "0 rows" and the column headers', /^0 rows$/.test(head.trim()) && cols===6, head+' cols='+cols);
    await p.click('[data-act="clear"]'); await p.click('[data-lang="python"]'); await p.waitForTimeout(150);
    ok('P back in Python, its undo is still offered', await p.isVisible('[data-act="undo-clear"]'));
    await p.fill('#code','x = 1\n'); await p.click('[data-act="undo-clear"]'); await p.waitForTimeout(100);
    ok('P undo (after confirming) brings the Python code back', (await p.inputValue('#code'))==='print("python draft")\n', await p.inputValue('#code'));
    await p.click('[data-lang="sql"]'); await p.waitForTimeout(150); await p.click('[data-act="undo-clear"]'); await p.waitForTimeout(100);
    ok('P SQL undo brings the SQL back', /WHERE 1 = 0/.test(await p.inputValue('#code')));
    await c.close(); }

  // ---------- S: search paging, filters, return position ----------
  { const c=await ctx(b, emptyState({ notes:{ 'lesson/l3':{ text:'zebrafish reminder about retries', at:1700000000000 } } })); const p=await page(c,'search');
    await p.fill('#search-q','data'); await p.waitForTimeout(300);
    const cnt=await p.innerText('#search-count'); const m=cnt.match(/of (\d+) results/); const N=m?+m[1]:0;
    ok('S over 50 results: shows "Showing 1–50 of N"', N>50 && /Showing 1–50 of/.test(cnt), cnt);
    await p.focus('#search-more'); await p.keyboard.press('Enter'); await p.waitForTimeout(100);
    ok('S keyboard "Show more" moves focus to the first new result', await p.evaluate(()=>document.activeElement && document.activeElement.dataset.k)==='50');
    while (await p.isVisible('#search-more')){ await p.click('#search-more'); await p.waitForTimeout(50); }
    ok('S the last result is reachable', (await p.$$eval('#search-results li', l=>l.length))===N && /Showing all/.test(await p.innerText('#search-count')), await p.innerText('#search-count'));
    const href=await p.getAttribute('[data-k="60"]','href'); await p.click('[data-k="60"]'); await p.waitForTimeout(250);
    ok('S result opens its page', (await p.evaluate(()=>location.hash))===href, href);
    await p.goBack(); await p.waitForTimeout(400);
    ok('S Back returns to the same result with focus', await p.evaluate(()=>document.activeElement && document.activeElement.dataset.k)==='60' && (await p.inputValue('#search-q'))==='data');
    await p.click('[data-filter="lesson"]'); await p.waitForTimeout(100);
    const types=await p.$$eval('#search-results .r-type', l=>[...new Set(l.map(x=>x.textContent))]);
    ok('S Lessons filter shows only lessons', types.length===1 && /lesson/i.test(types[0]), JSON.stringify(types));
    await p.click('[data-filter="all"]'); await p.fill('#search-q','zebrafish'); await p.waitForTimeout(250);
    ok('S finds a saved note', /note/i.test(await p.innerText('#search-results')), await p.innerText('#search-results'));
    await c.close(); }

  // ---------- K: backup preview, errors, restore, undo across reload ----------
  { const FIX=emptyState({ lessons:{l1:true,l2:true}, ex:{e1:true}, drafts:{e2:'mine\n'}, theme:'light' });
    const c=await ctx(b, FIX); const p=await page(c,'backup'); p.on('dialog',d=>d.accept());
    const put=async (name, text)=>{ const f=path.join(TMP,name); fs.writeFileSync(f,text); await p.setInputFiles('#restore-file', f); await p.waitForTimeout(250); return p.innerText('#restore-status'); };
    ok('K wrong file type rejected', /not valid JSON/.test(await put('notes.txt','hello there')) && !(await p.$('[data-act="restore-go"]')));
    ok('K malformed JSON rejected', /not valid JSON/.test(await put('bad.json','{"app":"ai-engineer-study",')));
    ok('K other JSON rejected', /not a backup from this site/.test(await put('other.json','{"hello":1}')));
    ok('K unsupported version rejected', /newer version/.test(await put('v99.json',JSON.stringify({app:'ai-engineer-study',version:99,state:emptyState()}))));
    let s=await st(p); ok('K nothing changed after the rejected files', s.lessons.l1===true && s.ex.e1===true);
    const R=emptyState({ lessons:{'ph1-l1':true}, drafts:{e3:'restored\n'}, theme:'light' });
    await put('good.json', JSON.stringify({app:'ai-engineer-study',version:1,key:KEY,exportedAt:'2026-11-01T10:00:00.000Z',state:R}));
    ok('K preview table shown before any change', await p.isVisible('.bk-preview table') && (await st(p)).lessons.l1===true);
    await p.click('[data-act="restore-cancel"]'); ok('K cancel changes nothing', /Cancelled/.test(await p.innerText('#restore-status')) && (await st(p)).lessons.l1===true);
    await put('good.json', JSON.stringify({app:'ai-engineer-study',version:1,key:KEY,exportedAt:'2026-11-01T10:00:00.000Z',state:R}));
    await p.click('[data-act="restore-go"]'); await p.waitForTimeout(400);
    s=await st(p); ok('K restore replaces progress', s.lessons['ph1-l1']===true && !s.lessons.l1 && s.drafts.e3==='restored\n', JSON.stringify(s.lessons));
    await p.reload(); await ready(p); await p.waitForTimeout(300);
    ok('K undo offered after reload', await p.isVisible('#undo-card') && /Undo brings back/.test(await p.innerText('#undo-card')));
    await go(p,'lesson/l8'); await p.click('[data-act="read"]'); await flush(p); await go(p,'backup'); await p.waitForTimeout(300);
    ok('K warns about activity saved since the restore', /since the restore/.test(await p.innerText('#undo-card')), await p.innerText('#undo-card'));
    await p.click('[data-act="undo"]'); await p.waitForTimeout(400);
    s=await st(p); ok('K undo brings back the earlier progress', s.lessons.l1===true && s.ex.e1===true && s.drafts.e2==='mine\n' && !s.lessons['ph1-l1'], JSON.stringify(s.lessons));
    await p.reload(); await ready(p); s=await st(p); ok('K undone progress survives reload', s.lessons.l1===true && s.ex.e1===true);
    await put('good.json', JSON.stringify({app:'ai-engineer-study',version:1,key:KEY,state:R})); await p.click('[data-act="restore-go"]'); await p.waitForTimeout(400);
    await p.click('[data-act="undo-forget"]'); await p.waitForTimeout(300); await p.reload(); await ready(p); await p.waitForTimeout(300);
    ok('K forget removes the undo for good', await p.isHidden('#undo-card'));
    await c.close(); }

  // ---------- D: downloads and counts ----------
  { const c=await ctx(b); const p=await page(c,'lesson/l1');
    const btn=await p.$('[data-act="snip-edit"], [data-act="snip-open"]');
    if (btn) await btn.click(); await p.waitForTimeout(150);
    const d=await download(p, ()=>p.click('[data-act="snip-download"] >> nth=0'));
    ok('D PowerShell block downloads as .ps1', /\.ps1$/.test(d.name), d.name);
    await go(p,'home'); const hero=await p.innerText('.hero-stats');
    ok('D Home shows 28 projects: 18 in browser, 10 local', /28/.test(hero) && /18 in browser · 10 local/.test(hero), hero);
    await go(p,'projects'); const lede=await p.innerText('.lede');
    const g=await p.evaluate(()=>['pf-g-portfolio','pf-g-phase','pf-g-local'].map(id=>{ const h=document.getElementById(id); return h.nextElementSibling.nextElementSibling.querySelectorAll('.pf-card, a.phase-card, .phase-card').length; }));
    ok('D Projects page says 28, 18 and 10, with 6 + 12 + 10 cards', /28 projects: 18 run in your browser/.test(lede) && /10 are larger/.test(lede) && JSON.stringify(g)==='[6,12,10]', lede+' '+JSON.stringify(g));
    // local ZIP equals the exported project
    await go(p,'local/ai-backend'); const z=await download(p, ()=>p.click('[data-act="local-zip"]'));
    const ex=path.join(TMP,'export'); cp.execFileSync('node',[path.join(ROOT,'scripts/export-local-projects.js'), path.join(ROOT,'index.html'), ex, 'ai-backend']);
    const cmp=cp.execFileSync('python3',['-I','-c',`
import zipfile,os,sys,json
z=zipfile.ZipFile(sys.argv[1]); names=[n for n in z.namelist() if not n.endswith('/')]
pre=os.path.commonprefix(names); pre=pre[:pre.rfind('/')+1] if '/' in pre else ''
zf={n[len(pre):]:z.read(n) for n in names}
root=sys.argv[2]; ef={}
for d,_,fs in os.walk(root):
  for f in fs: p=os.path.join(d,f); ef[os.path.relpath(p,root).replace(os.sep,'/')]=open(p,'rb').read()
diff=[k for k in set(zf)|set(ef) if zf.get(k)!=ef.get(k)]
print(json.dumps({'zip':len(zf),'export':len(ef),'diff':sorted(diff)[:10]}))`, z.file, path.join(ex,'ai-backend')]).toString();
    const cr=JSON.parse(cmp); ok('D local ZIP has exactly the exported files and contents', cr.diff.length===0 && cr.zip===cr.export && cr.zip>10, cmp);
    await c.close(); }

  // ---------- N: breadcrumb, phase navigation, Continue card ----------
  { const c=await ctx(b, emptyState({ lessons:{l1:true}, last:'lesson/l2', phase:'ph0' }), {viewport:{width:1440,height:900}}); const p=await page(c,'home');
    const cont=await p.innerText('.continue'); const chref=await p.getAttribute('.continue .btn.primary','href');
    ok('N Continue card is first and points to the next step', /Continue studying/.test(cont) && /Next:/.test(cont) && !!chref && await p.evaluate(()=>{ const v=document.querySelector('#view'); return v.firstElementChild && v.firstElementChild.classList.contains('continue') || v.querySelector('.continue')===v.querySelector('section'); }), cont);
    await p.click('.continue .btn.primary'); await p.waitForTimeout(200);
    ok('N Continue button opens that route', (await p.evaluate(()=>location.hash))===chref);
    await go(p,'ex/e1'); const cr=await p.$$eval('nav.crumbs li', l=>l.map(x=>x.textContent.trim()));
    ok('N breadcrumb on an exercise: All phases / Phase / Lesson / Exercise', cr[0]==='All phases' && /^Phase \d+$/.test(cr[1]) && /^Lesson \d+$/.test(cr[2]) && cr[3]==='Exercise', JSON.stringify(cr));
    await p.click('nav.crumbs li:nth-child(3) a'); await p.waitForTimeout(200);
    ok('N breadcrumb lesson link works', /#\/lesson\//.test(await p.evaluate(()=>location.hash)));
    const np=await p.$$eval('aside details.nav-phase', l=>l.length); ok('N sidebar lists all 12 phases', np===12, np);
    const openCur=await p.$$eval('details.nav-phase[open]', l=>l.length); ok('N the current phase is open', openCur>=1, openCur);
    const closed=await p.$('details.nav-phase:not([open]) > summary'); await closed.click(); await p.waitForTimeout(150);
    ok('N opening another phase lists its pages', await p.evaluate(()=>[...document.querySelectorAll('details.nav-phase[open] .np-body a')].length)>20);
    await c.close(); }

  // ---------- T: theme switch persists across navigation and reload ----------
  for (const scheme of ['light','dark']){
    const c=await ctx(b, null, {colorScheme:scheme, viewport:{width:1440,height:900}}); const p=await page(c,'home');
    const want = scheme==='light' ? 'dark' : 'light';
    ok('T('+scheme+' OS) switch visible at the top of the sidebar', await p.isVisible('.sidebar [data-theme-toggle], aside [data-theme-toggle]') && await p.evaluate(()=>{ const b=document.querySelector('aside [data-theme-toggle]'); return b && b.getBoundingClientRect().top<120; }));
    await p.click('aside [data-theme-toggle]'); await p.waitForTimeout(100);
    const bg=async()=>p.evaluate(()=>{ const c=getComputedStyle(document.body).backgroundColor.match(/\d+/g).map(Number); return (c[0]+c[1]+c[2])/3; });
    const isWant=async()=>{ const t=await p.evaluate(()=>document.documentElement.getAttribute('data-theme')); const l=await bg(); return t===want && (want==='dark' ? l<60 : l>200); };
    let allOk=await isWant(), bad='';
    for (const r of ['ph0','lesson/l1','quiz/l1','ex/e1','projects','local/ai-backend','search','backup','activity','review','playground','ph5','ph5/checkpoint']){
      if (r==='lesson/l1'){ await p.click('nav a[href="#/lesson/l1"] >> nth=0').catch(()=>go(p,r)); await p.waitForTimeout(150); } else await go(p,r);
      if (!(await isWant())){ allOk=false; bad+=r+' '; } }
    ok('T('+scheme+' OS) chosen '+want+' theme stays on 13 pages', allOk, bad);
    await p.reload(); await ready(p); await p.waitForTimeout(200); ok('T('+scheme+' OS) chosen theme survives reload', await isWant());
    const p2=await c.newPage(); await p2.goto(B+'#/ex/e2'); await ready(p2); await p2.waitForTimeout(200);
    ok('T('+scheme+' OS) chosen theme applies in a new tab', (await p2.evaluate(()=>document.documentElement.getAttribute('data-theme')))===want);
    const lbl=await p.getAttribute('aside [data-theme-toggle]','aria-label'); ok('T('+scheme+' OS) switch says what it does', new RegExp(want+' theme is on', 'i').test(lbl), lbl);
    await c.close(); }
  { const c=await ctx(b, null, {viewport:{width:375,height:800}}); const p=await page(c,'lesson/l1');
    await p.click('.mobile-top [data-theme-toggle]'); await p.waitForTimeout(100); await go(p,'ex/e1');
    ok('T mobile switch works and stays after navigation', (await p.evaluate(()=>document.documentElement.getAttribute('data-theme')))==='dark' && await p.isVisible('.mobile-top [data-theme-toggle]'));
    const box=await p.$eval('.mobile-top [data-theme-toggle]', e=>{ const r=e.getBoundingClientRect(); return [r.width,r.height]; }); ok('T mobile switch is at least 44px tall', box[1]>=44, JSON.stringify(box));
    await c.close(); }

  // ---------- C: checker says expected vs got ----------
  { const c=await ctx(b); const p=await page(c,'ex/e1');
    await p.click('[data-act="run"]'); await p.waitForFunction(()=>{ const b=document.querySelector('[data-act="run"]'); return b && !b.disabled && document.querySelector('#result .out'); }, null, {timeout:180000});
    const res=await p.innerText('#result'); const stt=await p.innerText('#run-status');
    ok('C a failing equality check says what was expected and what came back', /expected .+, got /i.test(res) || /passed/.test(res), res.slice(0,300));
    ok('C status line announces the check count', /\d+ of \d+ checks passed|error|took too long/i.test(stt), stt);
    await c.close(); }
  } catch(e){ out.push('CRASH '+(e && e.stack || e)); }
  await b.close(); console.log(out.join('\n')); console.log(out.filter(x=>!x.startsWith('PASS')).length+' not passing of '+out.length);
  process.exit(out.some(x=>!x.startsWith('PASS'))?1:0);
})();
