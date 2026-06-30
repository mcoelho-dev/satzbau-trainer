import sqlite3
import random


def get_random_sentence(db_path: str) -> dict | None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.id, s.german_text, s.translation
        FROM sentences s
        ORDER BY RANDOM()
        LIMIT 1
    """)
    sentence = cursor.fetchone()

    if not sentence:
        conn.close()
        return None

    cursor.execute("""
        SELECT text FROM chunks
        WHERE sentence_id = ?
        ORDER BY position
    """, (sentence["id"],))
    chunks = [row["text"] for row in cursor.fetchall()]

    cursor.execute("""
        SELECT p.name FROM patterns p
        JOIN sentence_patterns sp ON sp.pattern_id = p.id
        WHERE sp.sentence_id = ?
    """, (sentence["id"],))
    patterns = [row["name"] for row in cursor.fetchall()]

    conn.close()

    return {
        "id": sentence["id"],
        "german_text": sentence["german_text"],
        "translation": sentence["translation"],
        "chunks": chunks,
        "patterns": patterns,
    }


def shuffle_chunks(chunks: list[str]) -> list[str]:
    shuffled = chunks[:]
    while shuffled == chunks:
        random.shuffle(shuffled)
    return shuffled


def check_answer(user_answer: list[str], correct_chunks: list[str]) -> bool:
    return user_answer == correct_chunks


def record_attempt(db_path: str, sentence_id: int, is_correct: bool) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute("""
        INSERT INTO attempts (sentence_id, is_correct)
        VALUES (?, ?)
    """, (sentence_id, 1 if is_correct else 0))
    conn.commit()
    conn.close()


def get_sentence_by_id(db_path: str, sentence_id: int) -> dict | None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, german_text, translation
        FROM sentences WHERE id = ?
    """, (sentence_id,))
    sentence = cursor.fetchone()

    if not sentence:
        conn.close()
        return None

    cursor.execute("""
        SELECT text FROM chunks
        WHERE sentence_id = ?
        ORDER BY position
    """, (sentence["id"],))
    chunks = [row["text"] for row in cursor.fetchall()]

    conn.close()
    return {
        "id":          sentence["id"],
        "german_text": sentence["german_text"],
        "translation": sentence["translation"],
        "chunks":      chunks,
    }


def get_pattern_stats(db_path: str) -> list[dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            p.name AS pattern,
            COUNT(a.id) AS total_attempts,
            SUM(a.is_correct) AS correct_attempts,
            ROUND(100.0 * SUM(a.is_correct) / COUNT(a.id), 1) AS accuracy
        FROM attempts a
        JOIN sentences s ON s.id = a.sentence_id
        JOIN sentence_patterns sp ON sp.sentence_id = s.id
        JOIN patterns p ON p.id = sp.pattern_id
        GROUP BY p.name
        ORDER BY accuracy ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_overall_stats(db_path: str) -> dict:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS total_attempts,
            SUM(is_correct) AS correct_attempts,
            ROUND(100.0 * SUM(is_correct) / COUNT(*), 1) AS accuracy
        FROM attempts
    """)
    row = cursor.fetchone()
    conn.close()

    if row["total_attempts"] == 0:
        return {"total_attempts": 0, "correct_attempts": 0, "accuracy": 0}

    return dict(row)