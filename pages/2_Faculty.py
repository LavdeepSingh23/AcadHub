import streamlit as st
import plotly.express as px
import pandas as pd
from db import run_query, run_procedure, run_write
from styles import inject_styles, sidebar_logo, page_header, section_header, PLOTLY_LAYOUT

st.set_page_config(page_title="AcadHub — Faculty", layout="wide", initial_sidebar_state="expanded")
inject_styles()

if not st.session_state.get("logged_in") or st.session_state.get("role") != "Faculty":
    st.switch_page("app.py")

faculty_id = st.session_state.faculty_id
name       = st.session_state.user_name

# ── Sidebar ─────────────────────────────────────────────────
sidebar_logo(role="Faculty", user_name=name, sub_label=f"ID: {faculty_id}")

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
nav_items = ["📈 Course Analytics", "🧑‍🎓 Student Performance", "📋 Attendance Overview",
             "📤 Upload Material", "✏️ Record Marks"]
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

# ── Data ────────────────────────────────────────────────────
my_courses = run_query(
    "SELECT fc.course_code, c.course_name FROM FACULTY_COURSE fc "
    "JOIN COURSE c ON fc.course_code=c.course_code WHERE fc.faculty_id=%s",
    (faculty_id,),
)
course_list = my_courses["course_code"].tolist() if not my_courses.empty else []

# ── Page header ──────────────────────────────────────────────
page_header("Faculty Dashboard", f"Welcome, {name} — managing your courses & students")

# ── KPI row ──────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("Courses Assigned", len(course_list))

total_students = run_query(
    "SELECT COUNT(DISTINCT e.roll_no) AS n FROM ENROLLMENT e "
    "JOIN FACULTY_COURSE fc ON e.course_code=fc.course_code WHERE fc.faculty_id=%s",
    (faculty_id,),
)
c2.metric("Total Students", int(total_students["n"].iloc[0]) if not total_students.empty else 0)

materials = run_query(
    "SELECT COUNT(*) AS n FROM STUDY_MATERIAL WHERE faculty_id=%s", (faculty_id,)
)
c3.metric("Materials Uploaded", int(materials["n"].iloc[0]) if not materials.empty else 0)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────
tabs = st.tabs(["📈 Course Analytics", "🧑‍🎓 Student Performance", "📋 Attendance", "📤 Upload Material", "✏️ Record Marks"])

# ────────────────────────────────────────────
# TAB 1 — Course Analytics
# ────────────────────────────────────────────
with tabs[0]:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    section_header("Course-wise Analytics", "Assessment stats per assigned course")

    if not my_courses.empty:
        for _, row in my_courses.iterrows():
            code  = row["course_code"]
            cname = row["course_name"]

            st.markdown(
                f"""<div style="background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.15);
                                border-radius:12px;padding:10px 16px;margin-bottom:8px;">
                      <span style="font-family:'Inter',sans-serif;font-weight:700;font-size:0.88rem;
                                   color:#818CF8;">{code}</span>
                      <span style="font-family:'Inter',sans-serif;font-size:0.82rem;
                                   color:#475569;margin-left:10px;">{cname}</span>
                    </div>""",
                unsafe_allow_html=True,
            )

            with st.expander(f"View Analytics — {code}", expanded=False):
                stats = run_query(
                    """
                    SELECT a.assessment_type, a.total_marks,
                           ROUND(AVG(sp.marks_obtained),2) AS avg_marks,
                           MAX(sp.marks_obtained) AS highest,
                           MIN(sp.marks_obtained) AS lowest,
                           SUM(CASE WHEN sp.marks_obtained < a.passing_marks THEN 1 ELSE 0 END) AS fails
                    FROM ASSESSMENT a
                    LEFT JOIN STUDENT_PERFORMANCE sp ON a.assessment_id=sp.assessment_id
                    WHERE a.course_code=%s
                    GROUP BY a.assessment_type, a.total_marks, a.passing_marks
                    """,
                    (code,),
                )
                st.dataframe(stats, use_container_width=True, hide_index=True)

                if not stats.empty and stats["avg_marks"].notna().any():
                    fig = px.bar(
                        stats,
                        x="assessment_type",
                        y=["avg_marks", "highest", "lowest"],
                        barmode="group",
                        labels={"value": "Marks", "assessment_type": "Assessment", "variable": "Metric"},
                        color_discrete_sequence=["#6366F1", "#10B981", "#EF4444"],
                    )
                    fig.update_layout(**PLOTLY_LAYOUT)
                    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", zeroline=False)
                    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", zeroline=False)
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown(
            """<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
                           border-radius:12px;padding:40px;text-align:center;color:#475569;
                           font-family:'Inter',sans-serif;font-size:0.88rem;">
                No courses assigned yet.
               </div>""",
            unsafe_allow_html=True,
        )

