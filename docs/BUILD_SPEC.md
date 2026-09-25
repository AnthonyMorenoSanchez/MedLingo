# MedLingo: Complete Build Specification and Agent Guidelines

Version 1.0. Single-shot deliverable. Fully offline EN <-> ES medical translation trainer, gamified, no ads, no lives, runs on localhost.

This document is the entire contract for the coding agent. It defines what to build, exactly how it is structured, how it is tested, and what "done" means. The agent must deliver the whole project in one pass, run every verification step in Section 15, and return the handoff report in Section 16. Nothing is to be deferred, stubbed, or left as TODO unless explicitly marked OPTIONAL here.

## 0. How the agent must use this document

1. Read the whole document before writing any file.
2. Build in the order of Section 4's file tree, but deliver everything at once. Order is for dependency sanity only, not for partial delivery.
3. Every requirement written as MUST is mandatory. SHOULD is expected unless there is a documented technical reason. OPTIONAL may be skipped but the extension point must exist.
4. When a decision is not covered here, choose the simplest option that keeps the plugin contract (Section 13) intact, and record it in `docs/DECISIONS.md`.
5. If a network data source is unreachable during ingestion, fall back to the bundled fixture files in `backend/ingest/fixtures/` (Section 7.7) and note it in the report. Never fabricate translations.
6. Do not use any paid API, LLM, or cloud service at runtime by default. Plugins that use them MUST be disabled by default.
7. No em dashes anywhere in code comments, UI strings, or docs. Use commas, parentheses, or full stops.
8. Run `make verify` as the last step. It MUST exit 0. If it does not, fix and rerun before handing off.

## 1. Product summary

MedLingo is a local web application for a clinician or student to study Spanish medical vocabulary and sentences with a Duolingo-like loop but without ads, hearts, or streak punishment. It contains thousands of English <-> Spanish medical term pairs and templated clinical sentences pulled from open-licensed sources, tagged by specialty (urology, hematology, general medicine, etc.). Questions are multiple choice, typed fill-in-the-blank, drag-a-term-into-a-blank, drag-tiles-to-build-a-sentence, listening, and scripted patient encounters. Every item is spoken aloud on demand. Each question has a Hint button and a separate Give Up button that reveals the answer. The app tracks per-question time, per-session time, and total server runtime persistently across restarts, keeps right/wrong counts per question, builds wrong-only tests, and shows all of it in an attractive dashboard.

### 1.1 Non-negotiables

- Runs with a single command on localhost after `make setup`.
- Zero external runtime dependencies (no API keys) in the default configuration.
- Progress and timing survive closing the browser, killing the server, and rebooting.
- Content can be regenerated (`make ingest`) without losing progress.
- Adding a new specialty, question type, data source, dashboard widget, or plugin requires touching only the locations listed in Section 17.

## 2. Locked decisions

| Topic | Decision |
|---|---|
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2.x, SQLite (WAL), Alembic |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, Zustand, Recharts, dnd-kit, React Router |
| Content | Open-licensed data only: Wikidata (CC0), DeCS (BIREME), MedlinePlus (public domain), Wiktionary (CC BY-SA), plus curated YAML authored in this repo |
| AI | None at runtime by default. `ai_patient` plugin exists, disabled |
| TTS | Browser Web Speech API by default. `cloud_tts` plugin exists, disabled |
| Patient interaction | Scripted branching encounters (default) + optional AI chat plugin |
| Directions | Both EN -> ES and ES -> EN, selectable per session |
| Spanish variant | Neutral Latin American Spanish, with `regional_notes` per term where usage differs (e.g., Spain vs Mexico vs Caribbean) |
| Specialties | general_medicine, urology, hematology, cardiology, pulmonology, gastroenterology, neurology, obgyn, pediatrics, emergency, orthopedics, psychiatry, anatomy, patient_phrases |
| Users | Single default profile, but `profiles` table and `profile_id` on every user row so multi-profile is a UI-only addition later |
| Ports | Backend 8000, Vite dev 5173, production single port 8000 serving the built frontend |

## 3. Pinned tooling

Backend `pyproject.toml` (use uv or pip):

```
fastapi>=0.111,<1.0
uvicorn[standard]>=0.30
sqlalchemy>=2.0,<3.0
alembic>=1.13
pydantic>=2.7
pydantic-settings>=2.2
httpx>=0.27
pyyaml>=6.0
rapidfuzz>=3.9
unidecode>=1.3
python-multipart>=0.0.9
lxml>=5.2
pytest>=8.2
pytest-asyncio>=0.23
pytest-cov>=5.0
ruff>=0.4
mypy>=1.10
```

Frontend `package.json` key deps: react 18, react-dom 18, react-router-dom 6, zustand 4, recharts 2, @dnd-kit/core 6, @dnd-kit/sortable 8, tailwindcss 3, vite 5, typescript 5, vitest 1, @testing-library/react 15, @playwright/test 1.44, lucide-react (icons), clsx.

## 4. Repository structure

Every file listed MUST exist. Files marked (gen) are generated by build steps and gitignored.

