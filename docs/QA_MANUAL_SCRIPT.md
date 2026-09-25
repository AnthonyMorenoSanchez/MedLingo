Manual QA script (agent performs and records results in the handoff report)

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
