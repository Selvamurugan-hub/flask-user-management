from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"


# ---------- DATABASE INITIALIZE ----------
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------- HOME ----------
@app.route('/')
def home():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM users")
    users = cursor.fetchall()

    conn.close()

    return render_template("index.html", users=users)


# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM users")
    users = cursor.fetchall()

    conn.close()

    return render_template("dashboard.html",
                           user=session["user"],
                           users=users,
                           message="")


# ---------- ADD ----------
@app.route("/add", methods=["POST"])
def add():
    if "user" not in session:
        return redirect("/login")

    username = request.form["username"]

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (name) VALUES (?)", (username,))
    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ---------- DELETE ----------
@app.route("/delete", methods=["POST"])
def delete():
    if "user" not in session:
        return redirect("/login")

    name_to_delete = request.form["username"]

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE name=?", (name_to_delete,))
    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ---------- SEARCH ----------
@app.route("/search", methods=["POST"])
def search():
    if "user" not in session:
        return redirect("/login")

    searchname = request.form["searchname"]

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM users WHERE name LIKE ?",
        ('%' + searchname + '%',)
    )
    users = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        user=session["user"],
        users=users,
        message="No users found" if not users else ""
    )


# ---------- SIGNUP ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO accounts (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
        except:
            conn.close()
            return "Username already exists!"

        conn.close()
        return redirect("/login")

    return render_template("signup.html")


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("SELECT password FROM accounts WHERE username=?", (username,))
        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[0], password):
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid credentials"

    return render_template("login.html")


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

@app.route("/edit", methods=["POST"])
def edit():
    if "user" not in session:
        return redirect("/login")

    oldname = request.form["oldname"]
    newname = request.form["newname"]

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET name=? WHERE name=?",
        (newname, oldname)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ---------- RUN ----------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