```
medlingo/
  README.md
  LICENSE                          MIT for the code; data attributions in docs/ATTRIBUTION.md
  Makefile
  run.sh                           cross-platform wrapper calling make targets
  .env.example
  .gitignore
  plugins.toml
  docs/
    ARCHITECTURE.md
    DECISIONS.md
    ATTRIBUTION.md
    EXTENDING.md                   copy of Section 17 kept in sync
    QA_MANUAL_SCRIPT.md            copy of Section 15.5
    HANDOFF_REPORT.md              filled by the agent at completion (Section 16)
  data/
    seed.sqlite                    (gen) content DB from ingestion
    user.sqlite                    (gen) created on first backend start
    bank_report.md                 (gen) ingestion statistics
    audio_cache/                   (gen) cloud_tts plugin output
  backend/
    pyproject.toml
    alembic.ini
    alembic/
      env.py
      versions/
        0001_initial_user_schema.py
    app/
      __init__.py
      main.py                      app factory, lifespan (runtime heartbeat), static mount, plugin loader
      config.py                    pydantic-settings; reads .env and plugins.toml
      db.py                        two engines: seed (read-only) and user (read-write), WAL pragmas
      deps.py                      FastAPI dependencies (sessions, current profile)
      models/
        __init__.py
        seed.py                    Term, Sentence, Template, Specialty, Encounter, AudioCache
        user.py                    Profile, QuestionItem, ItemStat, Attempt, Session, RuntimeLog, Bank
      schemas/
        __init__.py
        terms.py  questions.py  attempts.py  sessions.py  stats.py  encounters.py  banks.py  tts.py
      api/
        __init__.py
        router.py                  aggregates all routers under /api
        health.py  terms.py  specialties.py  questions.py  attempts.py  sessions.py
        stats.py  banks.py  encounters.py  tts.py  runtime.py  profiles.py
      engine/
        __init__.py
        normalize.py               accent folding, punctuation strip, fuzzy compare
        distractors.py
        templates.py               slot rendering with Spanish gender/number agreement
        scheduler.py               SM-2 lite and session builder
        hints.py
        generators/
          __init__.py              registry: kind -> generator
          base.py
          mcq.py  fill_blank.py  drag_slot.py  drag_order.py  listening.py  encounter.py
      plugins/
        __init__.py
        base.py                    Plugin ABC and registry
        loader.py                  reads plugins.toml, imports, registers
        cloud_tts/
          __init__.py  plugin.py  providers/{base,google,azure,elevenlabs}.py  README.md
        ai_patient/
          __init__.py  plugin.py  providers/{base,openai,anthropic,ollama}.py  rubric.py  README.md
    ingest/
      __init__.py
      build_bank.py                orchestrator: sources -> normalize -> tag -> dedupe -> write seed -> report
      specialty_map.py             MeSH tree and ICD-10 chapter -> specialty rules
      gender.py                    Spanish gender/number inference and override loading
      dedupe.py
      report.py
      sources/
        __init__.py  base.py  wikidata.py  decs.py  medlineplus.py  wiktionary.py  curated.py
      curated/
        specialties.yaml
        templates/*.yaml           one file per specialty
        phrases/*.yaml             patient phrases per specialty
        encounters/*.yaml          scripted dialogues per specialty
        regional_notes.yaml
        gender_overrides.yaml
        term_overrides.yaml        manual corrections and blacklist
      fixtures/                    offline snapshots so ingestion always works
        wikidata_sample.json  decs_sample.xml  medlineplus_sample.xml  wiktionary_sample.json
    tests/
      conftest.py
      unit/
        test_normalize.py  test_templates.py  test_distractors.py  test_scheduler.py
        test_generators.py  test_gender.py  test_specialty_map.py  test_dedupe.py
      integration/
        test_api_questions.py  test_api_attempts.py  test_api_sessions.py
        test_api_stats.py  test_api_banks.py  test_api_encounters.py  test_persistence_restart.py
      ingest/
        test_build_bank_fixtures.py
  frontend/
    package.json  vite.config.ts  tsconfig.json  tailwind.config.ts  postcss.config.js  index.html
    playwright.config.ts
    public/
      favicon.svg  manifest.webmanifest
    src/
      main.tsx  App.tsx  router.tsx
      api/
        client.ts                  typed fetch wrapper
        types.ts                   generated-from-OpenAPI or hand-mirrored types
      store/
        session.ts  settings.ts  timer.ts  profile.ts
      lib/
        tts.ts                     TTSProvider interface, WebSpeechProvider, plugin hook
        time.ts  format.ts  normalize.ts
      registry/
        questionTypes.ts           kind -> component
        dashboardWidgets.ts        id -> widget component
        plugins.ts                 frontend plugin registration
      components/
        ui/                        Button, Card, Badge, ProgressRing, Modal, Toast, Tooltip, Skeleton
        layout/                    AppShell, Sidebar, TopBar, ThemeToggle
        SpeakButton.tsx  HintPanel.tsx  GiveUpButton.tsx  QuestionTimer.tsx  Feedback.tsx
      questionTypes/
        Mcq.tsx  FillBlank.tsx  DragSlot.tsx  DragOrder.tsx  Listening.tsx  Encounter.tsx
      pages/
        Home.tsx  StudySetup.tsx  StudySession.tsx  SessionSummary.tsx
        Review.tsx                 wrong / correct / leech tabs
        Banks.tsx  TestRunner.tsx
        Encounters.tsx  EncounterPlayer.tsx
        Dashboard.tsx  Settings.tsx  About.tsx
      dashboard/
        widgets/                   TotalTime, TodayTime, RuntimeCard, Accuracy, StreakXp,
                                   SpecialtyRadar, TimePerQuestionHist, DailyHeatmap,
                                   WrongBankTrend, LeechTable, WrongTable, CorrectTable
      styles/
        globals.css  tokens.css
    tests/
      unit/                        vitest: normalize, timer store, tts provider selection
      e2e/                         playwright: smoke.spec.ts, restart_persistence.spec.ts
  scripts/
    verify.sh                      the self-test runner used by `make verify`
    seed_dev_profile.py            creates demo attempts for dashboard screenshots (dev only)
```

## 5. Configuration

### 5.1 `.env.example`

```
MEDLINGO_HOST=127.0.0.1
MEDLINGO_PORT=8000
MEDLINGO_SEED_DB=data/seed.sqlite
MEDLINGO_USER_DB=data/user.sqlite
MEDLINGO_HEARTBEAT_SECONDS=30
MEDLINGO_LOG_LEVEL=info
# Plugin secrets (only read if the plugin is enabled in plugins.toml)
GOOGLE_TTS_API_KEY=
AZURE_TTS_KEY=
AZURE_TTS_REGION=
ELEVENLABS_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
```

### 5.2 `plugins.toml`

```toml
[cloud_tts]
enabled = false
provider = "google"      # google | azure | elevenlabs
voice = "es-US-Neural2-A"
cache_dir = "data/audio_cache"

[ai_patient]
enabled = false
provider = "ollama"      # openai | anthropic | ollama
model = "llama3.1"
max_turns = 12
```

### 5.3 Makefile targets (all MUST exist)

| Target | Behavior |
|---|---|
| `setup` | create venv, install backend deps, `npm ci` in frontend, copy `.env.example` to `.env` if missing |
| `ingest` | run `python -m ingest.build_bank` producing `data/seed.sqlite` and `data/bank_report.md` |
| `ingest-offline` | same with `--offline` forcing fixtures |
| `migrate` | alembic upgrade head on user DB |
| `dev` | start uvicorn with reload on 8000 and Vite on 5173 concurrently |
| `build` | `npm run build` into `frontend/dist` |
| `run` | `migrate` then start uvicorn serving API and `frontend/dist` on 8000 |
| `test` | backend pytest with coverage + frontend vitest |
| `e2e` | build, start server on a test port with temp DBs, run Playwright |
| `lint` | ruff, mypy, eslint, tsc --noEmit |
| `verify` | `scripts/verify.sh` (Section 15.6) |
| `clean-user` | delete `data/user.sqlite` after confirmation prompt |

## 6. Data layer

### 6.1 Seed database (`data/seed.sqlite`, read-only at runtime)

