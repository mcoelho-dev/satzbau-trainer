# Satzbau Trainer

A local web app for practicing German grammar through interactive exercises. Built for daily personal use, with a progress dashboard, activity heatmap, and a configurable exercise system that supports multiple grammar types.

## Overview

German grammar has a lot of moving parts — word order rules, grammatical cases, adjective declension, verb conjugation, noun genders and plurals — and most of it only clicks through active recall, not passive reading. This project was inspired by Duolingo's drag-the-words format and Anki's progress tracking: the goal was to combine the best of both into a focused tool built around the specific structures that are hardest to internalize.

The app runs entirely locally. Exercises are stored in a SQLite database, progress is tracked per attempt, and the weighted random algorithm surfaces exercises you struggle with more often than ones you already know well.

## Features

- **6 exercise types**: word order (drag-and-drop chunks), grammatical case, gender (der/die/das), verb conjugation, plural forms, and adjective declension
- **Configurable exercise system**: each type is defined by a JSON schema — adding a new type requires no schema migration, just a new row in `exercise_types`
- **Add exercises in-app**: a dynamic form reads the field schema for each type and renders the correct inputs automatically
- **Browse, edit and delete**: a searchable, filterable exercise browser with inline editing and deletion
- **Weighted random**: exercises you answer incorrectly more often appear with higher frequency; exercises you haven't seen in a while are also prioritized
- **New/Due counters**: each exercise type on the landing page shows how many exercises are unseen (New) and how many have been attempted before (Due)
- **Hint button**: each practice session has a "?" button that shows a plain-English explanation of the grammar rule being practiced
- **Daily goal**: configurable daily exercise target with a progress bar on the landing page
- **Streak tracking**: current and longest streak displayed on the stats page
- **Activity heatmap**: GitHub-style heatmap showing exercise activity by day, navigable by year

## Stack

- **Backend**: Python 3 + Flask
- **Database**: SQLite (`sqlite3` standard library, no ORM)
- **Frontend**: Vanilla HTML/CSS/JS, no framework

## Setup

```bash
# Install dependencies
pip install flask

# Create and seed the database
python seed_exercise_types.py
python seed_word_order.py
python seed_other_types.py

# Run the app
python app.py
```

Open `http://127.0.0.1:5000` in a browser.

## Project structure

```
Satzbau-Trainer/
  schema.sql               — database schema
  seed_exercise_types.py   — seeds exercise types and their field schemas
  seed_word_order.py       — seeds 31 word order exercises across 9 patterns
  seed_other_types.py      — seeds exercises for gender, conjugation, plural, case, adjective declension
  core.py                  — all database logic: queries, weighted random, stats, settings
  app.py                   — Flask routes
  templates/
    index.html             — landing page + practice screen + add exercise screen
    stats.html             — progress dashboard with heatmap, streak, daily goal, pattern accuracy
    exercises.html         — exercise browser with search, filter, inline edit and delete
```

## Schema overview

| Table | Purpose |
|---|---|
| `exercise_types` | Catalog of exercise types; each row defines `field_schema` (JSON) and `hint_text` |
| `patterns` | Grammar patterns scoped to an exercise type (e.g. "V2 simple", "Akkusativ") |
| `exercises` | One row per exercise; type-specific data stored as JSON in `data_json` |
| `attempts` | One row per attempt; links to `exercises`, stores `is_correct` and timestamp |
| `settings` | Key-value store for user preferences (e.g. `daily_goal`) |

## Adding more exercises

Run the app, go to the landing page, and click **+ Add Exercise**. Choose a type, fill in the fields, and save — the exercise enters the pool immediately.

To add exercises in bulk, create a new seed script following the pattern in `seed_word_order.py` and run it once.