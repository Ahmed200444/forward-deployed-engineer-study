import ast, re, builtins, html as H
BUILTINS=set(dir(builtins))
TRIVIAL={'builtin:print','syntax:call','syntax:assign','syntax:compare','syntax:arith'}
SQLKW=['SELECT','WHERE','GROUP BY','HAVING','ORDER BY','LIMIT','JOIN','LEFT JOIN','IS NULL','IS NOT NULL','COUNT(','SUM(','AVG(','MIN(','MAX(','DISTINCT','CASE','OVER (','PARTITION BY','WITH ','UNION','INSERT','UPDATE','DELETE','CREATE TABLE','LIKE','BETWEEN','IN (','COALESCE','ROUND(','strftime','julianday','ROW_NUMBER','RANK(','LAG(','LEAD(','EXISTS','SUBSTR','?']
def sql_feats(sqltext):
    f=set(); u=sqltext.upper()
    for k in SQLKW:
        if k=='?':
            if '?' in sqltext: f.add('sql:? parameter')
        elif k.upper() in u: f.add('sql:'+k.strip().rstrip('(').strip())
    return f
import sys as _sys
KNOWN_MODS=set(_sys.stdlib_module_names)|{'numpy','pandas','sklearn','matplotlib','pydantic','yaml','PIL','joblib','pytest','scipy','torch','fastapi','httpx','requests'}
def defined_names(code):
    try: tree=ast.parse(code)
    except Exception: return set()
    out=set()
    for n in ast.walk(tree):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)): out.add(n.name)
        elif isinstance(n,ast.Name) and isinstance(n.ctx,ast.Store): out.add(n.id)
        elif isinstance(n,ast.Attribute) and isinstance(n.ctx,ast.Store): out.add(n.attr)
        elif isinstance(n,ast.ImportFrom) and n.module and n.module.split('.')[0] not in KNOWN_MODS:
            for a in n.names: out.add(a.asname or a.name)
        elif isinstance(n,ast.Import):
            for a in n.names:
                if a.name.split('.')[0] not in KNOWN_MODS: out.add(a.asname or a.name)
    return out
def strip_defined(feats, names):
    out=set()
    for f in feats:
        kind,_,nm=f.partition(':')
        base=nm.lstrip('.').split('.')[0]; last=nm.split('.')[-1]
        if kind in ('func','method') and (base in names or last in names): continue
        if kind=='import' and nm not in KNOWN_MODS: continue
        out.add(f)
    return out
