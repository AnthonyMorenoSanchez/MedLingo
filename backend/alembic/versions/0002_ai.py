"""Profile-owned AI settings, conversations and generated material."""
from alembic import op
revision = '0002_ai'
down_revision = '0001'
branch_labels = None
depends_on = None

def upgrade():
    op.execute('CREATE TABLE ai_settings (profile_id INTEGER PRIMARY KEY REFERENCES profiles(id), config TEXT NOT NULL)')
    op.execute('CREATE TABLE ai_conversations (id INTEGER PRIMARY KEY, profile_id INTEGER NOT NULL REFERENCES profiles(id), mode TEXT NOT NULL, scenario TEXT NOT NULL, messages TEXT NOT NULL, ended INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL)')
    op.execute('CREATE TABLE generated_content (id INTEGER PRIMARY KEY, profile_id INTEGER NOT NULL REFERENCES profiles(id), en TEXT NOT NULL, es TEXT NOT NULL, specialty_id TEXT NOT NULL, difficulty INTEGER NOT NULL DEFAULT 2, UNIQUE(profile_id,en), UNIQUE(profile_id,es))')

def downgrade():
    for name in ('generated_content','ai_conversations','ai_settings'):
        op.execute('DROP TABLE '+name)
