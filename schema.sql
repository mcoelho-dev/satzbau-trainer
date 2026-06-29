CREATE TABLE patterns (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE sentences (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    german_text     TEXT NOT NULL,
    translation_pt  TEXT NOT NULL,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE sentence_patterns (
    sentence_id  INTEGER NOT NULL,
    pattern_id   INTEGER NOT NULL,
    PRIMARY KEY (sentence_id, pattern_id),
    FOREIGN KEY (sentence_id) REFERENCES sentences(id) ON DELETE CASCADE,
    FOREIGN KEY (pattern_id)  REFERENCES patterns(id)  ON DELETE CASCADE
);

CREATE TABLE chunks (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    sentence_id  INTEGER NOT NULL,
    position     INTEGER NOT NULL,
    text         TEXT NOT NULL,
    FOREIGN KEY (sentence_id) REFERENCES sentences(id) ON DELETE CASCADE,
    UNIQUE (sentence_id, position)
);

CREATE TABLE attempts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    sentence_id  INTEGER NOT NULL,
    is_correct   INTEGER NOT NULL CHECK (is_correct IN (0, 1)),
    attempted_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (sentence_id) REFERENCES sentences(id) ON DELETE CASCADE
);