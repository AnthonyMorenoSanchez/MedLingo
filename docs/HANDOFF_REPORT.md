# MedLingo handoff report

Build date: 2026-09-13

Commit: archive delivery, no external repository commit or publication.

Status: executable local application; automated verification passes. This does **not** certify complete conformity to every requirement in the supplied specification. See the explicit differences in DECISIONS.md.

## Contents and launch

The archive includes the Python backend, React/TypeScript frontend, source snapshots, curated YAML, built frontend, seed database, tests, documentation, and browser screenshots. It excludes user progress, provider keys, node_modules, and the Python virtual environment.

```bash
make setup
make run
```

Open http://localhost:8000. Windows uses WSL. Installation downloads dependencies; default runtime uses local data and device speech.

## Source ingestion

Network available during ingest: **yes**, except the DeCS endpoint returned HTTP 403.

Sources: Wikidata snapshots captured/refreshed 2026-09-13; MedlinePlus health-topic XML 2026-09-12; Wiktionary 300 real lookups with 186 parsed gender entries; MedLingo authored YAML 0.1. DeCS contains zero descriptors and is explicitly marked unavailable. Attribution, source URLs, raw revisions, and licenses are included in ATTRIBUTION.md and fixtures/PROVENANCE.json.

Bank counts: **7,175 unique terms, 14,008 sentences, 12 encounters**. Noun gender coverage: **86.14%**. Online and offline count checks pass. The raw-source and curated-material requirements that remain unmet are listed below and in DECISIONS.md.

| Specialty | Terms | Sentences | Encounters |
|---|---:|---:|---:|
| general_medicine | 4829 | 614 | 1 |
| urology | 248 | 1106 | 1 |
| hematology | 268 | 1298 | 1 |
| cardiology | 659 | 1260 | 1 |
| pulmonology | 207 | 890 | 1 |
| gastroenterology | 247 | 1286 | 1 |
| neurology | 511 | 1168 | 1 |
| obgyn | 204 | 794 | 1 |
| pediatrics | 347 | 1094 | 1 |
| emergency | 242 | 902 | 1 |
| orthopedics | 388 | 1186 | 1 |
| psychiatry | 292 | 1190 | 1 |
| anatomy | 1999 | 1110 | 0 |
| patient_phrases | 1540 | 110 | 0 |

## Bank threshold checks

| Threshold | Result |
|---|---|
| total terms | PASS |
| sentences | PASS |
| 12 encounters | PASS |
| noun gender >= 85% | PASS |
| unique pairs | PASS |
| general_medicine terms | PASS |
| general_medicine sentences | PASS |
| urology terms | PASS |
| urology sentences | PASS |
| hematology terms | PASS |
| hematology sentences | PASS |
| cardiology terms | PASS |
| cardiology sentences | PASS |
| pulmonology terms | PASS |
| pulmonology sentences | PASS |
| gastroenterology terms | PASS |
| gastroenterology sentences | PASS |
| neurology terms | PASS |
| neurology sentences | PASS |
| obgyn terms | PASS |
| obgyn sentences | PASS |
| pediatrics terms | PASS |
| pediatrics sentences | PASS |
| emergency terms | PASS |
| emergency sentences | PASS |
| orthopedics terms | PASS |
| orthopedics sentences | PASS |
| psychiatry terms | PASS |
| psychiatry sentences | PASS |
| anatomy terms | PASS |
| anatomy sentences | PASS |
| patient_phrases terms | PASS |
| patient_phrases sentences | PASS |

## Verification

`make verify` exited **0** and printed **VERIFY OK**.

- Backend: **94 tests passed**; engine + ingestion statement coverage **96.16%**.
- Frontend: **10 unit tests passed**; all-file statement coverage **18.75%**. This unit percentage does not include browser interaction coverage; no frontend coverage minimum was specified.
- Playwright: **3 tests passed**, covering a ten-question learning flow, hint and Give Up, keyboard tile selection, summary, dashboard, wrong-only review, settings persistence, a scripted encounter, and an actual server process restart.
- Lint and types: Ruff, mypy, ESLint, and TypeScript passed.
- Size: initial JavaScript **78,688 bytes gzipped**; seed database **9,113,600 bytes**.
- Session-creation benchmark: 20 requests, p95 **18.46 ms** in this Linux container. This is not a laptop benchmark. Server RSS was not reliably measurable through the managed process launcher and is not certified against the 150 MB target.

### Final verification output

