from flask import Flask, jsonify, render_template, request
from core import (
    get_random_exercise, get_exercise_by_id, shuffle_chunks,
    check_word_order_answer, record_attempt,
    get_pattern_stats, get_overall_stats,
    list_exercise_types, add_exercise
)

app = Flask(__name__)
DB_PATH = "app.db"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/exercise")
def exercise():
    exercise_type = request.args.get("type", "word_order")
    data = get_random_exercise(DB_PATH, exercise_type)
    if not data:
        return jsonify({"error": "No exercises found for this type"}), 404

    if exercise_type == "word_order":
        return jsonify({
            "id":          data["id"],
            "translation": data["translation"],
            "chunks":      shuffle_chunks(data["chunks"]),
            "pattern":     data["pattern"],
        })

    return jsonify({"error": "Exercise type not yet supported"}), 400


@app.route("/api/attempt", methods=["POST"])
def attempt():
    body        = request.get_json()
    exercise_id = body.get("exercise_id")
    user_answer = body.get("answer")

    exercise = get_exercise_by_id(DB_PATH, exercise_id)
    if not exercise:
        return jsonify({"error": "Exercise not found"}), 404

    if exercise["type_key"] == "word_order":
        is_correct = check_word_order_answer(user_answer, exercise["chunks"])
        correct_answer = exercise["chunks"]
    else:
        return jsonify({"error": "Exercise type not yet supported"}), 400

    record_attempt(DB_PATH, exercise_id, is_correct)

    return jsonify({
        "correct":        is_correct,
        "correct_answer": correct_answer,
    })


@app.route("/api/exercise-types")
def exercise_types():
    return jsonify(list_exercise_types(DB_PATH))


@app.route("/api/exercise", methods=["POST"])
def create_exercise():
    body          = request.get_json()
    exercise_type = body.get("type")
    pattern_name  = body.get("pattern")
    data          = body.get("data")

    if not exercise_type or not data:
        return jsonify({"error": "Missing type or data"}), 400

    try:
        add_exercise(DB_PATH, exercise_type, data, pattern_name)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"status": "created"})


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