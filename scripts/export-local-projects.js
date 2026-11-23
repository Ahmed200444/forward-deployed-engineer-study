#!/usr/bin/env node
// Writes each local project exactly as its "Download the project (.zip)" button packs it for a learner with no edits:
// <out>/<id>/<path> for every file in the page's local-projects-data. Used by CI to test what learners download.
// Usage: node scripts/export-local-projects.js [index.html] [out-dir] [id ...]
const fs = require("fs"), path = require("path");
const html = fs.readFileSync(process.argv[2] || path.join(__dirname, "..", "index.html"), "utf8");
const out = process.argv[3] || "local-projects";
const only = process.argv.slice(4);
const m = html.match(/<script type="application\/json" id="local-projects-data">([\s\S]*?)<\/script>/);
if (!m) { console.error("local-projects-data not found"); process.exit(1); }
const projects = JSON.parse(m[1]);
let n = 0;
for (const lp of projects) {
  if (only.length && !only.includes(lp.id)) continue;
  for (const [p, text] of Object.entries(lp.files)) {
    if (p.includes("..") || path.isAbsolute(p)) throw new Error("unsafe path " + p);
    const f = path.join(out, lp.id, p);
    fs.mkdirSync(path.dirname(f), { recursive: true });
    fs.writeFileSync(f, text);
    n++;
  }
  console.log(lp.id + ": " + Object.keys(lp.files).length + " files");
}
console.log(n + " files written to " + out);
