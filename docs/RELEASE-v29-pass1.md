# v29 pass 1: Python runtime, GitHub publish review, safe progress across tabs

Fixes the three P0 findings of the 23 November 2026 QA audit. Lessons, exercises, routes and the progress
key (`ai-study-phase0-v1`) are unchanged: 161 lessons, 234 exercises, 12 phase projects.

## 1. Python and SQL run again
- Cause: the page loads Python from `/py/`, but that folder was never part of the published site, so every
  start got Netlify's 404 page.
- `py/` now holds Pyodide 0.26.4 (unchanged official files) plus the 33 packages the course imports and their
  dependencies (numpy, pandas, scipy, scikit-learn, matplotlib, pydantic, PyYAML, Pillow, joblib, pytest, sqlite3).
  `py/pyodide-lock.json` lists only those, so other imports fail with a normal `ModuleNotFoundError`.
- Worker and compatibility mode use the same folder. Before starting, the page checks `py/pyodide.js` and
  `py/pyodide-lock.json`; if either is missing it says the deployment is incomplete instead of blaming the
  learner's connection. The draft is kept and Run works again.
- `node scripts/check-runtime.js [site-url]` verifies every runtime file and checksum, locally or on a deployed copy.

## 2. Publish to GitHub asks before writing
- The first click opens **Review before publishing**: GitHub account, repository with Public/Private, branch
  (default, existing or new), project folder (new or existing) and every file as Add, Replace, No change or Keep.
- Warnings for public repositories, the default branch, the existing portfolio and updates; those need a tick.
  **Use a test branch** and a link to create a private repository are offered. Cancel writes nothing.
- Signed-out sign-in returns to the same review screen. The server (`github-preview` + `github-publish`) only
  writes with a signed review for the same account, repository, branch, folder and files, and refuses if the
  branch moved after the review.

## 3. Two tabs no longer overwrite each other
- Saves go through one IndexedDB transaction that applies only this tab's changes to the latest saved state
  (activity counters are added, removals stay removals). Other tabs refresh through BroadcastChannel.
- A restore starts a new epoch: a tab opened before it cannot write its old snapshot back.
- First run copies the existing localStorage progress into IndexedDB in one transaction, together with the
  original text; the localStorage copy is kept as a mirror. An interrupted upgrade leaves it untouched and runs again.
- Version 1 backups restore as before.

Tests: see `tests/README.md`.
