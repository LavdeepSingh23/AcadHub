import streamlit as st
from db import authenticate, get_student_by_user, get_faculty_by_user

st.set_page_config(
    page_title="AcadHub — Sign In",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
#  ALL CSS — injected once, before any widget
# ─────────────────────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
/* ══════════════════════════════════════════
   RESET & FULL-VIEWPORT DARK CANVAS
══════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
.main, .block-container {
    background: #05060A !important;
    min-height: 100vh;
}

/* Strip all Streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stSidebarNav"],
section[data-testid="stSidebar"] { display: none !important; }

.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ══════════════════════════════════════════
   OUTER COLUMNS — full viewport split
══════════════════════════════════════════ */
[data-testid="stHorizontalBlock"] {
    gap: 0 !important;
    padding: 0 !important;
    min-height: 100vh;
    align-items: stretch !important;
}
[data-testid="column"] {
    padding: 0 !important;
    min-height: 100vh;
}

/* ══════════════════════════════════════════
   LEFT PANEL
══════════════════════════════════════════ */
.lp-root {
    position: relative;
    min-height: 100vh;
    background:
        radial-gradient(ellipse 80% 60% at 10% 20%, rgba(99,102,241,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 90% 80%, rgba(168,85,247,0.12) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 50% 50%, rgba(6,182,212,0.05) 0%, transparent 60%),
        linear-gradient(160deg, #0C0D16 0%, #0A0B12 50%, #070810 100%);
    border-right: 1px solid rgba(255,255,255,0.05);
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 4rem 4rem;
    overflow: hidden;
}

/* Animated glow orbs */
.orb {
    position: absolute; border-radius: 50%;
    filter: blur(80px); pointer-events: none;
    animation: drift 12s ease-in-out infinite alternate;
}
.orb-1 {
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(99,102,241,0.14) 0%, transparent 70%);
    top: -150px; left: -150px;
}
.orb-2 {
    width: 380px; height: 380px;
    background: radial-gradient(circle, rgba(168,85,247,0.10) 0%, transparent 70%);
    bottom: -80px; right: -80px;
    animation-delay: -6s;
}
.orb-3 {
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(6,182,212,0.07) 0%, transparent 70%);
    top: 50%; left: 40%;
    animation-delay: -3s;
}
@keyframes drift {
    from { transform: translate(0, 0) scale(1); }
    to   { transform: translate(30px, -30px) scale(1.05); }
}

/* Logo mark */
.lp-logo {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 3.5rem;
    position: relative; z-index: 2;
}
.lp-logo-mark {
    width: 42px; height: 42px; border-radius: 11px;
    background: linear-gradient(135deg, #6366F1, #818CF8);
    box-shadow: 0 0 28px rgba(99,102,241,0.4), 0 0 0 1px rgba(255,255,255,0.08);
    display: flex; align-items: center; justify-content: center;
    font-family: 'Inter', sans-serif; font-weight: 900;
    font-size: 1.15rem; color: #fff;
}
.lp-logo-text {
    font-family: 'Inter', sans-serif; font-weight: 800;
    font-size: 1.2rem; color: #F1F5F9; letter-spacing: -0.03em;
}

/* Headline */
.lp-headline {
    position: relative; z-index: 2;
    font-family: 'Inter', sans-serif; font-weight: 800;
    font-size: 2.6rem;
    line-height: 1.12; letter-spacing: -0.04em;
    color: #F1F5F9; margin-bottom: 1.1rem;
}
.lp-headline .grad {
    background: linear-gradient(90deg, #818CF8 0%, #A78BFA 40%, #67E8F9 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.lp-sub {
    position: relative; z-index: 2;
    font-family: 'Inter', sans-serif; font-size: 0.9rem;
    color: rgba(148,163,184,0.85); line-height: 1.7;
    max-width: 380px; margin-bottom: 2.8rem;
    font-weight: 400;
}

/* Feature pills */
.lp-features { position: relative; z-index: 2; display: flex; flex-direction: column; gap: 10px; }
.feat {
    display: flex; align-items: center; gap: 13px;
    padding: 13px 16px; border-radius: 13px;
    background: rgba(255,255,255,0.032);
    border: 1px solid rgba(255,255,255,0.06);
    backdrop-filter: blur(8px);
    transition: background 0.2s, border-color 0.2s;
    animation: slideUp 0.5s cubic-bezier(0.16,1,0.3,1) both;
}
.feat:hover { background: rgba(255,255,255,0.055); border-color: rgba(255,255,255,0.10); }
.feat-icon {
    width: 34px; height: 34px; border-radius: 8px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center; font-size: 0.9rem;
}
.feat-title {
    font-family: 'Inter', sans-serif; font-size: 0.83rem;
    font-weight: 600; color: #E2E8F0; margin-bottom: 2px;
}
.feat-desc {
    font-family: 'Inter', sans-serif; font-size: 0.74rem;
    color: rgba(100,116,139,0.9); line-height: 1.4;
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
.feat:nth-child(1) { animation-delay: 0.1s; }
.feat:nth-child(2) { animation-delay: 0.18s; }
.feat:nth-child(3) { animation-delay: 0.26s; }

/* Trust bar */
.lp-trust {
    position: relative; z-index: 2;
    margin-top: 2.5rem;
    display: flex; align-items: center; gap: 10px;
}
.trust-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #10B981; flex-shrink: 0;
    box-shadow: 0 0 8px rgba(16,185,129,0.6);
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
    0%,100% { box-shadow: 0 0 4px rgba(16,185,129,0.4); }
    50%      { box-shadow: 0 0 12px rgba(16,185,129,0.7); }
}
.trust-text {
    font-family: 'Inter', sans-serif; font-size: 0.74rem;
    color: rgba(100,116,139,0.8);
}
.trust-text b { color: rgba(148,163,184,0.9); font-weight: 600; }

/* Bottom footer */
.lp-footer {
    position: absolute; bottom: 28px; left: 4rem;
    font-family: 'Inter', sans-serif; font-size: 0.68rem;
    color: rgba(71,85,105,0.7); z-index: 2;
}

/* ══════════════════════════════════════════
   RIGHT PANEL
══════════════════════════════════════════ */
.rp-bg {
    position: fixed; top: 0; right: 0;
    width: 45%; height: 100vh;
    background:
        radial-gradient(ellipse 60% 40% at 60% 20%, rgba(99,102,241,0.06) 0%, transparent 60%),
        #07080E;
    z-index: 0; pointer-events: none;
}
.rp-grid {
    position: fixed; top: 0; right: 0;
    width: 45%; height: 100vh;
    background-image:
        linear-gradient(rgba(99,102,241,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(99,102,241,0.03) 1px, transparent 1px);
    background-size: 32px 32px;
    z-index: 0; pointer-events: none;
}

/* Card glow */
.rp-card-glow {
    position: absolute;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%);
    top: -90px; left: 50%; transform: translateX(-50%);
    pointer-events: none; filter: blur(40px);
    z-index: 1;
}

/* Logo on right */
.rp-logo-wrap {
    text-align: center; margin-bottom: 1.5rem; position: relative; z-index: 2;
}
.rp-logo-icon {
    display: inline-flex; align-items: center; justify-content: center;
    width: 48px; height: 48px; border-radius: 13px;
    background: linear-gradient(135deg, #6366F1, #818CF8);
    box-shadow: 0 0 32px rgba(99,102,241,0.35), 0 0 0 1px rgba(255,255,255,0.08);
    font-family: 'Inter', sans-serif; font-weight: 900;
    font-size: 1.3rem; color: #fff; margin-bottom: 14px;
}
.rp-title {
    font-family: 'Inter', sans-serif; font-weight: 700;
    font-size: 1.45rem; color: #F1F5F9;
    letter-spacing: -0.025em; margin-bottom: 5px;
}
.rp-subtitle {
    font-family: 'Inter', sans-serif; font-size: 0.84rem;
    color: #475569; font-weight: 400;
}

/* Role tabs */
.role-tabs {
    display: flex; gap: 5px;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px; padding: 4px;
    margin-bottom: 1.25rem; position: relative; z-index: 2;
}
.role-tab {
    flex: 1; padding: 7px 4px; border-radius: 7px;
    text-align: center; cursor: default;
    font-family: 'Inter', sans-serif; font-size: 0.73rem;
    font-weight: 500; color: #334155;
}
.role-tab.active {
    background: rgba(99,102,241,0.14);
    color: #818CF8; font-weight: 600;
    border: 1px solid rgba(99,102,241,0.18);
}

/* Form surface card */
.form-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px; padding: 1.75rem 1.6rem;
    box-shadow:
        0 0 0 1px rgba(99,102,241,0.04),
        0 24px 64px rgba(0,0,0,0.55),
        0 6px 20px rgba(0,0,0,0.3);
    position: relative; z-index: 2;
    animation: cardIn 0.5s cubic-bezier(0.16,1,0.3,1) both;
}
@keyframes cardIn {
    from { opacity: 0; transform: translateY(18px) scale(0.985); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* Label in card */
.form-label-section {
    font-family: 'Inter', sans-serif; font-size: 0.7rem;
    font-weight: 600; text-transform: uppercase; letter-spacing: 0.09em;
    color: #1E293B; margin-bottom: 14px; padding-bottom: 10px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}

/* Input fields */
[data-testid="stTextInput"] label {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important; font-size: 0.78rem !important;
    color: #64748B !important;
    text-transform: none !important; letter-spacing: 0 !important;
}
[data-testid="stTextInput"] input {
    height: 46px !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    background: rgba(255,255,255,0.035) !important;
    color: #F1F5F9 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 400 !important;
    transition: all 0.15s ease !important;
    caret-color: #6366F1 !important;
}
[data-testid="stTextInput"] input:hover {
    border-color: rgba(255,255,255,0.13) !important;
    background: rgba(255,255,255,0.05) !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(99,102,241,0.55) !important;
    background: rgba(99,102,241,0.04) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.10) !important;
    outline: none !important;
}
[data-testid="stTextInput"] input::placeholder {
    color: rgba(71,85,105,0.75) !important;
    font-size: 0.84rem !important;
}

/* Sign In button */
.stButton > button {
    height: 46px !important;
    border-radius: 10px !important;
    background: linear-gradient(135deg, #5153CC 0%, #6366F1 60%, #7C7FFA 100%) !important;
    border: none !important; color: #fff !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important; font-size: 0.9rem !important;
    letter-spacing: 0.005em !important;
    box-shadow:
        0 1px 0 rgba(255,255,255,0.1) inset,
        0 4px 18px rgba(99,102,241,0.32),
        0 1px 4px rgba(0,0,0,0.25) !important;
    transition: all 0.18s cubic-bezier(0.16,1,0.3,1) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow:
        0 1px 0 rgba(255,255,255,0.12) inset,
        0 8px 28px rgba(99,102,241,0.4),
        0 2px 8px rgba(0,0,0,0.25) !important;
    background: linear-gradient(135deg, #4D4FC8 0%, #5F62EE 60%, #797CF7 100%) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
    box-shadow: 0 2px 10px rgba(99,102,241,0.22) !important;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important; border: none !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary {
    color: #334155 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.78rem !important; font-weight: 500 !important;
}
[data-testid="stExpander"] summary:hover { color: #475569 !important; }

/* Credential chips */
.cred-chip {
    display: inline-block;
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.14);
    border-radius: 99px; padding: 3px 10px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.68rem;
    color: #818CF8; margin: 3px 2px;
}

/* Separator */
.sep {
    display: flex; align-items: center; gap: 10px; margin: 0.9rem 0;
    position: relative; z-index: 2;
}
.sep-line { flex: 1; height: 1px; background: rgba(255,255,255,0.05); }
.sep-text { font-family: 'Inter', sans-serif; font-size: 0.7rem; color: #1E293B; }

/* Tagline */
.rp-tagline {
    text-align: center; margin-top: 1.25rem;
    font-family: 'Inter', sans-serif; font-size: 0.7rem;
    color: rgba(51,65,85,0.8); position: relative; z-index: 2;
}

/* Gap between vertical blocks */
[data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
</style>
""", unsafe_allow_html=True)

# ── session defaults ──────────────────────────────────────────
for key, val in {
    "logged_in": False, "user_id": None, "user_name": "",
    "role": None, "roll_no": None, "faculty_id": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── redirect if already logged in ────────────────────────────
if st.session_state.logged_in:
    role = st.session_state.role
    if role == "Student":   st.switch_page("pages/1_Student.py")
    elif role == "Faculty": st.switch_page("pages/2_Faculty.py")
    elif role == "Admin":   st.switch_page("pages/3_Admin.py")

# ─────────────────────────────────────────────────────────────
#  LAYOUT — two columns
# ─────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1.1, 0.9], gap="small")

# ══════════════════════════════════════════════════════════════
#  LEFT — 100% pure HTML, zero Streamlit widgets
# ══════════════════════════════════════════════════════════════
with col_left:
    st.markdown("""
<div class="lp-root">
  <div class="orb orb-1"></div>
  <div class="orb orb-2"></div>
  <div class="orb orb-3"></div>
  <div class="lp-logo">
    <div class="lp-logo-mark">A</div>
    <span class="lp-logo-text">AcadHub</span>
  </div>
  <div class="lp-headline">
    Your academic world,<br>
    <span class="grad">unified &amp; simplified.</span>
  </div>
  <div class="lp-sub">
    A modern platform for students, faculty, and administrators —
    built to make academic workflows feel completely effortless.
  </div>
  <div class="lp-features">
    <div class="feat">
      <div class="feat-icon" style="background:rgba(99,102,241,0.12);color:#818CF8">📊</div>
      <div>
        <div class="feat-title">Real time Performance Analytics</div>
        <div class="feat-desc">Live grades, attendance trends, and GPA tracking at a glance.</div>
      </div>
    </div>
    <div class="feat">
      <div class="feat-icon" style="background:rgba(16,185,129,0.12);color:#34D399">📅</div>
      <div>
        <div class="feat-title">Smart Attendance Intelligence</div>
        <div class="feat-desc">Automated eligibility checks and subject-wise breakdowns.</div>
      </div>
    </div>
    <div class="feat">
      <div class="feat-icon" style="background:rgba(245,158,11,0.12);color:#FCD34D">⚙️</div>
      <div>
        <div class="feat-title">Centralized Academic Workflow</div>
        <div class="feat-desc">Courses, timetables, fees, and communication in one place.</div>
      </div>
    </div>
  </div>
  <div class="lp-trust">
    <div class="trust-dot"></div>
    <div class="trust-text">Used by <b>Students · Faculty · Administrators</b> across departments</div>
  </div>
  <div class="lp-footer">© 2026 AcadHub · Academic Management System</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  RIGHT — decorative HTML blocks + Streamlit widgets OUTSIDE HTML
#  GOLDEN RULE: every st.markdown() div is fully self-closed.
#               No widget ever lives inside an HTML string.
# ══════════════════════════════════════════════════════════════
with col_right:

    # Vertical centering spacer
    st.markdown("<div style='height:6vh'></div>", unsafe_allow_html=True)

    # Padding columns so form doesn't stretch full width
    _, mid, _ = st.columns([0.12, 1, 0.12])

    with mid:

        # ── Logo + heading (self-contained HTML) ────────────
        st.markdown("""
<div style="text-align:center;margin-bottom:1.6rem;position:relative;z-index:2">
  <div class="rp-card-glow"></div>
  <div class="rp-logo-icon">A</div>
  <div class="rp-title">Sign in to AcadHub</div>
  <div class="rp-subtitle">Enter your credentials to continue</div>
</div>
""", unsafe_allow_html=True)



   

        # ── Streamlit widgets — plain, styled only via CSS ──
        username  = st.text_input("Username",
                                   placeholder="e.g. kriti16",
                                   key="lg_user")

        st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

        password  = st.text_input("Password",
                                   type="password",
                                   placeholder="Enter your password",
                                   key="lg_pass")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        login_btn = st.button("Sign In →",
                               use_container_width=True,
                               key="lg_btn")

        # ── Auth logic ──────────────────────────────────────
        if login_btn:
            if not username or not password:
                st.error("Please fill in both fields.")
            else:
                user = authenticate(username.strip(), password.strip())
                if user:
                    st.session_state.logged_in  = True
                    st.session_state.user_id    = user["user_id"]
                    st.session_state.user_name  = user["name"]
                    st.session_state.role       = user["role"]
                    if user["role"] == "Student":
                        s = get_student_by_user(user["user_id"])
                        st.session_state.roll_no = s["roll_no"] if s else None
                    elif user["role"] == "Faculty":
                        f = get_faculty_by_user(user["user_id"])
                        st.session_state.faculty_id = f["faculty_id"] if f else None
                    st.success(f"Welcome back, {user['name']}! Redirecting…")
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")

        # ── Separator (self-contained HTML) ─────────────────
        st.markdown("""
<div class="sep">
  <div class="sep-line"></div>
  <div class="sep-text">demo access</div>
  <div class="sep-line"></div>
</div>
""", unsafe_allow_html=True)

        # ── Demo credentials — Streamlit expander ───────────
        with st.expander("View demo credentials"):
            st.markdown("""
<div style="padding:4px 0 2px">

  <div style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:700;
       text-transform:uppercase;letter-spacing:0.09em;color:#1E293B;margin-bottom:8px">
    🎓 Students
  </div>
  <span class="cred-chip">kriti16 / kri16</span>
  <span class="cred-chip">lavdeep23 / lav23</span>
  <span class="cred-chip">aman10 / ama10</span>
  <span class="cred-chip">sim90 / ravi90</span>

  <div style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:700;
       text-transform:uppercase;letter-spacing:0.09em;color:#1E293B;
       margin-top:14px;margin-bottom:8px">
    👩‍🏫 Faculty
  </div>
  <span class="cred-chip">rumneek24 / rum24</span>
  <span class="cred-chip">raj19 / pass12903</span>

  <div style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:700;
       text-transform:uppercase;letter-spacing:0.09em;color:#1E293B;
       margin-top:14px;margin-bottom:8px">
    ⚙️ Admin
  </div>
  <span class="cred-chip">doaa30 / adm@123</span>

</div>
""", unsafe_allow_html=True)

        # ── Tagline (self-contained HTML) ────────────────────
        st.markdown("""
<div class="rp-tagline">
  Secure academic platform &nbsp;·&nbsp; AcadHub 2026
</div>
""", unsafe_allow_html=True)

        st.markdown("<div style='height:4vh'></div>", unsafe_allow_html=True)