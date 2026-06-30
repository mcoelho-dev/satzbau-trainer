import sqlite3
import json

DB_PATH = "app.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_exercise_type_id(conn, key):
    row = conn.execute(
        "SELECT id FROM exercise_types WHERE key = ?", (key,)
    ).fetchone()
    return row[0]


def get_or_create_pattern(conn, exercise_type_id, name):
    row = conn.execute(
        "SELECT id FROM patterns WHERE exercise_type_id = ? AND name = ?",
        (exercise_type_id, name)
    ).fetchone()
    if row:
        return row[0]
    cursor = conn.execute(
        "INSERT INTO patterns (exercise_type_id, name) VALUES (?, ?)",
        (exercise_type_id, name)
    )
    conn.commit()
    return cursor.lastrowid


def insert_exercise(conn, type_key, data, pattern_name=None):
    type_id = get_exercise_type_id(conn, type_key)
    pattern_id = get_or_create_pattern(conn, type_id, pattern_name) if pattern_name else None
    conn.execute(
        "INSERT INTO exercises (exercise_type_id, pattern_id, data_json) VALUES (?, ?, ?)",
        (type_id, pattern_id, json.dumps(data))
    )
    conn.commit()


def seed_gender(conn):
    items = [
        ("Hund", "der", "Dog"),
        ("Katze", "die", "Cat"),
        ("Buch", "das", "Book"),
        ("Tisch", "der", "Table"),
        ("Blume", "die", "Flower"),
        ("Fenster", "das", "Window"),
        ("Auto", "das", "Car"),
        ("Straße", "die", "Street"),
        ("Apfel", "der", "Apple"),
        ("Mädchen", "das", "Girl"),
        ("Schule", "die", "School"),
        ("Brot", "das", "Bread"),
    ]
    for word, article, translation in items:
        insert_exercise(conn, "gender",
            {"word": word, "article": article, "translation": translation},
            pattern_name=article)
    print(f"{len(items)} gender exercises seeded.")


def seed_conjugation(conn):
    items = [
        ("gehen", "ich", "Präsens", "gehe"),
        ("gehen", "du", "Präsens", "gehst"),
        ("gehen", "er/sie/es", "Präsens", "geht"),
        ("sein", "ich", "Präsens", "bin"),
        ("sein", "wir", "Präsens", "sind"),
        ("haben", "du", "Präsens", "hast"),
        ("haben", "ihr", "Präsens", "habt"),
        ("sprechen", "er/sie/es", "Präsens", "spricht"),
        ("essen", "ich", "Präsens", "esse"),
        ("fahren", "du", "Präsens", "fährst"),
        ("gehen", "ich", "Präteritum", "ging"),
        ("sein", "er/sie/es", "Präteritum", "war"),
    ]
    for infinitive, pronoun, tense, correct in items:
        insert_exercise(conn, "conjugation",
            {"infinitive": infinitive, "pronoun": pronoun, "tense": tense, "correct_form": correct},
            pattern_name=tense)
    print(f"{len(items)} conjugation exercises seeded.")


def seed_plural(conn):
    items = [
        ("Hund", "der", "Hunde"),
        ("Katze", "die", "Katzen"),
        ("Buch", "das", "Bücher"),
        ("Auto", "das", "Autos"),
        ("Frau", "die", "Frauen"),
        ("Mann", "der", "Männer"),
        ("Kind", "das", "Kinder"),
        ("Tisch", "der", "Tische"),
        ("Stuhl", "der", "Stühle"),
        ("Lehrer", "der", "Lehrer"),
        ("Schwester", "die", "Schwestern"),
        ("Apfel", "der", "Äpfel"),
    ]
    for singular, article, plural in items:
        insert_exercise(conn, "plural",
            {"singular": singular, "article": article, "correct_plural": plural})
    print(f"{len(items)} plural exercises seeded.")


def seed_grammatical_case(conn):
    items = [
        ("Ich sehe ___ Hund.", "der Hund", "Accusative", "den Hund"),
        ("Ich gebe ___ Frau das Buch.", "die Frau", "Dative", "der Frau"),
        ("___ Mann liest die Zeitung.", "der Mann", "Nominative", "Der Mann"),
        ("Das ist das Auto ___ Lehrers.", "der Lehrer", "Genitive", "des Lehrers"),
        ("Ich kaufe ___ Buch.", "das Buch", "Accusative", "das Buch"),
        ("Sie hilft ___ Kind.", "das Kind", "Dative", "dem Kind"),
        ("___ Katze schläft.", "die Katze", "Nominative", "Die Katze"),
        ("Wir sprechen über ___ Film.", "der Film", "Accusative", "den Film"),
        ("Das Haus ___ Familie ist groß.", "die Familie", "Genitive", "der Familie"),
        ("Er dankt ___ Lehrerin.", "die Lehrerin", "Dative", "der Lehrerin"),
    ]
    for sentence, word, case, correct in items:
        insert_exercise(conn, "grammatical_case",
            {"sentence": sentence, "word": word, "case": case, "correct_form": correct},
            pattern_name=case)
    print(f"{len(items)} grammatical case exercises seeded.")


def seed_adjective_declension(conn):
    items = [
        ("Das ist ein ___ Hund.", "groß", "Nominative", "masculine", "großer"),
        ("Ich sehe einen ___ Hund.", "groß", "Accusative", "masculine", "großen"),
        ("Das ist die ___ Frau.", "klug", "Nominative", "feminine", "kluge"),
        ("Ich kenne die ___ Frau.", "klug", "Accusative", "feminine", "kluge"),
        ("Das ist ein ___ Buch.", "neu", "Nominative", "neuter", "neues"),
        ("Mit dem ___ Auto fahren wir.", "neu", "Dative", "neuter", "neuen"),
        ("Das sind die ___ Kinder.", "klein", "Nominative", "plural", "kleinen"),
        ("Ich helfe den ___ Kindern.", "klein", "Dative", "plural", "kleinen"),
        ("Das ist der ___ Mann.", "alt", "Nominative", "masculine", "alte"),
        ("Wegen des ___ Wetters bleiben wir.", "schlecht", "Genitive", "neuter", "schlechten"),
    ]
    for sentence, adjective, case, gender, correct in items:
        insert_exercise(conn, "adjective_declension",
            {
                "sentence": sentence, "adjective": adjective,
                "case": case, "gender": gender, "correct_form": correct
            },
            pattern_name=f"{case} {gender}")
    print(f"{len(items)} adjective declension exercises seeded.")


if __name__ == "__main__":
    conn = get_conn()
    seed_gender(conn)
    seed_conjugation(conn)
    seed_plural(conn)
    seed_grammatical_case(conn)
    seed_adjective_declension(conn)
    conn.close()
    print("All additional exercise types seeded successfully.")