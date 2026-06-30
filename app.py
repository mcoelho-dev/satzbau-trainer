from flask import Flask, jsonify, render_template, request
from core import (
    get_random_sentence, shuffle_chunks, check_answer,
    record_attempt, get_sentence_by_id,
    get_pattern_stats, get_overall_stats
)

app = Flask(__name__)
DB_PATH = "app.db"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/sentence")
def sentence():
    data = get_random_sentence(DB_PATH)
    if not data:
        return jsonify({"error": "No sentences found"}), 404
    return jsonify({
        "id":          data["id"],
        "translation": data["translation"],
        "chunks":      shuffle_chunks(data["chunks"]),
        "patterns":    data["patterns"],
    })


@app.route("/api/attempt", methods=["POST"])
def attempt():
    body        = request.get_json()
    sentence_id = body.get("sentence_id")
    user_answer = body.get("answer", [])

    sentence = get_sentence_by_id(DB_PATH, sentence_id)
    if not sentence:
        return jsonify({"error": "Sentence not found"}), 404

    correct    = sentence["chunks"]
    is_correct = check_answer(user_answer, correct)
    record_attempt(DB_PATH, sentence_id, is_correct)

    return jsonify({
        "correct":        is_correct,
        "correct_chunks": correct,
    })


@app.route("/api/stats")
def stats():
    return jsonify({
        "overall":  get_overall_stats(DB_PATH),
        "patterns": get_pattern_stats(DB_PATH),
    })


@app.route("/stats")
def stats_page():
    return render_template("stats.html")


if __name__ == "__main__":
    app.run(debug=True)