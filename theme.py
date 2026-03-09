import streamlit as st

# ==============================
# COLOR THEMES & CURRENCIES
# ==============================
COLOR_THEMES = {
    "Purple (Default)": {"a1": "#a78bfa", "a2": "#60a5fa", "a3": "#34d399"},
    "Ocean Blue":        {"a1": "#38bdf8", "a2": "#818cf8", "a3": "#34d399"},
    "Emerald":           {"a1": "#34d399", "a2": "#60a5fa", "a3": "#fbbf24"},
    "Rose":              {"a1": "#f87171", "a2": "#fb923c", "a3": "#34d399"},
    "Amber":             {"a1": "#fbbf24", "a2": "#f97316", "a3": "#34d399"},
    "Pink":              {"a1": "#e879f9", "a2": "#a78bfa", "a3": "#34d399"},
}
CURRENCIES = {
    "PKR (Rs)": "Rs", "USD ($)": "$", "EUR (€)": "€",
    "GBP (£)": "£",  "AED (د.إ)": "د.إ", "SAR (﷼)": "﷼"
}

# ==============================
# GET ACTIVE THEME VARIABLES
# ==============================
def get_theme_vars():
    if "color_theme" not in st.session_state:
        st.session_state["color_theme"] = "Purple (Default)"
    if "currency" not in st.session_state:
        st.session_state["currency"] = "PKR (Rs)"

    _t = COLOR_THEMES[st.session_state["color_theme"]]
    CURR_SYMBOL = CURRENCIES.get(st.session_state["currency"], "Rs")

    return dict(
        is_dark     = True,
        BG          = "#0d0d14",
        BG2         = "#13131f",
        BG3         = "#1a1a2e",
        BORDER      = "#2a2a45",
        TEXT        = "#f0f0f8",
        TEXT2       = "#8888aa",
        ACCENT1     = _t["a1"],
        ACCENT2     = _t["a2"],
        ACCENT3     = _t["a3"],
        SIDEBAR_BG  = "#0f0f1a",
        PLOT_PAPER  = "#0d0d14",
        PLOT_BG     = "#13131f",
        PLOT_GRID   = "#1e1e35",
        FILL_COLOR  = "rgba(167,139,250,0.08)",
        SHADOW      = "0 4px 24px rgba(0,0,0,0.5)",
        CHART_COLORS= [_t["a1"], _t["a2"], _t["a3"],
                       "#fbbf24", "#f87171", "#e879f9", "#22d3ee", "#fb923c"],
        CURR_SYMBOL = CURR_SYMBOL,
    )

# ==============================
# PLOTLY TEMPLATE
# ==============================
def get_plot_template(T):
    return dict(
        paper_bgcolor = T["PLOT_PAPER"],
        plot_bgcolor  = T["PLOT_BG"],
        font          = dict(color=T["TEXT"], family="Plus Jakarta Sans"),
        xaxis         = dict(gridcolor=T["PLOT_GRID"], linecolor=T["BORDER"],
                             tickfont=dict(color=T["TEXT2"]), showgrid=True),
        yaxis         = dict(gridcolor=T["PLOT_GRID"], linecolor=T["BORDER"],
                             tickfont=dict(color=T["TEXT2"]), showgrid=True),
        colorway      = T["CHART_COLORS"],
        margin        = dict(t=44, b=36, l=36, r=16),
        title_font    = dict(color=T["TEXT"], size=14),
        title_x       = 0.02,
        legend        = dict(bgcolor="rgba(0,0,0,0)", font=dict(color=T["TEXT2"]),
                             bordercolor=T["BORDER"], borderwidth=1),
    )

# ==============================
# INJECT CSS
# ==============================
def inject_css(T):
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: {T['BG']} !important;
    color: {T['TEXT']} !important;
}}
.main, .block-container {{
    background: {T['BG']} !important;
    padding-top: 1.5rem !important;
}}
section[data-testid="stSidebar"] {{
    background: {T['SIDEBAR_BG']} !important;
    border-right: 1px solid {T['BORDER']} !important;
    box-shadow: none !important;
}}
section[data-testid="stSidebar"] > div {{ padding-top: 0 !important; }}
section[data-testid="stSidebar"] * {{ color: {T['TEXT']} !important; }}

.sidebar-label {{
    font-size: 0.72rem; font-weight: 700; color: {T['TEXT2']};
    text-transform: uppercase; letter-spacing: 1.2px;
    margin: 16px 0 7px 0; padding-left: 2px;
    display: flex; align-items: center; gap: 5px;
}}

