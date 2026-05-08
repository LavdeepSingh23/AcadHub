import streamlit as st
import plotly.express as px
import pandas as pd
from db import run_query, run_procedure, run_write
from styles import inject_styles, sidebar_logo, page_header, section_header, PLOTLY_LAYOUT

st.set_page_config(page_title="AcadHub — Admin", layout="wide", initial_sidebar_state="expanded")
inject_styles()

if not st.session_state.get("logged_in") or st.session_state.get("role") != "Admin":
    st.switch_page("app.py")

name = st.session_state.user_name

# ── Sidebar ─────────────────────────────────────────────────
sidebar_logo(role="Admin", user_name=name)

st.sidebar.markdown(
    """
    <div style="margin-bottom:8px;">
        <div style="font-family:'Inter',sans-serif;font-size:0.7rem;font-weight:600;
                    text-transform:uppercase;letter-spacing:0.08em;color:#334155;
                    margin-bottom:8px;">Navigation</div>
    </div>
    """,
    unsafe_allow_html=True,
)
nav_items = ["🗂 Overview", "📊 Performance Report", "📅 Attendance", "⚠️ At-Risk Students",
             "🏆 Leaderboard", "👤 Manage Students", "📋 Manage Enrollment",
             "✅ Manage Attendance", "🔍 Raw Queries"]
for item in nav_items:
    st.sidebar.markdown(
        f"""<div style="padding:8px 12px;border-radius:8px;margin-bottom:3px;
                        color:#64748B;font-family:'Inter',sans-serif;font-size:0.82rem;">{item}</div>""",
        unsafe_allow_html=True,
    )

st.sidebar.markdown("<div style='height:1px;background:rgba(255,255,255,0.05);margin:16px 0'></div>", unsafe_allow_html=True)
if st.sidebar.button("Sign Out", use_container_width=True):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.switch_page("app.py")

# ── Page header ──────────────────────────────────────────────
page_header("Admin Control Panel", "Full system overview, analytics, and management")

# ── KPI Row ──────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Students",    int(run_query("SELECT COUNT(*) AS n FROM STUDENT")["n"].iloc[0]))
c2.metric("Total Faculty",     int(run_query("SELECT COUNT(*) AS n FROM FACULTY")["n"].iloc[0]))
c3.metric("Total Courses",     int(run_query("SELECT COUNT(*) AS n FROM COURSE")["n"].iloc[0]))
c4.metric("Total Assessments", int(run_query("SELECT COUNT(*) AS n FROM ASSESSMENT")["n"].iloc[0]))

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

tabs = st.tabs([
    "🗂 Overview", "📊 Performance", "📅 Attendance", "⚠️ At-Risk",
    "🏆 Leaderboard", "👤 Manage Students", "📋 Enrollment",
    "✅ Attendance Mgmt", "🔍 Raw Queries",
])

