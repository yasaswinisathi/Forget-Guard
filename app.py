from flask import Flask, render_template, request, redirect
from datetime import date
import json
import os

app = Flask(__name__)

HISTORY_FILE = "history.json"


# -----------------------------
# LOAD HISTORY
# -----------------------------

def load_history():

    if not os.path.exists(HISTORY_FILE):
        return []

    try:

        with open(HISTORY_FILE, "r") as file:
            return json.load(file)

    except:

        return []


# -----------------------------
# SAVE HISTORY
# -----------------------------

def save_history(history):

    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)


# -----------------------------
# CALCULATE RISK
# -----------------------------

def calculate_risk(
    days_left,
    importance,
    estimated_time,
    postponed
):

    risk = 0

    reasons = []


    # Deadline Risk

    if days_left < 0:

        risk += 45

        reasons.append(
            "The deadline has already passed."
        )

    elif days_left == 0:

        risk += 40

        reasons.append(
            "The deadline is today."
        )

    elif days_left == 1:

        risk += 35

        reasons.append(
            "Only 1 day is remaining."
        )

    elif days_left <= 3:

        risk += 25

        reasons.append(
            "The deadline is approaching."
        )

    elif days_left <= 7:

        risk += 10

        reasons.append(
            "The deadline is within one week."
        )


    # Importance Risk

    if importance == "High":

        risk += 25

        reasons.append(
            "This is a high-importance task."
        )

    elif importance == "Medium":

        risk += 15

        reasons.append(
            "This task has medium importance."
        )


    # Workload Risk

    if estimated_time >= 8:

        risk += 25

        reasons.append(
            "The estimated workload is very high."
        )

    elif estimated_time >= 5:

        risk += 20

        reasons.append(
            "The estimated work time is high."
        )

    elif estimated_time >= 3:

        risk += 10

        reasons.append(
            "The task requires several hours of work."
        )


    # Postponement Risk

    if postponed >= 5:

        risk += 30

        reasons.append(
            "This task has been postponed many times."
        )

    elif postponed >= 3:

        risk += 20

        reasons.append(
            "You have postponed this task multiple times."
        )

    elif postponed >= 1:

        risk += 10

        reasons.append(
            "This task has already been postponed."
        )


    # Maximum Risk

    risk = min(risk, 100)


    # Risk Level

    if risk >= 70:

        level = "HIGH RISK"

        recommendation = (
            "Start this task today and divide it into "
            "smaller parts. Avoid postponing it again."
        )

    elif risk >= 40:

        level = "MEDIUM RISK"

        recommendation = (
            "Plan a specific time to work on this task "
            "and complete it before the deadline."
        )

    else:

        level = "LOW RISK"

        recommendation = (
            "This task appears manageable. Keep it on "
            "your schedule and monitor the deadline."
        )


    return (
        risk,
        level,
        reasons,
        recommendation
    )


# -----------------------------
# HOME
# -----------------------------

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# -----------------------------
# HISTORY
# -----------------------------

@app.route("/history")
def history():

    tasks = load_history()

    return render_template(
        "history.html",
        tasks=tasks
    )


# -----------------------------
# DASHBOARD
# -----------------------------

@app.route("/dashboard")
def dashboard():

    tasks = load_history()

    total_tasks = len(tasks)

    high_risk = 0

    medium_risk = 0

    low_risk = 0

    total_risk = 0


    # -------------------------
    # PRIORITY ALERT
    # -------------------------

    priority_task = None

    highest_risk = -1


    # -------------------------
    # ANALYZE ALL TASKS
    # -------------------------

    for task in tasks:

        risk = task.get(
            "risk",
            0
        )

        total_risk += risk


        # Find highest-risk task

        if risk > highest_risk:

            highest_risk = risk

            priority_task = task


        # Count risk levels

        if risk >= 70:

            high_risk += 1

        elif risk >= 40:

            medium_risk += 1

        else:

            low_risk += 1


    # -------------------------
    # AVERAGE RISK
    # -------------------------

    if total_tasks > 0:

        average_risk = round(
            total_risk / total_tasks,
            1
        )

    else:

        average_risk = 0


    # -------------------------
    # SEND DATA TO DASHBOARD
    # -------------------------

    return render_template(

        "dashboard.html",

        total_tasks=total_tasks,

        high_risk=high_risk,

        medium_risk=medium_risk,

        low_risk=low_risk,

        average_risk=average_risk,

        priority_task=priority_task

    )


# -----------------------------
# CLEAR HISTORY
# -----------------------------

@app.route(
    "/clear-history",
    methods=["POST"]
)
def clear_history():

    save_history([])

    return redirect(
        "/history"
    )


# -----------------------------
# ANALYZE TASK
# -----------------------------

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    task = request.form.get(
        "task"
    )

    deadline = request.form.get(
        "deadline"
    )

    importance = request.form.get(
        "importance"
    )


    estimated_time = float(

        request.form.get(
            "estimated_time"
        ) or 0

    )


    postponed = int(

        request.form.get(
            "postponed"
        ) or 0

    )


    # -------------------------
    # DEADLINE CALCULATION
    # -------------------------

    deadline_date = date.fromisoformat(
        deadline
    )

    today = date.today()

    days_left = (
        deadline_date - today
    ).days


    # -------------------------
    # DEADLINE STATUS
    # -------------------------

    if days_left < 0:

        deadline_status = (
            "The deadline has already passed."
        )

    elif days_left == 0:

        deadline_status = (
            "The deadline is today."
        )

    elif days_left == 1:

        deadline_status = (
            "1 day remaining until the deadline."
        )

    else:

        deadline_status = (
            f"{days_left} days remaining "
            f"until the deadline."
        )


    # -------------------------
    # CALCULATE RISK
    # -------------------------

    (
        risk,
        level,
        reasons,
        recommendation
    ) = calculate_risk(

        days_left,

        importance,

        estimated_time,

        postponed

    )


    # -------------------------
    # SAVE TASK
    # -------------------------

    history = load_history()


    history.append({

        "task": task,

        "deadline": deadline,

        "importance": importance,

        "estimated_time": estimated_time,

        "postponed": postponed,

        "risk": risk,

        "level": level

    })


    save_history(
        history
    )


    # -------------------------
    # SHOW RESULT
    # -------------------------

    return render_template(

        "result.html",

        risk=risk,

        level=level,

        task=task,

        reasons=reasons,

        recommendation=recommendation,

        deadline_status=deadline_status

    )


# -----------------------------
# RUN APPLICATION
# -----------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )
    