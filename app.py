import streamlit as st
from db import authenticate, get_student_by_user, get_faculty_by_user
from styles import inject_styles, FONTS

st.set_page_config(
    page_title="AcadHub",
    page_icon="assets/logo.png" if False else None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_styles()

# ── hide sidebar nav on login screen ──
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    section[data-testid="stSidebar"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── session defaults ──
for key, val in {
    "logged_in": False,
    "user_id": None,
    "user_name": "",
    "role": None,
    "roll_no": None,
    "faculty_id": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── redirect if already logged in ──
if st.session_state.logged_in:
    role = st.session_state.role
    if role == "Student":
        st.switch_page("pages/1_Student.py")
    elif role == "Faculty":
        st.switch_page("pages/2_Faculty.py")
    elif role == "Admin":
        st.switch_page("pages/3_Admin.py")


# ─────────────────────────────────────────────
#  LOGIN PAGE
# ─────────────────────────────────────────────
col_l, col_c, col_r = st.columns([1, 1.1, 1])

with col_c:
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Logo
    st.markdown(
        """
        <div style="text-align:center; margin-bottom:36px;">
            <div style="
                display:inline-flex; align-items:center; justify-content:center;
                width:56px; height:56px; background:#6366F1; border-radius:14px;
                margin-bottom:14px;
            ">
                <span style="font-family:'Clash Display',sans-serif; font-size:1.5rem;
                             font-weight:700; color:#fff;">A</span>
            </div>
            <div style="font-family:'Clash Display',sans-serif; font-size:1.9rem;
                        font-weight:700; color:#0F172A; letter-spacing:-0.03em;">
                AcadHub
            </div>
            <div style="font-family:'Satoshi',sans-serif; font-size:0.9rem;
                        color:#64748B; margin-top:4px;">
                Academic Management System
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Card
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(
        """
        <p style="font-family:'Clash Display',sans-serif; font-size:1.25rem;
                  font-weight:600; color:#0F172A; margin-bottom:4px;">
            Sign in to your account
        </p>
        <p style="font-family:'Satoshi',sans-serif; font-size:0.875rem;
                  color:#64748B; margin-bottom:20px;">
            Enter your credentials to continue
        </p>
        """,
        unsafe_allow_html=True,
    )

    username = st.text_input("Username", placeholder="Enter username")
    password = st.text_input("Password", type="password", placeholder="Enter password")

    st.markdown("<br>", unsafe_allow_html=True)
    login_btn = st.button("Sign In", use_container_width=True)

    if login_btn:
        if not username or not password:
            st.error("Please enter both username and password.")
        else:
            user = authenticate(username.strip(), password.strip())
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id   = user["user_id"]
                st.session_state.user_name = user["name"]
                st.session_state.role      = user["role"]

                if user["role"] == "Student":
                    s = get_student_by_user(user["user_id"])
                    st.session_state.roll_no = s["roll_no"] if s else None

                elif user["role"] == "Faculty":
                    f = get_faculty_by_user(user["user_id"])
                    st.session_state.faculty_id = f["faculty_id"] if f else None

                st.success(f"Welcome, {user['name']}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    st.markdown("</div>", unsafe_allow_html=True)

    # Demo credentials hint
    with st.expander("Demo credentials"):
        st.markdown(
            """
            <div style="font-family:'Satoshi',sans-serif; font-size:0.83rem; color:#475569;">
            <b style="color:#6366F1;">Students</b><br>
            kriti16 / kri16 &nbsp;|&nbsp; lavdeep23 / lav23 &nbsp;|&nbsp;
            aman10 / ama10 &nbsp;|&nbsp; sim90 / ravi90<br><br>
            <b style="color:#6366F1;">Faculty</b><br>
            rumneek24 / rum24 &nbsp;|&nbsp; raj19 / pass12903<br><br>
            <b style="color:#6366F1;">Admin</b><br>
            doaa30 / adm@123
            </div>
            """,
            unsafe_allow_html=True,
        )
