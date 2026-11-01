"""PyTodo, performance lab version (Week 7).

Run on your own computer:
    python app.py
The server listens on http://127.0.0.1:5050

Demo login:
    username: demo
    password: demo1234

Routes
    POST /login                    form-encoded, starts a session, 200 or 401
    GET  /api/tasks                the 50 newest tasks, 200, JSON array
    POST /api/tasks                create a task, JSON body
                                   201 + the created task on success
                                   400 + {"errors": [...]} on invalid input
                                   503 + {"error": "storage busy"} when the
                                   storage write is not available within
                                   WAIT_LIMIT_MS
    GET  /health                   plain text "ok"
    POST /admin/reset              clears all tasks (local use only)

Storage: every create writes to a single storage file, one writer at a
time. A write takes WRITE_DELAY_MS milliseconds. A request waits up to
WAIT_LIMIT_MS for its turn, then the server answers 503.
"""
import os
import threading
import time
from functools import wraps

from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "lab7-local-secret")

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo1234"

WRITE_DELAY_MS = int(os.environ.get("WRITE_DELAY_MS", "60"))
WAIT_LIMIT_MS = int(os.environ.get("WAIT_LIMIT_MS", "500"))
THREADS = int(os.environ.get("THREADS", "16"))
PORT = int(os.environ.get("PORT", "5050"))

TASKS = []
_next_id = 1
_storage_lock = threading.Lock()
_id_lock = threading.Lock()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return jsonify({"error": "login required"}), 401
        return view(*args, **kwargs)
    return wrapped


def validate_task(data):
    errors = []
    if not isinstance(data, dict):
        return ["Request body must be a JSON object."]

    title = data.get("title")
    priority = data.get("priority")
    due_date = data.get("due_date")

    if not isinstance(title, str) or not (3 <= len(title.strip()) <= 50):
        errors.append("title must be a string of 3 to 50 characters.")

    if not isinstance(priority, int) or isinstance(priority, bool) or not (1 <= priority <= 5):
        errors.append("priority must be a whole number from 1 to 5.")

    if not isinstance(due_date, str) or not due_date.strip():
        errors.append("due_date is required.")

    return errors


@app.route("/login", methods=["POST"])
def login():
    u = request.form.get("username", "")
    p = request.form.get("password", "")
    if u == DEMO_USERNAME and p == DEMO_PASSWORD:
        session["user"] = u
        return jsonify({"status": "logged_in", "user": u}), 200
    return jsonify({"error": "invalid username or password"}), 401


@app.route("/api/tasks", methods=["GET"])
@login_required
def list_tasks():
    return jsonify(TASKS[-50:][::-1]), 200


@app.route("/api/tasks", methods=["POST"])
@login_required
def create_task():
    global _next_id
    data = request.get_json(silent=True)
    errors = validate_task(data)
    if errors:
        return jsonify({"errors": errors}), 400

    got_turn = _storage_lock.acquire(timeout=WAIT_LIMIT_MS / 1000.0)
    if not got_turn:
        return jsonify({"error": "storage busy"}), 503
    try:
        time.sleep(WRITE_DELAY_MS / 1000.0)  # the storage write
        with _id_lock:
            task_id = _next_id
            _next_id += 1
        task = {
            "id": task_id,
            "title": data["title"].strip(),
            "priority": data["priority"],
            "due_date": data["due_date"].strip(),
            "completed": False,
        }
        TASKS.append(task)
    finally:
        _storage_lock.release()
    return jsonify(task), 201


@app.route("/health")
def health():
    return "ok"


@app.route("/admin/reset", methods=["POST"])
def reset():
    global _next_id
    if request.remote_addr not in ("127.0.0.1", "::1"):
        return "forbidden", 403
    TASKS.clear()
    _next_id = 1
    return "reset"


if __name__ == "__main__":
    from waitress import serve
    print(f"PyTodo performance lab running on http://127.0.0.1:{PORT}")
    print(f"write delay {WRITE_DELAY_MS} ms, wait limit {WAIT_LIMIT_MS} ms, threads {THREADS}")
    serve(app, host="127.0.0.1", port=PORT, threads=THREADS)