```sql
CREATE TABLE specialties (
  id TEXT PRIMARY KEY,               -- 'urology'
  name_en TEXT NOT NULL,
  name_es TEXT NOT NULL,
  color TEXT NOT NULL,               -- hex for UI badges
  icon TEXT NOT NULL,                -- lucide icon name
  sort_order INTEGER NOT NULL
);

CREATE TABLE terms (
  id INTEGER PRIMARY KEY,
  en TEXT NOT NULL,
  es TEXT NOT NULL,
  en_aliases TEXT NOT NULL DEFAULT '[]',   -- JSON array
  es_aliases TEXT NOT NULL DEFAULT '[]',
  pos TEXT NOT NULL,                       -- noun | adj | verb | phrase
  gender_es TEXT,                          -- m | f | mf | NULL for non-nouns
  number_es TEXT NOT NULL DEFAULT 'sg',    -- sg | pl
  semantic_type TEXT NOT NULL,             -- disease | symptom | anatomy | drug | procedure | test | phrase | other
  definition_en TEXT,
  definition_es TEXT,
  frequency_rank INTEGER,                  -- lower = more common; NULL unknown
  difficulty INTEGER NOT NULL DEFAULT 3,   -- 1..5
  source TEXT NOT NULL,                    -- wikidata | decs | medlineplus | wiktionary | curated
  source_id TEXT,
  regional_notes TEXT NOT NULL DEFAULT '[]', -- JSON [{region, es, note}]
  UNIQUE(en, es)
);

CREATE TABLE term_specialties (
  term_id INTEGER NOT NULL REFERENCES terms(id),
  specialty_id TEXT NOT NULL REFERENCES specialties(id),
  PRIMARY KEY (term_id, specialty_id)
);

CREATE TABLE templates (
  id INTEGER PRIMARY KEY,
  key TEXT UNIQUE NOT NULL,
  en_pattern TEXT NOT NULL,     -- 'The patient reports {SYMPTOM} in the {BODY_PART}.'
  es_pattern TEXT NOT NULL,     -- 'El paciente refiere {SYMPTOM} en {DET:BODY_PART} {BODY_PART}.'
  slot_types TEXT NOT NULL,     -- JSON {"SYMPTOM":"symptom","BODY_PART":"anatomy"}
  specialty_id TEXT REFERENCES specialties(id),
  difficulty INTEGER NOT NULL DEFAULT 3,
  register TEXT NOT NULL DEFAULT 'clinical'   -- clinical | patient
);

CREATE TABLE sentences (
  id INTEGER PRIMARY KEY,
  template_id INTEGER REFERENCES templates(id),   -- NULL for curated fixed sentences
  en TEXT NOT NULL,
  es TEXT NOT NULL,
  slots TEXT NOT NULL DEFAULT '[]',   -- JSON [{slot, term_id, es_surface, en_surface, start_es, end_es}]
  specialty_id TEXT NOT NULL REFERENCES specialties(id),
  difficulty INTEGER NOT NULL DEFAULT 3,
  source TEXT NOT NULL,
  UNIQUE(en, es)
);

CREATE TABLE encounters (
  id TEXT PRIMARY KEY,
  title_en TEXT NOT NULL,
  title_es TEXT NOT NULL,
  specialty_id TEXT NOT NULL REFERENCES specialties(id),
  difficulty INTEGER NOT NULL,
  nodes TEXT NOT NULL              -- JSON graph, see Section 12
);

CREATE TABLE audio_cache (
  text_hash TEXT PRIMARY KEY,
  provider TEXT NOT NULL,
  voice TEXT NOT NULL,
  path TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE seed_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);  -- built_at, source versions, counts

CREATE INDEX idx_terms_semantic ON terms(semantic_type);
CREATE INDEX idx_terms_freq ON terms(frequency_rank);
CREATE INDEX idx_term_spec ON term_specialties(specialty_id, term_id);
CREATE INDEX idx_sentences_spec ON sentences(specialty_id, difficulty);
```

### 6.2 User database (`data/user.sqlite`, Alembic-managed)

```sql
CREATE TABLE profiles (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  settings TEXT NOT NULL DEFAULT '{}',  -- JSON: theme, tts voice, daily goal minutes, default direction
  created_at TEXT NOT NULL
);

CREATE TABLE question_items (
  id INTEGER PRIMARY KEY,
  profile_id INTEGER NOT NULL REFERENCES profiles(id),
  kind TEXT NOT NULL,          -- mcq | fill_blank | drag_slot | drag_order | listening | encounter
  direction TEXT NOT NULL,     -- en2es | es2en
  term_id INTEGER,             -- seed FK (not enforced cross-db)
  sentence_id INTEGER,
  encounter_id TEXT,
  node_id TEXT,
  specialty_id TEXT NOT NULL,
  payload TEXT NOT NULL,       -- JSON frozen question (prompt, options, answer, blanks, tiles)
  fingerprint TEXT NOT NULL,   -- sha1(kind|direction|term_id|sentence_id|encounter_id|node_id)
  created_at TEXT NOT NULL,
  UNIQUE(profile_id, fingerprint)
);

CREATE TABLE item_stats (
  item_id INTEGER PRIMARY KEY REFERENCES question_items(id),
  correct_count INTEGER NOT NULL DEFAULT 0,
  wrong_count INTEGER NOT NULL DEFAULT 0,
  gave_up_count INTEGER NOT NULL DEFAULT 0,
  hint_count INTEGER NOT NULL DEFAULT 0,
  streak INTEGER NOT NULL DEFAULT 0,
  ease REAL NOT NULL DEFAULT 2.5,
  interval_days REAL NOT NULL DEFAULT 0,
  due_at TEXT,
  last_result TEXT,            -- correct | wrong | NULL
  last_seen_at TEXT,
  total_time_ms INTEGER NOT NULL DEFAULT 0,
  attempts INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE sessions (
  id INTEGER PRIMARY KEY,
  profile_id INTEGER NOT NULL REFERENCES profiles(id),
  mode TEXT NOT NULL,          -- learn | review | wrong_test | correct_drill | bank | encounter
  filters TEXT NOT NULL,       -- JSON
  started_at TEXT NOT NULL,
  last_heartbeat_at TEXT NOT NULL,
  ended_at TEXT,
  planned_count INTEGER NOT NULL,
  completed_count INTEGER NOT NULL DEFAULT 0,
  correct_count INTEGER NOT NULL DEFAULT 0,
  xp_earned INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE attempts (
  id INTEGER PRIMARY KEY,
  item_id INTEGER NOT NULL REFERENCES question_items(id),
  session_id INTEGER NOT NULL REFERENCES sessions(id),
  result TEXT NOT NULL,        -- correct | wrong
  answer_given TEXT,
  time_ms INTEGER NOT NULL,
  hint_used INTEGER NOT NULL DEFAULT 0,
  gave_up INTEGER NOT NULL DEFAULT 0,
  ts TEXT NOT NULL
);

CREATE TABLE runtime_log (
  id INTEGER PRIMARY KEY,
  process_started_at TEXT NOT NULL,
  last_heartbeat_at TEXT NOT NULL,
  ended_cleanly INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE banks (
  id INTEGER PRIMARY KEY,
  profile_id INTEGER NOT NULL REFERENCES profiles(id),
  name TEXT NOT NULL,
  rule TEXT NOT NULL,          -- JSON, see Section 8.6
  created_at TEXT NOT NULL
);

CREATE TABLE daily_stats (          -- materialized nightly-or-on-write rollup for the dashboard
  profile_id INTEGER NOT NULL,
  day TEXT NOT NULL,                -- YYYY-MM-DD local
  study_ms INTEGER NOT NULL DEFAULT 0,
  attempts INTEGER NOT NULL DEFAULT 0,
  correct INTEGER NOT NULL DEFAULT 0,
  xp INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (profile_id, day)
);

CREATE INDEX idx_items_profile_spec ON question_items(profile_id, specialty_id, kind);
CREATE INDEX idx_stats_due ON item_stats(due_at);
CREATE INDEX idx_stats_last ON item_stats(last_result);
CREATE INDEX idx_attempts_session ON attempts(session_id);
CREATE INDEX idx_attempts_item_ts ON attempts(item_id, ts);
CREATE INDEX idx_sessions_profile ON sessions(profile_id, started_at);
```