```text
dist/assets/Banks-C9V2sLls.js                        1.87 kB │ gzip:   0.73 kB
dist/assets/tts-DRLxqW6I.js                          2.02 kB │ gzip:   1.00 kB
dist/assets/StudySetup-BdBXJ9H3.js                   2.29 kB │ gzip:   1.00 kB
dist/assets/Review-CkSvz4iW.js                       4.52 kB │ gzip:   1.66 kB
dist/assets/StudySession-B2Z6BUVv.js                 6.54 kB │ gzip:   2.56 kB
dist/assets/questionTypes-CFlgWfzL.js               50.86 kB │ gzip:  16.83 kB
dist/assets/index-CHEnuxWz.js                      238.28 kB │ gzip:  78.86 kB
dist/assets/dashboardWidgets-CTorbyo-.js           409.77 kB │ gzip: 109.91 kB
✓ built in 3.68s
/workspace/scratch/e553f40bd53b/medlingo/.venv/bin/python scripts/e2e.py
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

Running 3 tests using 1 worker

(node:419) Warning: The 'NO_COLOR' env is ignored due to the 'FORCE_COLOR' env being set.
(Use `node --trace-warnings ...` to show where the warning was created)
(node:419) Warning: The 'NO_COLOR' env is ignored due to the 'FORCE_COLOR' env being set.
(Use `node --trace-warnings ...` to show where the warning was created)
  ✓  1 tests/e2e/restart_persistence.spec.ts:2:1 › actual process restart preserves progress and increments restart count (1.2s)
  ✓  2 tests/e2e/smoke.spec.ts:3:1 › study, hints, give up, dashboard, review, wrong-only test (4.9s)
  ✓  3 tests/e2e/smoke.spec.ts:24:1 › settings persistence and scripted encounter (1.5s)

  3 passed (8.3s)
make[1]: Leaving directory '/workspace/scratch/e553f40bd53b/medlingo'
{
  "initial_js_gzip_bytes": 78688,
  "seed_bytes": 9113600,
  "budget": "PASS"
}
VERIFY OK
```

## Manual QA script results

The following distinguishes automated evidence from steps not performed exactly as written. No physical listening or cross-platform manual checks are claimed.

1. PASS (Linux, automated): make setup and online/offline ingestion ran successfully. Chromium loaded the home page with no uncaught application errors. The separate under-2-second load threshold was not instrumented.

2. PARTIAL: automated Urology learning covers all five standard exercise kinds; a separate scripted encounter covers the sixth. The exact two-session General medicine manual sequence was not performed.

3. PASS (mocked): Spanish speaker clicks and autoplay invoked the Web Speech stub. Audible OS voice output was not tested.

4. PASS: a hint was requested, its panel appeared, and the hint-used state was submitted and recorded.

5. PASS: Give Up revealed the answer and created a wrong-review item.

6. PASS (automated keyboard alternative): sentence tiles were selected with keyboard Enter and submitted. Pointer dragging is implemented with dnd-kit but a separate manual drag gesture was not recorded.

7. PASS: the ten-question study session reached a summary with answered count, accuracy, recorded time, and XP.

8. PASS: dashboard cards, runtime, specialty chart, histogram, heatmap, and review data rendered. Screenshots are bundled.

9. PASS (API and browser): a named Urology wrong-only rule bank produced the previewed item count. Bank test mode rejects hints; the built-in wrong-only test was completed in Chromium.

10. PASS: the browser harness terminated and restarted the backend process. Study totals were unchanged and restart count increased by one.

11. PASS: dark theme persisted after page reload; the test restored light theme afterward.

12. PARTIAL: daily goal was changed and persisted through a reload. Voice preference selection is implemented and unit tested; an audible selected OS voice was not exercised.

13. PARTIAL: six provider HTTP adapters were tested with mocked responses and broken-plugin import isolation was tested. A live cloud provider request with a fake key was not sent.

14. PASS for separate content/progress storage and deterministic IDs in automated tests. Online and offline ingestion both succeeded. A combined live-server manual reingestion sequence was not performed.

## Known limitations

- DeCS's required source snapshot is unavailable. The DeCS adapter still needs validation against a current official export.
- The seven usage-note entries are below the requested 60. The patient-phrase template count is 12 rather than 20. Generic communication templates and shared encounter structure reduce the clinical variety of the bank.
- Bulk imported terms have not received a full independent bilingual clinical review. Some scientific/anatomical labels may be less useful in routine clinical conversation.
- Single-blank exercises and the sentence distractors are simpler than the full specification. Alternate remediation branches are not executed in encounters.
- Wikidata retrieval is capped per class, frequency ranking does not use sitelink counts, and ingestion-source plugin self-registration is not implemented. Frontend plugin registration hooks are present.
- Some response objects remain dictionary schemas. macOS/WSL installation, physical speech, live paid-provider credentials, and the idle-RSS budget were not verified.

