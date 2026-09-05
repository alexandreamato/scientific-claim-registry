-- SCR registry — canonical SQLite schema (v0.1)
-- Centralizes claims + evidence + relations + curators + version history + consensus.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS claims (
  id                  TEXT PRIMARY KEY,         -- SCR-LIP-000001
  domain              TEXT,                     -- LIP
  version             TEXT DEFAULT '1.0',
  claim_type          TEXT,
  knowledge_state     TEXT,                     -- speculative|emerging|probable|established|foundational
  evidence_confidence TEXT,                     -- GRADE: high|moderate|low|very_low
  statement           TEXT NOT NULL,
  statement_pt        TEXT,
  population          TEXT, condition TEXT, exposure TEXT, comparator TEXT, outcome TEXT, scope TEXT,
  gaps                TEXT,
  primary_source      TEXT,
  in_registry         INTEGER DEFAULT 1,        -- 1 = published registry; 0 = staged/held-out
  license             TEXT DEFAULT 'CC-BY-4.0',
  created             TEXT, updated TEXT,
  history_json        TEXT,                     -- full change-log (R-VER-5), verbatim
  provenance_json     TEXT,                     -- full provenance object, verbatim
  raw_json            TEXT NOT NULL             -- LOSSLESS: the complete claim object (export source of truth)
);

CREATE TABLE IF NOT EXISTS evidence (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  claim_id       TEXT NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
  ref            TEXT,                          -- DOI:.. | PMID:.. | filename
  stance         TEXT,                          -- supporting|contradicting|mentioning
  study_design   TEXT,
  n              INTEGER,
  risk_of_bias   TEXT,                          -- low|moderate|high|unclear
  year           INTEGER,
  amato_authored INTEGER DEFAULT 0,
  note           TEXT,
  grade          TEXT,                          -- GRADE per source: high|moderate|low|very_low (R-CLM-11/13)
  grade_source   TEXT,                          -- e.g. 'bib_curated' when capped to the curated Oxford grau
  quote          TEXT,                          -- verbatim span grounding the stance (R-AI-13)
  extraction_confidence TEXT,                   -- high|moderate|low: confidence the source was read right ≠ GRADE (R-CLM-17)
  verified       INTEGER DEFAULT 0,             -- 1 iff verification.verdict='verified' (R-AI-14)
  verify_verdict TEXT,                           -- verified|disputed|unverified (R-AI-14)
  verify_json    TEXT,                           -- full verification object (lossless)
  title          TEXT, authors TEXT, journal TEXT
);

CREATE TABLE IF NOT EXISTS relations (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  claim_id    TEXT NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
  rel_type    TEXT,                             -- causes|associates|contradicts|co_occurs|...
  target_id   TEXT REFERENCES claims(id),       -- resolved link (nullable until graph is wired)
  target_hint TEXT,                             -- topic hint before resolution
  strength    REAL
);

CREATE TABLE IF NOT EXISTS curators (
  id    INTEGER PRIMARY KEY AUTOINCREMENT,
  name  TEXT,
  orcid TEXT UNIQUE,
  role  TEXT
);

CREATE TABLE IF NOT EXISTS claim_curators (
  claim_id   TEXT REFERENCES claims(id) ON DELETE CASCADE,
  curator_id INTEGER REFERENCES curators(id) ON DELETE CASCADE,
  PRIMARY KEY (claim_id, curator_id)
);

-- version history (the "evolution of belief" — empty until claims are revised)
CREATE TABLE IF NOT EXISTS claim_versions (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  claim_id   TEXT REFERENCES claims(id) ON DELETE CASCADE,
  version    TEXT, date TEXT, change TEXT, confidence TEXT, by_orcid TEXT, rationale TEXT
);

-- living consensus layer (empty until the expert panel votes)
CREATE TABLE IF NOT EXISTS consensus_votes (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  claim_id   TEXT REFERENCES claims(id) ON DELETE CASCADE,
  curator_id INTEGER REFERENCES curators(id),
  vote       TEXT CHECK (vote IN ('endorse','dissent','qualify','uncertain')),
  weight     REAL DEFAULT 1.0,
  comment    TEXT,
  created    TEXT
);

-- author's IIT2 theory, staged out of the registry (per author)
CREATE TABLE IF NOT EXISTS held_out_theory (
  id     INTEGER PRIMARY KEY AUTOINCREMENT,
  topic  TEXT, reason TEXT, ref TEXT
);

CREATE INDEX IF NOT EXISTS idx_ev_claim  ON evidence(claim_id);
CREATE INDEX IF NOT EXISTS idx_rel_claim ON relations(claim_id);
CREATE INDEX IF NOT EXISTS idx_claim_state ON claims(knowledge_state);

-- convenience view: one row per registry claim with evidence counts
CREATE VIEW IF NOT EXISTS v_claim_summary AS
SELECT c.id, c.claim_type, c.knowledge_state, c.evidence_confidence,
       (SELECT COUNT(*) FROM evidence e WHERE e.claim_id = c.id) AS n_evidence,
       (SELECT COUNT(*) FROM evidence e WHERE e.claim_id = c.id AND e.amato_authored = 1) AS n_amato,
       c.statement
