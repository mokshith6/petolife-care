from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "petolife.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            icon TEXT NOT NULL,
            weight INTEGER NOT NULL,
            completed INTEGER DEFAULT 0,
            completed_by TEXT,
            completed_at TEXT
        )
    """)

    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]

    if count == 0:
        tasks = [
            ("Morning Walk", "🌅", 15, 1, "Dad", "7:24 AM"),
            ("Morning Food", "🍖", 20, 1, "Mom", "8:05 AM"),
            ("Water Bowl Change", "💧", 10, 0, None, None),
            ("Medicine", "💊", 25, 1, "Mom", "9:00 AM"),
            ("Evening Walk", "🌆", 20, 0, None, None),
            ("Grooming", "🧼", 10, 0, None, None)
        ]

        conn.executemany("""
            INSERT INTO tasks
            (name, icon, weight, completed, completed_by, completed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, tasks)

    conn.commit()
    conn.close()


def get_state():
    conn = get_db()

    tasks = conn.execute(
        "SELECT * FROM tasks ORDER BY id"
    ).fetchall()

    conn.close()

    tasks = [dict(task) for task in tasks]

    score = sum(
        task["weight"]
        for task in tasks
        if task["completed"]
    )

    completed_count = sum(
        1 for task in tasks
        if task["completed"]
    )

    total_tasks = len(tasks)

    progress = round(
        (completed_count / total_tasks) * 100
    ) if total_tasks else 0

    return {
        "tasks": tasks,
        "score": score,
        "completed_count": completed_count,
        "total_tasks": total_tasks,
        "progress": progress
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/state")
def api_state():
    return jsonify(get_state())


@app.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):

    member = request.form.get("member", "Family Member")
    current_time = datetime.now().strftime("%I:%M %p")

    conn = get_db()

    conn.execute("""
        UPDATE tasks
        SET completed = 1,
            completed_by = ?,
            completed_at = ?
        WHERE id = ?
    """, (member, current_time, task_id))

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/reset", methods=["POST"])
def reset_day():

    conn = get_db()

    conn.execute("""
        UPDATE tasks
        SET completed = 0,
            completed_by = NULL,
            completed_at = NULL
    """)

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    setup_database()
    app.run(debug=True, port=5050)
