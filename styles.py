import streamlit as st

FONTS = """
<link rel="preconnect" href="https://api.fontshare.com">
<link href="https://api.fontshare.com/v2/css?f[]=clash-display@400,500,600,700&f[]=satoshi@400,500,700&display=swap" rel="stylesheet">
"""

CSS = """
<style>
/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Satoshi', sans-serif;
    color: #0F172A;
}

h1, h2, h3, .display {
    font-family: 'Clash Display', sans-serif;
    letter-spacing: -0.02em;
}

/* ── Background ── */
.stApp {
    background: #F8FAFC;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    font-family: 'Clash Display', sans-serif;
}

/* ── Metric cards ── */
div[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
div[data-testid="metric-container"] label {
    font-family: 'Satoshi', sans-serif;
    font-size: 0.75rem;
    font-weight: 500;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Clash Display', sans-serif;
    font-size: 1.8rem;
    color: #6366F1;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'Satoshi', sans-serif;
    font-weight: 600;
    background: #6366F1;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 22px;
    transition: background 0.18s ease, transform 0.12s ease;
}
.stButton > button:hover {
    background: #4F46E5;
    transform: translateY(-1px);
}

/* ── Inputs ── */
.stTextInput input, .stSelectbox select, .stNumberInput input {
    font-family: 'Satoshi', sans-serif;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    background: #FFFFFF;
}
.stTextInput input:focus {
    border-color: #6366F1;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12);
}

/* ── Tables / DataFrames ── */
.stDataFrame {
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    overflow: hidden;
}

/* ── Tab bar ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #F1F5F9;
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Satoshi', sans-serif;
    font-weight: 500;
    border-radius: 7px;
    color: #64748B;
}
.stTabs [aria-selected="true"] {
    background: #FFFFFF;
    color: #6366F1;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

/* ── Cards ── */
.card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* ── Status badges ── */
.badge-pass   { background:#D1FAE5; color:#065F46; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-fail   { background:#FEE2E2; color:#991B1B; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-risk   { background:#FEF3C7; color:#92400E; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-safe   { background:#D1FAE5; color:#065F46; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }

/* ── Page header ── */
.page-header {
    margin-bottom: 28px;
    padding-bottom: 16px;
    border-bottom: 1px solid #E2E8F0;
}
.page-header h1 {
    font-size: 1.9rem;
    margin-bottom: 2px;
    color: #0F172A;
}
.page-header p {
    color: #64748B;
    font-size: 0.95rem;
    margin: 0;
}

/* ── Divider ── */
hr { border: none; border-top: 1px solid #E2E8F0; margin: 24px 0; }

/* ── Sidebar logo area ── */
.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 0 24px 0;
    border-bottom: 1px solid #E2E8F0;
    margin-bottom: 20px;
}
.sidebar-logo-icon {
    width: 36px; height: 36px;
    background: #6366F1;
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    color: white;
    font-family: 'Clash Display', sans-serif;
    font-size: 1rem;
    font-weight: 700;
}
.sidebar-logo-text {
    font-family: 'Clash Display', sans-serif;
    font-size: 1.2rem;
    font-weight: 600;
    color: #0F172A;
}
.sidebar-logo-sub {
    font-size: 0.72rem;
    color: #94A3B8;
    font-family: 'Satoshi', sans-serif;
}

/* ── Success / Error alerts ── */
.stAlert {
    border-radius: 10px;
    font-family: 'Satoshi', sans-serif;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    font-family: 'Satoshi', sans-serif;
    font-weight: 600;
    color: #0F172A;
}
</style>
"""


def inject_styles():
    st.markdown(FONTS, unsafe_allow_html=True)
    st.markdown(CSS, unsafe_allow_html=True)


def sidebar_logo():
    st.sidebar.markdown(
        """
        <div class="sidebar-logo">
            <div class="sidebar-logo-icon">A</div>
            <div>
                <div class="sidebar-logo-text">AcadHub</div>
                <div class="sidebar-logo-sub">Academic Management System</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="page-header">
            <h1>{title}</h1>
            {"<p>" + subtitle + "</p>" if subtitle else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(text: str, kind: str = "pass") -> str:
    return f'<span class="badge-{kind}">{text}</span>'
