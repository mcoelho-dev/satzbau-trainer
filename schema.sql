CREATE TABLE exercise_types (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    key             TEXT NOT NULL UNIQUE,
    display_name    TEXT NOT NULL,
    hint_text       TEXT,
    field_schema    TEXT NOT NULL
);

CREATE TABLE patterns (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_type_id  INTEGER NOT NULL,
    name              TEXT NOT NULL,
    description       TEXT,
    FOREIGN KEY (exercise_type_id) REFERENCES exercise_types(id) ON DELETE CASCADE,
    UNIQUE (exercise_type_id, name)
);

CREATE TABLE exercises (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_type_id  INTEGER NOT NULL,
    pattern_id        INTEGER,
    data_json         TEXT NOT NULL,
    created_at        TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (exercise_type_id) REFERENCES exercise_types(id) ON DELETE CASCADE,
    FOREIGN KEY (pattern_id) REFERENCES patterns(id) ON DELETE SET NULL
);

CREATE TABLE attempts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id     INTEGER NOT NULL,
    is_correct      INTEGER NOT NULL CHECK (is_correct IN (0, 1)),
    attempted_at    TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS settings (
    key    TEXT PRIMARY KEY,
    value  TEXT NOT NULL
);