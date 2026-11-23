#!/usr/bin/env node
// Checks that the Python runtime the site needs is really in the publish directory.
//   node scripts/check-runtime.js              checks the files in py/
//   node scripts/check-runtime.js <site-url>   also checks that a deployed copy serves them (HTTP 200, right type)
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const root = path.join(__dirname, '..'), py = path.join(root, 'py');
const CORE = ['pyodide.js', 'pyodide.asm.js', 'pyodide.asm.wasm', 'python_stdlib.zip', 'pyodide-lock.json'];
const problems = [];
const sha = (f) => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');

const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
if (!/window\.__PY_BASE__="\/py\/"/.test(html)) problems.push('index.html does not load Python from /py/');
for (const f of CORE) if (!fs.existsSync(path.join(py, f))) problems.push('missing py/' + f);
const lock = JSON.parse(fs.readFileSync(path.join(py, 'pyodide-lock.json'), 'utf8'));
if (lock.info.version !== '0.26.4') problems.push('pyodide-lock.json is for Pyodide ' + lock.info.version + ', expected 0.26.4');
const pkgs = Object.values(lock.packages), norm = (s) => s.toLowerCase().replace(/[-_.]+/g, '-');
for (const p of pkgs){
  const f = path.join(py, p.file_name);
  if (!fs.existsSync(f)) problems.push('missing py/' + p.file_name);
  else if (sha(f) !== p.sha256) problems.push('checksum mismatch for py/' + p.file_name);
  for (const d of p.depends || []) if (!pkgs.some(q => norm(q.name) === norm(d))) problems.push(p.name + ' needs ' + d + ', which is not in py/');
}
for (const line of fs.readFileSync(path.join(py, 'SHA256SUMS.txt'), 'utf8').trim().split('\n')){
  const [h, n] = line.split(/\s+/); if (!fs.existsSync(path.join(py, n)) || sha(path.join(py, n)) !== h) problems.push('SHA256SUMS.txt does not match py/' + n);
}
console.log('Pyodide ' + lock.info.version + ', ' + pkgs.length + ' packages, ' + CORE.length + ' core files.');

async function remote(base){
  base = base.replace(/\/?$/, '/');
  const want = { 'pyodide.js': /javascript/, 'pyodide.asm.js': /javascript/, 'pyodide.asm.wasm': /application\/wasm/, 'pyodide-lock.json': /json/, 'python_stdlib.zip': /zip|octet/ };
  const names = CORE.concat(pkgs.map(p => p.file_name));
  for (const n of names){
    const r = await fetch(base + 'py/' + n, { method: 'HEAD' }).catch(e => ({ ok: false, status: String(e) }));
    const type = r.headers ? r.headers.get('content-type') || '' : '';
    if (!r.ok) problems.push(base + 'py/' + n + ' -> ' + r.status);
    else if (/text\/html/.test(type) || (want[n] && !want[n].test(type))) problems.push(base + 'py/' + n + ' served as ' + type);
  }
  console.log('Checked ' + names.length + ' URLs on ' + base);
}
(process.argv[2] ? remote(process.argv[2]) : Promise.resolve()).then(() => {
  if (problems.length){ console.error('FAIL\n- ' + problems.join('\n- ')); process.exit(1); }
  console.log('OK');
});