FROM claims c WHERE c.in_registry = 1 ORDER BY c.id;

-- ===== Question-centric layer (SQ) =====
-- Scientific questions are the primary navigable object; claims are evidence linked underneath.
CREATE TABLE IF NOT EXISTS questions (
  id               TEXT PRIMARY KEY,      -- SQ-LIP-0001
  domain           TEXT,
  text             TEXT NOT NULL,
  text_pt          TEXT,
  knowledge_state  TEXT,
  current_answer   TEXT,                  -- cautious, evidence-bounded; AI does not opine
  current_answer_pt TEXT,
  major_uncertainty TEXT,
  major_uncertainty_pt TEXT,
  version          TEXT DEFAULT '1.0',
  created          TEXT, updated TEXT,
  tags_json        TEXT, keywords_json TEXT,
  first_mention_json TEXT,
  history_json     TEXT,                  -- full per-question change-log, verbatim
  raw_json         TEXT NOT NULL          -- LOSSLESS: the complete question object (export source of truth)
);
-- alternative phrasings of the same question (R-Q-5) — projection for search/routing
CREATE TABLE IF NOT EXISTS question_phrasings (
  question_id TEXT REFERENCES questions(id) ON DELETE CASCADE,
  lang        TEXT,                       -- en|pt
  seq         INTEGER,
  text        TEXT,
  PRIMARY KEY (question_id, lang, seq)
);
-- versioned answers (each material change = a new commit)
CREATE TABLE IF NOT EXISTS question_versions (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  question_id      TEXT REFERENCES questions(id) ON DELETE CASCADE,
  version          TEXT, date TEXT, knowledge_state TEXT,
  current_answer   TEXT, whats_changed TEXT,
  supporting_count INTEGER, contradicting_count INTEGER, other_count INTEGER,
  major_uncertainty TEXT, reviewed_by_human INTEGER DEFAULT 0
);
-- claim <-> question links (a claim may answer several questions: it is a graph, not a tree)
CREATE TABLE IF NOT EXISTS claim_questions (
  question_id TEXT REFERENCES questions(id) ON DELETE CASCADE,
  claim_id    TEXT REFERENCES claims(id) ON DELETE CASCADE,
  role        TEXT,                       -- supporting|contradicting|refines|context
  PRIMARY KEY (question_id, claim_id)
);
CREATE INDEX IF NOT EXISTS idx_cq_question ON claim_questions(question_id);
CREATE INDEX IF NOT EXISTS idx_cq_claim    ON claim_questions(claim_id);

-- ===== ID allocation (R-ALLOC): temp(draft) -> validated -> final, com aliases/redirect =====
CREATE TABLE IF NOT EXISTS id_counters (
  scope    TEXT PRIMARY KEY,     -- 'SCR-LIP' (canônico) | 'SCR-LIP-D' (draft) | 'SQ-LIP' | 'SQ-LIP-D'
  next_seq INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS id_requests (
  temp_id      TEXT PRIMARY KEY, -- ex. SCR-LIP-D000007
  prefix       TEXT, domain TEXT, kind TEXT,         -- kind: claim|question
  status       TEXT DEFAULT 'draft',                 -- draft|published|merged|rejected
  canonical_id TEXT, note TEXT, source TEXT,
  created      TEXT, decided TEXT
);
CREATE TABLE IF NOT EXISTS id_aliases (
  from_code TEXT PRIMARY KEY,    -- temp ou código antigo
  to_code   TEXT,               -- canônico/destino (301)
  kind      TEXT,               -- promote|merge
  created   TEXT
);

-- ===== Sync bookkeeping: the DB is a deterministic, LOSSLESS rebuild of the JSON seeds =====
-- `meta` stores each seed file's top-level wrapper (everything except the big list) so export
-- reproduces it verbatim. `sync_state` records the last standardized sync + parity result.
CREATE TABLE IF NOT EXISTS meta (
  file TEXT PRIMARY KEY,   -- 'claims' | 'questions'
  wrapper_json TEXT        -- the wrapper object with the record list removed
);
CREATE TABLE IF NOT EXISTS sync_state (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  last_sync TEXT, parity_ok INTEGER, claims_n INTEGER, questions_n INTEGER, detail TEXT
);

-- ===== Layer 1: surveillance loop (ingest) =====
CREATE TABLE IF NOT EXISTS ingest_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, question_id TEXT, query TEXT,
  found INTEGER, new_n INTEGER, ran_at TEXT
);
CREATE TABLE IF NOT EXISTS ingest_candidates (
  id INTEGER PRIMARY KEY AUTOINCREMENT, question_id TEXT,
  source TEXT, ext_id TEXT, doi TEXT, pmid TEXT, title TEXT, year INTEGER, abstract TEXT,
  stance TEXT DEFAULT 'unclassified',          -- supporting|contradicting|refines|irrelevant|unclassified
  proposed_statement TEXT, temp_id TEXT,
  status TEXT DEFAULT 'pending',                -- pending|drafted|merged|rejected
  created TEXT,
  UNIQUE(question_id, ext_id)
);
