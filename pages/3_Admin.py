import streamlit as st
import plotly.express as px
import pandas as pd
from db import run_query, run_procedure, run_write
from styles import inject_styles, sidebar_logo, page_header

st.set_page_config(page_title="AcadHub — Admin", layout="wide")
inject_styles()

if not st.session_state.get("logged_in") or st.session_state.get("role") != "Admin":
    st.switch_page("app.py")

name = st.session_state.user_name

# ── Sidebar ──
sidebar_logo()
st.sidebar.markdown(
    f"""
    <div style="padding:12px 0;">
        <div style="font-family:'Satoshi',sans-serif; font-weight:700;
                    font-size:1rem; color:#0F172A;">{name}</div>
        <div style="margin-top:6px;">
            <span style="background:#FEF3C7; color:#92400E; padding:2px 10px;
                         border-radius:20px; font-size:0.75rem; font-weight:600;">
                Admin
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.divider()
if st.sidebar.button("Sign Out", use_container_width=True):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.switch_page("app.py")

# ─────────────────────────────────────────────
page_header("Admin Control Panel", "Full system overview and management")

# ── KPI Row ──
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Students",  int(run_query("SELECT COUNT(*) AS n FROM STUDENT")["n"].iloc[0]))
c2.metric("Total Faculty",   int(run_query("SELECT COUNT(*) AS n FROM FACULTY")["n"].iloc[0]))
c3.metric("Total Courses",   int(run_query("SELECT COUNT(*) AS n FROM COURSE")["n"].iloc[0]))
c4.metric("Total Assessments", int(run_query("SELECT COUNT(*) AS n FROM ASSESSMENT")["n"].iloc[0]))

st.markdown("<br>", unsafe_allow_html=True)

tabs = st.tabs([
    "Overview", "Performance Report", "Attendance", "At-Risk Students",
    "Leaderboard", "Manage Students", "Manage Enrollment",
    "Manage Attendance", "Raw Queries",
])

# ──────────── TAB 1: Overview ────────────
with tabs[0]:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### All Students")
        students = run_query(
            "SELECT s.roll_no, u.name, s.department, s.branch, s.semester, s.cgpa "
            "FROM STUDENT s JOIN USERS u ON s.user_id=u.user_id ORDER BY s.roll_no"
        )
        st.dataframe(students, use_container_width=True, hide_index=True)

    with col_b:
        st.markdown("#### Faculty — Course Assignment")
        fac = run_query(
            "SELECT u.name, f.designation, fc.course_code, c.course_name "
            "FROM FACULTY_COURSE fc JOIN FACULTY f ON fc.faculty_id=f.faculty_id "
            "JOIN USERS u ON f.user_id=u.user_id "
            "JOIN COURSE c ON fc.course_code=c.course_code"
        )
        st.dataframe(fac, use_container_width=True, hide_index=True)

    st.markdown("#### Course Catalog")
    courses = run_query("SELECT * FROM COURSE")
    st.dataframe(courses, use_container_width=True, hide_index=True)


# ──────────── TAB 2: Performance Report ────────────
with tabs[1]:
    st.markdown("#### Full Performance Report")
    perf = run_query(
        """
        SELECT s.roll_no, u.name, c.course_name, a.assessment_type,
               sp.marks_obtained, a.total_marks, sp.grade, sp.result,
               ROUND(sp.marks_obtained*100.0/a.total_marks,1) AS pct
        FROM STUDENT_PERFORMANCE sp
        JOIN STUDENT s ON sp.roll_no=s.roll_no
        JOIN USERS u ON s.user_id=u.user_id
        JOIN ASSESSMENT a ON sp.assessment_id=a.assessment_id
        JOIN COURSE c ON a.course_code=c.course_code
        ORDER BY s.roll_no
        """
    )

    def color_result(val):
        if val == "Pass": return "background:#D1FAE5; color:#065F46; font-weight:600"
        if val == "Fail": return "background:#FEE2E2; color:#991B1B; font-weight:600"
        return ""

    def color_grade(val):
        if val in ("O","A+","A"): return "background:#D1FAE5; color:#065F46; font-weight:600"
        if val == "F":            return "background:#FEE2E2; color:#991B1B; font-weight:600"
        return ""

    if not perf.empty:
        st.dataframe(
            perf.style.applymap(color_result, subset=["result"])
                      .applymap(color_grade,  subset=["grade"]),
            use_container_width=True, hide_index=True,
        )

        fig = px.box(
            perf, x="course_name", y="marks_obtained", color="course_name",
            labels={"marks_obtained": "Marks", "course_name": "Course"},
            color_discrete_sequence=["#6366F1", "#10B981", "#F59E0B"],
        )
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                          font_family="Satoshi", showlegend=False,
                          yaxis=dict(gridcolor="#F1F5F9"), margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)


# ──────────── TAB 3: Attendance ────────────
with tabs[2]:
    st.markdown("#### Attendance Summary — All Students")
    att = run_query(
        """
        SELECT s.roll_no, u.name, a.course_code,
               COUNT(*) AS total_classes,
               SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present,
               ROUND(SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*),1) AS pct,
               CASE WHEN SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*) >= 75
                    THEN 'Good' ELSE 'Low' END AS status
        FROM ATTENDANCE a
        JOIN STUDENT s ON a.roll_no=s.roll_no
        JOIN USERS u ON s.user_id=u.user_id
        GROUP BY s.roll_no, u.name, a.course_code
        ORDER BY pct
        """
    )

    def att_style(val):
        if val == "Low":  return "background:#FEE2E2; color:#991B1B; font-weight:600"
        if val == "Good": return "background:#D1FAE5; color:#065F46; font-weight:600"
        return ""

    if not att.empty:
        st.dataframe(
            att.style.applymap(att_style, subset=["status"]),
            use_container_width=True, hide_index=True,
        )


# ──────────── TAB 4: At-Risk Students ────────────
with tabs[3]:
    st.markdown("#### At-Risk Students")
    risk = run_query(
        """
        SELECT s.roll_no, u.name, c.course_code, c.course_name,
               ROUND(SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*),1) AS att_pct,
               ROUND(AVG(sp.marks_obtained),1) AS avg_marks,
               CASE WHEN AVG(sp.marks_obtained) < 40
                         OR SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*) < 75
                    THEN 'At Risk' ELSE 'Safe' END AS risk_status
        FROM STUDENT s
        JOIN USERS u ON s.user_id=u.user_id
        JOIN ENROLLMENT e ON s.roll_no=e.roll_no
        JOIN COURSE c ON e.course_code=c.course_code
        LEFT JOIN STUDENT_PERFORMANCE sp ON s.roll_no=sp.roll_no
        LEFT JOIN ATTENDANCE a ON s.roll_no=a.roll_no AND a.course_code=c.course_code
        GROUP BY s.roll_no, u.name, c.course_code, c.course_name
        ORDER BY risk_status DESC
        """
    )

    def risk_style(val):
        if val == "At Risk": return "background:#FEE2E2; color:#991B1B; font-weight:600"
        return "background:#D1FAE5; color:#065F46; font-weight:600"

    if not risk.empty:
        at_risk_count = (risk["risk_status"] == "At Risk").sum()
        st.warning(f"{at_risk_count} student-course combinations flagged as At Risk.")
        st.dataframe(
            risk.style.applymap(risk_style, subset=["risk_status"]),
            use_container_width=True, hide_index=True,
        )

        fig = px.scatter(
            risk, x="att_pct", y="avg_marks",
            color="risk_status", text="name",
            color_discrete_map={"At Risk": "#EF4444", "Safe": "#10B981"},
            labels={"att_pct": "Attendance %", "avg_marks": "Avg Marks"},
        )
        fig.add_hline(y=40, line_dash="dash", line_color="#6366F1",
                      annotation_text="40 mark threshold")
        fig.add_vline(x=75, line_dash="dash", line_color="#F59E0B",
                      annotation_text="75% attendance")
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                          font_family="Satoshi", margin=dict(t=10),
                          xaxis=dict(gridcolor="#F1F5F9"), yaxis=dict(gridcolor="#F1F5F9"))
        st.plotly_chart(fig, use_container_width=True)


# ──────────── TAB 5: Leaderboard ────────────
with tabs[4]:
    st.markdown("#### Student Leaderboard — Total Marks")
    lb = run_query(
        """
        SELECT s.roll_no, u.name, s.cgpa,
               SUM(sp.marks_obtained) AS total_marks
        FROM STUDENT s
        JOIN USERS u ON s.user_id=u.user_id
        JOIN STUDENT_PERFORMANCE sp ON s.roll_no=sp.roll_no
        GROUP BY s.roll_no, u.name, s.cgpa
        ORDER BY total_marks DESC
        """
    )
    if not lb.empty:
        lb.insert(0, "Rank", range(1, len(lb) + 1))
        st.dataframe(lb, use_container_width=True, hide_index=True)

        fig = px.bar(
            lb, x="name", y="total_marks",
            color="total_marks",
            color_continuous_scale=["#A5B4FC", "#6366F1", "#4338CA"],
            labels={"total_marks": "Total Marks", "name": "Student"},
            text="total_marks",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font_family="Satoshi", coloraxis_showscale=False,
            yaxis=dict(gridcolor="#F1F5F9"), margin=dict(t=30),
        )
        st.plotly_chart(fig, use_container_width=True)


# ──────────── TAB 6: Manage Students ────────────
with tabs[5]:
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Add New User + Student")
        with st.form("add_user_form"):
            u_id    = st.number_input("User ID", min_value=10, step=1)
            u_name  = st.text_input("Full Name")
            u_uname = st.text_input("Username")
            u_pass  = st.text_input("Password")
            st.form_submit_button  # just label
            st.markdown("---")
            s_roll  = st.number_input("Roll No", min_value=1000000000, step=1)
            s_dept  = st.text_input("Department", value="CSE")
            s_branch= st.text_input("Branch", value="COE")
            s_sem   = st.number_input("Semester", min_value=1, max_value=8, step=1, value=4)
            add_btn = st.form_submit_button("Add User & Student")

        if add_btn:
            if not u_name or not u_uname or not u_pass:
                st.warning("Fill all user fields.")
            else:
                msgs = run_procedure("proc_add_user",
                    (int(u_id), u_name, u_uname, u_pass, "Student"))
                for m in msgs:
                    st.info(m)
                msgs2 = run_procedure("proc_safe_insert_student",
                    (int(s_roll), s_dept, s_branch, int(s_sem), int(u_id)))
                for m in msgs2:
                    if "Error" in str(m): st.error(m)
                    else: st.success(m)

    with col_right:
        st.markdown("#### Update Student Marks")
        with st.form("update_marks_form"):
            um_roll  = st.number_input("Roll No", min_value=1000000000, step=1, key="um_roll")
            um_asmt  = st.number_input("Assessment ID", min_value=1, step=1)
            um_marks = st.number_input("New Marks", min_value=0, step=1)
            upd_btn  = st.form_submit_button("Update Marks")

        if upd_btn:
            msgs = run_procedure("proc_update_marks",
                (int(um_roll), int(um_asmt), int(um_marks)))
            for m in msgs:
                if "Error" in str(m) or "failed" in str(m): st.error(m)
                else: st.success(m)

        st.markdown("#### Update Student CGPA")
        with st.form("update_cgpa_form"):
            cgpa_roll = st.number_input("Roll No", min_value=1000000000, step=1, key="cgpa_roll")
            new_cgpa  = st.number_input("New CGPA", min_value=0.0, max_value=10.0, step=0.1)
            cgpa_btn  = st.form_submit_button("Update CGPA")

        if cgpa_btn:
            msg = run_write(
                "UPDATE STUDENT SET cgpa=%s WHERE roll_no=%s",
                (float(new_cgpa), int(cgpa_roll)),
            )
            if "Error" in str(msg): st.error(msg)
            else: st.success("CGPA updated successfully.")


# ──────────── TAB 7: Manage Enrollment ────────────
with tabs[6]:
    st.markdown("#### Enroll Student in Course")
    courses_all = run_query("SELECT course_code FROM COURSE")
    course_opts = courses_all["course_code"].tolist() if not courses_all.empty else []

    with st.form("enroll_form"):
        enr_id   = st.number_input("Enrollment ID (unique)", min_value=100, step=1)
        enr_roll = st.number_input("Student Roll No", min_value=1000000000, step=1)
        enr_code = st.selectbox("Course", course_opts)
        enr_btn  = st.form_submit_button("Enroll Student")

    if enr_btn:
        msgs = run_procedure("proc_enroll_student",
            (int(enr_id), int(enr_roll), enr_code))
        for m in msgs:
            if "Error" in str(m) or "already" in str(m): st.warning(m)
            else: st.success(m)

    st.markdown("#### Current Enrollments")
    enr_all = run_query(
        "SELECT e.enrollment_id, s.roll_no, u.name, e.course_code, c.course_name "
        "FROM ENROLLMENT e JOIN STUDENT s ON e.roll_no=s.roll_no "
        "JOIN USERS u ON s.user_id=u.user_id JOIN COURSE c ON e.course_code=c.course_code"
    )
    st.dataframe(enr_all, use_container_width=True, hide_index=True)


# ──────────── TAB 8: Manage Attendance ────────────
with tabs[7]:
    st.markdown("#### Record Attendance")
    with st.form("attendance_form"):
        att_id     = st.number_input("Attendance ID (unique)", min_value=100, step=1)
        att_roll   = st.number_input("Student Roll No", min_value=1000000000, step=1)
        att_course = st.selectbox("Course", course_opts, key="att_course_admin")
        att_date   = st.date_input("Date")
        att_status = st.selectbox("Status", ["Present", "Absent"])
        att_remarks= st.text_input("Remarks (optional)", value="")
        att_btn    = st.form_submit_button("Record Attendance")

    if att_btn:
        msgs = run_procedure("proc_record_attendance", (
            int(att_id), int(att_roll), att_course,
            att_date.strftime("%Y-%m-%d"),
            att_status,
            att_remarks if att_remarks else None,
        ))
        for m in msgs:
            if "Error" in str(m): st.error(m)
            else: st.success(m)


# ──────────── TAB 9: Raw Queries ────────────
with tabs[8]:
    st.markdown("#### Run Predefined Queries")

    QUERIES = {
        "Q1 — Full Performance Report": """
            SELECT s.roll_no, u.name, c.course_name, a.assessment_type,
                   sp.marks_obtained, sp.grade,
                   ROUND(sp.marks_obtained*100.0/a.total_marks,2) AS percentage
            FROM STUDENT s
            JOIN USERS u ON s.user_id=u.user_id
            JOIN STUDENT_PERFORMANCE sp ON sp.roll_no=s.roll_no
            JOIN ASSESSMENT a ON sp.assessment_id=a.assessment_id
            JOIN COURSE c ON a.course_code=c.course_code
            ORDER BY s.roll_no
        """,
        "Q2 — Class Topper": """
            SELECT u.name, s.roll_no, sp.marks_obtained
            FROM STUDENT_PERFORMANCE sp
            JOIN STUDENT s ON sp.roll_no=s.roll_no
            JOIN USERS u ON s.user_id=u.user_id
            WHERE sp.marks_obtained=(SELECT MAX(marks_obtained) FROM STUDENT_PERFORMANCE)
        """,
        "Q3 — Students Scoring Below 40": """
            SELECT u.name, s.roll_no, c.course_name, sp.marks_obtained
            FROM STUDENT_PERFORMANCE sp
            JOIN STUDENT s ON sp.roll_no=s.roll_no
            JOIN USERS u ON s.user_id=u.user_id
            JOIN ASSESSMENT a ON sp.assessment_id=a.assessment_id
            JOIN COURSE c ON a.course_code=c.course_code
            WHERE sp.marks_obtained < 40
        """,
        "Q4 — Attendance Summary with Status": """
            SELECT s.roll_no, u.name, a.course_code,
                   COUNT(*) AS total_classes,
                   SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present_count,
                   ROUND(SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS attendance_pct,
                   CASE WHEN SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*) >= 75
                        THEN 'Good' ELSE 'Low Attendance' END AS status
            FROM ATTENDANCE a
            JOIN STUDENT s ON a.roll_no=s.roll_no
            JOIN USERS u ON s.user_id=u.user_id
            GROUP BY s.roll_no, u.name, a.course_code
            ORDER BY attendance_pct DESC
        """,
        "Q5 — Overall Grade per Student per Course": """
            SELECT e.roll_no, u.name AS student_name, e.course_code, c.course_name,
                   fn_student_grade_letter(e.roll_no, e.course_code) AS overall_grade
            FROM ENROLLMENT e
            JOIN STUDENT s ON e.roll_no=s.roll_no
            JOIN USERS u ON s.user_id=u.user_id
            JOIN COURSE c ON e.course_code=c.course_code
            ORDER BY e.roll_no
        """,
        "Q6 — Class Average per Assessment": """
            SELECT a.assessment_id, a.course_code, c.course_name,
                   a.assessment_type, a.total_marks,
                   fn_course_avg_marks(a.assessment_id) AS class_avg
            FROM ASSESSMENT a JOIN COURSE c ON a.course_code=c.course_code
            ORDER BY a.course_code
        """,
        "Q7 — Exam Eligibility Report": """
            SELECT e.roll_no, u.name AS student_name, e.course_code, c.course_name,
                   fn_attendance_percentage(e.roll_no, e.course_code) AS attendance_pct,
                   CASE fn_is_eligible_for_exam(e.roll_no, e.course_code)
                        WHEN 1 THEN 'Eligible' ELSE 'NOT Eligible (< 75%)' END AS exam_eligibility
            FROM ENROLLMENT e
            JOIN STUDENT s ON e.roll_no=s.roll_no
            JOIN USERS u ON s.user_id=u.user_id
            JOIN COURSE c ON e.course_code=c.course_code
            ORDER BY exam_eligibility
        """,
        "Q8 — Comprehensive Student Dashboard": """
            SELECT s.roll_no, u.name AS student_name, s.cgpa,
                   COUNT(DISTINCT e.course_code) AS courses_enrolled,
                   fn_total_marks(s.roll_no) AS total_marks_all_assessments
            FROM STUDENT s
            JOIN USERS u ON s.user_id=u.user_id
            JOIN ENROLLMENT e ON s.roll_no=e.roll_no
            GROUP BY s.roll_no, u.name, s.cgpa
            ORDER BY s.roll_no
        """,
        "Q9 — Faculty Course Load + Class Avg": """
            SELECT u.name AS faculty_name, f.designation, fc.course_code,
                   c.course_name, a.assessment_type,
                   fn_course_avg_marks(a.assessment_id) AS class_avg_marks,
                   a.total_marks,
                   ROUND(fn_course_avg_marks(a.assessment_id)*100.0/a.total_marks,2) AS avg_pct
            FROM FACULTY_COURSE fc
            JOIN FACULTY f ON fc.faculty_id=f.faculty_id
            JOIN USERS u ON f.user_id=u.user_id
            JOIN COURSE c ON fc.course_code=c.course_code
            JOIN ASSESSMENT a ON c.course_code=a.course_code
            ORDER BY faculty_name, fc.course_code
        """,
        "Q10 — Topper per Course": """
            SELECT c.course_name, u.name, sp.marks_obtained
            FROM STUDENT_PERFORMANCE sp
            JOIN ASSESSMENT a ON sp.assessment_id=a.assessment_id
            JOIN COURSE c ON a.course_code=c.course_code
            JOIN STUDENT s ON sp.roll_no=s.roll_no
            JOIN USERS u ON s.user_id=u.user_id
            WHERE sp.marks_obtained=(
                SELECT MAX(sp2.marks_obtained)
                FROM STUDENT_PERFORMANCE sp2
                JOIN ASSESSMENT a2 ON sp2.assessment_id=a2.assessment_id
                WHERE a2.course_code=c.course_code
            )
        """,
        "Q11 — Dynamic Fail Detection": """
            SELECT u.name, s.roll_no, c.course_name, sp.marks_obtained, a.passing_marks
            FROM STUDENT_PERFORMANCE sp
            JOIN STUDENT s ON sp.roll_no=s.roll_no
            JOIN USERS u ON s.user_id=u.user_id
            JOIN ASSESSMENT a ON sp.assessment_id=a.assessment_id
            JOIN COURSE c ON a.course_code=c.course_code
            WHERE sp.marks_obtained < a.passing_marks
        """,
        "Q12 — Student Leaderboard": """
            SELECT s.roll_no, u.name, SUM(sp.marks_obtained) AS total_marks
            FROM STUDENT s
            JOIN USERS u ON s.user_id=u.user_id
            JOIN STUDENT_PERFORMANCE sp ON s.roll_no=sp.roll_no
            GROUP BY s.roll_no, u.name
            ORDER BY total_marks DESC
        """,
        "Q13 — Course-wise Avg Attendance": """
            SELECT course_code,
                   ROUND(AVG(CASE WHEN status='Present' THEN 100 ELSE 0 END),2) AS avg_attendance
            FROM ATTENDANCE GROUP BY course_code
        """,
        "Q14 — Students with No Attendance Records": """
            SELECT s.roll_no, u.name
            FROM STUDENT s
            JOIN USERS u ON s.user_id=u.user_id
            LEFT JOIN ATTENDANCE a ON s.roll_no=a.roll_no
            WHERE a.roll_no IS NULL
        """,
    }

    selected_q = st.selectbox("Select Query", list(QUERIES.keys()))
    if st.button("Run Query"):
        with st.spinner("Executing..."):
            try:
                result = run_query(QUERIES[selected_q])
                st.success(f"{len(result)} rows returned.")
                st.dataframe(result, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Query failed: {e}")

    with st.expander("View SQL"):
        st.code(QUERIES[selected_q].strip(), language="sql")