# ────────────────────────────────────────────
# TAB 1 — Overview
# ────────────────────────────────────────────
with tabs[0]:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        section_header("All Students")
        students = run_query(
            "SELECT s.roll_no, u.name, s.department, s.branch, s.semester, s.cgpa "
            "FROM STUDENT s JOIN USERS u ON s.user_id=u.user_id ORDER BY s.roll_no"
        )
        st.dataframe(students, use_container_width=True, hide_index=True)

    with col_b:
        section_header("Faculty — Course Assignment")
        fac = run_query(
            "SELECT u.name, f.designation, fc.course_code, c.course_name "
            "FROM FACULTY_COURSE fc JOIN FACULTY f ON fc.faculty_id=f.faculty_id "
            "JOIN USERS u ON f.user_id=u.user_id "
            "JOIN COURSE c ON fc.course_code=c.course_code"
        )
        st.dataframe(fac, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    section_header("Course Catalog")
    courses = run_query("SELECT * FROM COURSE")
    st.dataframe(courses, use_container_width=True, hide_index=True)

# ────────────────────────────────────────────
# TAB 2 — Performance Report
# ────────────────────────────────────────────
with tabs[1]:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    section_header("Full Performance Report", "All students across all courses and assessments")

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
        if val == "Pass": return "background-color:rgba(16,185,129,0.15); color:#34D399; font-weight:600"
        if val == "Fail": return "background-color:rgba(239,68,68,0.15); color:#F87171; font-weight:600"
        return "color:#CBD5E1"

    def color_grade(val):
        if val in ("O","A+","A"): return "background-color:rgba(16,185,129,0.15); color:#34D399; font-weight:600"
        if val == "F":            return "background-color:rgba(239,68,68,0.15); color:#F87171; font-weight:600"
        return "color:#CBD5E1"

    if not perf.empty:
        st.dataframe(
            perf.style.applymap(color_result, subset=["result"])
                      .applymap(color_grade,  subset=["grade"]),
            use_container_width=True, hide_index=True,
        )

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        section_header("Marks Distribution by Course", "Box plot — spread of marks per course")

        fig = px.box(
            perf, x="course_name", y="marks_obtained", color="course_name",
            labels={"marks_obtained": "Marks", "course_name": "Course"},
            color_discrete_sequence=["#6366F1", "#10B981", "#F59E0B", "#EC4899"],
        )
        fig.update_layout(**PLOTLY_LAYOUT, showlegend=False)
        fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", zeroline=False)
        fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", zeroline=False)
        st.plotly_chart(fig, use_container_width=True)

# ────────────────────────────────────────────
# TAB 3 — Attendance
# ────────────────────────────────────────────
with tabs[2]:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    section_header("Attendance Summary — All Students")

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
        if val == "Low":  return "background-color:rgba(239,68,68,0.15); color:#F87171; font-weight:600"
        if val == "Good": return "background-color:rgba(16,185,129,0.15); color:#34D399; font-weight:600"
        return "color:#CBD5E1"

    if not att.empty:
        # Quick counts
        good_count = (att["status"] == "Good").sum()
        low_count  = (att["status"] == "Low").sum()
        col_g, col_l, _ = st.columns([1, 1, 3])
        col_g.metric("Good Attendance", good_count)
        col_l.metric("Low Attendance",  low_count)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.dataframe(
            att.style.applymap(att_style, subset=["status"]),
            use_container_width=True, hide_index=True,
        )

# ────────────────────────────────────────────
# TAB 4 — At-Risk Students
# ────────────────────────────────────────────
with tabs[3]:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    section_header("At-Risk Students", "Flagged by low marks (<40) or low attendance (<75%)")

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
        if val == "At Risk": return "background-color:rgba(239,68,68,0.15); color:#F87171; font-weight:600"
        return "background-color:rgba(16,185,129,0.15); color:#34D399; font-weight:600"

    if not risk.empty:
        at_risk_count = (risk["risk_status"] == "At Risk").sum()
        safe_count    = (risk["risk_status"] == "Safe").sum()

        col_r, col_s, _ = st.columns([1, 1, 3])
        col_r.metric("At Risk", at_risk_count)
        col_s.metric("Safe",    safe_count)

        if at_risk_count > 0:
            st.markdown(
                f"""<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);
                                border-radius:10px;padding:12px 16px;margin:12px 0;
                                display:flex;align-items:center;gap:10px;">
                      <span style="font-size:1.1rem;">🚨</span>
                      <span style="font-family:'Inter',sans-serif;font-size:0.83rem;color:#F87171;">
                          <b>{at_risk_count}</b> student-course combinations require immediate attention.
                      </span>
                    </div>""",
                unsafe_allow_html=True,
            )

        st.dataframe(
            risk.style.applymap(risk_style, subset=["risk_status"]),
            use_container_width=True, hide_index=True,
        )

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        section_header("Risk Scatter Plot", "Attendance % vs Average Marks")

        fig = px.scatter(
            risk, x="att_pct", y="avg_marks",
            color="risk_status", text="name",
            color_discrete_map={"At Risk": "#EF4444", "Safe": "#10B981"},
            labels={"att_pct": "Attendance %", "avg_marks": "Avg Marks"},
        )
        fig.add_hline(y=40, line_dash="dash", line_color="#6366F1",
                      annotation_text="40 mark threshold",
                      annotation_font_color="#6366F1")
        fig.add_vline(x=75, line_dash="dash", line_color="#F59E0B",
                      annotation_text="75% attendance",
                      annotation_font_color="#F59E0B")
        fig.update_layout(**PLOTLY_LAYOUT)
        fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", zeroline=False)
        fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", zeroline=False)
        st.plotly_chart(fig, use_container_width=True)

# ────────────────────────────────────────────
# TAB 5 — Leaderboard
# ────────────────────────────────────────────
with tabs[4]:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    section_header("Student Leaderboard", "Ranked by total marks across all assessments")

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

        # Top-3 podium cards
        top3 = lb.head(3)
        medals = ["🥇", "🥈", "🥉"]
        medal_cols = st.columns(3)
        for i, (_, row) in enumerate(top3.iterrows()):
            with medal_cols[i]:
                accent = ["#FCD34D", "#94A3B8", "#D97706"][i]
                st.markdown(
                    f"""<div style="background:rgba(255,255,255,0.025);
                                    border:1px solid rgba(255,255,255,0.07);
                                    border-radius:14px;padding:20px;text-align:center;
                                    margin-bottom:12px;">
                          <div style="font-size:2rem;margin-bottom:8px;">{medals[i]}</div>
                          <div style="font-family:'Inter',sans-serif;font-weight:700;
                                      font-size:0.95rem;color:#E2E8F0;margin-bottom:4px;">{row['name']}</div>
                          <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;
                                      color:#475569;margin-bottom:10px;">Roll: {row['roll_no']}</div>
                          <div style="font-family:'Inter',sans-serif;font-weight:800;
                                      font-size:1.6rem;letter-spacing:-0.02em;
                                      color:{accent};">{int(row['total_marks'])}</div>
                          <div style="font-family:'Inter',sans-serif;font-size:0.68rem;
                                      color:#475569;text-transform:uppercase;letter-spacing:0.07em;">
                              total marks
                          </div>
                        </div>""",
                    unsafe_allow_html=True,
                )

        st.dataframe(lb, use_container_width=True, hide_index=True)

        fig = px.bar(
            lb, x="name", y="total_marks",
            color="total_marks",
            color_continuous_scale=["#4338CA", "#6366F1", "#A5B4FC"],
            labels={"total_marks": "Total Marks", "name": "Student"},
            text="total_marks",
        )
        fig.update_traces(textposition="outside", textfont_color="#94A3B8")
        fig.update_layout(**{**PLOTLY_LAYOUT, "margin": dict(t=32, b=8, l=8, r=8)},
                          coloraxis_showscale=False)
        fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", zeroline=False)
        fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", zeroline=False)
        st.plotly_chart(fig, use_container_width=True)

# ────────────────────────────────────────────
# TAB 6 — Manage Students
# ────────────────────────────────────────────
with tabs[5]:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2)

    with col_left:
        section_header("Add New User + Student")
        with st.form("add_user_form"):
            u_id    = st.number_input("User ID", min_value=10, step=1)
            u_name  = st.text_input("Full Name", placeholder="e.g. Priya Sharma")
            u_uname = st.text_input("Username",  placeholder="e.g. priya23")
            u_pass  = st.text_input("Password",  type="password")
            st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:8px 0'>", unsafe_allow_html=True)
            s_roll  = st.number_input("Roll No",    min_value=1000000000, step=1)
            s_dept  = st.text_input("Department",   value="CSE")
            s_branch= st.text_input("Branch",       value="COE")
            s_sem   = st.number_input("Semester",   min_value=1, max_value=8, step=1, value=4)
            add_btn = st.form_submit_button("Add User & Student →", use_container_width=True)

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
                    else: st.success(f"✓ {m}")

    with col_right:
        section_header("Update Student Marks")
        with st.form("update_marks_form"):
            um_roll  = st.number_input("Roll No",       min_value=1000000000, step=1, key="um_roll")
            um_asmt  = st.number_input("Assessment ID", min_value=1, step=1)
            um_marks = st.number_input("New Marks",     min_value=0, step=1)
            upd_btn  = st.form_submit_button("Update Marks →", use_container_width=True)

        if upd_btn:
            msgs = run_procedure("proc_update_marks",
                (int(um_roll), int(um_asmt), int(um_marks)))
            for m in msgs:
                if "Error" in str(m) or "failed" in str(m): st.error(m)
                else: st.success(f"✓ {m}")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        section_header("Update Student CGPA")
        with st.form("update_cgpa_form"):
            cgpa_roll = st.number_input("Roll No",   min_value=1000000000, step=1, key="cgpa_roll")
            new_cgpa  = st.number_input("New CGPA",  min_value=0.0, max_value=10.0, step=0.1)
            cgpa_btn  = st.form_submit_button("Update CGPA →", use_container_width=True)

        if cgpa_btn:
            msg = run_write(
                "UPDATE STUDENT SET cgpa=%s WHERE roll_no=%s",
                (float(new_cgpa), int(cgpa_roll)),
            )
            if "Error" in str(msg): st.error(msg)
            else: st.success("✓ CGPA updated successfully.")

