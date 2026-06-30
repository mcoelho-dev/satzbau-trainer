import sqlite3
import random


def get_random_sentence(db_path: str) -> dict | None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.id, s.german_text, s.translation_pt
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
        "translation_pt": sentence["translation_pt"],
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