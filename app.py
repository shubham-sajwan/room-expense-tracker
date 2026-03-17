from flask import Flask, render_template, request, redirect, session
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secretkey"

USERS_FILE = "users.json"
EXPENSE_FILE = "expenses.json"


# Create files if not exist
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(EXPENSE_FILE):
    with open(EXPENSE_FILE, "w") as f:
        json.dump([], f)


# Load Users
def load_users():
    with open(USERS_FILE) as f:
        return json.load(f)


# Save Users
def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)


# Load Expenses
def load_expenses():
    with open(EXPENSE_FILE) as f:
        return json.load(f)


# Save Expenses
def save_expenses(expenses):
    with open(EXPENSE_FILE, "w") as f:
        json.dump(expenses, f)


# Login Page
@app.route("/")
def login():
    return render_template("login.html")


# Handle Login
@app.route("/login", methods=["POST"])
def do_login():
    email = request.form["email"]
    session["user"] = email
    return redirect("/dashboard")


# Dashboard
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    expenses = load_expenses()

    current_month = datetime.now().month

    monthly_total = 0

    for e in expenses:
        if "date" in e:
            date = datetime.strptime(e["date"], "%Y-%m-%d")
            if date.month == current_month:
                monthly_total += e["amount"]

    return render_template(
        "dashboard.html",
        monthly_total=monthly_total,
        expenses=expenses
    )


# Users Page
@app.route("/users")
def users():
    return render_template(
        "users.html",
        users=load_users()
    )


# Add User
@app.route("/add_user", methods=["POST"])
def add_user():

    users = load_users()

    name = request.form["name"]

    if name not in users:
        users.append(name)

    save_users(users)

    return redirect("/users")


# Delete User
@app.route("/delete_user/<name>")
def delete_user(name):

    users = load_users()

    if name in users:
        users.remove(name)

    save_users(users)

    return redirect("/users")


# Expenses Page
@app.route("/expenses")
def expenses():

    return render_template(
        "expenses.html",
        users=load_users(),
        expenses=load_expenses()
    )


# Add Expense
@app.route("/add_expense", methods=["POST"])
def add_expense():

    expenses = load_expenses()

    expenses.append({
        "description": request.form["description"],
        "amount": float(request.form["amount"]),
        "paid_by": request.form["paid_by"],
        "date": request.form["date"]
    })

    save_expenses(expenses)

    return redirect("/expenses")


# SPLIT EXPENSES
@app.route("/split")
def split():

    users = load_users()
    expenses = load_expenses()

    total = sum(e["amount"] for e in expenses)

    if len(users) == 0:
        return "No users added"

    per_person = total / len(users)

    paid = {u: 0 for u in users}

    for e in expenses:
        payer = e["paid_by"]
        paid[payer] += e["amount"]

    balances = {}

    for u in users:
        balances[u] = paid[u] - per_person

    return render_template(
        "split.html",
        balances=balances,
        per_person=per_person,
        total=total
    )


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)(debug=True)