# Satzbau Trainer

A web app for practicing German word order. Sentences are broken into draggable chunks; the user reconstructs the correct order and gets immediate feedback, with a progress dashboard tracking accuracy per grammar pattern.

## Overview

German word order (Satzbau) follows strict positional rules — V2 in main clauses, verb-final in subordinate clauses, separable verb prefixes moving to the end, and more — that are easy to *know* but hard to *feel* without active practice. This project was inspired by Duolingo's drag-the-words exercise format, which forces a positional decision before submission rather than letting habits from another language's word order slip through.

The app pulls a random sentence from a SQLite database, shuffles its word chunks, and lets the user rebuild it. Every attempt is logged, and a `/stats` dashboard surfaces accuracy broken down by grammar pattern — making it possible to see exactly which structures need more practice.

## What I Practiced

- Relational schema design with normalized many-to-many relationships (`sentences` ↔ `patterns` via a join table)
- SQLite in Python (`sqlite3` module): connections, parameterized queries, `row_factory` for dict-like rows
- Flask: routing, JSON APIs, template rendering
- Vanilla JS DOM manipulation for the interactive chunk-reordering UI
- Writing analytical SQL (aggregation, `JOIN`s across three tables, `GROUP BY`) to power the progress dashboard
- Separating concerns: pure logic (`core.py`) decoupled from the web layer (`app.py`)

## Commands

```bash
# install dependencies
pip install flask

# create and seed the database
python seed.py

# run the app
python app.py
```

Then open `http://127.0.0.1:5000` in a browser. Progress dashboard is at `/stats`.

## Files

- `schema.sql` — database schema: `sentences`, `chunks`, `patterns`, `sentence_patterns`, `attempts`
- `seed.py` — populates the database with curated sentences across 9 German word order patterns
- `core.py` — core logic: loading sentences, shuffling chunks, validating answers, recording attempts, stats queries
- `app.py` — Flask routes serving the exercise and the dashboard
- `templates/index.html` — main exercise interface
- `templates/stats.html` — progress dashboard
- `app.db` — generated SQLite database (not version-controlled, see `.gitignore`)

## Completion

Core trainer and dashboard are functional: random sentence retrieval, chunk shuffling, answer validation, attempt logging, and per-pattern accuracy stats. Possible next steps: expanding the sentence pool (e.g. via Tatoeba), spaced repetition for weak patterns, and difficulty levels.