from pathlib import Path
if input('Delete all local study progress? Type DELETE: ')=='DELETE':
    root=Path(__file__).resolve().parents[1]
    for suffix in ('','-wal','-shm'):(root/('data/user.sqlite'+suffix)).unlink(missing_ok=True)
    print('Progress deleted. Restart MedLingo to create a new profile.')