# ────────────────────────────────────────────
# TAB 7 — Manage Enrollment
# ────────────────────────────────────────────
with tabs[6]:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    section_header("Enroll Student in Course")

    courses_all = run_query("SELECT course_code FROM COURSE")
    course_opts = courses_all["course_code"].tolist() if not courses_all.empty else []

    _, form_enr, _ = st.columns([0.1, 1, 0.1])
    with form_enr:
        with st.form("enroll_form"):
            enr_id   = st.number_input("Enrollment ID (unique)", min_value=100, step=1)
            enr_roll = st.number_input("Student Roll No",         min_value=1000000000, step=1)
            enr_code = st.selectbox("Course", course_opts)
            enr_btn  = st.form_submit_button("Enroll Student →", use_container_width=True)

        if enr_btn:
            msgs = run_procedure("proc_enroll_student",
                (int(enr_id), int(enr_roll), enr_code))
            for m in msgs:
                if "Error" in str(m) or "already" in str(m): st.warning(m)
                else: st.success(f"✓ {m}")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    section_header("Current Enrollments")
    enr_all = run_query(
        "SELECT e.enrollment_id, s.roll_no, u.name, e.course_code, c.course_name "
        "FROM ENROLLMENT e JOIN STUDENT s ON e.roll_no=s.roll_no "
        "JOIN USERS u ON s.user_id=u.user_id JOIN COURSE c ON e.course_code=c.course_code"
    )
    st.dataframe(enr_all, use_container_width=True, hide_index=True)

