import sqlite3
import os

DB_PATH = "app.db"
SCHEMA_PATH = "schema.sql"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(conn):
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())

def insert_patterns(conn):
    patterns = [
        ("V2 simple",
         "Verb always in second position; subject comes first."),
        ("V2 with Vorfeld",
         "Adverb or other element occupies first position; subject and verb invert."),
        ("Separable verb",
         "Separable verb: prefix moves to the end of the clause."),
        ("Modal question",
         "Modal verb in first position, infinitive at the end."),
        ("Yes/No question",
         "Conjugated verb in first position, no question word."),
        ("W-question",
         "Question word in first position, verb in second."),
        ("Subordinate clause verb-final",
         "Subordinating conjunction sends the verb to the end of the clause."),
        ("TEKAMOLO",
         "Adverb order: temporal → causal → modal → local."),
        ("Perfekt",
         "Compound tense: auxiliary in second position, participle at the end."),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO patterns (name, description) VALUES (?, ?)",
        patterns
    )
    conn.commit()

def get_pattern_id(conn, name):
    row = conn.execute(
        "SELECT id FROM patterns WHERE name = ?", (name,)
    ).fetchone()
    return row[0]

def insert_sentence(conn, german, translation, chunks, pattern_names):
    cursor = conn.execute(
        "INSERT INTO sentences (german_text, translation) VALUES (?, ?)",
        (german, translation)
    )
    sentence_id = cursor.lastrowid

    conn.executemany(
        "INSERT INTO chunks (sentence_id, position, text) VALUES (?, ?, ?)",
        [(sentence_id, i, chunk) for i, chunk in enumerate(chunks)]
    )

    for name in pattern_names:
        pattern_id = get_pattern_id(conn, name)
        conn.execute(
            "INSERT OR IGNORE INTO sentence_patterns (sentence_id, pattern_id) VALUES (?, ?)",
            (sentence_id, pattern_id)
        )

    conn.commit()

