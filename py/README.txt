Python runtime for the study site
=================================

This folder is Pyodide 0.26.4 (Python 3.12.1), copied unchanged from the official release
https://github.com/pyodide/pyodide/releases/download/0.26.4/pyodide-0.26.4.tar.bz2
(sha256 f6ee209650babf1669f1a9560a5f89f66c0d38aacc2d5b8cd8b4dd6a7537cba9).

Only the core runtime and the packages the course imports are included, with their
dependencies: numpy, pandas, scipy, scikit-learn, matplotlib, pydantic, PyYAML, Pillow,
joblib, pytest and sqlite3. pyodide-lock.json lists exactly the packages in this folder,
so importing anything else gives a normal ModuleNotFoundError instead of a failed download.

index.html loads Python from /py/ (window.__PY_BASE__), in a Web Worker first and in the
page itself as a fallback. Both paths use this folder.

To check a build: node scripts/check-runtime.js  (verifies every file and checksum).
Pyodide is licensed under MPL-2.0; each package keeps its own license.
