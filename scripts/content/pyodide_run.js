// Runs build.py's RUNNER in the bundled Pyodide (py/), so charts are drawn by the same Matplotlib the site uses.
// node pyodide_run.js RUNNER.py SPEC.json   -> prints the runner's JSON line
const path = require('path'), fs = require('fs');
(async () => {
  const PY = path.join(__dirname, '..', '..', 'py') + path.sep;
  const { loadPyodide } = require(path.join(PY, 'pyodide.js'));
  const py = await loadPyodide({ indexURL: PY, stdout: () => {}, stderr: () => {} });
  const runner = fs.readFileSync(process.argv[2], 'utf8');
  const spec = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
  spec.dir = '/home/pyodide/work';
  py.FS.mkdirTree(spec.dir);
  py.FS.writeFile('/tmp/_spec.json', JSON.stringify(spec));
  await py.loadPackage(['matplotlib']);
  await py.loadPackagesFromImports(spec.setup + '\n' + spec.code);
  py.globals.set('__argv', ['_run.py', '/tmp/_spec.json']);
  let captured = '';
  py.setStdout({ batched: s => { captured += s + '\n'; } });
  await py.runPythonAsync('import sys; sys.argv = list(__argv)\n' + runner);
  const lines = captured.trim().split('\n');
  process.stdout.write(lines[lines.length - 1] + '\n');
})().catch(e => { console.error(String(e)); process.exit(1); });
