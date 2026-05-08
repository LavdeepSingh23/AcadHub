import streamlit as st

FONTS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
"""

CSS = """
<style>
/* ══════════════════════════════════════════
   RESET & DARK CANVAS
══════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
.main {
    background: #05060A !important;
    font-family: 'Inter', sans-serif !important;
    color: #E2E8F0 !important;
}

.main .block-container {
    padding: 2rem 2.5rem 3rem 2.5rem !important;
    max-width: 1400px !important;
}

/* Streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

/* ══════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: #0A0B12 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
section[data-testid="stSidebar"] > div {
    padding: 1.5rem 1.2rem !important;
}
[data-testid="stSidebarNav"] { display: none !important; }

/* ══════════════════════════════════════════
   METRIC CARDS
══════════════════════════════════════════ */
div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.028) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important;
    padding: 18px 20px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4), 0 0 0 1px rgba(99,102,241,0.04) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    backdrop-filter: blur(8px) !important;
}
div[data-testid="metric-container"]:hover {
    border-color: rgba(99,102,241,0.25) !important;
    box-shadow: 0 4px 32px rgba(99,102,241,0.12), 0 0 0 1px rgba(99,102,241,0.1) !important;
}
div[data-testid="metric-container"] label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    color: #475569 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    background: linear-gradient(135deg, #818CF8, #A78BFA) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.76rem !important;
}

/* ══════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════ */
.stButton > button {
    height: 42px !important;
    border-radius: 10px !important;
    background: linear-gradient(135deg, #5153CC 0%, #6366F1 60%, #7C7FFA 100%) !important;
    border: none !important;
    color: #fff !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.005em !important;
    box-shadow: 0 4px 18px rgba(99,102,241,0.28), 0 1px 0 rgba(255,255,255,0.1) inset !important;
    transition: all 0.18s cubic-bezier(0.16,1,0.3,1) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 28px rgba(99,102,241,0.4), 0 1px 0 rgba(255,255,255,0.12) inset !important;
    background: linear-gradient(135deg, #4D4FC8 0%, #5F62EE 60%, #797CF7 100%) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Sign out / secondary */
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #64748B !important;
    box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.07) !important;
    color: #94A3B8 !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ══════════════════════════════════════════
   INPUTS & SELECTS
══════════════════════════════════════════ */
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stDateInput"] label,
[data-testid="stTextArea"] label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.76rem !important;
    font-weight: 500 !important;
    color: #64748B !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    margin-bottom: 4px !important;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    height: 44px !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    background: rgba(255,255,255,0.035) !important;
    color: #F1F5F9 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    caret-color: #6366F1 !important;
    transition: all 0.15s ease !important;
}
[data-testid="stTextArea"] textarea { height: auto !important; min-height: 90px !important; }
[data-testid="stTextInput"] input:hover,
[data-testid="stNumberInput"] input:hover,
[data-testid="stTextArea"] textarea:hover {
    border-color: rgba(255,255,255,0.13) !important;
    background: rgba(255,255,255,0.05) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(99,102,241,0.55) !important;
    background: rgba(99,102,241,0.04) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.10) !important;
    outline: none !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
    color: rgba(71,85,105,0.75) !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    background: rgba(255,255,255,0.035) !important;
    color: #F1F5F9 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
}
[data-testid="stSelectbox"] > div > div:hover {
    border-color: rgba(255,255,255,0.13) !important;
}

/* ══════════════════════════════════════════
   TABS
══════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 3px !important;
    background: rgba(255,255,255,0.025) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    border-radius: 8px !important;
    color: #475569 !important;
    padding: 7px 16px !important;
    transition: color 0.15s !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(99,102,241,0.14) !important;
    color: #818CF8 !important;
    font-weight: 600 !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    box-shadow: none !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #94A3B8 !important; }

/* ══════════════════════════════════════════
   DATAFRAMES / TABLES
══════════════════════════════════════════ */
.stDataFrame {
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    background: rgba(255,255,255,0.02) !important;
}
[data-testid="stDataFrame"] th {
    background: rgba(99,102,241,0.08) !important;
    color: #64748B !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stDataFrame"] td {
    background: transparent !important;
    color: #CBD5E1 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.84rem !important;
    border-bottom: 1px solid rgba(255,255,255,0.03) !important;
}

