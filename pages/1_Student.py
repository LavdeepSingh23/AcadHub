import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from db import run_query, run_procedure
from styles import inject_styles, sidebar_logo, page_header

st.set_page_config(page_title="AcadHub — Student", layout="wide")
inject_styles()

# ── Auth guard ──
if not st.session_state.get("logged_in") or st.session_state.get("role") != "Student":
    st.switch_page("app.py")

roll = st.session_state.roll_no
name = st.session_state.user_name

# ── Sidebar ──
sidebar_logo()
st.sidebar.markdown(
    f"""
    <div style="padding:12px 0;">
        <div style="font-family:'Satoshi',sans-serif; font-weight:700;
                    font-size:1rem; color:#0F172A;">{name}</div>
        <div style="font-size:0.78rem; color:#64748B; margin-top:2px;">
            Roll No: {roll}
        </div>
        <div style="margin-top:6px;">
            <span style="background:#EEF2FF; color:#6366F1; padding:2px 10px;
                         border-radius:20px; font-size:0.75rem; font-weight:600;">
                Student
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
#  MAIN
# ─────────────────────────────────────────────
page_header("Student Dashboard", f"Welcome back, {name}")

# ── Metric row ──
dash = run_query(
    "SELECT cgpa, COUNT(DISTINCT e.course_code) AS courses "
    "FROM STUDENT s LEFT JOIN ENROLLMENT e ON s.roll_no=e.roll_no "
    "WHERE s.roll_no=%s GROUP BY s.roll_no, s.cgpa",
    (roll,),
)
total_marks = run_query(
    "SELECT COALESCE(SUM(marks_obtained),0) AS total FROM STUDENT_PERFORMANCE WHERE roll_no=%s",
    (roll,),
)

cgpa    = dash["cgpa"].iloc[0]      if not dash.empty    else "N/A"
courses = dash["courses"].iloc[0]   if not dash.empty    else 0
t_marks = total_marks["total"].iloc[0] if not total_marks.empty else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("CGPA", cgpa)
c2.metric("Courses Enrolled", int(courses))
c3.metric("Total Marks Scored", int(t_marks))

# Attendance overall
att = run_query(
    "SELECT ROUND(SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*),1) AS pct "
    "FROM ATTENDANCE WHERE roll_no=%s",
    (roll,),
)
att_pct = att["pct"].iloc[0] if not att.empty and att["pct"].iloc[0] is not None else 0
c4.metric("Overall Attendance", f"{att_pct}%")

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──
tabs = st.tabs(["Performance", "Attendance", "Courses & PYQ", "Exam Eligibility"])

# ──────────── TAB 1: Performance ────────────
with tabs[0]:
    st.markdown("#### Assessment Results")
    perf = run_query(
        """
        SELECT c.course_name, a.assessment_type, sp.marks_obtained,
               a.total_marks, sp.grade, sp.result,
               ROUND(sp.marks_obtained*100.0/a.total_marks,1) AS pct
        FROM STUDENT_PERFORMANCE sp
        JOIN ASSESSMENT a ON sp.assessment_id=a.assessment_id
        JOIN COURSE c ON a.course_code=c.course_code
        WHERE sp.roll_no=%s
        ORDER BY c.course_name, a.assessment_type
        """,
        (roll,),
    )

    if perf.empty:
        st.info("No performance records found.")
    else:
        # Color grade column
        def color_grade(val):
            if val in ("O", "A+", "A"):
                return "background-color:#D1FAE5; color:#065F46; font-weight:600"
            elif val == "F":
                return "background-color:#FEE2E2; color:#991B1B; font-weight:600"
            return ""

        def color_result(val):
            if val == "Pass":
                return "background-color:#D1FAE5; color:#065F46; font-weight:600"
            elif val == "Fail":
                return "background-color:#FEE2E2; color:#991B1B; font-weight:600"
            return ""

        styled = perf.style.applymap(color_grade, subset=["grade"]).applymap(
            color_result, subset=["result"]
        )
        st.dataframe(styled, use_container_width=True, hide_index=True)

        # Bar chart
        fig = px.bar(
            perf,
            x="assessment_type",
            y="pct",
            color="course_name",
            barmode="group",
            labels={"pct": "Score (%)", "assessment_type": "Assessment", "course_name": "Course"},
            color_discrete_sequence=["#6366F1", "#10B981", "#F59E0B"],
        )
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font_family="Satoshi",
            legend_title="Course",
            yaxis=dict(range=[0, 110], gridcolor="#F1F5F9"),
            xaxis=dict(gridcolor="#F1F5F9"),
            margin=dict(t=20),
        )
        st.plotly_chart(fig, use_container_width=True)


# ──────────── TAB 2: Attendance ────────────
with tabs[1]:
    st.markdown("#### Attendance by Course")
    att_detail = run_query(
        """
        SELECT course_code,
               COUNT(*) AS total,
               SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) AS present,
               ROUND(SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*),1) AS pct
        FROM ATTENDANCE WHERE roll_no=%s GROUP BY course_code
        """,
        (roll,),
    )

    if att_detail.empty:
        st.info("No attendance records found.")
    else:
        cols = st.columns(len(att_detail))
        for i, row in att_detail.iterrows():
            with cols[i]:
                color = "#10B981" if row["pct"] >= 75 else "#EF4444"
                fig = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=float(row["pct"]),
                        number={"suffix": "%", "font": {"family": "Clash Display", "size": 28}},
                        gauge={
                            "axis": {"range": [0, 100]},
                            "bar": {"color": color},
                            "bgcolor": "#F1F5F9",
                            "threshold": {
                                "line": {"color": "#6366F1", "width": 2},
                                "thickness": 0.8,
                                "value": 75,
                            },
                        },
                        title={"text": row["course_code"], "font": {"family": "Satoshi"}},
                    )
                )
                fig.update_layout(height=220, margin=dict(t=30, b=10, l=20, r=20),
                                  paper_bgcolor="white")
                st.plotly_chart(fig, use_container_width=True)
                status = "Eligible" if row["pct"] >= 75 else "Low Attendance"
                color_cls = "#D1FAE5" if row["pct"] >= 75 else "#FEE2E2"
                text_cls  = "#065F46" if row["pct"] >= 75 else "#991B1B"
                st.markdown(
                    f"<div style='text-align:center; background:{color_cls}; color:{text_cls};"
                    f"border-radius:8px; padding:4px; font-size:0.8rem; font-weight:600'>"
                    f"{status}</div>",
                    unsafe_allow_html=True,
                )

        st.markdown("#### Attendance Log")
        log = run_query(
            "SELECT attendance_date, course_code, status, remarks "
            "FROM ATTENDANCE WHERE roll_no=%s ORDER BY attendance_date DESC",
            (roll,),
        )
        st.dataframe(log, use_container_width=True, hide_index=True)


# ──────────── TAB 3: Courses & PYQ ────────────
with tabs[2]:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Enrolled Courses")
        enr = run_query(
            """
            SELECT c.course_code, c.course_name, c.credits, c.semester, c.description
            FROM ENROLLMENT e JOIN COURSE c ON e.course_code=c.course_code
            WHERE e.roll_no=%s
            """,
            (roll,),
        )
        st.dataframe(enr, use_container_width=True, hide_index=True)

    with col_b:
        st.markdown("#### Study Materials")
        sm = run_query(
            """
            SELECT sm.title, sm.material_type, u.name AS faculty, sm.upload_date
            FROM STUDY_MATERIAL sm
            JOIN FACULTY f ON sm.faculty_id=f.faculty_id
            JOIN USERS u ON f.user_id=u.user_id
            JOIN ENROLLMENT e ON sm.course_code=e.course_code
            WHERE e.roll_no=%s
            ORDER BY sm.upload_date DESC
            """,
            (roll,),
        )
        st.dataframe(sm, use_container_width=True, hide_index=True)

    st.markdown("#### Previous Year Questions")
    pyq_courses = enr["course_code"].tolist() if not enr.empty else []
    if pyq_courses:
        sel_course = st.selectbox("Select Course", pyq_courses)
        pyq = run_query(
            "SELECT question, year, exam_type FROM PYQ WHERE course_code=%s ORDER BY year DESC",
            (sel_course,),
        )
        if pyq.empty:
            st.info("No PYQs available for this course.")
        else:
            for _, r in pyq.iterrows():
                st.markdown(
                    f"""
                    <div class="card" style="margin-bottom:10px;">
                        <div style="font-family:'Satoshi',sans-serif; font-weight:600;
                                    color:#0F172A; margin-bottom:4px;">{r['question']}</div>
                        <div style="font-size:0.78rem; color:#64748B;">
                            {r['exam_type']} &nbsp;·&nbsp; {r['year']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ──────────── TAB 4: Eligibility ────────────
with tabs[3]:
    st.markdown("#### Exam Eligibility Report")
    if not enr.empty:
        rows = []
        for _, r in enr.iterrows():
            code = r["course_code"]
            att_q = run_query(
                "SELECT ROUND(SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*),1) AS pct "
                "FROM ATTENDANCE WHERE roll_no=%s AND course_code=%s",
                (roll, code),
            )
            pct = att_q["pct"].iloc[0] if not att_q.empty and att_q["pct"].iloc[0] is not None else 0
            eligible = "Eligible" if pct >= 75 else "NOT Eligible (< 75%)"
            rows.append({"Course": code, "Course Name": r["course_name"],
                         "Attendance %": pct, "Status": eligible})

        import pandas as pd
        df_elig = pd.DataFrame(rows)

        def elig_style(val):
            if val == "Eligible":
                return "background:#D1FAE5; color:#065F46; font-weight:600"
            return "background:#FEE2E2; color:#991B1B; font-weight:600"

        st.dataframe(
            df_elig.style.applymap(elig_style, subset=["Status"]),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No enrollments found.")
