# MedLingo — profiles, offline voices, and AI practice

## Start on Windows (no Make or WSL required)

Install Python 3.11 or 3.12 with **Add Python to PATH** enabled. Extract this package and open PowerShell in its `medlingo` folder:

```powershell
.\run.ps1 setup
.\run.ps1 run
```

Open http://localhost:8000. Keep the terminal open. Ctrl+C stops the app.
If PowerShell blocks `.ps1` scripts, the equivalent commands require no execution-policy change:

```powershell
py -3 scripts/manage.py setup
py -3 scripts/manage.py run
```

Paths containing spaces are supported. Node.js is only needed to rebuild the frontend; the built frontend is included.

## Start in WSL

Use a WSL folder such as `~/MedLingo` for best filesystem performance. Install Python 3.11+ and its venv support. From the extracted `medlingo` directory:

```bash
bash run.sh setup
bash run.sh run
```

Do not copy a Windows `.venv` into WSL or the reverse. Each environment needs its own virtual environment. The Makefile also now quotes Python paths correctly.

## Preserve existing progress when upgrading

Stop the old app first. Keep a backup of its entire `data` directory. Extract the update into a separate folder, then copy the old `data/user.sqlite` into the new package's `data` directory while both apps are stopped. If SQLite `-wal`/`-shm` files remain after stopping, use a SQLite backup rather than copying only the main file. Keep your old `.env` only if its paths still point to the intended data files. Do not copy the old `.venv` or old frontend build over the update.

Startup migrates the old database in place. Its existing learner remains **Default**; new profiles start with independent history. Back up before migration: the older version is not a supported downgrade target for an upgraded database.

## Profiles and fresh questions

At first launch choose Default or create a named profile. Switch users from the top bar. Profiles keep separate settings, attempts, banks, dashboards, conversations, generated material, and AI keys. They are local user labels, not password-protected accounts.

New practice shuffles content and exercise formats. A source is reserved when a session is created, so opening multiple sessions cannot assign the same example again. Once assigned, that term/example is excluded from all formats and both translation directions in new practice. The same vocabulary may occur inside a different sentence. Matching ignores case and punctuation in existing question content.

Reviews, correct drills, wrong-only tests and review banks explicitly reuse questions. Due review contains due questions only; it no longer pads the session with new questions. Scripted encounters require **Review this encounter** to replay an assigned case. If fewer fresh examples remain, the session contains only those available; if none remain, use Review, broaden filters, or generate material with a configured model. Never silently recycles an exhausted bank.

## Offline speech and microphone

Windows device voices are usable without additional Python packages when the browser exposes them as local voices. English and Spanish are selected independently. An English voice is never substituted for missing Spanish speech. Install a matching Windows speech language pack or use Piper if no matching device voice is exposed.

For consistent Windows/WSL offline speech, download the optional packs once:

```powershell
.\run.ps1 voices
```

WSL:

```bash
bash run.sh voices
```

This installs Piper, the optional Edge client, and Vosk, then downloads English male/female and Spanish Mexican male/Argentine female packs plus the small Spanish transcription model. Initial installation needs internet and disk space; subsequent Piper playback and Vosk microphone transcription run locally without internet. Model binaries are downloaded separately and are not inside this ZIP.

Restart the app. Under **Settings → Pronunciation voices**, select **Offline Piper voices** separately for English and Español, choose a downloaded voice, and save. Additional Spain Spanish and British English choices are listed; these need their own downloads.

To list all English and Spanish packs or select specific packs:

```powershell
.\.venv\Scripts\python.exe scripts/setup_voices.py --list
.\.venv\Scripts\python.exe scripts/setup_voices.py --voices en_GB-alan-medium es_ES-davefx-medium
```

In WSL replace `.\.venv\Scripts\python.exe` with `.venv/bin/python`. You can also put trusted Piper `.onnx` and matching `.onnx.json` files in `data/voices`; filenames should start with a locale such as `es_MX-`. The app discovers them. Packs retain their upstream model cards and licenses; availability of accents depends on the voice catalog. Mexico is listed as Mexico, not as a Central American accent. The included catalog offers Mexican, Argentine, and Spain Spanish; Central American options are available through the optional online catalog where supported.

Microphone input uses browser permission and sends a mono WAV to the local backend, not to a transcription cloud. Spanish transcription is editable before submission; recordings are capped at one minute. Speech output can be enabled separately from the microphone.

## Optional free online voices

