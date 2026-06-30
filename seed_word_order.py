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


def insert_word_order_exercise(conn, exercise_type_id, german, translation, chunks, pattern_name):
    pattern_id = get_or_create_pattern(conn, exercise_type_id, pattern_name)
    data = json.dumps({
        "german_text": german,
        "translation": translation,
        "chunks": chunks
    })
    conn.execute(
        "INSERT INTO exercises (exercise_type_id, pattern_id, data_json) VALUES (?, ?, ?)",
        (exercise_type_id, pattern_id, data)
    )
    conn.commit()


def seed(conn):
    word_order_id = get_exercise_type_id(conn, "word_order")

    sentences = [
        ("Ich gehe heute ins Kino", "I am going to the cinema today.",
         ["Ich", "gehe", "heute", "ins Kino"], "V2 simple"),
        ("Sie kauft jeden Tag frisches Brot", "She buys fresh bread every day.",
         ["Sie", "kauft", "jeden Tag", "frisches Brot"], "V2 simple"),
        ("Wir lernen zusammen Deutsch", "We are learning German together.",
         ["Wir", "lernen", "zusammen", "Deutsch"], "V2 simple"),

        ("Gestern habe ich einen interessanten Film gesehen", "Yesterday I watched an interesting film.",
         ["Gestern", "habe", "ich", "einen interessanten Film", "gesehen"], "V2 with Vorfeld"),
        ("Morgen fahre ich nach Berlin", "Tomorrow I am going to Berlin.",
         ["Morgen", "fahre", "ich", "nach Berlin"], "V2 with Vorfeld"),
        ("Heute Abend koche ich für meine Familie", "Tonight I am cooking for my family.",
         ["Heute Abend", "koche", "ich", "für meine Familie"], "V2 with Vorfeld"),
        ("Manchmal trinke ich morgens Kaffee", "Sometimes I drink coffee in the morning.",
         ["Manchmal", "trinke", "ich", "morgens", "Kaffee"], "V2 with Vorfeld"),

        ("Ich rufe dich morgen an", "I will call you tomorrow.",
         ["Ich", "rufe", "dich", "morgen", "an"], "Separable verb"),
        ("Er steht jeden Morgen früh auf", "He gets up early every morning.",
         ["Er", "steht", "jeden Morgen", "früh", "auf"], "Separable verb"),
        ("Wir machen das Licht aus", "We are turning the light off.",
         ["Wir", "machen", "das Licht", "aus"], "Separable verb"),
        ("Wann kommt der Zug an", "When does the train arrive?",
         ["Wann", "kommt", "der Zug", "an"], "Separable verb"),

        ("Kannst du mir bitte helfen", "Can you please help me?",
         ["Kannst", "du", "mir", "bitte", "helfen"], "Modal question"),
        ("Musst du heute arbeiten", "Do you have to work today?",
         ["Musst", "du", "heute", "arbeiten"], "Modal question"),
        ("Können wir morgen zusammen lernen", "Can we study together tomorrow?",
         ["Können", "wir", "morgen", "zusammen", "lernen"], "Modal question"),
        ("Darf ich das Fenster öffnen", "May I open the window?",
         ["Darf", "ich", "das Fenster", "öffnen"], "Modal question"),

        ("Hast du das Buch gelesen", "Have you read the book?",
         ["Hast", "du", "das Buch", "gelesen"], "Yes/No question"),
        ("Bist du heute müde", "Are you tired today?",
         ["Bist", "du", "heute", "müde"], "Yes/No question"),
        ("Sprichst du Deutsch", "Do you speak German?",
         ["Sprichst", "du", "Deutsch"], "Yes/No question"),

        ("Wo wohnst du", "Where do you live?",
         ["Wo", "wohnst", "du"], "W-question"),
        ("Was machst du am Wochenende", "What do you do on the weekend?",
         ["Was", "machst", "du", "am Wochenende"], "W-question"),
        ("Wie lange lernst du schon Deutsch", "How long have you been learning German?",
         ["Wie lange", "lernst", "du", "schon", "Deutsch"], "W-question"),

        ("Ich weiß dass er heute nicht kommt", "I know that he is not coming today.",
         ["Ich", "weiß", "dass", "er", "heute", "nicht", "kommt"], "Subordinate clause verb-final"),
        ("Weil ich müde bin gehe ich früh ins Bett", "Because I am tired, I am going to bed early.",
         ["Weil", "ich", "müde", "bin", "gehe", "ich", "früh", "ins Bett"], "Subordinate clause verb-final"),
        ("Er lernt Deutsch weil er nach Deutschland reisen möchte",
         "He is learning German because he wants to travel to Germany.",
         ["Er", "lernt", "Deutsch", "weil", "er", "nach Deutschland", "reisen", "möchte"],
         "Subordinate clause verb-final"),
        ("Wenn es regnet bleibe ich zu Hause", "When it rains, I stay at home.",
         ["Wenn", "es", "regnet", "bleibe", "ich", "zu Hause"], "Subordinate clause verb-final"),
        ("Obwohl es kalt ist gehe ich spazieren", "Although it is cold, I am going for a walk.",
         ["Obwohl", "es", "kalt", "ist", "gehe", "ich", "spazieren"], "Subordinate clause verb-final"),

        ("Er fährt jeden Tag mit dem Fahrrad zur Arbeit", "He rides his bike to work every day.",
         ["Er", "fährt", "jeden Tag", "mit dem Fahrrad", "zur Arbeit"], "TEKAMOLO"),
        ("Sie geht heute wegen der Arbeit in die Stadt", "She is going into the city today because of work.",
         ["Sie", "geht", "heute", "wegen der Arbeit", "in die Stadt"], "TEKAMOLO"),

        ("Ich habe gestern ein neues Buch gekauft", "I bought a new book yesterday.",
         ["Ich", "habe", "gestern", "ein neues Buch", "gekauft"], "Perfekt"),
        ("Sie ist letzte Woche nach Paris geflogen", "She flew to Paris last week.",
         ["Sie", "ist", "letzte Woche", "nach Paris", "geflogen"], "Perfekt"),
        ("Wir haben das ganze Wochenende gespielt", "We played the whole weekend.",
         ["Wir", "haben", "das ganze Wochenende", "gespielt"], "Perfekt"),
    ]

    for german, translation, chunks, pattern in sentences:
        insert_word_order_exercise(conn, word_order_id, german, translation, chunks, pattern)

    print(f"{len(sentences)} word order exercises seeded successfully.")


if __name__ == "__main__":
    conn = get_conn()
    seed(conn)
    conn.close()