### 6.3 Database rules

- Both engines set `PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; PRAGMA foreign_keys=ON;`.
- Seed engine opens with `?mode=ro` URI. Any write attempt is a bug.
- All timestamps stored as ISO 8601 UTC. The frontend converts to local for display; `daily_stats.day` uses the profile's local date sent by the client.
- On startup: run Alembic migrations, create default profile "Default" if none exists, insert a `runtime_log` row, start heartbeat task.

## 7. Ingestion pipeline

Entry point: `python -m ingest.build_bank [--offline] [--limit N] [--sources wikidata,decs,...]`. Output: `data/seed.sqlite`, `data/bank_report.md`. Must be idempotent and deterministic given the same inputs (sort before insert, fixed random seed for any sampling).

### 7.1 Common normalization (`sources/base.py`)

Each source yields `RawTerm(en, es, en_aliases, es_aliases, semantic_type, definition_en, definition_es, source, source_id, mesh_ids, icd10_codes, pos_hint)`.

Normalization: trim, collapse whitespace, strip trailing periods, lowercase first character unless proper noun or acronym, drop entries where `en == es` for non-cognate check unless `semantic_type in (drug, anatomy)` and length > 6 (cognates like "apendicitis" vs "appendicitis" differ; identical strings such as "insulina" vs "insulin" do not occur, but "asma" vs "asthma" do and are kept). Drop entries containing parentheses qualifiers longer than 30 chars. Drop any `es` that contains no Spanish-indicative characters and equals `en` exactly.

### 7.2 Wikidata (`sources/wikidata.py`)

SPARQL endpoint `https://query.wikidata.org/sparql`, User-Agent header set, 5 requests/second max, retry with backoff. One query per semantic class, paginated with LIMIT/OFFSET 5000:

| semantic_type | Wikidata class (P31/P279*) |
|---|---|
| disease | Q12136 disease |
| symptom | Q169872 symptom, Q1441305 medical sign |
| anatomy | Q4936952 anatomical structure (restrict to human: P703 Q15978631 where present) |
| drug | Q12140 medication |
| procedure | Q796194 medical procedure, Q1444061 surgical procedure |
| test | Q2671652 medical test |

Fields: `rdfs:label@en`, `rdfs:label@es`, `skos:altLabel@en/@es`, `P486` MeSH descriptor ID, `P494` ICD-10, `P672` MeSH tree code, `schema:description@en/@es`. Keep only rows with both labels. Reject labels longer than 60 chars or containing digits-only tokens.

### 7.3 DeCS (`sources/decs.py`)

Download the DeCS XML or use the DeCS API (`https://api.bvsalud.org/decs/v2/`) for Spanish descriptors with English equivalents, tree numbers, and definitions. Parse: descriptor `es`, English `en`, synonyms as aliases, tree numbers for specialty mapping. Include only categories A, C, D (drugs), E (procedures/techniques), F03 (mental disorders), G (phenomena, limited to physiology), skip publication types and geographic categories (V, Z). Record the DeCS version in `seed_meta`. If terms of use cannot be confirmed programmatically, the source is still ingested but `docs/ATTRIBUTION.md` MUST include the BIREME attribution block and a note for the user to confirm current terms.

### 7.4 MedlinePlus (`sources/medleplus.py`)

Health topics XML (`https://medlineplus.gov/xml/mplus_topics_YYYY-MM-DD.xml`) contains English and Spanish topic pairs via `language-mapped-topic`. Extract title pairs as terms (semantic_type from topic groups) and the first sentence of each `full-summary` where an aligned Spanish summary exists as patient-register sentences. Aligned sentence pairs are only kept when both sides have 6 to 30 words and share at least one aligned term from the term bank; otherwise discard (no machine alignment guessing).

### 7.5 Wiktionary (`sources/wiktionary.py`)

Use the Wiktionary REST/Action API for the Spanish entries of already-collected `es` nouns to fetch gender and plural forms. Cache responses in `ingest/.cache/`. This source enriches; it does not create terms on its own.

### 7.6 Curated YAML (`sources/curated.py`)

The agent MUST author these files with real, correct, neutral Latin American Spanish. Minimum quantities:

| File set | Minimum |
|---|---|
| `templates/*.yaml` | 12 templates per clinical specialty (12 x 12 = 144), 20 for patient_phrases, 10 for anatomy |
| `phrases/*.yaml` | 30 fixed patient/clinician phrase pairs per specialty (420 total) |
| `encounters/*.yaml` | 1 encounter per clinical specialty (12), each 6 to 10 nodes |
| `regional_notes.yaml` | 60 entries |
| `gender_overrides.yaml` | all irregulars encountered in tests (e.g., "la mano", "el problema", "la radio") |

Template YAML schema:

```yaml
- key: urology_dysuria_1
  specialty: urology
  register: patient
  difficulty: 2
  en: "Do you feel {SYMPTOM} when you {ACTION}?"
  es: "¿Siente {SYMPTOM} cuando {ACTION}?"
  slots:
    SYMPTOM: { type: symptom, filter: { specialty: urology } }
    ACTION: { type: fixed, options: [{ en: "urinate", es: "orina" }, { en: "pass urine", es: "orina" }] }
```

Slot syntax in `es` patterns: `{X}` surface form, `{DET:X}` definite article agreeing with X, `{INDEF:X}` indefinite article, `{ADJ:X:inflamado}` adjective agreeing with X, `{PL:X}` plural form. `templates.py` MUST implement all four and raise `TemplateRenderError` when gender is unknown for a slot needing agreement; the generator then skips that (template, term) pair and counts it in the report under `skipped_unknown_gender`.

Phrase YAML schema: `- { en: "...", es: "...", specialty: hematology, difficulty: 2, notes: "..." }`.

### 7.7 Fixtures and offline mode

