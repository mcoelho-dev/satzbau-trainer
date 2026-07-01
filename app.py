from flask import Flask, jsonify, render_template, request
from core import (
    get_weighted_exercise, get_exercise_by_id, shuffle_chunks,
    check_word_order_answer, check_text_answer, record_attempt,
    get_pattern_stats, get_overall_stats,
    list_exercise_types, add_exercise, get_type_counts
)

app = Flask(__name__)
import os
import sys

def get_db_path():
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "app.db")

DB_PATH = get_db_path()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/exercise")
def exercise():
    exercise_type = request.args.get("type", "word_order")
    data = get_weighted_exercise(DB_PATH, exercise_type)
    if not data:
        return jsonify({"error": "No exercises found for this type"}), 404

    if exercise_type == "word_order":
        return jsonify({
            "id":          data["id"],
            "translation": data["translation"],
            "chunks":      shuffle_chunks(data["chunks"]),
            "pattern":     data["pattern"],
        })

    if exercise_type == "gender":
        return jsonify({
            "id":      data["id"],
            "prompt":  data["word"],
            "sub":     data["translation"],
            "pattern": data["pattern"],
            "options": ["der", "die", "das"],
        })

    if exercise_type == "conjugation":
        return jsonify({
            "id":      data["id"],
            "prompt":  f'{data["infinitive"]} — {data["pronoun"]} ({data["tense"]})',
            "sub":     None,
            "pattern": data["pattern"],
        })

    if exercise_type == "plural":
        return jsonify({
            "id":      data["id"],
            "prompt":  f'{data["article"]} {data["singular"]}',
            "sub":     "Write the plural form",
            "pattern": data["pattern"],
        })

    if exercise_type == "grammatical_case":
        return jsonify({
            "id":      data["id"],
            "prompt":  data["sentence"],
            "sub":     f'Decline: {data["word"]} ({data["case"]})',
            "pattern": data["pattern"],
        })

    if exercise_type == "adjective_declension":
        return jsonify({
            "id":      data["id"],
            "prompt":  data["sentence"],
            "sub":     f'Decline: {data["adjective"]} ({data["case"]}, {data["gender"]})',
            "pattern": data["pattern"],
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

    type_key = exercise["type_key"]

    if type_key == "word_order":
        is_correct     = check_word_order_answer(user_answer, exercise["chunks"])
        correct_answer = " ".join(exercise["chunks"])

    elif type_key == "gender":
        is_correct     = check_text_answer(user_answer, exercise["article"])
        correct_answer = exercise["article"]

    elif type_key in ("conjugation", "grammatical_case", "adjective_declension"):
        is_correct     = check_text_answer(user_answer, exercise["correct_form"])
        correct_answer = exercise["correct_form"]

    elif type_key == "plural":
        is_correct     = check_text_answer(user_answer, exercise["correct_plural"])
        correct_answer = exercise["correct_plural"]

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


@app.route("/api/type-counts")
def type_counts():
    return jsonify(get_type_counts(DB_PATH))


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

from core import (
    get_weighted_exercise, get_exercise_by_id, shuffle_chunks,
    check_word_order_answer, check_text_answer, record_attempt,
    get_pattern_stats, get_overall_stats,
    list_exercise_types, add_exercise, get_type_counts,
    list_exercises, update_exercise, delete_exercise,
    get_daily_progress, get_heatmap_data,
    get_setting, set_setting
)


@app.route("/api/daily-progress")
def daily_progress():
    return jsonify(get_daily_progress(DB_PATH))


@app.route("/api/heatmap")
def heatmap():
    return jsonify(get_heatmap_data(DB_PATH))


@app.route("/api/settings", methods=["GET"])
def get_settings():
    return jsonify({
        "daily_goal": get_setting(DB_PATH, "daily_goal", "20")
    })


@app.route("/api/settings", methods=["POST"])
def post_settings():
    body = request.get_json()
    goal = body.get("daily_goal")
    if goal is not None:
        set_setting(DB_PATH, "daily_goal", str(int(goal)))
    return jsonify({"status": "saved"})

@app.route("/exercises")
def exercises_page():
    return render_template("exercises.html")

@app.route("/api/exercises")
def get_exercises():
    type_key = request.args.get("type")
    return jsonify(list_exercises(DB_PATH, type_key))

@app.route("/api/exercises/<int:exercise_id>", methods=["PUT"])
def put_exercise(exercise_id):
    body = request.get_json()
    data = body.get("data")
    if not data:
        return jsonify({"error": "Missing data"}), 400
    update_exercise(DB_PATH, exercise_id, data)
    return jsonify({"status": "updated"})

@app.route("/api/exercises/<int:exercise_id>", methods=["DELETE"])
def del_exercise(exercise_id):
    delete_exercise(DB_PATH, exercise_id)
    return jsonify({"status": "deleted"})

if __name__ == "__main__":
    app.run(debug=True)