def py_feats(code):
    try: tree=ast.parse(code)
    except Exception: return None
    f=set(); aliases={}
    for n in ast.walk(tree):
        if isinstance(n,(ast.Import,)):
            for a in n.names: f.add('import:'+a.name.split('.')[0]); aliases[a.asname or a.name.split('.')[0]]=a.name
        elif isinstance(n,ast.ImportFrom):
            if n.module: f.add('import:'+n.module.split('.')[0])
            for a in n.names: aliases[a.asname or a.name]=(n.module or '')+'.'+a.name
        elif isinstance(n,ast.Call):
            fn=n.func
            if isinstance(fn,ast.Name):
                if fn.id in BUILTINS: f.add('builtin:'+fn.id)
                elif fn.id in aliases: f.add('func:'+aliases[fn.id].split('.')[-1])
            elif isinstance(fn,ast.Attribute):
                v=fn.value
                if isinstance(v,ast.Name) and v.id in aliases: f.add('func:'+v.id+'.'+fn.attr)
                else: f.add('method:.'+fn.attr)
            for k in n.keywords:
                if k.arg in ('key','reverse','start','encoding','default','sep','end'): f.add('kwarg:'+k.arg+'=')
        elif isinstance(n,ast.FunctionDef): f.add('syntax:def'); 
        elif isinstance(n,ast.Return): f.add('syntax:return')
        elif isinstance(n,ast.For): f.add('syntax:for loop')
        elif isinstance(n,ast.While): f.add('syntax:while loop')
        elif isinstance(n,ast.If): f.add('syntax:if')
        elif isinstance(n,ast.ListComp): f.add('syntax:list comprehension')
        elif isinstance(n,ast.DictComp): f.add('syntax:dict comprehension')
        elif isinstance(n,ast.SetComp): f.add('syntax:set comprehension')
        elif isinstance(n,ast.GeneratorExp): f.add('syntax:generator expression')
        elif isinstance(n,ast.Lambda): f.add('syntax:lambda')
        elif isinstance(n,ast.Try): f.add('syntax:try/except')
        elif isinstance(n,ast.Raise): f.add('syntax:raise')
        elif isinstance(n,ast.With): f.add('syntax:with')
        elif isinstance(n,ast.ClassDef): f.add('syntax:class')
        elif isinstance(n,ast.AugAssign): f.add('syntax:+= (augmented assignment)')
        elif isinstance(n,ast.Yield): f.add('syntax:yield')
        elif isinstance(n,(ast.AsyncFunctionDef,ast.Await)): f.add('syntax:async/await')
        elif isinstance(n,ast.FormattedValue):
            f.add('syntax:f-string')
            if n.format_spec is not None: f.add('syntax:f-string format spec')
        elif isinstance(n,ast.Subscript):
            if isinstance(n.slice,ast.Slice): f.add('syntax:slice')
        elif isinstance(n,ast.BinOp):
            if isinstance(n.op,ast.Mod) and not isinstance(n.left,ast.Constant): f.add('syntax:% (remainder)')
            if isinstance(n.op,ast.FloorDiv): f.add('syntax:// (floor division)')
            if isinstance(n.op,(ast.BitAnd,ast.BitOr)): f.add('syntax:& | (set or bit operators)')
            if isinstance(n.op,ast.MatMult): f.add('syntax:@ (matrix multiply)')
        elif isinstance(n,ast.Compare):
            for o in n.ops:
                if isinstance(o,(ast.In,ast.NotIn)): f.add('syntax:in / not in')
                if isinstance(o,(ast.Is,ast.IsNot)): f.add('syntax:is None')
        elif isinstance(n,ast.Assign):
            for t in n.targets:
                if isinstance(t,ast.Tuple): f.add('syntax:tuple unpacking')
        elif isinstance(n,ast.Dict): f.add('syntax:dict literal')
        elif isinstance(n,ast.Set): f.add('syntax:set literal')
        elif isinstance(n,ast.Constant) and isinstance(n.value,str) and re.search(r'\b(SELECT|INSERT|CREATE TABLE|UPDATE)\b',n.value):
            f|=sql_feats(n.value)
        if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple): f.add('syntax:tuple unpacking')
        if isinstance(n,ast.comprehension) and isinstance(n.target,ast.Tuple): f.add('syntax:tuple unpacking')
        if isinstance(n,ast.arguments) and (n.defaults or n.kw_defaults): f.add('syntax:default argument')
        if isinstance(n,ast.Starred) or (isinstance(n,ast.arguments) and (n.vararg or n.kwarg)): f.add('syntax:*args / unpacking')
    return f
# teaching text: names mentioned in prose <code>..</code>
def prose_mentions(h):
    toks=set()
    for c in re.findall(r'<code>(.*?)</code>', h, re.S):
        c=H.unescape(re.sub(r'<[^>]+>','',c))
        for m in re.findall(r'\.([A-Za-z_]\w*)\s*\(', c): toks.add('method:.'+m)
        for m in re.findall(r'(?<![\w.])([A-Za-z_]\w*)\s*\(', c):
            if m in BUILTINS: toks.add('builtin:'+m)
        for a_,b_ in re.findall(r'(?<![\w.])([A-Za-z_]\w*)\.(\w+)\(', c): toks.add('func:'+a_+'.'+b_)
        for f_ in re.findall(r'\b([A-Z][A-Z_]+)\(', c): toks.add('sql:'+f_)
        if re.fullmatch(r'\.?[A-Za-z_]\w*\(?\)?', c.strip()):
            w=c.strip().strip('.()')
            toks.add('method:.'+w); 
            if w in BUILTINS: toks.add('builtin:'+w)
        f=py_feats(c)
        if f: toks|=f
        toks|=sql_feats(c) if re.search(r'\b(SELECT|WHERE|GROUP BY|HAVING|ORDER BY|JOIN|IS NULL)\b',c) else set()
    return toks
def teach_feats(h):
    """features taught by a block of lesson HTML: code blocks parsed + prose code mentions"""
    f=set()
    for c in re.findall(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', h, re.S):
        code=H.unescape(re.sub(r'<[^>]+>','',c))
        pf=py_feats(code)
        if pf is None:
            pf=set()
            # partial: try line by line
            for line in code.split('\n'):
                g=py_feats(line.strip())
                if g: pf|=g
            pf|=sql_feats(code) if re.search(r'\bSELECT\b',code,re.I) else set()
        f|=pf
    prose=re.sub(r'<pre.*?</pre>','',h,flags=re.S)
    f|=prose_mentions(prose)
    return f