`fixtures/` MUST contain real snapshots (not invented) of at least 800 Wikidata rows, 800 DeCS descriptors, 60 MedlinePlus topic pairs, and 300 Wiktionary gender lookups, captured by the agent during the first successful online run via `--dump-fixtures`. If the agent never gets network access, it MUST say so in the handoff report, and curated YAML MUST be expanded to reach the Section 7.9 minimums on its own (raise phrase minimums to 80 per specialty).

### 7.8 Specialty mapping (`specialty_map.py`)

Ordered rules; a term can map to several specialties.

| Specialty | MeSH tree prefixes | ICD-10 chapters | Extra |
|---|---|---|---|
| urology | C12, A05 (urinary), E04.950 (urologic surgical procedures) | N00-N39, N40-N51 | curated list |
| hematology | C15, D17 (blood proteins), E01.370.225 (hematologic tests), A15 | D50-D89 | |
| cardiology | C14, A07, E04.100 | I00-I99 | |
| pulmonology | C08, A04 | J00-J99 | |
| gastroenterology | C06, A03 | K00-K93 | |
| neurology | C10, A08 | G00-G99 | |
| obgyn | C13, A05 (genital female), A16 (embryonic structures) | O00-O99, N70-N98 | |
| orthopedics | C05, A02 | M00-M99, S00-T14 (fractures) | |
| psychiatry | F03, F01 (behavior) | F00-F99 | |
| pediatrics | C16 (congenital), qualifier "pediatric" in label | P00-P96, Q00-Q99 | curated list |
| emergency | curated list: trauma, resuscitation, triage vocabulary, C26 (wounds and injuries) | S, T, R57 (shock) | curated list |
| anatomy | A (all) | none | |
| general_medicine | any term with `frequency_rank <= 2000` or `semantic_type in (symptom, test)` not otherwise mapped | R00-R99 | |
| patient_phrases | curated only | | |

`frequency_rank` is computed from Wikidata sitelink count (more sitelinks = more common), rank ordered, with curated phrases forced to rank 1..N.

### 7.9 Minimum bank thresholds (build fails if unmet)

- Total terms >= 6,000 (online) or >= 2,500 (offline fixtures + curated).
- Each clinical specialty >= 200 terms; anatomy >= 400; patient_phrases >= 300.
- Terms with known `gender_es` among nouns >= 85%.
- Rendered sentences >= 3,000 (online) or >= 1,500 (offline), distributed so no specialty has fewer than 80.
- Encounters = 12, all nodes validated (every non-terminal node has exactly one correct option, all `next` IDs resolve).
- Zero duplicate (en, es) pairs.

### 7.10 `bank_report.md` contents

Counts per specialty (terms, sentences, encounters), per semantic type, per source, gender coverage, skipped counts by reason, source versions and fetch timestamps, threshold pass/fail table, and 20 random sample rows per specialty for human spot checking.

## 8. Question engine

### 8.1 Item generation policy

Items are generated lazily when a session requests them and frozen into `question_items.payload` so a user always re-tests the exact same question. `fingerprint` prevents duplicates per profile. Generators MUST use a seeded RNG from `(profile_id, fingerprint)` so regeneration is deterministic.

### 8.2 Payload schemas (JSON)

```
mcq:        { prompt, prompt_lang, options: [ {id, text} x4 ], answer_id, term_id|sentence_id, audio_text, audio_lang, explanation }
fill_blank: { sentence_masked, sentence_full, blank: {start, end, answer, accepted: [..]}, lang, audio_text, hint_seed }
drag_slot:  { sentence_masked (with {{1}},{{2}} markers), blanks: [{index, answer_tile_id}], tiles: [{id, text}], lang }
drag_order: { target_sentence, tiles: [{id, text}] shuffled, distractor_tile_ids: [], lang, audio_text }
listening:  { audio_text, audio_lang, mode: 'mcq'|'typed', options?, answer, accepted? }
encounter:  { encounter_id, node_id, patient_line_es, patient_line_en, options: [{id, text_es, text_en}], correct_id, feedback: {id: text} }
```

All payloads carry `hint: { type, value }` precomputed and `giveup: { answer_display, explanation_en, explanation_es, regional_notes }`.

### 8.3 Distractors (`distractors.py`)

For MCQ and drag tiles: sample from the seed DB with SQL `ORDER BY random()` constrained to same `semantic_type`, same specialty where possible (fallback any specialty), same `pos`, same `number_es`, not sharing the first 4 characters with the answer, Levenshtein distance >= 3 from the answer and from each other (rapidfuzz). Exactly 3 distractors for MCQ. For drag_order, add 2 distractor tiles of matching part of speech from another sentence in the same specialty.

### 8.4 Answer checking (`normalize.py`)

Typed answers: fold case, trim, collapse spaces, strip terminal punctuation, normalize `¿¡`. Compare exactly; if not equal, compare with accents folded (unidecode). If accent-folded equal, result is `correct` with `feedback: 'accents'` flag (counts as correct, shown as a yellow "watch the accents" note). Accept any `accepted` alias. Fuzzy ratio >= 92 yields `wrong` with feedback `near_miss` showing the diff; it is still wrong. Articles at the start ("el", "la", "los", "las", "un", "una") are optional unless the payload flag `article_required` is true (used by gender drills).

### 8.5 Scheduler (`scheduler.py`)

SM-2 lite, applied per item after every attempt:

```
if result == correct and not gave_up:
    streak += 1
    ease = max(1.3, ease + (0.1 if not hint_used else 0.0))
    interval_days = 1 if streak == 1 else (3 if streak == 2 else interval_days * ease)
else:
    streak = 0
    ease = max(1.3, ease - 0.2)
    interval_days = 0
due_at = now + interval_days (wrong items are due immediately)
```

Session builder input: `{mode, direction, specialties[], kinds[], difficulty_min, difficulty_max, count, bank_id?}`.

| mode | selection |
|---|---|
| learn | 70% unseen (create new items from terms/sentences ordered by frequency_rank), 30% due items |
| review | items with `due_at <= now`, oldest due first; if fewer than count, top up with unseen |
| wrong_test | items where `last_result = 'wrong'` OR `wrong_count > correct_count` OR `gave_up_count > 0 and streak < 2`; no hints allowed; scored; no top-up (returns fewer if fewer exist) |
| correct_drill | items with `last_result = 'correct'` ordered by longest since seen |
| bank | apply `banks.rule` (Section 8.6) |
| encounter | nodes of the chosen encounter in graph order |

Leech: `wrong_count >= 5 and correct_count < wrong_count`. Surfaced on Review page and as a dashboard table.

### 8.6 Bank rule JSON

```json
{ "specialties": ["urology"], "kinds": ["mcq","fill_blank"], "direction": "en2es",
  "result_filter": "wrong_only|correct_only|leech|any", "min_wrong": 1, "max_ease": 2.0,
  "seen_within_days": 30, "limit": 40 }
```

Every field optional. Banks page shows a live count preview via `POST /api/banks/preview`.

### 8.7 Hints (`hints.py`)

