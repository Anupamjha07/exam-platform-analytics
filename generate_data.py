import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

random.seed(42)
np.random.seed(42)

os.makedirs("data", exist_ok=True)

# -----------------------------
# 1. Students
# -----------------------------
num_students = 300
students = []

for i in range(1, num_students + 1):
    students.append({
        "student_id": i,
        "student_name": f"Student_{i}",
        "course": random.choice(["BCA", "B.Tech", "MCA"]),
        "city": random.choice(["Kolkata", "Patna", "Ranchi", "Delhi", "Lucknow"]),
        "join_date": (datetime(2025, 1, 1) + timedelta(days=random.randint(0, 365))).date()
    })

students_df = pd.DataFrame(students)
students_df.to_csv("data/students.csv", index=False)

# -----------------------------
# 2. Quizzes
# -----------------------------
quiz_titles = [
    "Python Basics Test",
    "SQL Fundamentals Quiz",
    "DBMS Mock Test",
    "Operating System Quiz",
    "Computer Networks Quiz",
    "DSA Practice Test",
    "Aptitude Round 1",
    "Reasoning Assessment",
    "Java Basics Quiz",
    "Web Development Test"
]

quizzes = []

for i in range(1, 11):
    quizzes.append({
        "quiz_id": i,
        "quiz_title": quiz_titles[i-1],
        "subject": random.choice(["Python", "SQL", "DBMS", "OS", "CN", "DSA", "Aptitude"]),
        "difficulty": random.choice(["Easy", "Medium", "Hard"]),
        "price": random.choice([49, 99, 149, 199, 299]),
        "total_marks": 100,
        "duration_minutes": random.choice([30, 45, 60, 90])
    })

quizzes_df = pd.DataFrame(quizzes)
quizzes_df.to_csv("data/quizzes.csv", index=False)

# -----------------------------
# 3. Attempts
# -----------------------------
attempts = []
attempt_id = 1
start_base = datetime(2026, 1, 1)

for _ in range(1200):
    student_id = random.randint(1, num_students)
    quiz_id = random.randint(1, 10)

    start_time = start_base + timedelta(days=random.randint(0, 80), hours=random.randint(0, 23), minutes=random.randint(0, 59))
    status = random.choices(
        ["completed", "dropped", "incomplete"],
        weights=[70, 20, 10],
        k=1
    )[0]

    if status == "completed":
        score = random.randint(35, 98)
        end_time = start_time + timedelta(minutes=random.randint(15, 90))
    elif status == "dropped":
        score = random.randint(0, 55)
        end_time = ""
    else:
        score = random.randint(0, 65)
        end_time = ""

    attempts.append({
        "attempt_id": attempt_id,
        "student_id": student_id,
        "quiz_id": quiz_id,
        "attempt_date": start_time.date(),
        "start_time": start_time,
        "end_time": end_time,
        "status": status,
        "score": score,
        "passed": 1 if score >= 40 and status == "completed" else 0
    })

    attempt_id += 1

attempts_df = pd.DataFrame(attempts)
attempts_df.to_csv("data/attempts.csv", index=False)

# -----------------------------
# 4. Payments
# -----------------------------
payments = []
payment_id = 1

for _, row in attempts_df.iterrows():
    if row["status"] in ["completed", "dropped", "incomplete"]:
        quiz_price = quizzes_df.loc[quizzes_df["quiz_id"] == row["quiz_id"], "price"].values[0]

        # assume most attempts are paid
        payment_status = random.choices(["paid", "failed"], weights=[90, 10], k=1)[0]
        amount = quiz_price if payment_status == "paid" else 0

        payments.append({
            "payment_id": payment_id,
            "attempt_id": row["attempt_id"],
            "student_id": row["student_id"],
            "quiz_id": row["quiz_id"],
            "amount": amount,
            "payment_status": payment_status,
            "payment_date": row["attempt_date"]
        })
        payment_id += 1

payments_df = pd.DataFrame(payments)
payments_df.to_csv("data/payments.csv", index=False)

# -----------------------------
# 5. Proctoring Events
# -----------------------------
event_types = ["tab_switch", "camera_off", "fullscreen_exit", "multiple_faces"]
proctoring_events = []
event_id = 1

for _, row in attempts_df.iterrows():
    num_events = random.choices([0, 1, 2, 3], weights=[45, 30, 15, 10], k=1)[0]

    for _ in range(num_events):
        proctoring_events.append({
            "event_id": event_id,
            "attempt_id": row["attempt_id"],
            "student_id": row["student_id"],
            "quiz_id": row["quiz_id"],
            "event_type": random.choice(event_types),
            "severity": random.choice(["low", "medium", "high"]),
            "event_time": row["start_time"]
        })
        event_id += 1

proctoring_df = pd.DataFrame(proctoring_events)
proctoring_df.to_csv("data/proctoring_events.csv", index=False)

print("Synthetic platform data generated successfully in /data folder")