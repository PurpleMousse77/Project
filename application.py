import os

import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required



# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///care.db")


@app.route("/")
@login_required
def home():
    return render_template("home.html")


@app.route("/maintenance", methods=["GET", "POST"])
@login_required
def maintenance():
    """Browse added recipes"""
    return render_template("maintenance.html")

@app.route("/cleaning", methods=["GET", "POST"])
@login_required
def cleaning():
    """Browse added recipes"""
    return render_template("cleaning.html")

@app.route("/parking", methods=["GET", "POST"])
@login_required
def parking():
    """Browse added recipes"""
    return render_template("parking.html")

@app.route("/about", methods=["GET", "POST"])
@login_required
def about():
    """Add recipes"""
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():

    return render_template("contact.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/submit", methods=["GET", "POST"])
@login_required
def submit():
    """Add users"""
    data = db.execute("""
        SELECT fname,lname,email,phone,owner,sub,message
        FROM data
        WHERE fname=:fname
    """,fname=session["fname"])

    return render_template("submit.html",data=data)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username=request.form.get("username")
        password=request.form.get("password") == request.form.get("confirmation")
        if request.form.get("password") != request.form.get("confirmation"):
            return("Password must match")

        try:
            primary_key = db.execute("INSERT INTO users (username,hash) VALUES (:username, :hash)",
            username=request.form.get("username"),
            hash=generate_password_hash(request.form.get("password")))

        except:
            return("Username you entered already exist.")

        if primary_key == None:
            return("Registration Error: Check if username already exist.")

        # Remember which user has logged in
        session["user_id"] = primary_key

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)