Choose **Online Edge voices**, then **Load online voices**. Pick a voice per language and save. The catalog includes gender and locale labels, including Central American and South American options when available. This uses the community [edge-tts client](https://github.com/rany2/edge-tts) to access Microsoft's online speech service without an API key. It is an optional, unofficial integration with no availability guarantee. Spoken text leaves the computer when you select it. It does not automatically replace offline speech on failure.

## Ollama setup and recommendation

Windows:

```powershell
.\run.ps1 ollama
```

WSL:

```bash
bash run.sh ollama
```

The script detects visible RAM, available memory, OS/WSL, and GPU names when available. It offers installation (winget on Windows, Ollama's installer on Linux/WSL), starts a local server if needed, recommends a model, and asks before downloading. If winget is unavailable, it gives the official Windows installer link. Linux installation may ask for sudo credentials.

The conservative catalog uses Qwen3 0.6B, 1.7B, 4B, or 8B depending on memory headroom. For 16 GB RAM with at least 6 GB free, **qwen3:4b** is the default; **qwen3:1.7b** is a lighter alternative. WSL may see a lower RAM cap and recommend a smaller model. These are practical defaults, not a claim that one model is universally best. You may override the recommendation or choose an installed Ollama model.

The RX 5700 XT is not in Ollama's documented ROCm support list. CPU execution remains available. Current Ollama also supports Vulkan on Windows/Linux, which may provide acceleration depending on drivers; this package does not force unsupported ROCm overrides or assume that GPU execution is working. Check `ollama ps` while chatting to inspect CPU/GPU usage.

In **Settings → AI connection**, choose Ollama, `http://127.0.0.1:11434`, and your downloaded model, then **Save & test connection**. Settings also lets you list installed models or explicitly download the selected model.

Running the app and Ollama both on Windows, or both in WSL, is simplest. A WSL app cannot always reach Windows Ollama through localhost under NAT networking. For mixed environments, use WSL mirrored networking where supported or a deliberately configured local address; this update does not open firewall ports or expose Ollama automatically. Default app binding remains 127.0.0.1.

## Cloud and other model servers

Settings supports OpenAI, Anthropic, Gemini, Groq, Mistral, OpenRouter, and generic OpenAI-compatible endpoints (such as a local LM Studio server). Enter a model ID available to your account and your key, then save/test. Provider APIs and model catalogs change; models are editable rather than fixed to a stale ID.

Keys are stored locally in `data/user.sqlite`, are write-only through the API, and are never included in settings responses. The database is not encrypted; protect its backups. Changing the provider or endpoint clears the old key unless you supply a new one. Cloud use sends conversation text and generated-example requests to the selected provider and may incur charges. No keys are supplied with this package.

## Conversation and clinical encounters

**AI conversation** opens text-first practice with optional spoken output and offline Spanish microphone input. Ordinary conversation gives language corrections turn by turn. Clinical role-play stays in the fictional patient's character, responds to each learner message, and gives a final language-practice rubric when you select **End & get feedback**. The rubric covers clarity/grammar, vocabulary, empathy/register, and relevant information gathering, each out of 25. The model must cite examples and corrections; this is formative feedback, not validated clinical scoring.

Conversations persist per profile. Resume one from the selector. Sessions are limited to 20 learner turns to keep context manageable for small local models. Transcript speech buttons let you select English for feedback and Spanish for patient dialogue; mixed-language text is not automatically segmented.

**Generate 10 fresh examples** in study setup is available only after model configuration. It requires a functioning model connection; failures do not create substitute material. Bilingual JSON is structurally validated and exact duplicate pairs are excluded before saving to the active profile. Generated translations are not clinically or linguistically certified and can be reported using the existing content-issue action.

## Implementation references

- [Ollama Windows setup](https://docs.ollama.com/windows)
- [Ollama hardware support](https://docs.ollama.com/gpu)
- [Qwen3 4B model](https://ollama.com/library/qwen3:4b)
- [Piper local speech](https://github.com/OHF-Voice/piper1-gpl)
- [Piper voice catalog](https://huggingface.co/rhasspy/piper-voices)
- [Vosk models](https://alphacephei.com/vosk/models)
- [OpenAI Chat Completions](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)
- [Anthropic Messages](https://platform.claude.com/docs/en/api/messages)

See `UPDATE_TEST_REPORT.md` for verified behavior and limits. Original seed-content limitations in `docs/HANDOFF_REPORT.md` remain; this update does not replace the original curated content bank.
