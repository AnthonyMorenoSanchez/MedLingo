Post-delivery editing guide (also saved as `docs/EXTENDING.md`)

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