# ────────────────────────────────────────────
# TAB 8 — Manage Attendance
# ────────────────────────────────────────────
with tabs[7]:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    section_header("Record Attendance")

    _, form_att, _ = st.columns([0.1, 1, 0.1])
    with form_att:
        with st.form("attendance_form"):
            att_id     = st.number_input("Attendance ID (unique)", min_value=100, step=1)
            att_roll   = st.number_input("Student Roll No",         min_value=1000000000, step=1)
            att_course = st.selectbox("Course", course_opts, key="att_course_admin")
            att_date   = st.date_input("Date")
            att_status = st.selectbox("Status", ["Present", "Absent"])
            att_remarks= st.text_input("Remarks (optional)", value="", placeholder="e.g. Medical leave")
            att_btn    = st.form_submit_button("Record Attendance →", use_container_width=True)

        if att_btn:
            msgs = run_procedure("proc_record_attendance", (
                int(att_id), int(att_roll), att_course,
                att_date.strftime("%Y-%m-%d"),
                att_status,
                att_remarks if att_remarks else None,
            ))
            for m in msgs:
                if "Error" in str(m): st.error(m)
                else: st.success(f"✓ {m}")

# ────────────────────────────────────────────
# TAB 9 — Raw Queries
# ────────────────────────────────────────────
with tabs[8]:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    section_header("Predefined SQL Queries", "Run any of the 14 analytical queries against the live database")

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

    col_q, col_btn = st.columns([3, 1])
    with col_q:
        selected_q = st.selectbox("Select Query", list(QUERIES.keys()))
    with col_btn:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        run_btn = st.button("▶  Run Query", use_container_width=True)

    with st.expander("View SQL"):
        st.code(QUERIES[selected_q].strip(), language="sql")

    if run_btn:
        with st.spinner("Executing query…"):
            try:
                result = run_query(QUERIES[selected_q])
                st.markdown(
                    f"""<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.18);
                                    border-radius:8px;padding:10px 14px;margin-bottom:8px;
                                    font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:#34D399;">
                          ✓ {len(result)} rows returned
                        </div>""",
                    unsafe_allow_html=True,
                )
                st.dataframe(result, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Query failed: {e}")