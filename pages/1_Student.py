import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from db import run_query, run_procedure
from styles import inject_styles, sidebar_logo, page_header, section_header, PLOTLY_LAYOUT

st.set_page_config(page_title="AcadHub — Student", layout="wide", initial_sidebar_state="expanded")
inject_styles()

# ── Auth guard ──────────────────────────────────────────────
if not st.session_state.get("logged_in") or st.session_state.get("role") != "Student":
    st.switch_page("app.py")

roll = st.session_state.roll_no
name = st.session_state.user_name

# ── Sidebar ─────────────────────────────────────────────────
sidebar_logo(role="Student", user_name=name, sub_label=f"Roll No: {roll}")

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

nav_items = ["📊 Performance", "📅 Attendance", "📚 Courses & PYQ", "🎓 Exam Eligibility"]
for item in nav_items:
    st.sidebar.markdown(
        f"""<div style="padding:8px 12px;border-radius:8px;margin-bottom:3px;
                        color:#64748B;font-family:'Inter',sans-serif;font-size:0.82rem;
                        cursor:default;transition:background 0.15s;">{item}</div>""",
        unsafe_allow_html=True,
    )

st.sidebar.markdown("<div style='height:1px;background:rgba(255,255,255,0.05);margin:16px 0'></div>", unsafe_allow_html=True)

if st.sidebar.button("Sign Out", use_container_width=True):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.switch_page("app.py")

# ── Page header ──────────────────────────────────────────────
page_header("Student Dashboard", f"Welcome back, {name} — here's your academic snapshot")

# ── KPI Row ──────────────────────────────────────────────────
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
att = run_query(
    "SELECT ROUND(SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*),1) AS pct "
    "FROM ATTENDANCE WHERE roll_no=%s",
    (roll,),
)

cgpa    = dash["cgpa"].iloc[0]        if not dash.empty          else "N/A"
courses = int(dash["courses"].iloc[0]) if not dash.empty          else 0
t_marks = int(total_marks["total"].iloc[0]) if not total_marks.empty else 0
att_pct = float(att["pct"].iloc[0])   if not att.empty and att["pct"].iloc[0] is not None else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("CGPA", cgpa)
c2.metric("Courses Enrolled", courses)
c3.metric("Total Marks Scored", t_marks)
c4.metric("Overall Attendance", f"{att_pct}%")

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# Attendance alert strip
if att_pct < 75:
    st.markdown(
        f"""<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);
                        border-radius:10px;padding:12px 16px;margin-bottom:8px;
                        display:flex;align-items:center;gap:10px;">
              <span style="font-size:1.1rem;">⚠️</span>
              <span style="font-family:'Inter',sans-serif;font-size:0.83rem;color:#F87171;">
                  Your overall attendance is <b>{att_pct}%</b> — below the 75% threshold.
                  Risk of exam ineligibility in some courses.
              </span>
            </div>""",
        unsafe_allow_html=True,
    )

# ── Tabs ─────────────────────────────────────────────────────
tabs = st.tabs(["📊 Performance", "📅 Attendance", "📚 Courses & PYQ", "🎓 Exam Eligibility"])

