import streamlit as st
import pandas as pd

st.set_page_config(page_title="Exam Platform Analytics", layout="wide")

# -----------------------------
# Load data
# -----------------------------
students = pd.read_csv("data/students.csv")
quizzes = pd.read_csv("data/quizzes.csv")
attempts = pd.read_csv("data/attempts.csv")
payments = pd.read_csv("data/payments.csv")
proctoring = pd.read_csv("data/proctoring_events.csv")

# -----------------------------
# Data preprocessing
# -----------------------------
attempts["attempt_date"] = pd.to_datetime(attempts["attempt_date"], errors="coerce")
payments["payment_date"] = pd.to_datetime(payments["payment_date"], errors="coerce")

attempts_merged = attempts.merge(quizzes, on="quiz_id", how="left")
payments_paid = payments[payments["payment_status"] == "paid"].copy()

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.title("📊 Dashboard Filters")

selected_subjects = st.sidebar.multiselect(
    "Select Subject",
    sorted(quizzes["subject"].dropna().unique()),
    default=sorted(quizzes["subject"].dropna().unique())
)

selected_difficulties = st.sidebar.multiselect(
    "Select Difficulty",
    sorted(quizzes["difficulty"].dropna().unique()),
    default=sorted(quizzes["difficulty"].dropna().unique())
)

selected_status = st.sidebar.multiselect(
    "Select Attempt Status",
    sorted(attempts["status"].dropna().unique()),
    default=sorted(attempts["status"].dropna().unique())
)

# Filter quizzes first
filtered_quizzes = quizzes[
    (quizzes["subject"].isin(selected_subjects)) &
    (quizzes["difficulty"].isin(selected_difficulties))
]

# Filter attempts using selected quizzes + selected status
filtered_attempts = attempts_merged[
    (attempts_merged["quiz_id"].isin(filtered_quizzes["quiz_id"])) &
    (attempts_merged["status"].isin(selected_status))
].copy()

# -----------------------------
# Date filter
# -----------------------------
if not filtered_attempts.empty:
    min_date = filtered_attempts["attempt_date"].min().date()
    max_date = filtered_attempts["attempt_date"].max().date()

    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_attempts = filtered_attempts[
            (filtered_attempts["attempt_date"] >= pd.to_datetime(start_date)) &
            (filtered_attempts["attempt_date"] <= pd.to_datetime(end_date))
        ].copy()

# Filter payments based on filtered attempts
filtered_payments = payments_paid[
    payments_paid["attempt_id"].isin(filtered_attempts["attempt_id"])
].copy()

# Filter proctoring based on filtered attempts
filtered_proctoring = proctoring[
    proctoring["attempt_id"].isin(filtered_attempts["attempt_id"])
].copy()

# -----------------------------
# KPIs
# -----------------------------
total_students = filtered_attempts["student_id"].nunique()
total_quizzes = filtered_attempts["quiz_id"].nunique()
total_attempts = filtered_attempts["attempt_id"].nunique()

completed_attempts = filtered_attempts[filtered_attempts["status"] == "completed"].shape[0]
dropped_attempts = filtered_attempts[filtered_attempts["status"] == "dropped"].shape[0]

completion_rate = round((completed_attempts / total_attempts) * 100, 2) if total_attempts > 0 else 0
drop_rate = round((dropped_attempts / total_attempts) * 100, 2) if total_attempts > 0 else 0

total_revenue = filtered_payments["amount"].sum()
avg_score = round(
    filtered_attempts[filtered_attempts["status"] == "completed"]["score"].mean(), 2
) if completed_attempts > 0 else 0

pass_rate = round(
    (filtered_attempts["passed"].sum() / completed_attempts) * 100, 2
) if completed_attempts > 0 else 0

# -----------------------------
# Title
# -----------------------------
st.title("🎓 Exam Platform Business Analytics Dashboard")
st.caption("Analytics for quizzes, attempts, completion, drop-offs, revenue, scores, and proctoring events")

# -----------------------------
# KPI Section
# -----------------------------
st.subheader("📌 Key Business Metrics")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Students", total_students)
col2.metric("Total Quizzes", total_quizzes)
col3.metric("Total Attempts", total_attempts)
col4.metric("Total Revenue", f"₹{total_revenue:,.0f}")

col5, col6, col7, col8 = st.columns(4)
col5.metric("Completed Attempts", completed_attempts)
col6.metric("Dropped Attempts", dropped_attempts)
col7.metric("Completion Rate", f"{completion_rate}%")
col8.metric("Drop Rate", f"{drop_rate}%")

col9, col10 = st.columns(2)
col9.metric("Average Score", avg_score)
col10.metric("Pass Rate", f"{pass_rate}%")

st.markdown("---")

# -----------------------------
# Charts Row 1
# -----------------------------
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Attempts by Status")
    if not filtered_attempts.empty:
        st.bar_chart(filtered_attempts["status"].value_counts())
    else:
        st.info("No data available for selected filters")

with col_b:
    st.subheader("Revenue by Quiz")
    if not filtered_payments.empty:
        revenue_by_quiz = (
            filtered_payments
            .merge(quizzes, on="quiz_id")
            .groupby("quiz_title")["amount"]
            .sum()
            .sort_values(ascending=False)
        )
        st.bar_chart(revenue_by_quiz)
    else:
        st.info("No revenue data available")

# -----------------------------
# Charts Row 2
# -----------------------------
col_c, col_d = st.columns(2)

