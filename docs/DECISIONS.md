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