# ────────────────────────────────────────────
# TAB 1 — Performance
# ────────────────────────────────────────────
with tabs[0]:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    section_header("Assessment Results", "All assessments across enrolled courses")

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
        st.markdown(
            """<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
                           border-radius:12px;padding:40px;text-align:center;color:#475569;
                           font-family:'Inter',sans-serif;font-size:0.88rem;">
                No performance records found yet.
               </div>""",
            unsafe_allow_html=True,
        )
    else:
        def color_grade(val):
            if val in ("O", "A+", "A"):
                return "background-color:rgba(16,185,129,0.15); color:#34D399; font-weight:600"
            elif val == "F":
                return "background-color:rgba(239,68,68,0.15); color:#F87171; font-weight:600"
            return "color:#CBD5E1"

        def color_result(val):
            if val == "Pass":
                return "background-color:rgba(16,185,129,0.15); color:#34D399; font-weight:600"
            elif val == "Fail":
                return "background-color:rgba(239,68,68,0.15); color:#F87171; font-weight:600"
            return "color:#CBD5E1"

        styled = (
            perf.style
            .applymap(color_grade,  subset=["grade"])
            .applymap(color_result, subset=["result"])
        )
        st.dataframe(styled, use_container_width=True, hide_index=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        section_header("Score Distribution by Assessment", "Group comparison across courses")

        fig = px.bar(
            perf,
            x="assessment_type", y="pct", color="course_name",
            barmode="group",
            labels={"pct": "Score (%)", "assessment_type": "Assessment", "course_name": "Course"},
            color_discrete_sequence=["#6366F1", "#10B981", "#F59E0B", "#EC4899"],
        )
        fig.update_layout(**PLOTLY_LAYOUT, legend_title="Course")
        fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", zeroline=False)
        fig.update_yaxes(range=[0, 110], gridcolor="rgba(255,255,255,0.05)", zeroline=False)
        st.plotly_chart(fig, use_container_width=True)

# ────────────────────────────────────────────
# TAB 2 — Attendance
# ────────────────────────────────────────────
with tabs[1]:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    section_header("Attendance by Course", "75% minimum required for exam eligibility")

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
        st.markdown(
            """<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
                           border-radius:12px;padding:40px;text-align:center;color:#475569;
                           font-family:'Inter',sans-serif;font-size:0.88rem;">
                No attendance records found.
               </div>""",
            unsafe_allow_html=True,
        )
    else:
        cols = st.columns(min(len(att_detail), 4))
        for i, row in att_detail.iterrows():
            pct_val = float(row["pct"]) if row["pct"] is not None else 0
            color = "#10B981" if pct_val >= 75 else "#EF4444"
            with cols[i % min(len(att_detail), 4)]:
                fig = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=pct_val,
                        number={"suffix": "%", "font": {"family": "Inter", "size": 26, "color": "#F1F5F9"}},
                        gauge={
                            "axis": {"range": [0, 100], "tickcolor": "#334155",
                                     "tickfont": {"color": "#334155", "size": 9}},
                            "bar": {"color": color},
                            "bgcolor": "rgba(255,255,255,0.04)",
                            "bordercolor": "rgba(255,255,255,0.06)",
                            "steps": [{"range": [0, 75], "color": "rgba(239,68,68,0.05)"},
                                      {"range": [75, 100], "color": "rgba(16,185,129,0.05)"}],
                            "threshold": {
                                "line": {"color": "#6366F1", "width": 2},
                                "thickness": 0.8, "value": 75,
                            },
                        },
                        title={"text": row["course_code"],
                               "font": {"family": "Inter", "color": "#64748B", "size": 13}},
                    )
                )
                fig.update_layout(
                    height=210, margin=dict(t=28, b=10, l=16, r=16),
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig, use_container_width=True)

                is_eligible = pct_val >= 75
                bg = "rgba(16,185,129,0.12)" if is_eligible else "rgba(239,68,68,0.12)"
                fc = "#34D399" if is_eligible else "#F87171"
                lbl = "✓ Eligible" if is_eligible else "✗ Low Attendance"
                st.markdown(
                    f"""<div style="text-align:center;background:{bg};color:{fc};
                                   border-radius:8px;padding:5px;font-size:0.78rem;
                                   font-weight:600;font-family:'Inter',sans-serif;
                                   margin-bottom:8px;">{lbl}</div>""",
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        section_header("Attendance Log", "Most recent records first")
        log = run_query(
            "SELECT attendance_date, course_code, status, remarks "
            "FROM ATTENDANCE WHERE roll_no=%s ORDER BY attendance_date DESC",
            (roll,),
        )

        def status_style(val):
            if val == "Present":
                return "background-color:rgba(16,185,129,0.15); color:#34D399; font-weight:600"
            return "background-color:rgba(239,68,68,0.15); color:#F87171; font-weight:600"

        st.dataframe(
            log.style.applymap(status_style, subset=["status"]),
            use_container_width=True, hide_index=True,
        )

# ────────────────────────────────────────────
# TAB 3 — Courses & PYQ
# ────────────────────────────────────────────
with tabs[2]:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    enr = run_query(
        """
        SELECT c.course_code, c.course_name, c.credits, c.semester, c.description
        FROM ENROLLMENT e JOIN COURSE c ON e.course_code=c.course_code
        WHERE e.roll_no=%s
        """,
        (roll,),
    )

    with col_a:
        section_header("Enrolled Courses")
        st.dataframe(enr, use_container_width=True, hide_index=True)

    with col_b:
        section_header("Study Materials")
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

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    section_header("Previous Year Questions")

    pyq_courses = enr["course_code"].tolist() if not enr.empty else []
    if pyq_courses:
        sel_course = st.selectbox("Select Course", pyq_courses)
        pyq = run_query(
            "SELECT question, year, exam_type FROM PYQ WHERE course_code=%s ORDER BY year DESC",
            (sel_course,),
        )
        if pyq.empty:
            st.markdown(
                """<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
                               border-radius:12px;padding:30px;text-align:center;color:#475569;
                               font-family:'Inter',sans-serif;font-size:0.85rem;">
                    No PYQs available for this course.
                   </div>""",
                unsafe_allow_html=True,
            )
        else:
            for _, r in pyq.iterrows():
                st.markdown(
                    f"""
                    <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);
                                border-radius:12px;padding:16px 18px;margin-bottom:8px;
                                transition:border-color 0.2s;">
                        <div style="font-family:'Inter',sans-serif;font-weight:600;
                                    color:#E2E8F0;font-size:0.88rem;margin-bottom:6px;
                                    line-height:1.5;">{r['question']}</div>
                        <div style="display:flex;gap:8px;align-items:center;">
                            <span style="background:rgba(99,102,241,0.12);color:#818CF8;padding:2px 9px;
                                         border-radius:99px;font-size:0.7rem;font-weight:600;
                                         border:1px solid rgba(99,102,241,0.2);">{r['exam_type']}</span>
                            <span style="background:rgba(255,255,255,0.05);color:#475569;padding:2px 9px;
                                         border-radius:99px;font-size:0.7rem;font-family:'JetBrains Mono',monospace;">{r['year']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# ────────────────────────────────────────────
# TAB 4 — Exam Eligibility
# ────────────────────────────────────────────
with tabs[3]:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    section_header("Exam Eligibility Report", "Based on 75% attendance threshold per course")

    if not enr.empty:
        import pandas as pd
        rows = []
        for _, r in enr.iterrows():
            code = r["course_code"]
            att_q = run_query(
                "SELECT ROUND(SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*),1) AS pct "
                "FROM ATTENDANCE WHERE roll_no=%s AND course_code=%s",
                (roll, code),
            )
            pct = float(att_q["pct"].iloc[0]) if not att_q.empty and att_q["pct"].iloc[0] is not None else 0.0
            eligible = "✓ Eligible" if pct >= 75 else "✗ Not Eligible (< 75%)"
            rows.append({"Course": code, "Course Name": r["course_name"],
                         "Attendance %": pct, "Status": eligible})

        df_elig = pd.DataFrame(rows)

        # Summary chips
        elig_count = sum(1 for row in rows if "✓" in row["Status"])
        not_elig   = len(rows) - elig_count
        st.markdown(
            f"""<div style="display:flex;gap:10px;margin-bottom:16px;">
                  <div style="background:rgba(16,185,129,0.10);border:1px solid rgba(16,185,129,0.2);
                              border-radius:10px;padding:12px 20px;flex:1;text-align:center;">
                      <div style="font-family:'Inter',sans-serif;font-size:1.5rem;font-weight:800;
                                  color:#34D399;">{elig_count}</div>
                      <div style="font-family:'Inter',sans-serif;font-size:0.73rem;color:#475569;
                                  text-transform:uppercase;letter-spacing:0.07em;margin-top:2px;">Eligible</div>
                  </div>
                  <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);
                              border-radius:10px;padding:12px 20px;flex:1;text-align:center;">
                      <div style="font-family:'Inter',sans-serif;font-size:1.5rem;font-weight:800;
                                  color:#F87171;">{not_elig}</div>
                      <div style="font-family:'Inter',sans-serif;font-size:0.73rem;color:#475569;
                                  text-transform:uppercase;letter-spacing:0.07em;margin-top:2px;">Not Eligible</div>
                  </div>
                </div>""",
            unsafe_allow_html=True,
        )

        def elig_style(val):
            if "✓" in str(val):
                return "background-color:rgba(16,185,129,0.15); color:#34D399; font-weight:600"
            return "background-color:rgba(239,68,68,0.15); color:#F87171; font-weight:600"

        st.dataframe(
            df_elig.style.applymap(elig_style, subset=["Status"]),
            use_container_width=True, hide_index=True,
        )
    else:
        st.info("No enrollments found.")