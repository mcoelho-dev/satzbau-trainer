import sqlite3
import json

DB_PATH = "app.db"
SCHEMA_PATH = "schema.sql"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn):
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())


def insert_exercise_types(conn):
    exercise_types = [
        (
            "word_order",
            "Word Order",
            "German clauses follow strict positional rules. Main clauses are V2 "
            "(verb in second position). Subordinate clauses send the verb to the "
            "end. Separable verb prefixes move to the end. Adverb order follows "
            "TEKAMOLO: time, cause, manner, place.",
            json.dumps({
                "fields": [
                    {"name": "german_text", "label": "German sentence", "type": "text"},
                    {"name": "translation", "label": "English translation", "type": "text"},
                    {"name": "chunks", "label": "Word chunks", "type": "chunk_list"}
                ]
            })
        ),
        (
            "grammatical_case",
            "Grammatical Case",
            "German has four cases: Nominative (subject), Accusative (direct "
            "object), Dative (indirect object), Genitive (possession). The "
            "article and adjective endings change depending on the case.",
            json.dumps({
                "fields": [
                    {"name": "sentence", "label": "Sentence with blank", "type": "text"},
                    {"name": "word", "label": "Word to decline", "type": "text"},
                    {"name": "case", "label": "Correct case", "type": "select",
                     "options": ["Nominative", "Accusative", "Dative", "Genitive"]},
                    {"name": "correct_form", "label": "Correct form", "type": "text"}
                ]
            })
        ),
        (
            "gender",
            "Gender",
            "Every German noun has a grammatical gender: der (masculine), "
            "die (feminine), or das (neuter). Gender is mostly arbitrary and "
            "must be memorized along with the noun.",
            json.dumps({
                "fields": [
                    {"name": "word", "label": "Noun", "type": "text"},
                    {"name": "article", "label": "Correct article", "type": "select",
                     "options": ["der", "die", "das"]},
                    {"name": "translation", "label": "English translation", "type": "text"}
                ]
            })
        ),
        (
            "conjugation",
            "Conjugation",
            "German verbs change form depending on the subject (ich, du, er/sie/es, "
            "wir, ihr, sie/Sie) and tense. Strong verbs also change their stem vowel.",
            json.dumps({
                "fields": [
                    {"name": "infinitive", "label": "Infinitive", "type": "text"},
                    {"name": "pronoun", "label": "Pronoun", "type": "select",
                     "options": ["ich", "du", "er/sie/es", "wir", "ihr", "sie/Sie"]},
                    {"name": "tense", "label": "Tense", "type": "select",
                     "options": ["Präsens", "Präteritum", "Perfekt"]},
                    {"name": "correct_form", "label": "Correct conjugated form", "type": "text"}
                ]
            })
        ),
        (
            "plural",
            "Plural",
            "German plural forms are irregular and follow several patterns "
            "(adding -e, -er, -n, -s, an umlaut, or no change at all). "
            "There's no single rule, so each noun's plural must be learned individually.",
            json.dumps({
                "fields": [
                    {"name": "singular", "label": "Singular form", "type": "text"},
                    {"name": "article", "label": "Article", "type": "select",
                     "options": ["der", "die", "das"]},
                    {"name": "correct_plural", "label": "Correct plural form", "type": "text"}
                ]
            })
        ),
        (
            "adjective_declension",
            "Adjective Declension",
            "Adjective endings change depending on case, gender, and whether "
            "the noun is preceded by a definite article, indefinite article, "
            "or no article at all.",
            json.dumps({
                "fields": [
                    {"name": "sentence", "label": "Sentence with blank", "type": "text"},
                    {"name": "adjective", "label": "Base adjective", "type": "text"},
                    {"name": "case", "label": "Case", "type": "select",
                     "options": ["Nominative", "Accusative", "Dative", "Genitive"]},
                    {"name": "gender", "label": "Gender", "type": "select",
                     "options": ["masculine", "feminine", "neuter", "plural"]},
                    {"name": "correct_form", "label": "Correct adjective form", "type": "text"}
                ]
            })
        ),
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO exercise_types (key, display_name, hint_text, field_schema) "
        "VALUES (?, ?, ?, ?)",
        exercise_types
    )
    conn.commit()


if __name__ == "__main__":
    conn = get_conn()
    init_db(conn)
    insert_exercise_types(conn)
    conn.close()
    print("Exercise types seeded successfully.")