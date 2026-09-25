# MedLingo architecture

MedLingo serves a React 18 application and a FastAPI API on localhost:8000. Vite provides the separate localhost:5173 development server. Fonts, JavaScript, CSS, curated material, and source snapshots are bundled. Network access is needed for installation and source refresh, not ordinary study. Offline speech needs an installed local device voice.

## Persistence

`seed.sqlite` is rebuilt from attributed snapshots and authored YAML. Runtime connections open it with SQLite `mode=ro`. `user.sqlite` uses WAL, foreign keys, and Alembic migrations. Source IDs are deterministic hashes of bilingual text, preserving identity across sorted imports. Question payloads are frozen with a per-profile fingerprint, so a content refresh cannot change an existing review question.

The additional `session_items` table stores membership and order. Attempt submission verifies membership, takes an immediate SQLite write transaction, and prevents duplicate submissions with a unique `(session_id, item_id)` index. Answers are evaluated on the server. Sessions resume with unanswered items, in batches of 20.

Session time is the interval from session start to last heartbeat or end. Active per-question time pauses when the document is hidden. These are different measurements: session duration includes thinking and pauses while the session remains open. Runtime is stored in a separate heartbeat log, with a new row per process start. Shutdown finalizes that row; crashes lose at most the heartbeat interval.

## Content and exercise engine

Sources normalize into bilingual term dictionaries, then pass through normalization, deduplication, specialty mapping, gender enrichment, template rendering, and an atomic seed replacement. Stable term IDs are below JavaScript's safe integer ceiling. The report checks the supplied offline and online bank thresholds.

Question kinds register through `app/engine/generators/__init__.py`; React renderers register through `src/registry/questionTypes.ts`. Random choices are seeded by profile and fingerprint. Both English-to-Spanish and Spanish-to-English sessions are supported. Scripted encounter graphs are validated for unique node IDs, one advancing correct answer per node, valid edges, no cycles, and a reachable terminal.

## Interface

The application uses React Router, Zustand, Tailwind tokens, local Inter fonts, Recharts dashboard widgets, and dnd-kit exercises. Heavy question and dashboard modules load by route. Pagination keeps review lists at 30 rows. Settings live in the profile record, including theme, device voice, daily goal, and widget order.

## Optional providers

Cloud speech and AI patient plugins are disabled by default. Failed plugin imports are isolated. The three speech adapters and three chat adapters use asynchronous HTTP requests only after the user explicitly selects or invokes an enabled provider. Cloud audio metadata uses `data/audio_cache/index.sqlite`, not the read-only seed database. Source response fixtures retain provenance separately from synthetic parser examples in tests.

## Tests

`make verify` runs lint, type checking, backend and frontend unit tests, offline ingestion, threshold checks, production build, browser tests against disposable databases, a real backend restart, and asset budgets. Browser tests use a mocked Web Speech API. Provider tests use mocked HTTP and make no paid calls.