.hero-wrap {{
    background: linear-gradient(135deg,#13131f,#1a1a2e);
    border: 1px solid {T['BORDER']}; border-radius: 20px;
    padding: 30px 36px; margin-bottom: 24px;
    box-shadow: {T['SHADOW']}; position: relative; overflow: hidden;
}}
.hero-wrap::before {{
    content:''; position:absolute; top:-80px; right:-80px;
    width:240px; height:240px;
    background: radial-gradient(circle, rgba(167,139,250,0.12), transparent 70%);
    border-radius:50%;
}}
.hero-title {{
    font-family: 'Syne', sans-serif; font-size: 2.2rem; font-weight: 800;
    color: {T['ACCENT1']}; margin: 0 0 8px 0; line-height: 1.1;
}}
.hero-sub {{ color: {T['TEXT2']}; font-size: 0.95rem; margin: 0; }}

.metric-card {{
    background: linear-gradient(135deg,#13131f,#1a1a2e);
    border: 1px solid {T['BORDER']}; border-radius: 16px;
    padding: 22px; margin: 6px 0; box-shadow: {T['SHADOW']};
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    position: relative; overflow: hidden; text-align: center;
}}
.metric-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(167,139,250,0.25);
    border-color: {T['ACCENT1']};
}}
.metric-value {{
    font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800;
    color: {T['ACCENT1']}; line-height: 1.1;
}}
.metric-label {{
    font-size: 0.75rem; color: {T['TEXT2']};
    text-transform: uppercase; letter-spacing: 1.5px;
    margin-top: 5px; font-weight: 600;
}}

.section-title {{
    font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700;
    color: {T['TEXT']}; margin: 24px 0 14px 0; padding-bottom: 10px;
    border-bottom: 2px solid {T['BORDER']};
    display: flex; align-items: center; gap: 8px;
}}

.ai-response {{
    background: linear-gradient(135deg,#0d1b2e,#0f2040);
    border: 1px solid #1e4a7a; border-left: 4px solid {T['ACCENT2']};
    border-radius: 14px; padding: 22px 26px; margin: 12px 0;
    line-height: 1.8; font-size: 0.94rem;
    color: {T['TEXT']}; box-shadow: {T['SHADOW']};
}}

.upload-hint {{
    text-align: center; padding: 48px 40px 36px 40px;
    border: 2.5px dashed {T['ACCENT1']}; border-radius: 22px;
    margin: 20px 0 8px 0;
    background: linear-gradient(135deg,#13131f,#1a1a2e);
    transition: all 0.3s ease; position: relative; overflow: hidden;
}}
.upload-hint:hover {{
    border-color: {T['ACCENT2']};
    box-shadow: 0 0 32px rgba(167,139,250,0.15);
    transform: translateY(-2px);
}}
.upload-icon-wrap {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 72px; height: 72px; border-radius: 50%;
    background: linear-gradient(135deg, {T['ACCENT1']}22, {T['ACCENT2']}22);
    border: 2px solid {T['ACCENT1']}55; margin-bottom: 16px; font-size: 2rem;
}}

.step-card {{
    background: linear-gradient(135deg,#13131f,#1a1a2e);
    border: 1px solid {T['BORDER']}; border-radius: 14px;
    padding: 20px; text-align: center; box-shadow: {T['SHADOW']};
    height: 100%; transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.step-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 10px 28px rgba(167,139,250,0.2);
}}
.step-num {{
    display: inline-flex; width: 34px; height: 34px;
    background: linear-gradient(135deg, {T['ACCENT1']}, {T['ACCENT2']});
    border-radius: 50%; align-items: center; justify-content: center;
    color: white; font-weight: 700; font-size: 0.9rem; margin-bottom: 10px;
}}

.stButton > button {{
    background: linear-gradient(135deg, {T['ACCENT1']}, {T['ACCENT2']}) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; padding: 10px 22px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(167,139,250,0.3) !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(167,139,250,0.5) !important;
}}

.stTabs [data-baseweb="tab-list"] {{
    background: {T['BG3']}; border-radius: 16px; padding: 6px 8px;
    gap: 8px; border: 1px solid {T['BORDER']}; box-shadow: {T['SHADOW']};
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important; color: {T['TEXT2']} !important;
    border-radius: 10px !important; font-weight: 600 !important;
    font-size: 0.88rem !important; padding: 10px 22px !important;
    letter-spacing: 0.2px !important; transition: all 0.2s ease !important;
    min-width: 120px !important; text-align: center !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    color: {T['ACCENT1']} !important;
    background: rgba(167,139,250,0.08) !important;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {T['ACCENT1']}, {T['ACCENT2']}) !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(167,139,250,0.4) !important;
}}

.stTextInput > div > div,
.stSelectbox > div > div,
.stTextArea > div > div {{
    background: {T['BG2']} !important; border-color: {T['BORDER']} !important;
    color: {T['TEXT']} !important; border-radius: 9px !important;
}}
.stDataFrame {{ border-radius: 12px !important; overflow: hidden !important; }}
::-webkit-scrollbar {{ width: 5px; }}
::-webkit-scrollbar-track {{ background: {T['BG']}; }}
::-webkit-scrollbar-thumb {{ background: {T['BORDER']}; border-radius: 3px; }}
.js-plotly-plot {{ border-radius: 14px; overflow: hidden; }}

@media (max-width: 768px) {{
    .hero-title {{ font-size: 1.4rem !important; }}
    .hero-wrap {{ padding: 18px 16px !important; }}
    .metric-value {{ font-size: 1.4rem !important; }}
    .metric-card {{ padding: 14px !important; }}
    .section-title {{ font-size: 0.95rem !important; }}
    .stTabs [data-baseweb="tab"] {{
        padding: 8px 10px !important; min-width: 70px !important;
        font-size: 0.75rem !important;
    }}
    .ai-response {{ padding: 14px 16px !important; }}
    .block-container {{ padding-left: 0.5rem !important; padding-right: 0.5rem !important; }}
}}
</style>
""", unsafe_allow_html=True)