# ────────────────────────────────────────────
# TAB 2 — Student Performance
# ────────────────────────────────────────────
with tabs[1]:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    section_header("Student Performance", "Per-course assessment results")

    if course_list:
        sel = st.selectbox("Select Course", course_list, key="perf_course")
        perf = run_query(
            """
            SELECT u.name, s.roll_no, a.assessment_type,
                   sp.marks_obtained, a.total_marks, sp.grade, sp.result
            FROM STUDENT_PERFORMANCE sp
            JOIN STUDENT s ON sp.roll_no=s.roll_no
            JOIN USERS u ON s.user_id=u.user_id
            JOIN ASSESSMENT a ON sp.assessment_id=a.assessment_id
            WHERE a.course_code=%s ORDER BY s.roll_no
            """,
            (sel,),
        )
        if perf.empty:
            st.markdown(
                """<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
                               border-radius:12px;padding:40px;text-align:center;color:#475569;
                               font-family:'Inter',sans-serif;font-size:0.88rem;">
                    No performance data recorded for this course yet.
                   </div>""",
                unsafe_allow_html=True,
            )
        else:
            def color_result(val):
                if val == "Pass": return "background-color:rgba(16,185,129,0.15); color:#34D399; font-weight:600"
                if val == "Fail": return "background-color:rgba(239,68,68,0.15); color:#F87171; font-weight:600"
                return "color:#CBD5E1"

            st.dataframe(
                perf.style.applymap(color_result, subset=["result"]),
                use_container_width=True, hide_index=True,
            )

            # Pass / fail donut
            pass_count = (perf["result"] == "Pass").sum()
            fail_count = (perf["result"] == "Fail").sum()
            if pass_count + fail_count > 0:
                col_chart, col_space = st.columns([1, 2])
                with col_chart:
                    fig_donut = px.pie(
                        values=[pass_count, fail_count],
                        names=["Pass", "Fail"],
                        hole=0.65,
                        color_discrete_sequence=["#10B981", "#EF4444"],
                    )
                    fig_donut.update_traces(textposition="inside", textfont_color="white")
                    fig_donut.update_layout(
                        **PLOTLY_LAYOUT,
                        height=260,
                        annotations=[dict(text=f"{pass_count+fail_count}<br>total", x=0.5, y=0.5,
                                          font_size=14, font_color="#94A3B8", showarrow=False)],
                        showlegend=True,
                        legend=dict(orientation="v", x=1, y=0.5,
                                    font=dict(color="#94A3B8", size=12),
                                    bgcolor="rgba(0,0,0,0)"),
                    )
                    st.plotly_chart(fig_donut, use_container_width=True)

# ────────────────────────────────────────────
# TAB 3 — Attendance Overview
# ────────────────────────────────────────────
with tabs[2]:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    section_header("Attendance Summary", "Per-student breakdown with eligibility flag")

    if course_list:
        sel_att = st.selectbox("Select Course", course_list, key="att_course")
        att = run_query(
            """
            SELECT s.roll_no, u.name,
                   COUNT(*) AS total,
                   SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present,
                   ROUND(SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*),1) AS pct
            FROM ATTENDANCE a
            JOIN STUDENT s ON a.roll_no=s.roll_no
            JOIN USERS u ON s.user_id=u.user_id
            WHERE a.course_code=%s GROUP BY s.roll_no, u.name ORDER BY pct
            """,
            (sel_att,),
        )
        if att.empty:
            st.markdown(
                """<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
                               border-radius:12px;padding:40px;text-align:center;color:#475569;
                               font-family:'Inter',sans-serif;font-size:0.88rem;">
                    No attendance records for this course.
                   </div>""",
                unsafe_allow_html=True,
            )
        else:
            def att_color(val):
                try:
                    v = float(val)
                    if v < 75: return "background-color:rgba(239,68,68,0.15); color:#F87171; font-weight:600"
                    return "background-color:rgba(16,185,129,0.15); color:#34D399; font-weight:600"
                except:
                    return "color:#CBD5E1"

            st.dataframe(
                att.style.applymap(att_color, subset=["pct"]),
                use_container_width=True, hide_index=True,
            )

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            fig = px.bar(
                att, x="name", y="pct",
                color="pct",
                color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
                range_color=[0, 100],
                labels={"pct": "Attendance %", "name": "Student"},
            )
            fig.add_hline(y=75, line_dash="dash", line_color="#6366F1",
                          annotation_text="75% threshold",
                          annotation_font_color="#6366F1")
            fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
            fig.update_yaxes(range=[0, 110], gridcolor="rgba(255,255,255,0.05)", zeroline=False)
            fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", zeroline=False)
            st.plotly_chart(fig, use_container_width=True)