Hint order for a given item: first letter and length ("m _ _ _ _ _"), then gender article, then a synonym or alias, then the English definition. Each hint press increments `hint_count`. Hints are unavailable in `wrong_test` mode.

### 8.8 Give Up

Separate red-outlined button, requires no confirmation but has a 400 ms press delay animation to prevent accidental clicks. Reveals answer with translation, explanation, regional notes, and speaks it. Records `result=wrong, gave_up=1`.

### 8.9 XP and gamification (no lives)

+10 correct, +5 correct with hint, +2 accent-only correct, 0 wrong, +25 finishing a session, +15 daily goal reached. Daily goal defaults to 15 minutes, editable in Settings. Badges per specialty at 50 / 200 / 500 correct answers. No penalty of any kind for wrong answers other than scheduling.

## 9. API contract (prefix `/api`)

All responses JSON. Errors use `{ "error": { "code", "message" } }`. Every endpoint has a Pydantic response model and appears in `/docs`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | `{status, seed_built_at, term_count, uptime_s}` |
| GET | `/specialties` | list with counts |
| GET | `/terms?specialty=&q=&page=&size=` | paginated search, size <= 100 |
| GET | `/terms/{id}` | term with regional notes and example sentences (max 5) |
| POST | `/sessions` | body = session builder input; returns session and first batch of 20 items |
| GET | `/sessions/{id}/next?after_item_id=` | next batch of up to 20 items |
| POST | `/sessions/{id}/heartbeat` | updates `last_heartbeat_at` |
| POST | `/sessions/{id}/end` | sets `ended_at`, returns summary |
| GET | `/sessions?limit=` | history |
| POST | `/attempts` | `{item_id, session_id, answer_given, time_ms, hint_used, gave_up, client_day}` returns `{result, feedback, correct_answer, stats_after, xp}` (server re-checks the answer; the client never decides correctness) |
| POST | `/items/{id}/hint?level=` | returns hint text, increments count |
| GET | `/review?tab=wrong|correct|leech&specialty=&page=` | tables for the Review page |
| GET | `/stats/overview` | dashboard cards |
| GET | `/stats/specialties` | accuracy and counts per specialty |
| GET | `/stats/time?from=&to=` | daily study minutes, per-question time histogram |
| GET | `/stats/wrong_trend` | wrong-bank size per day (from attempts) |
| GET | `/runtime` | `{current_uptime_s, total_runtime_s, restarts}` from `runtime_log` |
| GET/POST/DELETE | `/banks` | CRUD |
| POST | `/banks/preview` | count of items matching a rule |
| GET | `/encounters?specialty=` | list |
| GET | `/encounters/{id}` | full graph |
| GET | `/tts/providers` | `[{id, label, enabled}]` (web_speech always present) |
| POST | `/tts/synthesize` | only when a cloud plugin is enabled; returns audio URL from cache |
| GET/PUT | `/profiles/current` | settings |
| GET | `/plugins` | enabled plugins and the frontend modules they expose |

## 10. Frontend

### 10.1 Routes

`/` Home (continue last session, daily goal ring, quick start per specialty), `/study/setup`, `/study/session/:id`, `/study/summary/:id`, `/review`, `/banks`, `/test/:bankId`, `/encounters`, `/encounters/:id`, `/dashboard`, `/settings`, `/about`.

### 10.2 Design system

- Tailwind with CSS variables in `tokens.css`. Light and dark themes; respect `prefers-color-scheme`, toggle persisted in profile settings.
- Palette: background neutral slate; accent teal `#0F9D8A`; correct green `#22A06B`; wrong rose `#E5484D`; warning amber `#F5A524`; specialty colors from `specialties.color`.
- Type: Inter (bundled locally, no CDN), tabular numerals for timers.
- Motion: 150 to 250 ms transitions, reduced-motion respected.
- Components MUST be keyboard accessible; drag interactions MUST have a keyboard alternative (dnd-kit keyboard sensor plus tap-to-select then tap-target fallback).

### 10.3 Study session runner

- Loads a batch, shows progress bar (n of planned), specialty badge, direction badge.
- `QuestionTimer` starts when the question is rendered and stops on submit or give up. Pausing when the tab loses visibility (Page Visibility API) is MUST; paused time is excluded from `time_ms`.
- Heartbeat POST every 30 s while a session is open; `beforeunload` sends a final `sessions/{id}/end` with `keepalive: true`.
- Feedback card after each answer: correct or wrong, correct answer, explanation, regional notes chips, speaker button, "Report content issue" that writes to `docs/content_issues.jsonl` via `POST /api/content_issues` (simple append, OPTIONAL endpoint but the button MUST exist and degrade gracefully).
- Speaker button on prompt, on each option, on each tile, and on the revealed answer.
- Hint button (blue, secondary) and Give Up button (red outline) are visually and spatially separate; Give Up sits at the far right of the action bar.

### 10.4 TTS (`lib/tts.ts`)

```ts
export interface TTSProvider { id: string; label: string; speak(text: string, lang: 'es'|'en', opts?): Promise<void>; cancel(): void; voices(): Promise<Voice[]>; }
```

`WebSpeechProvider` picks the best voice by preference list: `es-US`, `es-MX`, `es-419`, `es-ES`, any `es-*`. Rate default 0.9 for Spanish. If no Spanish voice exists, show a one-time toast explaining how to install one on the OS and fall back to any available voice. The active provider is selected from `/api/tts/providers` and Settings. A cloud provider fetches `/api/tts/synthesize` and plays the returned audio, caching object URLs in memory (max 100 entries, LRU).

### 10.5 Question components

Each component receives `{ item, onSubmit(answer), onGiveUp(), onHint(), disabled }` and MUST be self-contained. Registered in `registry/questionTypes.ts`. `DragSlot` and `DragOrder` use dnd-kit with sortable tiles; correct placements snap and highlight after submit. `Listening` auto-plays once, shows a replay button, and hides the text until answered.

### 10.6 Dashboard

Widgets registered in `registry/dashboardWidgets.ts` and laid out in a responsive 12-column grid with a saved order in profile settings. Required widgets:

1. Total study time (all sessions) and today's time, with daily goal ring.
2. Server runtime card: current uptime, lifetime runtime, number of restarts.
3. Accuracy overall and last 7 days, streak (days with any study), XP and level.
4. Specialty radar (accuracy per specialty) plus a bar of items seen per specialty.
5. Time per question histogram (buckets 0-5 s, 5-10, 10-20, 20-40, 40+).
6. Daily minutes heatmap for the last 16 weeks.
7. Wrong-bank size trend line.
8. Tables: Wrong items, Correct items, Leeches, each with "Practice these" and "Save as bank" actions.

Empty states MUST look intentional (illustration-free, a sentence and a call to action).

### 10.7 Review page

Tabs Wrong / Correct / Leech, filters by specialty, kind, direction, and search. Each row: prompt, answer, correct count, wrong count, last seen, average time, speaker button, "Retry now" button. Bulk select to create a bank or start a test.

