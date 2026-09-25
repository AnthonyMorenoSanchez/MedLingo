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

CREATE TABLE session_items (session_id INTEGER NOT NULL REFERENCES sessions(id), item_id INTEGER NOT NULL REFERENCES question_items(id), position INTEGER NOT NULL, PRIMARY KEY(session_id,item_id), UNIQUE(session_id,position));
CREATE UNIQUE INDEX idx_attempt_once ON attempts(session_id,item_id);
ALTER TABLE attempts ADD COLUMN profile_id INTEGER NOT NULL DEFAULT 1 REFERENCES profiles(id);
ALTER TABLE item_stats ADD COLUMN profile_id INTEGER NOT NULL DEFAULT 1 REFERENCES profiles(id);