# ────────────────────────────────────────────
# TAB 4 — Upload Material
# ────────────────────────────────────────────
with tabs[3]:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    section_header("Upload Study Material", "Share notes, slides, and references with your students")

    _, form_col, _ = st.columns([0.1, 1, 0.1])
    with form_col:
        with st.form("upload_material_form"):
            mat_course  = st.selectbox("Course", course_list)
            mat_title   = st.text_input("Title", placeholder="e.g. Unit 3 — Memory Management")
            mat_type    = st.selectbox("Type", ["Notes", "Slides", "Tutorials", "Reference"])
            mat_content = st.text_area("Content / Description", placeholder="Brief description or content summary…")
            mat_date    = st.date_input("Upload Date")
            mat_id      = st.number_input("Material ID (unique)", min_value=100, step=1)
            submitted   = st.form_submit_button("Upload Material →", use_container_width=True)

        if submitted:
            if not mat_title:
                st.warning("Please enter a title.")
            else:
                msg = run_write(
                    "INSERT INTO STUDY_MATERIAL (material_id, course_code, faculty_id, title, "
                    "material_type, content, upload_date) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (int(mat_id), mat_course, faculty_id, mat_title,
                     mat_type, mat_content, mat_date.strftime("%Y-%m-%d")),
                )
                if "Error" in str(msg):
                    st.error(msg)
                else:
                    st.success(f"✓ Material '{mat_title}' uploaded successfully.")

    # Existing materials
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    section_header("Uploaded Materials", "All materials you have shared")
    existing = run_query(
        "SELECT title, material_type, course_code, upload_date FROM STUDY_MATERIAL "
        "WHERE faculty_id=%s ORDER BY upload_date DESC",
        (faculty_id,),
    )
    if not existing.empty:
        st.dataframe(existing, use_container_width=True, hide_index=True)

# ────────────────────────────────────────────
# TAB 5 — Record Marks
# ────────────────────────────────────────────
with tabs[4]:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    section_header("Record Student Marks", "Submit assessment results for your students")

    if course_list:
        asmt_df = run_query(
            "SELECT assessment_id, course_code, assessment_type, total_marks "
            "FROM ASSESSMENT WHERE course_code IN (%s)" % ",".join(["%s"] * len(course_list)),
            tuple(course_list),
        )
        if asmt_df.empty:
            st.markdown(
                """<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
                               border-radius:12px;padding:40px;text-align:center;color:#475569;
                               font-family:'Inter',sans-serif;font-size:0.88rem;">
                    No assessments found for your courses.
                   </div>""",
                unsafe_allow_html=True,
            )
        else:
            asmt_options = {
                f"{r['assessment_type']} — {r['course_code']} (max {r['total_marks']})": r["assessment_id"]
                for _, r in asmt_df.iterrows()
            }
            _, form_col2, _ = st.columns([0.1, 1, 0.1])
            with form_col2:
                with st.form("record_marks_form"):
                    sel_asmt_label = st.selectbox("Assessment", list(asmt_options.keys()))
                    sel_asmt_id    = asmt_options[sel_asmt_label]
                    roll_input     = st.number_input("Student Roll No", min_value=1000000000, step=1)
                    marks_input    = st.number_input("Marks Obtained", min_value=0, step=1)
                    perf_id        = st.number_input("Performance Record ID (unique)", min_value=100, step=1)
                    sub_marks      = st.form_submit_button("Submit Marks →", use_container_width=True)

                if sub_marks:
                    msgs = run_procedure(
                        "proc_mark_performance_safe",
                        (int(perf_id), int(roll_input), int(sel_asmt_id), int(marks_input)),
                    )
                    for m in msgs:
                        if "Error" in str(m) or "error" in str(m):
                            st.error(m)
                        else:
                            st.success(f"✓ {m}")