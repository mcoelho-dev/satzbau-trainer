import sqlite3
import json
import random


def get_conn(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_exercise_type(db_path, key):
    conn = get_conn(db_path)
    row = conn.execute(
        "SELECT id, key, display_name, hint_text, field_schema FROM exercise_types WHERE key = ?",
        (key,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row["id"],
        "key": row["key"],
        "display_name": row["display_name"],
        "hint_text": row["hint_text"],
        "field_schema": json.loads(row["field_schema"]),
    }


def list_exercise_types(db_path):
    conn = get_conn(db_path)
    rows = conn.execute(
        "SELECT id, key, display_name, hint_text, field_schema FROM exercise_types"
    ).fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "key": r["key"],
            "display_name": r["display_name"],
            "hint_text": r["hint_text"],
            "field_schema": json.loads(r["field_schema"]),
        }
        for r in rows
    ]


def get_random_exercise(db_path, exercise_type_key):
    conn = get_conn(db_path)

    type_row = conn.execute(
        "SELECT id FROM exercise_types WHERE key = ?", (exercise_type_key,)
    ).fetchone()
    if not type_row:
        conn.close()
        return None

    row = conn.execute("""
        SELECT e.id, e.data_json, p.name AS pattern_name
        FROM exercises e
        LEFT JOIN patterns p ON p.id = e.pattern_id
        WHERE e.exercise_type_id = ?
        ORDER BY RANDOM()
        LIMIT 1
    """, (type_row["id"],)).fetchone()

    conn.close()

    if not row:
        return None

    data = json.loads(row["data_json"])
    data["id"] = row["id"]
    data["pattern"] = row["pattern_name"]
    return data


def get_exercise_by_id(db_path, exercise_id):
    conn = get_conn(db_path)
    row = conn.execute("""
        SELECT e.id, e.data_json, et.key AS type_key, p.name AS pattern_name
        FROM exercises e
        JOIN exercise_types et ON et.id = e.exercise_type_id
        LEFT JOIN patterns p ON p.id = e.pattern_id
        WHERE e.id = ?
    """, (exercise_id,)).fetchone()
    conn.close()

    if not row:
        return None

    data = json.loads(row["data_json"])
    data["id"] = row["id"]
    data["type_key"] = row["type_key"]
    data["pattern"] = row["pattern_name"]
    return data


def shuffle_chunks(chunks):
    shuffled = chunks[:]
    while shuffled == chunks:
        random.shuffle(shuffled)
    return shuffled


def check_word_order_answer(user_answer, correct_chunks):
    return user_answer == correct_chunks


def check_text_answer(user_answer, correct_answer):
    return user_answer.strip().lower() == correct_answer.strip().lower()


def record_attempt(db_path, exercise_id, is_correct):
    conn = get_conn(db_path)
    conn.execute(
        "INSERT INTO attempts (exercise_id, is_correct) VALUES (?, ?)",
        (exercise_id, 1 if is_correct else 0)
    )
    conn.commit()
    conn.close()


def add_exercise(db_path, exercise_type_key, data, pattern_name=None):
    conn = get_conn(db_path)

    type_row = conn.execute(
        "SELECT id FROM exercise_types WHERE key = ?", (exercise_type_key,)
    ).fetchone()
    if not type_row:
        conn.close()
        raise ValueError(f"Unknown exercise type: {exercise_type_key}")

    pattern_id = None
    if pattern_name:
        pattern_row = conn.execute(
            "SELECT id FROM patterns WHERE exercise_type_id = ? AND name = ?",
            (type_row["id"], pattern_name)
        ).fetchone()
        if pattern_row:
            pattern_id = pattern_row["id"]
        else:
            cursor = conn.execute(
                "INSERT INTO patterns (exercise_type_id, name) VALUES (?, ?)",
                (type_row["id"], pattern_name)
            )
            pattern_id = cursor.lastrowid

    conn.execute(
        "INSERT INTO exercises (exercise_type_id, pattern_id, data_json) VALUES (?, ?, ?)",
        (type_row["id"], pattern_id, json.dumps(data))
    )
    conn.commit()
    conn.close()


def get_pattern_stats(db_path):
    conn = get_conn(db_path)
    rows = conn.execute("""
        SELECT
            et.display_name AS exercise_type,
            p.name AS pattern,
            COUNT(a.id) AS total_attempts,
            SUM(a.is_correct) AS correct_attempts,
            ROUND(100.0 * SUM(a.is_correct) / COUNT(a.id), 1) AS accuracy
        FROM attempts a
        JOIN exercises e ON e.id = a.exercise_id
        JOIN exercise_types et ON et.id = e.exercise_type_id
        LEFT JOIN patterns p ON p.id = e.pattern_id
        GROUP BY et.display_name, p.name
        ORDER BY accuracy ASC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_overall_stats(db_path):
    conn = get_conn(db_path)
    row = conn.execute("""
        SELECT
            COUNT(*) AS total_attempts,
            SUM(is_correct) AS correct_attempts,
            ROUND(100.0 * SUM(is_correct) / COUNT(*), 1) AS accuracy
        FROM attempts
    """).fetchone()
    conn.close()

    if row["total_attempts"] == 0:
        return {"total_attempts": 0, "correct_attempts": 0, "accuracy": 0}

    return dict(row)