### 10.8 Banks and Test Runner

Banks page lists saved rules with live counts. "Wrong-only test" is a built-in bank that cannot be deleted. Test Runner is the session runner in `wrong_test` mode: hints disabled, timer visible, score shown at the end with per-item breakdown and an offer to make a new bank from the misses.

## 11. Time tracking (persistence guarantees)

| Metric | Source of truth | Survives restart |
|---|---|---|
| Time per question | `attempts.time_ms` from client timer with visibility pause | yes |
| Session duration | `min(ended_at, last_heartbeat_at) - started_at`; unended sessions use last heartbeat | yes, loses at most 30 s |
| Total study time | SUM of session durations | yes |
| Server current uptime | `now - runtime_log.process_started_at` of current row | n/a |
| Server lifetime runtime | SUM over `runtime_log` of `last_heartbeat_at - process_started_at` | yes, loses at most 30 s per crash |
| Restarts | COUNT of `runtime_log` rows minus 1 | yes |

Backend lifespan task updates the current `runtime_log` row every `MEDLINGO_HEARTBEAT_SECONDS` and sets `ended_cleanly=1` on graceful shutdown. `test_persistence_restart.py` MUST start the app twice against the same temp DB and assert two rows and correct totals.

## 12. Scripted patient encounters

YAML schema:

```yaml
id: urology_dysuria_intake
title_en: "Painful urination intake"
title_es: "Consulta por dolor al orinar"
specialty: urology
difficulty: 2
start: n1
nodes:
  - id: n1
    patient_es: "Doctor, me arde cuando orino desde hace tres días."
    patient_en: "Doctor, it burns when I urinate, for three days now."
    options:
      - { id: a, es: "¿Ha notado sangre en la orina?", en: "Have you noticed blood in your urine?", correct: true, next: n2, feedback_en: "Good: screening for hematuria." }
      - { id: b, es: "¿Tiene dolor en la rodilla?", en: "Do you have knee pain?", correct: false, feedback_en: "Unrelated to the complaint." }
      - { id: c, es: "Tome más café.", en: "Drink more coffee.", correct: false, feedback_en: "Caffeine can irritate the bladder." }
  - id: n2
    ...
  - id: end
    terminal: true
    summary_en: "..."
    summary_es: "..."
```

Validation at ingest: exactly one correct option per non-terminal node, every `next` resolves, no cycles, reachable terminal. The player shows the patient line, speaks it in Spanish automatically, and shows options in Spanish with a "Show English" toggle per option (counts as a hint). Each node answer is recorded as an `encounter` item attempt.

The `ai_patient` plugin (disabled) adds a "Free chat" tab on the encounter page: the LLM plays a patient given the encounter's specialty and a persona, the user types Spanish, and after 12 turns or "End visit" the plugin returns a rubric-scored feedback (grammar, terminology, empathy phrases) using `rubric.py`. No progress rows are written by the plugin except an `attempts` row of kind `encounter_ai` (OPTIONAL).

## 13. Plugin system

### 13.1 Backend contract (`plugins/base.py`)

```python
class Plugin(ABC):
    id: str
    version: str
    def configure(self, settings: dict) -> None: ...
    def register_routes(self, app: FastAPI) -> None: ...          # mount under /api/plugins/{id}
    def register_question_types(self) -> dict[str, type[BaseGenerator]]: return {}
    def register_data_sources(self) -> list[type[BaseSource]]: return []
    def register_tts_providers(self) -> list[type[TTSProviderBase]]: return []
    def frontend_manifest(self) -> dict: return {}   # { "modules": ["ai_patient/ChatPanel"], "widgets": [], "questionTypes": [] }
```

`loader.py` reads `plugins.toml`, imports `app.plugins.<id>.plugin:PLUGIN`, calls `configure` with the table and env, and registers. A plugin that raises on import is logged and skipped; the app MUST still start.

### 13.2 Frontend contract (`registry/plugins.ts`)

Plugins ship React modules under `frontend/src/plugins/<id>/`. `GET /api/plugins` tells the frontend which to lazy-load (`import()` with Vite glob). Modules can register question type components, dashboard widgets, and settings panels through the three registries.

### 13.3 Shipped plugins

- `cloud_tts`: provider interface with `synthesize(text, lang, voice) -> bytes`; caches MP3 to `data/audio_cache/<sha1>.mp3` and records in `audio_cache`. Google, Azure, ElevenLabs implementations with unit tests using mocked HTTP.
- `ai_patient`: provider interface `chat(messages) -> str`; OpenAI, Anthropic, Ollama implementations with mocked tests. Rubric scoring is deterministic string analysis plus one LLM call for corrections.

Both have a README with enable steps and expected costs.

## 14. Performance and memory budget

- Backend idle RSS < 150 MB; never load whole tables into Python lists. Use `LIMIT` and `ORDER BY random()` within filtered subsets for sampling.
- Batches of 20 items per request; frontend keeps at most 2 batches in memory.
- Frontend initial JS < 350 KB gzipped; Recharts and dnd-kit code-split by route.
- Review and term lists use pagination (server) and virtualization for > 200 rows.
- Seed DB < 60 MB. Run `VACUUM` at the end of ingest.
- API p95 latency for `/sessions` (creating 20 items) < 300 ms on a laptop.

## 15. Testing and self-verification (mandatory before handoff)

### 15.1 Backend unit tests (pytest, coverage >= 85% on `app/engine` and `ingest`)

- `test_normalize.py`: accent fold, article optionality, near-miss threshold, `¿` handling.
- `test_templates.py`: `{DET}`, `{INDEF}`, `{ADJ}`, `{PL}` for m/f/sg/pl including irregulars ("el agua", "la mano"), unknown gender raises.
- `test_distractors.py`: 3 unique distractors, none share 4-char prefix, Levenshtein >= 3, fallback across specialties.
- `test_scheduler.py`: SM-2 transitions, wrong resets, mode selection queries against a seeded temp DB, wrong_test returns fewer when fewer exist.
- `test_generators.py`: every kind produces a valid payload against its Pydantic schema, deterministic given the same fingerprint.
- `test_gender.py`: heuristic accuracy >= 90% on a labeled fixture of 200 nouns.
- `test_specialty_map.py`: tree prefixes and ICD codes map as in the table.
- `test_dedupe.py`.

### 15.2 Backend integration tests (TestClient, temp DBs)

- Create session (each mode), fetch next, post attempts, verify `item_stats` and `daily_stats` updates, end session, stats endpoints return consistent totals.
- Banks CRUD and preview count equals actual session size.
- Encounters: every seed encounter loads and validates.
- `test_persistence_restart.py`: two app lifespans on the same user DB; assert `runtime_log` has 2 rows and `/runtime.total_runtime_s` >= sum of both.
- Seed DB is read-only: an attempted write raises.

### 15.3 Ingestion test

