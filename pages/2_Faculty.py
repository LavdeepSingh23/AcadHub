import streamlit as st
import plotly.express as px
import pandas as pd
from db import run_query, run_procedure, run_write
from styles import inject_styles, sidebar_logo, page_header

st.set_page_config(page_title="AcadHub — Faculty", layout="wide")
inject_styles()

if not st.session_state.get("logged_in") or st.session_state.get("role") != "Faculty":
    st.switch_page("app.py")

faculty_id = st.session_state.faculty_id
name       = st.session_state.user_name

# ── Sidebar ──
sidebar_logo()
st.sidebar.markdown(
    f"""
    <div style="padding:12px 0;">
        <div style="font-family:'Satoshi',sans-serif; font-weight:700;
                    font-size:1rem; color:#0F172A;">{name}</div>
        <div style="font-size:0.78rem; color:#64748B; margin-top:2px;">
            Faculty ID: {faculty_id}
        </div>
        <div style="margin-top:6px;">
            <span style="background:#F0FDF4; color:#166534; padding:2px 10px;
                         border-radius:20px; font-size:0.75rem; font-weight:600;">
                Faculty
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

# ── My courses ──
my_courses = run_query(
    "SELECT fc.course_code, c.course_name FROM FACULTY_COURSE fc "
    "JOIN COURSE c ON fc.course_code=c.course_code WHERE fc.faculty_id=%s",
    (faculty_id,),
)
course_list = my_courses["course_code"].tolist() if not my_courses.empty else []

# ─────────────────────────────────────────────
page_header("Faculty Dashboard", f"Welcome, {name}")

# Metric row
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

st.markdown("<br>", unsafe_allow_html=True)

tabs = st.tabs(["Course Analytics", "Student Performance", "Attendance Overview",
                "Upload Material", "Record Marks"])

# ──────────── TAB 1: Course Analytics ────────────
with tabs[0]:
    st.markdown("#### Course-wise Analytics")
    if not my_courses.empty:
        for _, row in my_courses.iterrows():
            code = row["course_code"]
            cname = row["course_name"]
            with st.expander(f"{code} — {cname}", expanded=True):
                stats = run_query(
                    """
                    SELECT a.assessment_type, a.total_marks,
                           ROUND(AVG(sp.marks_obtained),2) AS avg_marks,
                           MAX(sp.marks_obtained) AS highest,
                           MIN(sp.marks_obtained) AS lowest,
                           SUM(CASE WHEN sp.marks_obtained < a.passing_marks THEN 1 ELSE 0 END) AS fails
                    FROM ASSESSMENT a
                    LEFT JOIN STUDENT_PERFORMANCE sp ON a.assessment_id=sp.assessment_id
                    WHERE a.course_code=%s GROUP BY a.assessment_type, a.total_marks, a.passing_marks
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
                        labels={"value": "Marks", "assessment_type": "Assessment",
                                "variable": "Metric"},
                        color_discrete_sequence=["#6366F1", "#10B981", "#EF4444"],
                    )
                    fig.update_layout(
                        plot_bgcolor="white", paper_bgcolor="white",
                        font_family="Satoshi", margin=dict(t=10),
                        yaxis=dict(gridcolor="#F1F5F9"),
                    )
                    st.plotly_chart(fig, use_container_width=True)


# ──────────── TAB 2: Student Performance ────────────
with tabs[1]:
    st.markdown("#### Students in My Courses")
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
            st.info("No performance data yet.")
        else:
            def color_result(val):
                if val == "Pass":  return "background:#D1FAE5; color:#065F46; font-weight:600"
                if val == "Fail":  return "background:#FEE2E2; color:#991B1B; font-weight:600"
                return ""
            st.dataframe(
                perf.style.applymap(color_result, subset=["result"]),
                use_container_width=True, hide_index=True,
            )


# ──────────── TAB 3: Attendance Overview ────────────
with tabs[2]:
    st.markdown("#### Attendance Summary")
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
            WHERE a.course_code=%s GROUP BY s.roll_no, u.name
            ORDER BY pct
            """,
            (sel_att,),
        )
        if att.empty:
            st.info("No attendance records.")
        else:
            def att_color(val):
                try:
                    v = float(val)
                    if v < 75:  return "background:#FEE2E2; color:#991B1B; font-weight:600"
                    return "background:#D1FAE5; color:#065F46; font-weight:600"
                except:
                    return ""
            st.dataframe(
                att.style.applymap(att_color, subset=["pct"]),
                use_container_width=True, hide_index=True,
            )

            fig = px.bar(
                att, x="name", y="pct",
                color="pct",
                color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
                range_color=[0, 100],
                labels={"pct": "Attendance %", "name": "Student"},
            )
            fig.add_hline(y=75, line_dash="dash", line_color="#6366F1",
                          annotation_text="75% threshold")
            fig.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                font_family="Satoshi", margin=dict(t=10),
                coloraxis_showscale=False,
                yaxis=dict(range=[0, 110], gridcolor="#F1F5F9"),
            )
            st.plotly_chart(fig, use_container_width=True)


# ──────────── TAB 4: Upload Material ────────────
with tabs[3]:
    st.markdown("#### Upload Study Material")
    with st.form("upload_material_form"):
        mat_course = st.selectbox("Course", course_list)
        mat_title  = st.text_input("Title")
        mat_type   = st.selectbox("Type", ["Notes", "Slides", "Tutorials", "Reference"])
        mat_content = st.text_area("Content / Description")
        mat_date   = st.date_input("Upload Date")
        mat_id     = st.number_input("Material ID (unique)", min_value=100, step=1)
        submitted  = st.form_submit_button("Upload Material")

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
                st.success(f"Material '{mat_title}' uploaded successfully.")


# ──────────── TAB 5: Record Marks ────────────
with tabs[4]:
    st.markdown("#### Record Student Marks")

    # Get assessments for faculty courses
    if course_list:
        asmt_df = run_query(
            "SELECT assessment_id, course_code, assessment_type, total_marks "
            "FROM ASSESSMENT WHERE course_code IN (%s)" % ",".join(["%s"] * len(course_list)),
            tuple(course_list),
        )
        if asmt_df.empty:
            st.info("No assessments found for your courses.")
        else:
            asmt_options = {
                f"{r['assessment_type']} — {r['course_code']} (max {r['total_marks']})": r["assessment_id"]
                for _, r in asmt_df.iterrows()
            }
            with st.form("record_marks_form"):
                sel_asmt_label = st.selectbox("Assessment", list(asmt_options.keys()))
                sel_asmt_id    = asmt_options[sel_asmt_label]
                roll_input     = st.number_input("Student Roll No", min_value=1000000000, step=1)
                marks_input    = st.number_input("Marks Obtained", min_value=0, step=1)
                perf_id        = st.number_input("Performance Record ID (unique)", min_value=100, step=1)
                sub_marks      = st.form_submit_button("Submit Marks")

            if sub_marks:
                msgs = run_procedure(
                    "proc_mark_performance_safe",
                    (int(perf_id), int(roll_input), int(sel_asmt_id), int(marks_input)),
                )
                for m in msgs:
                    if "Error" in str(m) or "error" in str(m):
                        st.error(m)
                    else:
                        st.success(m)