with col_c:
    st.subheader("Average Score by Quiz")
    completed_data = filtered_attempts[filtered_attempts["status"] == "completed"]
    if not completed_data.empty:
        avg_score_by_quiz = (
            completed_data
            .groupby("quiz_title")["score"]
            .mean()
            .sort_values(ascending=False)
        )
        st.bar_chart(avg_score_by_quiz)
    else:
        st.info("No completed attempts available")

with col_d:
    st.subheader("Attempts by Subject")
    if not filtered_attempts.empty:
        attempts_by_subject = (
            filtered_attempts
            .groupby("subject")["attempt_id"]
            .count()
            .sort_values(ascending=False)
        )
        st.bar_chart(attempts_by_subject)
    else:
        st.info("No subject data available")

# -----------------------------
# Charts Row 3
# -----------------------------
col_e, col_f = st.columns(2)

with col_e:
    st.subheader("Proctoring Event Distribution")
    if not filtered_proctoring.empty:
        st.bar_chart(filtered_proctoring["event_type"].value_counts())
    else:
        st.info("No proctoring events found")

with col_f:
    st.subheader("Daily Revenue Trend")
    if not filtered_payments.empty:
        daily_revenue = (
            filtered_payments
            .groupby("payment_date")["amount"]
            .sum()
            .sort_index()
        )
        st.line_chart(daily_revenue)
    else:
        st.info("No daily revenue data available")

st.markdown("---")

# -----------------------------
# Quiz summary table
# -----------------------------
st.subheader("📋 Quiz-wise Detailed Summary")

if not filtered_attempts.empty:
    quiz_summary = filtered_attempts.groupby("quiz_title").agg(
        attempts=("attempt_id", "count"),
        completed=("status", lambda x: (x == "completed").sum()),
        dropped=("status", lambda x: (x == "dropped").sum()),
        avg_score=("score", "mean")
    ).reset_index()

    if not filtered_payments.empty:
        quiz_revenue = (
            filtered_payments
            .merge(quizzes, on="quiz_id")
            .groupby("quiz_title")["amount"]
            .sum()
            .reset_index()
        )
        quiz_summary = quiz_summary.merge(quiz_revenue, on="quiz_title", how="left")
    else:
        quiz_summary["amount"] = 0

    quiz_summary["amount"] = quiz_summary["amount"].fillna(0)
    quiz_summary.rename(columns={"amount": "revenue"}, inplace=True)
    quiz_summary["avg_score"] = quiz_summary["avg_score"].round(2)

    st.dataframe(quiz_summary, use_container_width=True)
else:
    st.info("No summary available for selected filters")

# -----------------------------
# Quick insights
# -----------------------------
st.markdown("---")
st.subheader("🚀 Quick Insights")

if not filtered_attempts.empty:
    top_quiz_by_attempts = filtered_attempts["quiz_title"].value_counts().idxmax()

    if not filtered_payments.empty:
        revenue_temp = (
            filtered_payments
            .merge(quizzes, on="quiz_id")
            .groupby("quiz_title")["amount"]
            .sum()
        )
        top_revenue_quiz = revenue_temp.idxmax()
    else:
        top_revenue_quiz = "N/A"

    if completed_attempts > 0:
        best_score_quiz = (
            filtered_attempts[filtered_attempts["status"] == "completed"]
            .groupby("quiz_title")["score"]
            .mean()
            .idxmax()
        )
    else:
        best_score_quiz = "N/A"

    drop_data = filtered_attempts.groupby("quiz_title")["status"].apply(lambda x: (x == "dropped").sum())
    worst_drop_quiz = drop_data.idxmax() if not drop_data.empty else "N/A"

    st.write(f"✅ Most attempted quiz: **{top_quiz_by_attempts}**")
    st.write(f"💰 Highest revenue generating quiz: **{top_revenue_quiz}**")
    st.write(f"🏆 Best average score quiz: **{best_score_quiz}**")
    st.write(f"⚠️ Highest drop-off quiz: **{worst_drop_quiz}**")
else:
    st.info("No insights available")

# -----------------------------
# Suspicious attempts analysis
# -----------------------------
st.markdown("---")
st.subheader("⚠️ Suspicious Attempts Analysis")

if not filtered_proctoring.empty:
    suspicious_counts = filtered_proctoring.groupby("attempt_id").size()
    risky_attempts = suspicious_counts[suspicious_counts >= 2]

    st.write(f"Total Risky Attempts: **{len(risky_attempts)}**")
    st.bar_chart(filtered_proctoring["event_type"].value_counts())
else:
    st.info("No suspicious activity found")

# -----------------------------
# Business insights
# -----------------------------
st.markdown("---")
st.subheader("🧠 Business Insights")

if total_attempts == 0:
    st.info("No data available for business insights")
else:
    if completion_rate < 60:
        st.warning("Low completion rate detected. Many users are not finishing quizzes.")

    if drop_rate > 20:
        st.warning("High drop rate detected. Quiz difficulty or user experience may need improvement.")

    if avg_score < 50:
        st.warning("Average score is low. Questions may be too difficult or students may need better preparation.")

    if total_revenue > 50000:
        st.success("Strong revenue performance detected.")

    if not filtered_proctoring.empty and len(filtered_proctoring) > 200:
        st.warning("High suspicious activity detected. Proctoring controls may need strengthening.")

# -----------------------------
# Download data
# -----------------------------
st.markdown("---")
st.subheader("⬇️ Download Data")

csv = filtered_attempts.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Attempts Data",
    data=csv,
    file_name="filtered_attempts.csv",
    mime="text/csv"
)