# Update verification — 2026-09-19

## Implemented

- Local profile picker, creation and switching; per-profile settings, learning records, banks, generated content, AI credentials and conversation history.
- Random content/format selection with source-level exclusions across formats and translation directions. Reservations also prevent duplicates across concurrently opened new-practice sessions. Review modes remain explicit.
- Separate English/Spanish voice choices. Device speech strictly matches the language and uses local voices only. Optional offline Piper packs and offline Vosk Spanish microphone transcription. Optional online Edge catalog with gender/locale labels.
- Ollama, OpenAI, Anthropic, Gemini, Groq, Mistral, OpenRouter and generic OpenAI-compatible HTTP adapters; profile-scoped keys are not returned by the API.
- Text-first conversation, optional spoken output, saved transcripts, fictional clinical role-play, and end-of-encounter formative language scoring.
- AI-generated bilingual examples with structural validation and duplicate rejection, saved only for the current profile.
- Windows-native and WSL launchers using argument-safe Python subprocesses. Hardware/memory recommendation and opt-in Ollama installation/download helpers.

## Verified in this Linux environment

- **112 backend tests passed.** Includes existing regression tests, profile isolation/ownership, fresh-content exhaustion, cross-format and direction exclusions, review behavior, generated-content validation/deduplication, conversations, credentials, and eight provider wire formats.
- **11 frontend unit tests passed.** Includes matching-language voice selection, rejection of wrong-language fallback, and rejection of remote voices in offline device mode.
- **6 browser scenarios passed.** Profile creation/switching, settings isolation, independent voice selection, AI config persistence, clinical chat and final feedback UI, study/hints/review/testing, scripted encounters, and actual backend restart persistence.
- Python lint/type checks and frontend lint/type checks passed during development; production frontend build succeeded.
- Real offline Piper synthesis succeeded for English (`en_US-lessac-low`, 52,780-byte WAV) and Spanish (`es_MX-ald-x_low`, 107,564-byte WAV). Real local Vosk transcription of the Spanish WAV returned **“hola me duele la cabeza desde ayer”**. The test downloaded models once, then used local model files; synthesis/transcription did not call a cloud API.
- Engine plus ingestion coverage: approximately **95%**. This number does not claim 95% coverage of the new AI/speech service modules.

**Final full verification: `make verify` completed with `VERIFY OK`**, including lint, type checks, tests, offline ingestion, production build, browser scenarios and size checks.

The final command log is `data/update-verify.log`. Browser screenshots are in `data/clinical-preview.png` and `data/settings-profiles-preview.png`.

## Practical limits

- Windows-native installation, real WSL host/guest networking, physical microphone capture, and Radeon 5700 XT acceleration cannot be exercised on this Linux host. Launchers and recommendations were implemented for those environments; GPU performance is not promised.
- Provider integration tests use mocked HTTP responses. No user API keys were supplied, so there were no paid/live model calls. The clinical browser test uses a deterministic mock response; its displayed score is a test fixture, not evidence of model scoring accuracy.
- Live Ollama installation/model inference and live online Edge synthesis have not been verified here. Their optional setup and adapters require the user's machine/network. Missing services produce actionable errors rather than simulated production conversations.
- Piper/Vosk model binaries and Ollama model weights are not included in the ZIP. One-time optional setup requires internet. Downloaded Piper/Vosk models remain offline afterward.
- Default offline Spanish choices cover Mexico/Argentina plus downloadable Spain voices. Central American choices depend on installed device packs or the optional online catalog; the package does not invent unavailable offline accents.
- AI text may mix Spanish dialogue with English corrections. Transcript speech controls let the user choose the matching language; automatic speech uses the Spanish voice for partner replies and does not segment mixed-language text.
- Local profiles do not provide password protection or encryption. API keys are stored in the local user database; backups should be treated accordingly.
- Generated translations and formative clinical-language grades are model outputs, not independently validated medical content or competency scores.
- Original content-bank limitations documented in `docs/HANDOFF_REPORT.md` remain unchanged.