def seed(conn):
    sentences = [

        # ── V2 simple ────────────────────────────────────────────────────────
        (
            "Ich gehe heute ins Kino",
            "I am going to the cinema today.",
            ["Ich", "gehe", "heute", "ins Kino"],
            ["V2 simple"]
        ),
        (
            "Sie kauft jeden Tag frisches Brot",
            "She buys fresh bread every day.",
            ["Sie", "kauft", "jeden Tag", "frisches Brot"],
            ["V2 simple"]
        ),
        (
            "Wir lernen zusammen Deutsch",
            "We are learning German together.",
            ["Wir", "lernen", "zusammen", "Deutsch"],
            ["V2 simple"]
        ),

        # ── V2 with Vorfeld ──────────────────────────────────────────────────
        (
            "Gestern habe ich einen interessanten Film gesehen",
            "Yesterday I watched an interesting film.",
            ["Gestern", "habe", "ich", "einen interessanten Film", "gesehen"],
            ["V2 with Vorfeld", "Perfekt"]
        ),
        (
            "Morgen fahre ich nach Berlin",
            "Tomorrow I am going to Berlin.",
            ["Morgen", "fahre", "ich", "nach Berlin"],
            ["V2 with Vorfeld"]
        ),
        (
            "Heute Abend koche ich für meine Familie",
            "Tonight I am cooking for my family.",
            ["Heute Abend", "koche", "ich", "für meine Familie"],
            ["V2 with Vorfeld"]
        ),
        (
            "Manchmal trinke ich morgens Kaffee",
            "Sometimes I drink coffee in the morning.",
            ["Manchmal", "trinke", "ich", "morgens", "Kaffee"],
            ["V2 with Vorfeld"]
        ),

        # ── Separable verb ───────────────────────────────────────────────────
        (
            "Ich rufe dich morgen an",
            "I will call you tomorrow.",
            ["Ich", "rufe", "dich", "morgen", "an"],
            ["Separable verb"]
        ),
        (
            "Er steht jeden Morgen früh auf",
            "He gets up early every morning.",
            ["Er", "steht", "jeden Morgen", "früh", "auf"],
            ["Separable verb"]
        ),
        (
            "Wir machen das Licht aus",
            "We are turning the light off.",
            ["Wir", "machen", "das Licht", "aus"],
            ["Separable verb"]
        ),
        (
            "Wann kommt der Zug an",
            "When does the train arrive?",
            ["Wann", "kommt", "der Zug", "an"],
            ["Separable verb", "W-question"]
        ),

        # ── Modal question ───────────────────────────────────────────────────
        (
            "Kannst du mir bitte helfen",
            "Can you please help me?",
            ["Kannst", "du", "mir", "bitte", "helfen"],
            ["Modal question"]
        ),
        (
            "Musst du heute arbeiten",
            "Do you have to work today?",
            ["Musst", "du", "heute", "arbeiten"],
            ["Modal question"]
        ),
        (
            "Können wir morgen zusammen lernen",
            "Can we study together tomorrow?",
            ["Können", "wir", "morgen", "zusammen", "lernen"],
            ["Modal question"]
        ),
        (
            "Darf ich das Fenster öffnen",
            "May I open the window?",
            ["Darf", "ich", "das Fenster", "öffnen"],
            ["Modal question"]
        ),

        # ── Yes/No question ──────────────────────────────────────────────────
        (
            "Hast du das Buch gelesen",
            "Have you read the book?",
            ["Hast", "du", "das Buch", "gelesen"],
            ["Yes/No question", "Perfekt"]
        ),
        (
            "Bist du heute müde",
            "Are you tired today?",
            ["Bist", "du", "heute", "müde"],
            ["Yes/No question"]
        ),
        (
            "Sprichst du Deutsch",
            "Do you speak German?",
            ["Sprichst", "du", "Deutsch"],
            ["Yes/No question"]
        ),

        # ── W-question ───────────────────────────────────────────────────────
        (
            "Wo wohnst du",
            "Where do you live?",
            ["Wo", "wohnst", "du"],
            ["W-question"]
        ),
        (
            "Was machst du am Wochenende",
            "What do you do on the weekend?",
            ["Was", "machst", "du", "am Wochenende"],
            ["W-question"]
        ),
        (
            "Wie lange lernst du schon Deutsch",
            "How long have you been learning German?",
            ["Wie lange", "lernst", "du", "schon", "Deutsch"],
            ["W-question"]
        ),

        # ── Subordinate clause verb-final ────────────────────────────────────
        (
            "Ich weiß dass er heute nicht kommt",
            "I know that he is not coming today.",
            ["Ich", "weiß", "dass", "er", "heute", "nicht", "kommt"],
            ["Subordinate clause verb-final"]
        ),
        (
            "Weil ich müde bin gehe ich früh ins Bett",
            "Because I am tired, I am going to bed early.",
            ["Weil", "ich", "müde", "bin", "gehe", "ich", "früh", "ins Bett"],
            ["Subordinate clause verb-final", "V2 with Vorfeld"]
        ),
        (
            "Er lernt Deutsch weil er nach Deutschland reisen möchte",
            "He is learning German because he wants to travel to Germany.",
            ["Er", "lernt", "Deutsch", "weil", "er", "nach Deutschland", "reisen", "möchte"],
            ["Subordinate clause verb-final"]
        ),
        (
            "Wenn es regnet bleibe ich zu Hause",
            "When it rains, I stay at home.",
            ["Wenn", "es", "regnet", "bleibe", "ich", "zu Hause"],
            ["Subordinate clause verb-final", "V2 with Vorfeld"]
        ),
        (
            "Obwohl es kalt ist gehe ich spazieren",
            "Although it is cold, I am going for a walk.",
            ["Obwohl", "es", "kalt", "ist", "gehe", "ich", "spazieren"],
            ["Subordinate clause verb-final", "V2 with Vorfeld"]
        ),

        # ── TEKAMOLO ─────────────────────────────────────────────────────────
        (
            "Er fährt jeden Tag mit dem Fahrrad zur Arbeit",
            "He rides his bike to work every day.",
            ["Er", "fährt", "jeden Tag", "mit dem Fahrrad", "zur Arbeit"],
            ["TEKAMOLO"]
        ),
        (
            "Sie geht heute wegen der Arbeit in die Stadt",
            "She is going into the city today because of work.",
            ["Sie", "geht", "heute", "wegen der Arbeit", "in die Stadt"],
            ["TEKAMOLO"]
        ),

        # ── Perfekt ──────────────────────────────────────────────────────────
        (
            "Ich habe gestern ein neues Buch gekauft",
            "I bought a new book yesterday.",
            ["Ich", "habe", "gestern", "ein neues Buch", "gekauft"],
            ["Perfekt", "V2 with Vorfeld"]
        ),
        (
            "Sie ist letzte Woche nach Paris geflogen",
            "She flew to Paris last week.",
            ["Sie", "ist", "letzte Woche", "nach Paris", "geflogen"],
            ["Perfekt", "V2 with Vorfeld"]
        ),
        (
            "Wir haben das ganze Wochenende gespielt",
            "We played the whole weekend.",
            ["Wir", "haben", "das ganze Wochenende", "gespielt"],
            ["Perfekt"]
        ),
    ]

    for german, translation, chunks, patterns in sentences:
        insert_sentence(conn, german, translation, chunks, patterns)

    print(f"{len(sentences)} sentences inserted successfully.")

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"Creating database at {DB_PATH}...")
    conn = get_conn()
    init_db(conn)
    insert_patterns(conn)
    seed(conn)
    conn.close()