## Decisions taken

The complete decision record is copied below so this handoff remains self-contained.

# Decisions and specification differences

## Additional decisions

1. A durable `session_items` table records session membership and order. Attempts have a unique session/item index to prevent double counting retries or repeated clicks.
2. Term and sentence IDs are SHA-256-derived 52-bit integers, safe in JavaScript and stable when other content is added. Questions retain their original frozen payloads.
3. Cloud audio metadata is stored in a separate cache SQLite database. The supplied specification asks both for a read-only seed database and runtime audio-cache writes to it; separating the cache preserves the read-only invariant.
4. PowerShell launches the same Linux workflow through WSL. This package does not claim native Windows Python/Make compatibility.
5. Imported bilingual titles are study data, not clinical treatment instructions. Authored templates avoid prescribing or diagnostic recommendations. No LLM generated external-source labels or fabricated source snapshots are included.
6. Automated Chromium interaction is used for browser QA, including screenshots and mocked speech. No audible OS voice or macOS/Windows installation was tested in this environment.

## Known differences from the full specification

This is an executable implementation with tested primary workflows, not a claim that every requirement in BUILD_SPEC.md is satisfied.

- DeCS access returned HTTP 403. The DeCS snapshot file explicitly records unavailability; it contains zero descriptors. The required 800-descriptor snapshot could not be captured. Its adapter currently accepts normalized descriptor XML and would need validation against the current official DeCS export schema.
- Wiktionary has 300 real lookup requests, of which 186 yielded parsed gender records. The raw responses are bundled. Unknown genders use explicit overrides and conservative morphology, and remain unknown where neither is sufficient.
- Seven editorial usage-note entries are provided, fewer than the requested 60. These are not padded with unsupported regional claims.
- Templates are intentionally general communication patterns rather than 144 independently varied clinical scenarios. The patient-phrase template file currently has 12 entries instead of 20. Each specialty has 110 authored phrase pairs. Encounter scenarios share a six-exchange intake structure tailored by specialty; they do not simulate diagnosis or treatment.
- The ingestion renderer supports declared term and fixed-option slots with deterministic combinations. It caps expansions at 100 combinations per template; it does not enumerate a full Cartesian product of all possible slots.
- Wikidata retrieval uses one capped query per class with retries, not exhaustive multi-page collection or sitelink-derived frequency ranks. Source labels are sorted deterministically, with curated vocabulary prioritized. Specialty assignment uses source ICD/tree values and lexical rules. Some imported anatomical or scientific labels can be outside a clinician's usual vocabulary; a complete bilingual clinical review is outstanding.
- MedlinePlus topic titles are aligned through explicit language-mapped-topic links. Unaligned summaries are not used as sentence pairs.
- Fill-blank and drag-slot exercises use a single translation blank, rather than multi-blank clinical sentences. Sentence ordering uses the full sentence with two time-word distractors, rather than POS-tagged distractors from another sentence.
- Answer payloads are frozen and returned to the browser for rendering. Server scoring prevents accidental client-side result errors; this local trainer is not an anti-cheating examination platform.
- Encounter wrong responses record an incorrect attempt and proceed through the intended correct-path sequence. The stored graph is validated, but conditional alternative remediation branches are not implemented.
- The optional plugin manifest supports lazy module loading and question/widget/settings registration hooks. Ingestion-source plugin registration is not yet wired into the build command; the bundled cloud speech and AI chat integrations work through explicit routes.
- Some HTTP response schemas use JSON dictionary response models rather than fully specified per-field Pydantic objects. The OpenAPI interface documents requests, but response typing is less strict than specified.
- Daily activity uses accumulated active question time; total study time uses session duration. The dashboard supports widget ordering with move-up buttons. It does not provide drag reordering.
- Platform checks were performed on Linux with Chromium. macOS, WSL, native speech, and live paid-provider credentials were not verified.


## Suggested next extensions

Prioritize bilingual clinical review, obtaining a licensed DeCS export, and enriching regional usage notes. Then expand specialty-specific encounter branches, multi-blank exercises, and source-level extension registration. Add platform smoke checks for macOS and WSL and validate installed offline speech voices.