/* ══════════════════════════════════════════
   EXPANDER
══════════════════════════════════════════ */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.022) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary {
    color: #64748B !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
}
[data-testid="stExpander"] summary:hover { color: #94A3B8 !important; }

/* ══════════════════════════════════════════
   ALERTS
══════════════════════════════════════════ */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    border: none !important;
    background: rgba(255,255,255,0.04) !important;
}

/* ══════════════════════════════════════════
   DIVIDER
══════════════════════════════════════════ */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.06) !important;
    margin: 20px 0 !important;
}

/* ══════════════════════════════════════════
   FORM SUBMIT BUTTON
══════════════════════════════════════════ */
[data-testid="stForm"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important;
    padding: 1.4rem 1.4rem !important;
}

/* ══════════════════════════════════════════
   SPINNER
══════════════════════════════════════════ */
[data-testid="stSpinner"] { color: #6366F1 !important; }

/* ══════════════════════════════════════════
   SCROLLBAR
══════════════════════════════════════════ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(99,102,241,0.25);
    border-radius: 99px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.45); }

/* ══════════════════════════════════════════
   BADGE UTILITIES (used inline)
══════════════════════════════════════════ */
.badge-pass   { background:rgba(16,185,129,0.14); color:#34D399; padding:3px 11px; border-radius:99px; font-size:0.73rem; font-weight:600; border:1px solid rgba(16,185,129,0.2); }
.badge-fail   { background:rgba(239,68,68,0.12);  color:#F87171; padding:3px 11px; border-radius:99px; font-size:0.73rem; font-weight:600; border:1px solid rgba(239,68,68,0.2); }
.badge-risk   { background:rgba(245,158,11,0.12); color:#FCD34D; padding:3px 11px; border-radius:99px; font-size:0.73rem; font-weight:600; border:1px solid rgba(245,158,11,0.2); }
.badge-safe   { background:rgba(16,185,129,0.14); color:#34D399; padding:3px 11px; border-radius:99px; font-size:0.73rem; font-weight:600; border:1px solid rgba(16,185,129,0.2); }

/* ══════════════════════════════════════════
   VERTICAL BLOCK GAP
══════════════════════════════════════════ */
[data-testid="stVerticalBlock"] { gap: 0.6rem !important; }
</style>
"""

_DARK_AXIS = dict(
    gridcolor="rgba(255,255,255,0.05)",
    zeroline=False,
    tickfont=dict(color="#475569", size=11),
)

PLOTLY_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_family="Inter",
    font_color="#94A3B8",
    legend=dict(
        bgcolor="rgba(255,255,255,0.04)",
        bordercolor="rgba(255,255,255,0.07)",
        borderwidth=1,
        font=dict(color="#94A3B8", size=11),
    ),
    margin=dict(t=24, b=8, l=8, r=8),
)

# Convenience: base axis style. Merge into update_layout calls like:
#   fig.update_layout(**PLOTLY_LAYOUT)
#   fig.update_xaxes(**DARK_AXIS)
#   fig.update_yaxes(**DARK_AXIS)
DARK_AXIS = _DARK_AXIS


def inject_styles():
    st.markdown(FONTS, unsafe_allow_html=True)
    st.markdown(CSS, unsafe_allow_html=True)


def sidebar_logo(role: str = "", user_name: str = "", sub_label: str = ""):
    """Render sidebar header with logo, username, role badge."""
    role_colors = {
        "Student": ("rgba(99,102,241,0.14)", "#818CF8"),
        "Faculty": ("rgba(16,185,129,0.14)", "#34D399"),
        "Admin":   ("rgba(245,158,11,0.14)",  "#FCD34D"),
    }
    bg, fg = role_colors.get(role, ("rgba(99,102,241,0.14)", "#818CF8"))

    # Build pieces with plain string concat — avoids nested f-string rgba() issues
    logo_block = (
        "<div style='display:flex;align-items:center;gap:10px;margin-bottom:16px;'>"
        "<div style='width:36px;height:36px;border-radius:9px;"
        "background:linear-gradient(135deg,#6366F1,#818CF8);"
        "display:flex;align-items:center;justify-content:center;"
        "font-family:Inter,sans-serif;font-weight:900;font-size:1rem;color:#fff;'>A</div>"
        "<div>"
        "<div style='font-family:Inter,sans-serif;font-weight:800;font-size:1rem;"
        "color:#F1F5F9;letter-spacing:-0.02em;'>AcadHub</div>"
        "<div style='font-size:0.67rem;color:#334155;'>Academic Management System</div>"
        "</div></div>"
    )

    if user_name:
        sub_html = (
            "<div style='font-size:0.73rem;color:#475569;"
            "font-family:JetBrains Mono,monospace;margin-bottom:6px;'>"
            + sub_label + "</div>"
        ) if sub_label else ""
        user_card = (
            "<div style='background:rgba(255,255,255,0.025);"
            "border:1px solid rgba(255,255,255,0.06);"
            "border-radius:10px;padding:10px 12px;'>"
            "<div style='font-family:Inter,sans-serif;font-weight:700;"
            "font-size:0.9rem;color:#E2E8F0;margin-bottom:2px;'>" + user_name + "</div>"
            + sub_html
            + "<span style='background:" + bg + ";color:" + fg + ";"
            "padding:2px 10px;border-radius:99px;"
            "font-size:0.7rem;font-weight:600;'>" + role + "</span>"
            "</div>"
        )
    else:
        user_card = ""

    html = (
        "<div style='padding:0 0 20px 0;"
        "border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:20px;'>"
        + logo_block + user_card + "</div>"
    )

    st.sidebar.markdown(html, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    """Render a dark-theme page header with optional ambient glow."""
    st.markdown(
        f"""
        <div style="position:relative;margin-bottom:2rem;padding-bottom:1.2rem;
                    border-bottom:1px solid rgba(255,255,255,0.06);">
            <div style="position:absolute;top:-40px;left:-20px;width:300px;height:120px;
                        background:radial-gradient(ellipse,rgba(99,102,241,0.08) 0%,transparent 70%);
                        pointer-events:none;"></div>
            <h1 style="font-family:'Inter',sans-serif;font-weight:800;font-size:1.75rem;
                       letter-spacing:-0.03em;color:#F1F5F9;margin-bottom:4px;
                       position:relative;z-index:1;">{title}</h1>
            {"" if not subtitle else f'<p style="font-family:Inter,sans-serif;font-size:0.88rem;color:#475569;margin:0;position:relative;z-index:1;">{subtitle}</p>'}
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_card(label: str, value, icon: str = "", accent: str = "#6366F1"):
    """Render a custom stat card (use inside st.markdown)."""
    return f"""
    <div style="background:rgba(255,255,255,0.028);border:1px solid rgba(255,255,255,0.07);
                border-radius:14px;padding:18px 20px;
                box-shadow:0 4px 24px rgba(0,0,0,0.4);
                transition:border-color 0.2s;">
        <div style="font-size:1.4rem;margin-bottom:8px;">{icon}</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:600;
                    text-transform:uppercase;letter-spacing:0.08em;color:#475569;
                    margin-bottom:4px;">{label}</div>
        <div style="font-family:'Inter',sans-serif;font-size:1.9rem;font-weight:800;
                    letter-spacing:-0.03em;
                    background:linear-gradient(135deg,{accent},{accent}99);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;">{value}</div>
    </div>
    """


def status_badge(text: str, kind: str = "pass") -> str:
    return f'<span class="badge-{kind}">{text}</span>'


def section_header(text: str, sub: str = ""):
    sub_html = f'<div style="font-size:0.78rem;color:#475569;margin-top:2px;">{sub}</div>' if sub else ""
    st.markdown(
        f"""
        <div style="margin-bottom:14px;padding-bottom:10px;
                    border-bottom:1px solid rgba(255,255,255,0.05);">
            <div style="font-family:'Inter',sans-serif;font-size:0.95rem;font-weight:700;
                        color:#CBD5E1;letter-spacing:-0.01em;">{text}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )