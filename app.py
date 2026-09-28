from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "petolife-demo-secret-key"
DATABASE = "petolife_v2.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def setup_database():
    conn = get_db()

    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS families (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS family_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        family_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        role TEXT DEFAULT 'Member',
        FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS pets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        family_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        species TEXT NOT NULL,
        breed TEXT,
        age TEXT,
        gender TEXT,
        photo TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        icon TEXT NOT NULL,
        weight INTEGER NOT NULL,
        completed INTEGER DEFAULT 0,
        completed_by TEXT,
        completed_at TEXT,
        FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper


def current_family():
    conn = get_db()
    row = conn.execute("""
        SELECT f.*
        FROM families f
        JOIN family_members fm ON fm.family_id = f.id
        WHERE fm.user_id = ?
        LIMIT 1
    """, (session["user_id"],)).fetchone()
    conn.close()
    return row


def seed_default_pet(family_id):
    conn = get_db()

    count = conn.execute(
        "SELECT COUNT(*) FROM pets WHERE family_id = ?", (family_id,)
    ).fetchone()[0]

    if count == 0:
        cur = conn.execute("""
            INSERT INTO pets
            (family_id, name, species, breed, age, gender, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            family_id, "Jessie", "Dog", "Golden Retriever",
            "3 Years", "Female",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        pet_id = cur.lastrowid

        tasks = [
            ("Morning Walk", "🌅", 15),
            ("Morning Food", "🍖", 20),
            ("Water Bowl Change", "💧", 10),
            ("Medicine", "💊", 25),
            ("Evening Walk", "🌆", 20),
            ("Grooming", "🧼", 10)
        ]

        conn.executemany("""
            INSERT INTO tasks (pet_id, name, icon, weight)
            VALUES (?, ?, ?, ?)
        """, [(pet_id, n, i, w) for n, i, w in tasks])

    conn.commit()
    conn.close()


@app.route("/")
@login_required
def home():
    family = current_family()
    conn = get_db()

    pets = conn.execute(
        "SELECT * FROM pets WHERE family_id = ? ORDER BY id",
        (family["id"],)
    ).fetchall()

    selected_pet_id = request.args.get("pet_id", type=int)

    if selected_pet_id:
        pet = conn.execute("""
            SELECT * FROM pets
            WHERE id = ? AND family_id = ?
        """, (selected_pet_id, family["id"])).fetchone()
    else:
        pet = pets[0] if pets else None

    tasks = []
    score = 0
    total_weight = 0
    members = []

    if pet:
        tasks = conn.execute("""
            SELECT * FROM tasks WHERE pet_id = ? ORDER BY id
        """, (pet["id"],)).fetchall()

        score = sum(t["weight"] for t in tasks if t["completed"])
        total_weight = sum(t["weight"] for t in tasks)

        members = conn.execute("""
            SELECT u.name, fm.role
            FROM family_members fm
            JOIN users u ON u.id = fm.user_id
            WHERE fm.family_id = ?
        """, (family["id"],)).fetchall()

    conn.close()

    return render_template(
        "index.html",
        family=family,
        pets=pets,
        pet=pet,
        tasks=tasks,
        score=score,
        total_weight=total_weight,
        members=members
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if not name or not email or not password:
            flash("Please fill all fields.")
            return redirect("/register")

        conn = get_db()

        try:
            cur = conn.execute("""
                INSERT INTO users (name, email, password, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                name, email, generate_password_hash(password),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            user_id = cur.lastrowid

            family = conn.execute(
                "INSERT INTO families (name, created_at) VALUES (?, ?)",
                (f"{name}'s Family", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )

            family_id = family.lastrowid

            conn.execute("""
                INSERT INTO family_members (family_id, user_id, role)
                VALUES (?, ?, ?)
            """, (family_id, user_id, "Owner"))

            conn.commit()

            session["user_id"] = user_id
            session["user_name"] = name

            conn.close()

            seed_default_pet(family_id)

            return redirect("/")

        except sqlite3.IntegrityError:
            conn.close()
            flash("Email already registered.")
            return redirect("/register")

    return render_template("auth.html", mode="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect("/")

        flash("Invalid email or password.")

    return render_template("auth.html", mode="login")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/add-member", methods=["POST"])
@login_required
def add_member():
    family = current_family()

    name = request.form["name"].strip()
    role = request.form.get("role", "Member").strip()

    if not name:
        return redirect("/")

    conn = get_db()

    # Create a simple family member profile without requiring another login.
    email = f"member_{family['id']}_{name.lower().replace(' ', '_')}@petolife.local"

    try:
        cur = conn.execute("""
            INSERT INTO users (name, email, password, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            generate_password_hash("family-member"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        user_id = cur.lastrowid

        conn.execute("""
            INSERT INTO family_members (family_id, user_id, role)
            VALUES (?, ?, ?)
        """, (family["id"], user_id, role))

        conn.commit()
    except sqlite3.IntegrityError:
        pass

    conn.close()
    return redirect("/")


@app.route("/add-pet", methods=["POST"])
@login_required
def add_pet():
    family = current_family()

    name = request.form["name"].strip()
    species = request.form["species"].strip()
    breed = request.form.get("breed", "").strip()
    age = request.form.get("age", "").strip()
    gender = request.form.get("gender", "").strip()

    conn = get_db()

    cur = conn.execute("""
        INSERT INTO pets
        (family_id, name, species, breed, age, gender, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        family["id"], name, species, breed, age, gender,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    pet_id = cur.lastrowid

    tasks = [
        ("Morning Walk", "🌅", 15),
        ("Morning Food", "🍖", 20),
        ("Water Bowl Change", "💧", 10),
        ("Medicine", "💊", 25),
        ("Evening Walk", "🌆", 20),
        ("Grooming", "🧼", 10)
    ]

    conn.executemany("""
        INSERT INTO tasks (pet_id, name, icon, weight)
        VALUES (?, ?, ?, ?)
    """, [(pet_id, n, i, w) for n, i, w in tasks])

    conn.commit()
    conn.close()

    return redirect(f"/?pet_id={pet_id}")


@app.route("/complete/<int:task_id>", methods=["POST"])
@login_required
def complete_task(task_id):
    member = request.form.get("member", session.get("user_name", "Family Member"))

    conn = get_db()

    conn.execute("""
        UPDATE tasks
        SET completed = 1,
            completed_by = ?,
            completed_at = ?
        WHERE id = ?
    """, (
        member,
        datetime.now().strftime("%I:%M %p"),
        task_id
    ))

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/reset", methods=["POST"])
@login_required
def reset_day():
    family = current_family()

    conn = get_db()

    conn.execute("""
        UPDATE tasks
        SET completed = 0,
            completed_by = NULL,
            completed_at = NULL
        WHERE pet_id IN (
            SELECT id FROM pets WHERE family_id = ?
        )
    """, (family["id"],))

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    setup_database()
    app.run(host="0.0.0.0", port=5050, debug=True)
