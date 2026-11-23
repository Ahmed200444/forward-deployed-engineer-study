import re,json
def load(path='/home/user/forward-deployed-engineer-study/index.html'):
    s=open(path).read()
    i=s.index('var INLINE_Q = ')+len('var INLINE_Q = ')
    dec=json.JSONDecoder(); obj,end=dec.raw_decode(s,i)
    return s,obj,i,end
def text(h): return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',h)).strip()
