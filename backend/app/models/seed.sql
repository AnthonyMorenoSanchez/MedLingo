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
