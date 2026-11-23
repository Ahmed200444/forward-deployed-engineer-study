"""Turn quiz_edits/*.txt (lines 'lesson#index a: text' or 'lesson#index wN: text') into ../quiz_v312.json.
'a' replaces the right answer's text, 'wN' replaces wrong option N. Option order and the keyed answer never change."""
import glob, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
base = open(sys.argv[1], encoding="utf-8").read()
quiz = {}
for m in re.finditer(r'<script type="application/json" class="quiz-data">(.*?)</script>', base, re.S):
    quiz.update(json.loads(m.group(1)))
out = {}
for path in sorted(glob.glob(os.path.join(HERE, "part*.txt"))):
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        m = re.match(r"^(\S+)#(\d+) (a|w\d): (.+)$", line)
        if not m:
            raise SystemExit(f"{path}:{n}: bad line")
        lid, idx, key, text = m.group(1), int(m.group(2)), m.group(3), m.group(4)
        q = quiz[lid][idx]
        e = out.setdefault(lid, {}).setdefault(str(idx), {"check": q["o"][q["a"]][:40], "o": list(q["o"])})
        j = q["a"] if key == "a" else int(key[1:])
        if key != "a" and j == q["a"]:
            raise SystemExit(f"{path}:{n}: w{j} is the right answer")
        e["o"][j] = text
json.dump(out, open(os.path.join(HERE, "..", "quiz_v312.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(sum(len(v) for v in out.values()), "questions edited")