`test_build_bank_fixtures.py` runs `build_bank --offline` into a temp path and asserts all Section 7.9 offline thresholds and that `bank_report.md` exists with the pass/fail table.

### 15.4 Frontend tests

- vitest: `normalize.ts` mirrors backend behavior on a shared JSON case list (`tests/shared/normalize_cases.json` used by both pytest and vitest), timer store pauses on visibility hidden, TTS voice selection order.
- Playwright `smoke.spec.ts`: setup -> 10-question learn session in urology covering at least mcq, fill_blank, drag_slot, drag_order -> uses Hint once and Give Up once -> summary shows 10 answered -> Dashboard shows nonzero total time -> Review Wrong tab lists the given-up item -> create wrong-only test -> complete it.
- Playwright `restart_persistence.spec.ts`: record totals, stop server, start server, assert totals unchanged and restart count incremented.
- Playwright runs with Web Speech stubbed (`window.speechSynthesis` mock) and asserts `speak` was called with Spanish text when the speaker button is clicked.

### 15.5 Manual QA script (agent performs and records results in the handoff report)

1. `make setup && make ingest && make run`; open `http://localhost:8000`. Page loads under 2 s, no console errors.
2. Start Learn, General medicine, EN -> ES, 15 questions. Confirm each kind appears at least once across two sessions.
3. Click speaker on a Spanish term; audible or mocked call logged.
4. Use Hint; hint text appears and a hint badge shows in feedback.
5. Use Give Up; answer revealed, marked wrong, appears in Review > Wrong.
6. Drag-order a sentence; keyboard-only completion also works.
7. Finish session; summary shows accuracy, time, XP.
8. Dashboard: total time, runtime card, radar, heatmap render with data.
9. Create a bank "Urology wrong only" and run it; hints disabled.
10. Stop the server (Ctrl+C), start again; dashboard totals identical, restarts = 1 more.
11. Switch theme; persists after reload.
12. Settings: change TTS voice and daily goal; persists.
13. Enable `cloud_tts` with a fake key; app still boots and shows a clear error toast only when synthesis is attempted.
14. `make ingest` again; progress unchanged, seed_meta.built_at updated.

### 15.6 `scripts/verify.sh` (what `make verify` runs, MUST exit 0)

```
set -euo pipefail
make lint
make test                          # backend + frontend unit/integration
make ingest-offline                # proves the pipeline runs without network
python -m ingest.report --check    # thresholds
make build
make e2e                           # Playwright on a temp port and temp DBs
python scripts/check_budget.py     # bundle size < 350 KB gz, seed DB < 60 MB
echo "VERIFY OK"
```

If online ingestion was performed, also run `make ingest` and re-check thresholds at the online level.

## 16. Definition of done and handoff report

Done means all of the following are true:

- `make setup`, `make ingest` (or `ingest-offline`), `make run` work from a clean clone on macOS, Linux, and Windows (WSL or PowerShell via `run.sh`/`run.ps1`).
- `make verify` prints `VERIFY OK`.
- `data/bank_report.md` shows all thresholds passing.
- Every file in Section 4 exists and is non-empty.
- README explains install, run, ingest, plugins, data attribution, and how to reset progress.
- `docs/HANDOFF_REPORT.md` is completed using this template:

```
# MedLingo handoff report
Build date:
Commit:
Network available during ingest: yes/no
Sources ingested and versions:
Bank counts (from bank_report.md): terms, sentences, encounters, per specialty
Thresholds: pass/fail table
make verify output (last 30 lines):
Coverage: backend %, frontend %
Manual QA script results: 14 numbered lines with PASS/FAIL and notes
Known limitations:
Decisions taken not covered by the spec (mirror of docs/DECISIONS.md):
Suggested next extensions:
```

## 17. Post-delivery editing guide (also saved as `docs/EXTENDING.md`)

| To add | Touch only |
|---|---|
| A specialty | `ingest/curated/specialties.yaml` (id, names, color, icon), a rule row in `specialty_map.py`, new `templates/<id>.yaml`, `phrases/<id>.yaml`, `encounters/<id>.yaml`; run `make ingest` |
| Terms or fixes | `term_overrides.yaml` (add, correct, blacklist), `gender_overrides.yaml`, `regional_notes.yaml`; run `make ingest` |
| A sentence template | one YAML entry; the renderer and generators pick it up automatically |
| A question type | `engine/generators/<kind>.py` registered in `generators/__init__.py`, Pydantic payload in `schemas/questions.py`, React component in `questionTypes/<Kind>.tsx` registered in `registry/questionTypes.ts`, one unit test each side |
| A data source | subclass `BaseSource` in `ingest/sources/`, add to the source list in `build_bank.py`, add a fixture and attribution entry |
| A dashboard widget | component in `dashboard/widgets/`, register in `registry/dashboardWidgets.ts`, optional stats endpoint in `api/stats.py` |
| A plugin | folder under `app/plugins/<id>/` with `plugin.py` exposing `PLUGIN`, optional `frontend/src/plugins/<id>/`, entry in `plugins.toml` |
| A user profile UI | pages only; the schema already scopes by `profile_id` |
| A DB field | Alembic revision in `alembic/versions/`, model, schema; never edit an existing revision |

Rules for editors: never write to the seed DB at runtime; keep every UI string in `frontend/src/i18n/en.json` and `es.json` (UI language toggle is OPTIONAL but strings MUST be centralized); keep tests green with `make verify` before merging.

## 18. Licensing and attribution (`docs/ATTRIBUTION.md`)

- Wikidata: CC0 1.0. Cite "Wikidata contributors".
- DeCS: BIREME/PAHO/WHO. Include the DeCS attribution block and version; user to confirm current terms of use.
- MedlinePlus: U.S. National Library of Medicine, public domain; follow MedlinePlus linking and attribution guidelines, do not imply endorsement.
- Wiktionary: CC BY-SA 3.0; include attribution and note share-alike applies to derived gender/plural data.
- Curated content in this repo: MIT (code) and CC BY 4.0 (YAML content).
- The About page in the app MUST display these attributions and the seed build date.

## 19. Risks and required behavior when blocked

| Risk | Required behavior |
|---|---|
| Wikidata SPARQL timeouts | reduce page size to 2000, retry 5 times with exponential backoff, then fall back to fixtures for that class and record it |
| DeCS API changes or unreachable | use fixture; report |
| Spanish gender unknown for many nouns | heuristic + Wiktionary + overrides; report coverage; templates needing agreement skip rather than guess |
| Bad or archaic translations in sources | `term_overrides.yaml` blacklist; the in-app "Report content issue" button appends to `docs/content_issues.jsonl` for later curation |
| No Spanish voice on the user's OS | toast with OS-specific instructions; app remains usable |
| Windows path and process handling | `run.ps1` provided; Makefile uses python for cross-platform file operations |
| Time zones | client sends `client_day` for `daily_stats`; all storage UTC |

End of specification.
