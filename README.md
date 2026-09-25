# MedLingo

A local English ↔ Spanish medical vocabulary trainer with persistent progress, six exercise formats, scripted patient encounters, personal review banks, and a progress dashboard. No ads, lives, subscriptions, or runtime API keys in the default configuration.

**Status:** working local application, with known differences from the full supplied specification documented in [docs/DECISIONS.md](docs/DECISIONS.md). See [docs/HANDOFF_REPORT.md](docs/HANDOFF_REPORT.md) for actual verification results. Imported content has not received a complete bilingual clinical review.

## Start — updated Windows and WSL launchers

Requires Python 3.11+ (3.11 or 3.12 recommended). Node.js and Make are no longer required to run the bundled build.

Windows PowerShell, in the extracted medlingo folder:

```powershell
.\run.ps1 setup
.\run.ps1 run
```

If script execution is blocked, use `py -3 scripts/manage.py setup` and `py -3 scripts/manage.py run`.

WSL:

```bash
bash run.sh setup
bash run.sh run
```

Open **http://localhost:8000**. Paths containing spaces are supported. Existing `make` commands remain available for development. See [UPDATE_GUIDE.md](UPDATE_GUIDE.md) for safe progress migration, offline voice packs, microphone input, Ollama setup, cloud keys, and profiles. See [UPDATE_TEST_REPORT.md](UPDATE_TEST_REPORT.md) for this update's verification. Older plugin instructions below describe legacy extensions; the new AI and speech controls are built into Settings and do not require enabling those plugins.


## Study

Choose a specialty, direction, question count, and exercise types. Use the speaker buttons for device speech. Install a Spanish OS voice for offline pronunciation. Learn sessions support hints and Give Up; wrong-only tests disable hints. Typed answers tolerate missing accent marks while flagging them for practice. Fuzzy near-matches are still incorrect.

Review has Wrong, Correct, and Needs extra practice tabs, filters, paging, and selection. Save a dynamic rule as a bank or retry selected items. Encounters practice respectful intake communication. Settings stores your theme, daily goal, voice, and speech provider in SQLite.

## Content

```bash
make ingest-offline  # use bundled snapshots and curated YAML
make ingest          # refresh Wikidata/MedlinePlus with fallback, then rebuild
```

Stop the running server before replacing content so it opens the new seed file on restart. Progress is stored separately and is not deleted by ingestion. Frozen questions keep their original text. Read `data/bank_report.md` for thresholds, samples, and source counts. Use the feedback panel's report button to append to `docs/content_issues.jsonl`. External source outages and limitations are recorded in the handoff.

## Development and tests

```bash
make dev              # API 8000, Vite 5173
make lint
make test
cd frontend && npx playwright install chromium && cd ..
make verify
```

The browser suite uses disposable databases, an isolated server on 8765, and a test-only process-control server on 8766. Those ports must be free. The control server is never part of normal production startup. Test snapshots and screenshots go under `data/` and `frontend/test-results/`.

## Plugins

Both optional plugins are disabled in `plugins.toml`. See their README files under `backend/app/plugins/` for enable instructions. Remote speech and AI services require keys and may charge for use. Ollama requires a separate local model installation. No model or paid API is required for the default application.

## Data, backups, and reset

Back up `data/user.sqlite` after stopping the server. If backing up while it runs, use SQLite's backup API rather than copying the main file alone. `make clean-user` asks you to type DELETE before removing progress. Deleting content snapshots does not delete progress, but a seed database is needed to run the application.

Configuration is in `.env` and `plugins.toml`; `.env.example` lists available settings. Never commit real provider keys. Code is MIT licensed; data licenses are separate, see [docs/ATTRIBUTION.md](docs/ATTRIBUTION.md).
