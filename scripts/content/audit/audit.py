import re, json, html as H, csv, sys, collections
import os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from iq import load, text
from feat import *
IDX=sys.argv[1]
OUT=sys.argv[2]
s,Q,_,_=load(IDX)
_m=re.search(r'<script type="application/json" id="ex-newhere">(.*?)</script>',s,re.S)
EXN=json.loads(_m.group(1)) if _m else {}
phases=[]
starts=[m.start() for m in re.finditer(r'<div class="phase-src" data-phase=', s)]
ends=starts[1:]+[s.find('</div>', s.find('<section', starts[-1]) and s.rfind('</section>')) ]
class M:
    def __init__(s2,body): s2.b=body
    def group(s2,i): return s2.b
for a,b in zip(starts,ends):
    m=M(s[a:b])
    meta=json.loads(re.search(r'<script type="application/json" class="phase-meta">(.*?)</script>',m.group(2),re.S).group(1))
    lessons=[]
    for x in re.finditer(r'<section class="lesson-src"([^>]*)>(.*?)</section>', m.group(2), re.S):
        a=dict(re.findall(r'data-([\w-]+)="([^"]*)"',x.group(1))); lessons.append((a['id'],H.unescape(a['title']),x.group(2)))
    exs=[]
    for x in re.finditer(r'<section class="ex-src"([^>]*)>(.*?)</section>', m.group(2), re.S):
        a=dict(re.findall(r'data-([\w-]+)="([^"]*)"',x.group(1)))
        def sc(cls):
            y=re.search(r'<script type="text/[\w-]+" class="%s">(.*?)</script>'%cls,x.group(2),re.S); return H.unescape(y.group(1)) if y else ''
        exs.append(dict(id=a.get('id'),title=a.get('title'),lesson=a.get('lesson'),prompt=x.group(2),solution=sc('solution'),starter=sc('starter'),given=sc('given'),setup=sc('setup'),files=sc('files'),lang='js' if 'text/javascript' in x.group(2) or a.get('lang')=='js' else 'py'))
    phases.append((meta,lessons,exs))
assert phases, 'no phases'
rows=[]; known=set(); firstTaught={}   # feature -> (lesson id, title, phase n)
def record(feats, lid, title, pn):
    for f in feats:
        if f not in firstTaught: firstTaught[f]=(lid,title,pn)
lessonNo={}
for meta,lessons,exs in phases:
    for k,(lid,title,h) in enumerate(lessons,1):
        lessonNo[lid]=(meta['n'],k,title)
        parts=re.split(r'(<h2>.*?</h2>)',h)
        sections=[]; cur=('',parts[0])
        for p in parts[1:]:
            if p.startswith('<h2>'): sections.append(cur); cur=(text(p),'')
            else: cur=(cur[0],cur[1]+p)
        sections.append(cur)
        before=set(known); qorder=0
        for sec,body in sections:
            tf=teach_feats(body); before|=tf
            for q in [q for q in Q.get(lid,[]) if q['after']==sec and not q.get('optional')]:
                qorder+=1
                names=defined_names(q['solution'])|defined_names(q.get('starter',''))|set().union(*[defined_names(v) for v in (q.get('files') or {}).values()] or [set()])
                req=strip_defined((py_feats(q['solution']) or set())-(py_feats(q.get('starter','')) or set())-TRIVIAL, names)
                inprompt=prose_mentions(q['prompt'])|teach_feats(q['prompt'])
                bf=prose_mentions(q.get('before',''))|teach_feats(q.get('before',''))
                miss=sorted(req-before-bf)
                before|=bf   # a note shown on this question also covers later questions in the lesson
                rows.append(dict(phase=meta['n'],lesson=lid,lesson_title=title,qid=q['id'],kind='inline',title=q['title'],section=sec,
                   missing=[m for m in miss],named_in_prompt=[m for m in miss if m in inprompt],
                   earlier=[(m,firstTaught[m]) for m in miss if m in firstTaught]))
        # questions whose heading no longer exists
        heads=[x for x,_ in sections]
        for q in Q.get(lid,[]):
            if q.get('optional'):
                names=defined_names(q['solution'])|defined_names(q.get('starter',''))
                req=strip_defined((py_feats(q['solution']) or set())-(py_feats(q.get('starter','')) or set())-TRIVIAL, names)
                bf=prose_mentions(q.get('before',''))|teach_feats(q.get('before',''))
                miss=sorted(req-before-bf)
                before|=bf
                rows.append(dict(phase=meta['n'],lesson=lid,lesson_title=title,qid=q['id'],kind='inline',title=q['title'],section='(optional practice)',missing=miss,named_in_prompt=[],earlier=[(m,firstTaught[m]) for m in miss if m in firstTaught]))
            elif q['after'] not in heads: rows.append(dict(phase=meta['n'],lesson=lid,lesson_title=title,qid=q['id'],kind='inline',title=q['title'],section='(UNPLACED '+q['after']+')',missing=['UNPLACED'],named_in_prompt=[],earlier=[]))
        lessonfeats=before
        for e in [e for e in exs if e['lesson']==lid]:
            if e['lang']!='py': continue
            names=defined_names(e['solution'])|defined_names(e['starter'])|defined_names(e['given'])|defined_names(e.get('setup',''))|defined_names(e.get('files',''))
            req=strip_defined((py_feats(e['solution']) or set())-(py_feats(e['starter']) or set())-(py_feats(e['given']) or set())-TRIVIAL, names)
            inprompt=prose_mentions(e['prompt'])|teach_feats(e['prompt'])
            exn=EXN.get(e['id'],'')
            bf=prose_mentions(exn)|teach_feats(exn)
            miss=sorted(req-lessonfeats-bf)
            lessonfeats=lessonfeats|bf
            rows.append(dict(phase=meta['n'],lesson=lid,lesson_title=title,qid=e['id'],kind='exercise',title=e['title'],section='(end of lesson)',missing=miss,named_in_prompt=[m for m in miss if m in inprompt],earlier=[(m,firstTaught[m]) for m in miss if m in firstTaught]))
        record(lessonfeats-known, lid, title, meta['n']); known|=lessonfeats
json.dump(dict(rows=rows,firstTaught=firstTaught,lessonNo=lessonNo),open(OUT,'w'))
c=collections.Counter(); untaught=collections.Counter()
for r in rows:
    un=[m for m in r['missing'] if m not in dict(r['earlier'])]
    r['untaught']=un
    c['questions']+=1; c['with_gap']+= bool(r['missing']); c['untaught_gap']+=bool(un)
    for m in un: untaught[m]+=1
print(dict(c)); print(len(untaught),'distinct never-taught features'); print(untaught.most_common(60))
for r in rows:
    if r['lesson'] in ('l2','l4'): print(r['qid'], r['missing'], '| prompt:',r['named_in_prompt'])
