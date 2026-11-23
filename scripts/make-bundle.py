"""Build the downloadable offline copy: python scripts/make-bundle.py OUT_DIR
Writes OUT_DIR/fde-study-offline/ (index.html, py/, launchers, instructions) and OUT_DIR/fde-study-offline.zip."""
import hashlib, os, shutil, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "scripts", "bundle")
out = os.path.abspath(sys.argv[1])
name = "fde-study-offline"
dst = os.path.join(out, name)
if os.path.exists(dst):
    shutil.rmtree(dst)
os.makedirs(dst)
shutil.copy2(os.path.join(ROOT, "index.html"), dst)
shutil.copytree(os.path.join(ROOT, "py"), os.path.join(dst, "py"))
for f, crlf in [("Start FDE Study.cmd", True), ("serve.ps1", True), ("HOW-TO-START.txt", True), ("start.sh", False)]:
    text = open(os.path.join(HERE, f), encoding="utf-8").read().replace("\r\n", "\n")
    if crlf:
        text = text.replace("\n", "\r\n")
    with open(os.path.join(dst, f), "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
os.chmod(os.path.join(dst, "start.sh"), 0o755)

zpath = os.path.join(out, name + ".zip")
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for base, _, files in os.walk(dst):
        for f in sorted(files):
            full = os.path.join(base, f)
            arc = os.path.relpath(full, out).replace(os.sep, "/")
            info = zipfile.ZipInfo.from_file(full, arc)
            if f == "start.sh":
                info.external_attr = (0o100755 << 16)
            # wheels and zips are already compressed
            info.compress_type = zipfile.ZIP_STORED if f.endswith((".whl", ".zip")) else zipfile.ZIP_DEFLATED
            with open(full, "rb") as fh:
                z.writestr(info, fh.read())
h = hashlib.sha256(open(zpath, "rb").read()).hexdigest()
print(zpath, os.path.getsize(zpath), h)
