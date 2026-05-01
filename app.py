import streamlit as st
import pandas as pd
from db import get_connection

st.set_page_config(page_title="AcadHub", layout="wide")

st.title("📘 AcadHub - Unified Academic System")

# Tabs instead of sidebar
tab1, tab2, tab3 = st.tabs(["🎓 Student Dashboard", "🧑‍🏫 Faculty Panel", "📂 PYQ Viewer"])

conn = get_connection()
cursor = conn.cursor(dictionary=True)

# -------------------------------
# 🎓 STUDENT DASHBOARD
# -------------------------------
with tab1:
    st.subheader("Student Dashboard")

    col1, col2 = st.columns(2)
    roll = col1.number_input("Enter Roll Number", step=1)

    if st.button("Fetch Data"):
        # Student name
        cursor.execute("""
            SELECT u.name
            FROM STUDENT s
            JOIN USERS u ON s.user_id = u.user_id
            WHERE s.roll_no = %s
        """, (roll,))
        student = cursor.fetchone()

        if not student:
            st.error("Student not found")
        else:
            st.success(f"Showing data for {student['name']}")

            # Marks
            cursor.execute("""
                SELECT c.course_name, sp.marks_obtained, sp.grade
                FROM STUDENT_PERFORMANCE sp
                JOIN ASSESSMENT a ON sp.assessment_id = a.assessment_id
                JOIN COURSE c ON a.course_code = c.course_code
                WHERE sp.roll_no = %s
            """, (roll,))
            marks = cursor.fetchall()

            st.markdown("### 📊 Marks")
            st.dataframe(pd.DataFrame(marks))

            # Attendance
            cursor.execute("""
                SELECT course_code,
                       ROUND(SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS attendance_pct
                FROM ATTENDANCE
                WHERE roll_no = %s
                GROUP BY course_code
            """, (roll,))
            attendance = cursor.fetchall()

            st.markdown("### 📅 Attendance")
            st.dataframe(pd.DataFrame(attendance))

            # Total Marks (function demo)
            cursor.execute("SELECT fn_total_marks(%s) AS total", (roll,))
            total = cursor.fetchone()

            st.info(f"Total Marks: {total['total']}")

# -------------------------------
# 🧑‍🏫 FACULTY PANEL
# -------------------------------
with tab2:
    st.subheader("Update Student Marks")

    col1, col2, col3 = st.columns(3)

    roll = col1.number_input("Roll No", step=1)
    assessment = col2.number_input("Assessment ID", step=1)
    marks = col3.number_input("Marks", step=1)

    if st.button("Update Marks"):
        try:
            cursor.callproc("proc_update_marks", (roll, assessment, marks))
            conn.commit()
            st.success("Marks updated successfully")
        except Exception as e:
            st.error(str(e))

    st.markdown("---")

    # 🔥 Topper section
    st.markdown("### 🏆 Topper")

    cursor.execute("""
        SELECT u.name, s.roll_no, MAX(sp.marks_obtained) AS marks
        FROM STUDENT_PERFORMANCE sp
        JOIN STUDENT s ON sp.roll_no = s.roll_no
        JOIN USERS u ON s.user_id = u.user_id
    """)
    topper = cursor.fetchone()

    if topper:
        st.success(f"{topper['name']} (Roll {topper['roll_no']}) - {topper['marks']} marks")

# -------------------------------
# 📂 PYQ VIEWER
# -------------------------------
with tab3:
    st.subheader("Previous Year Questions")

    course = st.text_input("Enter Course Code (e.g. CS101)")

    if st.button("Load PYQs"):
        cursor.execute("""
            SELECT question, year, exam_type
            FROM PYQ
            WHERE course_code = %s
        """, (course,))
        pyqs = cursor.fetchall()

        if pyqs:
            st.dataframe(pd.DataFrame(pyqs))
        else:
            st.warning("No PYQs found")

    st.markdown("---")

    # 🔥 Low attendance alert (extra feature)
    st.markdown("### ⚠️ Low Attendance (<75%)")

    cursor.execute("""
        SELECT s.roll_no, u.name,
               ROUND(SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS pct
        FROM ATTENDANCE a
        JOIN STUDENT s ON a.roll_no = s.roll_no
        JOIN USERS u ON s.user_id = u.user_id
        GROUP BY s.roll_no, u.name
        HAVING pct < 75
    """)
    low_att = cursor.fetchall()

    if low_att:
        st.dataframe(pd.DataFrame(low_att))
    else:
        st.success("All students above 75%")