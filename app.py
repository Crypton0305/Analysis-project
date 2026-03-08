import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from groq import Groq
import io
from datetime import datetime
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="SpendSense AI",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# THEME VARIABLES
# ==============================
COLOR_THEMES = {
    "Purple (Default)": {"a1": "#a78bfa", "a2": "#60a5fa", "a3": "#34d399"},
    "Ocean Blue":        {"a1": "#38bdf8", "a2": "#818cf8", "a3": "#34d399"},
    "Emerald":           {"a1": "#34d399", "a2": "#60a5fa", "a3": "#fbbf24"},
    "Rose":              {"a1": "#f87171", "a2": "#fb923c", "a3": "#34d399"},
    "Amber":             {"a1": "#fbbf24", "a2": "#f97316", "a3": "#34d399"},
    "Pink":              {"a1": "#e879f9", "a2": "#a78bfa", "a3": "#34d399"},
}
CURRENCIES = {"PKR (Rs)":"Rs","USD ($)":"$","EUR (€)":"€","GBP (£)":"£","AED (د.إ)":"د.إ","SAR (﷼)":"﷼"}

if "color_theme" not in st.session_state:
    st.session_state["color_theme"] = "Purple (Default)"
if "currency" not in st.session_state:
    st.session_state["currency"] = "PKR (Rs)"

_t = COLOR_THEMES[st.session_state["color_theme"]]
CURR_SYMBOL = CURRENCIES.get(st.session_state["currency"], "Rs")

is_dark     = True
BG          = "#0d0d14"
BG2         = "#13131f"
BG3         = "#1a1a2e"
BORDER      = "#2a2a45"
TEXT        = "#f0f0f8"
TEXT2       = "#8888aa"
ACCENT1     = _t["a1"]
ACCENT2     = _t["a2"]
ACCENT3     = _t["a3"]
SIDEBAR_BG  = "#0f0f1a"
PLOT_PAPER  = "#0d0d14"
PLOT_BG     = "#13131f"
PLOT_GRID   = "#1e1e35"
FILL_COLOR  = "rgba(167,139,250,0.08)"
SHADOW      = "0 4px 24px rgba(0,0,0,0.5)"
CHART_COLORS = [_t["a1"], _t["a2"], _t["a3"], "#fbbf24","#f87171","#e879f9","#22d3ee","#fb923c"]

# ==============================
# CSS
# ==============================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: {BG} !important;
    color: {TEXT} !important;
}}
.main, .block-container {{
    background: {BG} !important;
    padding-top: 1.5rem !important;
}}
section[data-testid="stSidebar"] {{
    background: {SIDEBAR_BG} !important;
    border-right: 1px solid {BORDER} !important;
    box-shadow: none !important;
}}
section[data-testid="stSidebar"] > div {{
    padding-top: 0 !important;
}}
section[data-testid="stSidebar"] * {{ color: {TEXT} !important; }}

.sidebar-label {{
    font-size: 0.72rem;
    font-weight: 700;
    color: {TEXT2};
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin: 16px 0 7px 0;
    padding-left: 2px;
    display: flex;
    align-items: center;
    gap: 5px;
}}

.hero-wrap {{
    background: linear-gradient(135deg,#13131f,#1a1a2e);
    border: 1px solid {BORDER};
    border-radius: 20px;
    padding: 30px 36px;
    margin-bottom: 24px;
    box-shadow: {SHADOW};
    position: relative;
    overflow: hidden;
}}
.hero-wrap::before {{
    content:'';
    position:absolute; top:-80px; right:-80px;
    width:240px; height:240px;
    background: radial-gradient(circle, rgba(167,139,250,0.12), transparent 70%);
    border-radius:50%;
}}
.hero-title {{
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, {ACCENT1}, {ACCENT2});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 8px 0;
}}
.hero-sub {{ color: {TEXT2}; font-size: 0.95rem; margin: 0; }}

.metric-card {{
    background: linear-gradient(135deg,#13131f,#1a1a2e);
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 22px;
    margin: 6px 0;
    box-shadow: {SHADOW};
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    position: relative;
    overflow: hidden;
}}
.metric-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(167,139,250,0.25);
    border-color: {ACCENT1};
}}
.metric-value {{
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, {ACCENT1}, {ACCENT2});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
}}
.metric-label {{
    font-size: 0.75rem;
    color: {TEXT2};
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 5px;
    font-weight: 600;
}}

.section-title {{
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: {TEXT};
    margin: 24px 0 14px 0;
    padding-bottom: 10px;
    border-bottom: 2px solid {BORDER};
    display: flex;
    align-items: center;
    gap: 8px;
}}

.ai-response {{
    background: linear-gradient(135deg,#0d1b2e,#0f2040);
    border: 1px solid #1e4a7a;
    border-left: 4px solid {ACCENT2};
    border-radius: 14px;
    padding: 22px 26px;
    margin: 12px 0;
    line-height: 1.8;
    font-size: 0.94rem;
    color: {TEXT};
    box-shadow: {SHADOW};
}}

.upload-hint {{
    text-align: center;
    padding: 60px 40px;
    border: 2px dashed {BORDER};
    border-radius: 20px;
    margin: 20px 0;
    background: #13131f;
    transition: border-color 0.2s;
}}
.upload-hint:hover {{ border-color: {ACCENT1}; }}

.step-card {{
    background: linear-gradient(135deg,#13131f,#1a1a2e);
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    box-shadow: {SHADOW};
    height: 100%;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.step-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 10px 28px rgba(167,139,250,0.2);
}}
.step-num {{
    display: inline-flex;
    width: 34px; height: 34px;
    background: linear-gradient(135deg, {ACCENT1}, {ACCENT2});
    border-radius: 50%;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 700;
    font-size: 0.9rem;
    margin-bottom: 10px;
}}

.stButton > button {{
    background: linear-gradient(135deg, {ACCENT1}, {ACCENT2}) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 22px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(167,139,250,0.3) !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(167,139,250,0.5) !important;
}}

.stTabs [data-baseweb="tab-list"] {{
    background: {BG3};
    border-radius: 16px;
    padding: 6px 8px;
    gap: 8px;
    border: 1px solid {BORDER};
    box-shadow: {SHADOW};
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {TEXT2} !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 10px 22px !important;
    letter-spacing: 0.2px !important;
    transition: all 0.2s ease !important;
    min-width: 120px !important;
    text-align: center !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    color: {ACCENT1} !important;
    background: rgba(167,139,250,0.08) !important;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {ACCENT1}, {ACCENT2}) !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(167,139,250,0.4) !important;
}}

.stTextInput > div > div,
.stSelectbox > div > div,
.stTextArea > div > div {{
    background: {BG2} !important;
    border-color: {BORDER} !important;
    color: {TEXT} !important;
    border-radius: 9px !important;
}}

.stDataFrame {{ border-radius: 12px !important; overflow: hidden !important; }}

::-webkit-scrollbar {{ width: 5px; }}
::-webkit-scrollbar-track {{ background: {BG}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 3px; }}

.js-plotly-plot {{ border-radius: 14px; overflow: hidden; }}

/* ===== MOBILE RESPONSIVE ===== */
@media (max-width: 768px) {{
    .hero-title {{ font-size: 1.4rem !important; }}
    .hero-wrap {{ padding: 18px 16px !important; }}
    .metric-value {{ font-size: 1.4rem !important; }}
    .metric-card {{ padding: 14px !important; }}
    .section-title {{ font-size: 0.95rem !important; }}
    .stTabs [data-baseweb="tab"] {{
        padding: 8px 10px !important;
        min-width: 70px !important;
        font-size: 0.75rem !important;
    }}
    .ai-response {{ padding: 14px 16px !important; }}
    .block-container {{ padding-left: 0.5rem !important; padding-right: 0.5rem !important; }}
}}
</style>
""", unsafe_allow_html=True)

# ==============================
# PLOTLY TEMPLATE
# ==============================
PLOT_TPL = dict(
    paper_bgcolor=PLOT_PAPER,
    plot_bgcolor=PLOT_BG,
    font=dict(color=TEXT, family="Plus Jakarta Sans"),
    xaxis=dict(gridcolor=PLOT_GRID, linecolor=BORDER, tickfont=dict(color=TEXT2), showgrid=True),
    yaxis=dict(gridcolor=PLOT_GRID, linecolor=BORDER, tickfont=dict(color=TEXT2), showgrid=True),
    colorway=CHART_COLORS,
    margin=dict(t=44, b=36, l=36, r=16),
    title_font=dict(color=TEXT, size=14),
    title_x=0.02,
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT2), bordercolor=BORDER, borderwidth=1),
)

# ==============================
# HELPER FUNCTIONS
# ==============================
def clean_dataframe(df):
    df = df.drop_duplicates()
    for col in df.select_dtypes(include=np.number).columns:
        df[col] = df[col].fillna(df[col].median())
    for col in df.select_dtypes(include=["object"]).columns:
        if df[col].mode().shape[0] > 0:
            df[col] = df[col].fillna(df[col].mode()[0])
    for col in df.columns:
        if "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="coerce")
            df["Year"]       = df[col].dt.year
            df["Month"]      = df[col].dt.month
            df["Month_Name"] = df[col].dt.strftime("%b")
            df["Day"]        = df[col].dt.day
    return df

def get_numeric_cols(df):
    skip = ["Year","Month","Day","Row_Total","Row_Mean"]
    return [c for c in df.select_dtypes(include=np.number).columns if c not in skip]

def generate_summary_stats(df):
    numeric_cols = get_numeric_cols(df)
    cat_cols     = df.select_dtypes(include=["object"]).columns.tolist()
    summary = {
        "rows": len(df), "columns": len(df.columns),
        "numeric_cols": numeric_cols, "cat_cols": cat_cols,
        "describe": df[numeric_cols].describe().to_string() if numeric_cols else "N/A",
        "corr": df[numeric_cols].corr().to_string() if len(numeric_cols) > 1 else "N/A",
        "cat_summary": {}
    }
    for col in cat_cols[:3]:
        summary["cat_summary"][col] = df[col].value_counts().head(5).to_dict()
    return summary

def ask_claude(prompt, api_key):
    client = Groq(api_key=api_key)
    model  = st.session_state.get("groq_model", "llama-3.1-8b-instant")
    resp   = client.chat.completions.create(
        model=model,
        messages=[{"role":"user","content":prompt}],
        max_tokens=1000,
    )
    return resp.choices[0].message.content

def build_ai_prompt(analysis_type, summary, extra=""):
    cat_str = ""
    for k, v in list(summary["cat_summary"].items())[:2]:
        cat_str += f"{k}: {list(v.items())[:3]}\n"
    base = (
        f"Expense data: {summary['rows']} rows. "
        f"Numeric cols: {', '.join(summary['numeric_cols'][:4])}. "
        f"Categories: {cat_str.strip()}. "
    )
    extra_short = str(extra)[:200] if extra else ""
    lang = st.session_state.get("ai_lang", "English")
    if "Urdu" in lang:
        lang_note = " Respond in Urdu or Roman Urdu. Be friendly."
    elif "Hindi" in lang:
        lang_note = " Respond in Hindi. Be friendly."
    else:
        lang_note = ""
    prompts = {
        "overview": base + "Give a 3-sentence overview of this spending data and financial health." + lang_note,
        "savings":  base + "Give 4 specific savings tips. Use bullet points. Be concise." + lang_note,
        "income":   base + "Suggest 4 ways to grow income or optimize finances. Bullet points." + lang_note,
        "warnings": base + "List 3 spending red flags from this data. Be direct and brief." + lang_note,
        "monthly":  base + "Analyze monthly pattern. Recommend a budget split. Keep it short." + lang_note,
        "custom":   base + f"Answer this: {extra_short}" + lang_note,
    }
    return prompts.get(analysis_type, prompts["overview"])

# ==============================
# SIDEBAR
# ==============================
with st.sidebar:

    st.markdown(f"""
    <div style='padding:20px 4px 16px 4px;border-bottom:2px solid {BORDER};margin-bottom:4px;'>
        <div style='font-family:Syne,sans-serif;font-size:1.55rem;font-weight:800;
        color:{ACCENT1};line-height:1.1;'>
            💸 SpendSense AI
        </div>
        <div style='color:{TEXT2};font-size:0.78rem;margin-top:5px;letter-spacing:0.3px;'>
            Smart Expense Analyzer
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='sidebar-label'>🔑 Groq API Key</div>", unsafe_allow_html=True)
    api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...", label_visibility="collapsed")
    st.markdown(f"<div style='font-size:0.73rem;color:{TEXT2};margin-top:3px;'>Get free key → <a href='https://console.groq.com' target='_blank' style='color:{ACCENT2};font-weight:600;'>console.groq.com</a></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='sidebar-label'>🤖 AI Model</div>", unsafe_allow_html=True)
    groq_model = st.selectbox("model", label_visibility="collapsed",
        options=["llama-3.1-8b-instant","llama-3.3-70b-versatile","llama3-8b-8192","gemma2-9b-it","mixtral-8x7b-32768"],
        index=0)
    model_meta = {
        "llama-3.1-8b-instant":    ("⚡","Fast","14,400 req/day"),
        "llama-3.3-70b-versatile": ("🧠","Smart","1,000 req/day"),
        "llama3-8b-8192":          ("⚡","Fast","14,400 req/day"),
        "gemma2-9b-it":            ("🔷","Google","14,400 req/day"),
        "mixtral-8x7b-32768":      ("🌀","Mixtral","14,400 req/day"),
    }
    ic, spd, lim = model_meta.get(groq_model, ("🤖","","N/A"))
    st.markdown(f"""
    <div style='background:#13131f;border:1px solid {BORDER};
    border-radius:10px;padding:10px 13px;margin-top:4px;'>
        <div style='font-weight:700;color:{ACCENT1};font-size:0.82rem;'>{ic} {groq_model}</div>
        <div style='color:{TEXT2};font-size:0.74rem;margin-top:2px;'>{spd} · {lim}</div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state["groq_model"] = groq_model

    st.markdown(f"<div class='sidebar-label'>🌐 AI Language</div>", unsafe_allow_html=True)
    ai_lang = st.selectbox("lang", label_visibility="collapsed",
        options=["English", "Urdu (اردو)", "Hindi (हिंदी)"], index=0)
    st.session_state["ai_lang"] = ai_lang

    # ---- COLOR THEME ----
    st.markdown(f"<div class='sidebar-label'>🎨 Color Theme</div>", unsafe_allow_html=True)
    theme_keys = list(COLOR_THEMES.keys())
    chosen_theme = st.selectbox("theme", label_visibility="collapsed", options=theme_keys,
        index=theme_keys.index(st.session_state["color_theme"]))
    if chosen_theme != st.session_state["color_theme"]:
        st.session_state["color_theme"] = chosen_theme
        st.rerun()
    _prev = COLOR_THEMES[chosen_theme]
    st.markdown(
        f"<div style='display:flex;gap:6px;margin:4px 0 10px 0;'>"
        f"<div style='width:16px;height:16px;border-radius:50%;background:{_prev['a1']};'></div>"
        f"<div style='width:16px;height:16px;border-radius:50%;background:{_prev['a2']};'></div>"
        f"<div style='width:16px;height:16px;border-radius:50%;background:{_prev['a3']};'></div>"
        f"</div>", unsafe_allow_html=True)

    # ---- CURRENCY ----
    st.markdown(f"<div class='sidebar-label'>🔢 Currency</div>", unsafe_allow_html=True)
    curr_keys = list(CURRENCIES.keys())
    chosen_curr = st.selectbox("currency", label_visibility="collapsed", options=curr_keys,
        index=curr_keys.index(st.session_state["currency"]))
    if chosen_curr != st.session_state["currency"]:
        st.session_state["currency"] = chosen_curr
        st.rerun()

    # ---- UPLOAD ----
    st.markdown(f"<div class='sidebar-label'>📁 Upload CSV</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("CSV", type=["csv"], label_visibility="collapsed")

    st.markdown(f"""
    <div style='margin-top:14px;padding:11px 13px;background:#13131f;
    border-radius:10px;border:1px solid {BORDER};font-size:0.76rem;color:{TEXT2};line-height:1.75;'>
        <b style='color:{ACCENT1};'>Supported columns:</b><br>
        • Date (auto-detected)<br>
        • Numeric spend columns<br>
        • Category columns
    </div>
    """, unsafe_allow_html=True)

# ==============================
# MAIN CONTENT
# ==============================

if uploaded_file is None and "df" not in st.session_state:

    st.markdown(f"""
    <div class='hero-wrap'>
        <div class='hero-title'>💸 SpendSense AI</div>
        <p class='hero-sub'>Your AI-powered personal expense analyzer — upload a CSV and get instant charts, trends, and smart financial advice from Groq AI.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<div class='section-title'>🚀 How It Works</div>", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    for col_w, num, title, sub in zip(
        [s1,s2,s3,s4],
        ["1","2","3","4"],
        ["Upload CSV","Explore Charts","Add Groq Key","Get AI Insights"],
        ["Your expense data","Interactive visuals","Free from groq.com","Savings & tips"],
    ):
        with col_w:
            st.markdown(f"""
            <div class='step-card'>
                <div class='step-num'>{num}</div>
                <div style='font-weight:700;color:{TEXT};font-size:0.9rem;'>{title}</div>
                <div style='color:{TEXT2};font-size:0.78rem;margin-top:4px;'>{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='upload-hint'>
        <div style='font-size:3.5rem;margin-bottom:14px;'>📊</div>
        <div style='font-family:Syne,sans-serif;font-size:1.2rem;font-weight:700;color:{TEXT};margin-bottom:8px;'>
            Upload your expense CSV from the sidebar
        </div>
        <div style='color:{TEXT2};font-size:0.88rem;'>Supports any CSV with date, amount, and category columns</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<div class='section-title'>🎲 No CSV? Try Sample Data</div>", unsafe_allow_html=True)
    if st.button("▶ Load Sample Data"):
        np.random.seed(42)
        categories = ["Food","Transport","Shopping","Utilities","Entertainment","Health"]
        months = pd.date_range("2024-01-01", periods=120, freq="W")
        demo_df = pd.DataFrame({
            "Date":     months,
            "Amount":   np.random.randint(500,15000,120),
            "Category": np.random.choice(categories,120),
            "Income":   np.random.randint(30000,60000,120),
            "Savings":  np.random.randint(1000,10000,120),
        })
        st.session_state["df"] = clean_dataframe(demo_df)
        st.rerun()

else:
    if uploaded_file is not None:
        df_raw = pd.read_csv(uploaded_file)
        df     = clean_dataframe(df_raw)
        st.session_state["df"] = df

    df           = st.session_state["df"]
    numeric_cols = get_numeric_cols(df)
    cat_cols     = df.select_dtypes(include=["object"]).columns.tolist()
    summary      = generate_summary_stats(df)

    # ---- AUTO SUMMARY ----
    df_key = f"auto_{df.shape[0]}_{df.shape[1]}"
    if api_key and df_key not in st.session_state:
        with st.spinner("🤖 AI data analyze kar raha hai..."):
            try:
                auto_resp = ask_claude(build_ai_prompt("overview", summary), api_key)
                st.session_state[df_key] = auto_resp
                st.session_state["ai_result_overview"] = auto_resp
            except:
                pass
    if df_key in st.session_state:
        st.markdown(f"""
        <div class='ai-response' style='margin-bottom:18px;border-left:4px solid {ACCENT3};'>
            <div style='font-weight:700;color:{ACCENT3};margin-bottom:8px;font-size:0.95rem;'>
                🤖 Auto AI Summary
            </div>
            {st.session_state[df_key].replace(chr(10), "<br>")}
        </div>
        """, unsafe_allow_html=True)

    # HERO (compact)
    st.markdown(f"""
    <div class='hero-wrap' style='padding:20px 28px;margin-bottom:20px;'>
        <div class='hero-title' style='font-size:1.7rem;'>💸 Personal Expense Intelligence</div>
        <p class='hero-sub'>
            {df.shape[0]} records &nbsp;·&nbsp; {df.shape[1]} columns &nbsp;·&nbsp;
            {len(numeric_cols)} numeric fields &nbsp;·&nbsp;
            {'Year '+str(int(df["Year"].min()))+'–'+str(int(df["Year"].max())) if "Year" in df.columns else ""}
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<div class='section-title'>📈 Dataset Overview</div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    for col_w, (icon, val, lbl, sub) in zip([m1,m2,m3,m4], [
        ("📋", f"{df.shape[0]:,}", "Total Rows",    "Records loaded"),
        ("🗂️", str(df.shape[1]),   "Columns",       "Data fields"),
        ("🔢", str(len(numeric_cols)), "Numeric Cols", "Analyzable"),
        ("📅", f"{int(df['Year'].min())}–{int(df['Year'].max())}" if "Year" in df.columns else "N/A", "Date Range", "Coverage"),
    ]):
        with col_w:
            st.markdown(f"""
            <div class='metric-card'>
                <div style='font-size:1.5rem;margin-bottom:8px;'>{icon}</div>
                <div class='metric-value'>{val}</div>
                <div class='metric-label'>{lbl}</div>
                <div style='font-size:0.78rem;color:{TEXT2};margin-top:4px;'>{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    if numeric_cols:
        st.markdown("<br>", unsafe_allow_html=True)
        stat_cols = st.columns(min(4, len(numeric_cols)))
        for col_widget, col_name in zip(stat_cols, numeric_cols[:4]):
            with col_widget:
                col_total = df[col_name].sum()
                col_avg   = df[col_name].mean()
                col_max   = df[col_name].max()
                st.markdown(f"""
                <div class='metric-card'>
                    <div style='font-size:0.72rem;font-weight:700;color:{TEXT2};
                    text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>{col_name}</div>
                    <div class='metric-value' style='font-size:1.7rem;'>{col_total:,.0f}</div>
                    <div class='metric-label'>Total</div>
                    <div style='margin-top:8px;color:{TEXT2};font-size:0.8rem;'>
                        Avg <span style='color:{ACCENT2};font-weight:600;'>{col_avg:,.0f}</span>
                        &nbsp;·&nbsp;
                        Max <span style='color:{ACCENT1};font-weight:600;'>{col_max:,.0f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ==============================
    # TABS
    # ==============================
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Analytics", "🗃️ Raw Data", "🔬 Deep Dive",
        "🤖 AI Insights", "🎯 Savings Goal", "📈 Forecast & PDF", "💬 Chat"
    ])

    # ---- TAB 1: ANALYTICS ----
    with tab1:
        if numeric_cols:
            st.markdown(f"<div class='section-title'>Distribution Analysis</div>", unsafe_allow_html=True)
            for i in range(0, min(len(numeric_cols), 4), 2):
                row_cols = st.columns(2)
                for j, col_name in enumerate(numeric_cols[i:i+2]):
                    with row_cols[j]:
                        fig = px.histogram(df, x=col_name, nbins=30,
                            title=f"Distribution of {col_name}",
                            color_discrete_sequence=[CHART_COLORS[j]])
                        fig.update_layout(**PLOT_TPL)
                        fig.update_traces(marker_line_width=0.4, marker_line_color=PLOT_BG)
                        st.plotly_chart(fig, use_container_width=True)

        if "Month_Name" in df.columns and numeric_cols:
            st.markdown(f"<div class='section-title'>📅 Monthly Trend</div>", unsafe_allow_html=True)
            selected_metric = st.selectbox("Select metric:", numeric_cols, key="ts_metric")
            month_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                         7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
            monthly = df.groupby("Month")[selected_metric].sum().reset_index().sort_values("Month")
            monthly["Month_Name"] = monthly["Month"].map(month_map)
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=monthly["Month_Name"], y=monthly[selected_metric],
                mode="lines+markers",
                line=dict(color=ACCENT1, width=3, shape="spline"),
                marker=dict(size=9, color=ACCENT2, line=dict(color=ACCENT1, width=2)),
                fill="tozeroy", fillcolor=FILL_COLOR, name=selected_metric
            ))
            fig_line.update_layout(title=f"Monthly {selected_metric} Trend", **PLOT_TPL)
            st.plotly_chart(fig_line, use_container_width=True)

        if cat_cols:
            st.markdown(f"<div class='section-title'>🏷️ Category Breakdown</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            selected_cat = st.selectbox("Select category column:", cat_cols, key="cat_col")
            cat_counts = df[selected_cat].value_counts().reset_index()
            cat_counts.columns = [selected_cat, "Count"]
            with c1:
                fig_bar = px.bar(cat_counts.head(10), x=selected_cat, y="Count",
                    title=f"Top {selected_cat} Categories", color="Count",
                    color_continuous_scale=[PLOT_BG, ACCENT1, ACCENT2])
                fig_bar.update_layout(**PLOT_TPL)
                st.plotly_chart(fig_bar, use_container_width=True)
            with c2:
                fig_pie = px.pie(cat_counts.head(8), values="Count", names=selected_cat,
                    title=f"{selected_cat} Distribution",
                    color_discrete_sequence=CHART_COLORS, hole=0.38)
                fig_pie.update_layout(**PLOT_TPL)
                fig_pie.update_traces(textposition="outside", textinfo="percent+label",
                                      textfont=dict(color=TEXT))
                st.plotly_chart(fig_pie, use_container_width=True)

            if numeric_cols:
                st.markdown(f"<div class='section-title'>💰 Spending by Category</div>", unsafe_allow_html=True)
                selected_num = st.selectbox("Select numeric metric:", numeric_cols, key="cat_num")
                cat_spend = df.groupby(selected_cat)[selected_num].sum().reset_index().sort_values(selected_num, ascending=True)
                fig_h = px.bar(cat_spend, y=selected_cat, x=selected_num, orientation="h",
                    title=f"Total {selected_num} by {selected_cat}", color=selected_num,
                    color_continuous_scale=[PLOT_BG, ACCENT1, ACCENT2])
                fig_h.update_layout(**PLOT_TPL)
                st.plotly_chart(fig_h, use_container_width=True)

        if len(numeric_cols) > 1:
            st.markdown(f"<div class='section-title'>🔗 Correlation Matrix</div>", unsafe_allow_html=True)
            corr_matrix = df[numeric_cols].corr()
            fig_heat = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                color_continuous_scale=[PLOT_BG, ACCENT1, ACCENT2],
                title="Correlation Heatmap")
            fig_heat.update_layout(**PLOT_TPL)
            st.plotly_chart(fig_heat, use_container_width=True)

    # ---- TAB 2: RAW DATA ----
    with tab2:
        st.markdown(f"<div class='section-title'>🗃️ Dataset</div>", unsafe_allow_html=True)
        search = st.text_input("🔍 Filter rows:", placeholder="Type to filter...", key="search")
        if search:
            mask = df.astype(str).apply(lambda row: row.str.contains(search, case=False)).any(axis=1)
            st.dataframe(df[mask], use_container_width=True, height=400)
        else:
            st.dataframe(df, use_container_width=True, height=400)
        st.markdown(f"<div class='section-title'>📊 Statistical Summary</div>", unsafe_allow_html=True)
        st.dataframe(df[numeric_cols].describe().round(2), use_container_width=True)
        csv_buf = io.StringIO()
        df.to_csv(csv_buf, index=False)
        st.download_button("⬇️ Download Cleaned Data", csv_buf.getvalue().encode(),
            file_name=f"spendsense_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")

    # ---- TAB 3: DEEP DIVE ----
    with tab3:
        st.markdown(f"<div class='section-title'>🔬 Custom Analysis</div>", unsafe_allow_html=True)
        if len(numeric_cols) >= 2:
            c1, c2 = st.columns(2)
            with c1: x_col = st.selectbox("X Axis:", numeric_cols, key="x_col")
            with c2: y_col = st.selectbox("Y Axis:", numeric_cols, index=min(1, len(numeric_cols)-1), key="y_col")
            color_col = st.selectbox("Color by (optional):", ["None"] + cat_cols, key="color_col")
            color_arg = None if color_col == "None" else color_col
            fig_scatter = px.scatter(df, x=x_col, y=y_col, color=color_arg,
                title=f"{x_col} vs {y_col}", trendline="ols",
                color_discrete_sequence=CHART_COLORS, opacity=0.75)
            fig_scatter.update_layout(**PLOT_TPL)
            st.plotly_chart(fig_scatter, use_container_width=True)

        if cat_cols and numeric_cols:
            st.markdown(f"<div class='section-title'>📦 Distribution by Category</div>", unsafe_allow_html=True)
            bc1, bc2 = st.columns(2)
            with bc1: box_cat = st.selectbox("Category:", cat_cols, key="box_cat")
            with bc2: box_num = st.selectbox("Numeric:", numeric_cols, key="box_num")
            fig_box = px.box(df, x=box_cat, y=box_num,
                title=f"{box_num} by {box_cat}", color=box_cat,
                color_discrete_sequence=CHART_COLORS)
            fig_box.update_layout(**PLOT_TPL)
            st.plotly_chart(fig_box, use_container_width=True)

    # ---- TAB 4: AI INSIGHTS ----
    with tab4:
        st.markdown(f"""
        <div class='ai-response' style='margin-bottom:20px;'>
            <div style='font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;
            color:{ACCENT1};margin-bottom:8px;'>🤖 Groq AI Financial Advisor</div>
            <span style='color:{TEXT2};font-size:0.88rem;'>
            Enter your Groq API key in the sidebar → select analysis type → click Generate.
            </span>
        </div>
        """, unsafe_allow_html=True)

        analysis_options = {
            "📋 Dataset Overview":    "overview",
            "💰 Savings Tips":        "savings",
            "📈 Income Growth Ideas": "income",
            "⚠️ Spending Red Flags":  "warnings",
            "📅 Monthly Budget Plan": "monthly",
            "❓ Ask a Custom Question": "custom",
        }
        selected_analysis = st.selectbox("Choose analysis type:", list(analysis_options.keys()))
        analysis_key = analysis_options[selected_analysis]

        extra_context = ""
        if analysis_key == "custom":
            extra_context = st.text_area("Your question:", height=100,
                placeholder="e.g. Which category is draining my budget?")
        elif analysis_key == "monthly":
            if "Month" in df.columns and numeric_cols:
                extra_context = df.groupby("Month")[numeric_cols].sum().to_string()

        if st.button("🚀 Generate AI Insight", use_container_width=True):
            if not api_key:
                st.error("⚠️ Please enter your Groq API key in the sidebar first.")
            else:
                with st.spinner("🤔 Groq AI is analyzing your financial data..."):
                    try:
                        prompt   = build_ai_prompt(analysis_key, summary, extra_context)
                        response = ask_claude(prompt, api_key)
                        st.session_state[f"ai_result_{analysis_key}"] = response
                    except Exception as e:
                        st.error(f"API Error: {str(e)}")

        if f"ai_result_{analysis_key}" in st.session_state:
            st.markdown(f"<div class='section-title'>💡 AI Analysis</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='ai-response'>
                <div style='font-weight:700;color:{ACCENT1};margin-bottom:10px;'>{selected_analysis}</div>
                {st.session_state[f'ai_result_{analysis_key}'].replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)
            st.download_button("⬇️ Download Insight",
                st.session_state[f"ai_result_{analysis_key}"],
                file_name=f"insight_{analysis_key}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain")

        st.markdown("---")
        st.markdown(f"<div class='section-title'>⚡ Quick Insights</div>", unsafe_allow_html=True)
        qc1, qc2, qc3 = st.columns(3)
        quick_map = {
            "💸 Spending Alert": "warnings",
            "🎯 Savings Tips":   "savings",
            "🚀 Income Ideas":   "income",
        }
        for col_w, (label, key) in zip([qc1,qc2,qc3], quick_map.items()):
            with col_w:
                if st.button(label, key=f"quick_{key}", use_container_width=True):
                    if not api_key:
                        st.warning("Add Groq API key in sidebar!")
                    else:
                        with st.spinner("Analyzing..."):
                            try:
                                result = ask_claude(build_ai_prompt(key, summary), api_key)
                                st.session_state[f"quick_result_{key}"] = result
                            except Exception as e:
                                st.error(str(e))

        for key in ["warnings","savings","income"]:
            if f"quick_result_{key}" in st.session_state:
                icons = {"warnings":"⚠️","savings":"💰","income":"🚀"}
                st.markdown(f"""
                <div class='ai-response' style='margin-top:10px;'>
                    <div style='font-weight:700;color:{ACCENT1};margin-bottom:8px;'>
                        {icons[key]} {key.title()} Analysis
                    </div>
                    {st.session_state[f'quick_result_{key}'].replace(chr(10),'<br>')}
                </div>
                """, unsafe_allow_html=True)

    # ---- TAB 5: SAVINGS GOAL ----
    with tab5:
        st.markdown(f"<div class='section-title'>🎯 Savings Goal Tracker</div>", unsafe_allow_html=True)
        sc1, sc2 = st.columns(2)
        with sc1:
            goal_name   = st.text_input("Goal Name", placeholder="e.g. New Laptop, Trip to Dubai")
            goal_amount = st.number_input(f"Target Amount ({CURR_SYMBOL})", min_value=1000, value=50000, step=1000)
        with sc2:
            if numeric_cols:
                savings_col  = st.selectbox("Savings Column:", numeric_cols, key="goal_col")
                saved_so_far = st.number_input(f"Already Saved ({CURR_SYMBOL})", min_value=0, value=0, step=500)

        if st.button("📊 Calculate Progress", use_container_width=True):
            total_saved = df[savings_col].sum() + saved_so_far if numeric_cols else saved_so_far
            remaining   = max(goal_amount - total_saved, 0)
            pct         = min((total_saved / goal_amount) * 100, 100)
            monthly_avg = df[savings_col].mean() if numeric_cols else 0
            months_left = int(remaining / monthly_avg) if monthly_avg > 0 else 999
            bar_color   = ACCENT3 if pct >= 75 else ACCENT2 if pct >= 40 else ACCENT1
            st.markdown(f"""
            <div class='metric-card' style='margin-top:16px;'>
                <div style='font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;color:{TEXT};margin-bottom:16px;'>
                    🎯 {goal_name if goal_name else "My Goal"}
                </div>
                <div style='display:flex;justify-content:space-between;margin-bottom:8px;'>
                    <span style='color:{TEXT2};font-size:0.85rem;'>Progress</span>
                    <span style='font-weight:700;color:{bar_color};font-size:0.95rem;'>{pct:.1f}%</span>
                </div>
                <div style='background:{BG3};border-radius:50px;height:14px;overflow:hidden;margin-bottom:16px;'>
                    <div style='width:{pct}%;height:100%;background:linear-gradient(90deg,{ACCENT1},{bar_color});border-radius:50px;'></div>
                </div>
                <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;'>
                    <div style='text-align:center;background:{BG3};border-radius:10px;padding:12px;'>
                        <div style='font-size:1.2rem;font-weight:800;color:{ACCENT2};'>{CURR_SYMBOL} {total_saved:,.0f}</div>
                        <div style='font-size:0.72rem;color:{TEXT2};margin-top:2px;'>SAVED</div>
                    </div>
                    <div style='text-align:center;background:{BG3};border-radius:10px;padding:12px;'>
                        <div style='font-size:1.2rem;font-weight:800;color:{ACCENT1};'>{CURR_SYMBOL} {remaining:,.0f}</div>
                        <div style='font-size:0.72rem;color:{TEXT2};margin-top:2px;'>REMAINING</div>
                    </div>
                    <div style='text-align:center;background:{BG3};border-radius:10px;padding:12px;'>
                        <div style='font-size:1.2rem;font-weight:800;color:{ACCENT3};'>{months_left if months_left < 999 else "N/A"}</div>
                        <div style='font-size:0.72rem;color:{TEXT2};margin-top:2px;'>MONTHS LEFT</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if pct >= 100:
                st.success("🎉 Goal Achieved! Mubarak ho!")
            elif pct >= 75:
                st.info(f"🔥 Almost there! Sirf {CURR_SYMBOL} {remaining:,.0f} aur chahiye!")
            elif monthly_avg > 0:
                st.info(f"📅 Current rate pe approx {months_left} months mein goal achieve hoga.")

        st.markdown(f"<div class='section-title'>📋 Quick Goals Overview</div>", unsafe_allow_html=True)
        preset_goals = {"Emergency Fund":150000,"New Phone":80000,"Vacation":100000,"New Laptop":120000}
        if numeric_cols:
            total_saved_all = df[savings_col].sum()
            gcols = st.columns(2)
            for i, (gname, gtarget) in enumerate(preset_goals.items()):
                gpct   = min((total_saved_all / gtarget) * 100, 100)
                gcolor = ACCENT3 if gpct >= 75 else ACCENT2 if gpct >= 40 else ACCENT1
                with gcols[i % 2]:
                    st.markdown(f"""
                    <div class='metric-card' style='margin-bottom:10px;'>
                        <div style='font-size:0.88rem;font-weight:600;color:{TEXT};margin-bottom:8px;'>{gname}</div>
                        <div style='background:{BG3};border-radius:50px;height:8px;overflow:hidden;margin-bottom:6px;'>
                            <div style='width:{gpct}%;height:100%;background:linear-gradient(90deg,{ACCENT1},{gcolor});border-radius:50px;'></div>
                        </div>
                        <div style='display:flex;justify-content:space-between;font-size:0.78rem;'>
                            <span style='color:{gcolor};font-weight:600;'>{gpct:.0f}%</span>
                            <span style='color:{TEXT2};'>Target: {CURR_SYMBOL} {gtarget:,}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # ---- TAB 6: FORECAST + PDF ----
    with tab6:
        st.markdown(f"<div class='section-title'>📈 Spending Forecast</div>", unsafe_allow_html=True)
        if numeric_cols and "Month" in df.columns:
            fc1, fc2 = st.columns(2)
            with fc1: forecast_col = st.selectbox("Column to forecast:", numeric_cols, key="fc_col")
            with fc2: forecast_months = st.slider("Months ahead:", 1, 6, 3)
            monthly_data = df.groupby("Month")[forecast_col].sum().reset_index().sort_values("Month")
            month_map2   = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                            7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
            monthly_data["Month_Name"] = monthly_data["Month"].map(month_map2)
            if len(monthly_data) >= 2:
                x      = np.arange(len(monthly_data))
                y      = monthly_data[forecast_col].values
                coeffs = np.polyfit(x, y, 1)
                trend  = np.poly1d(coeffs)
                future_x      = np.arange(len(monthly_data), len(monthly_data) + forecast_months)
                future_y      = trend(future_x)
                last_month    = monthly_data["Month"].iloc[-1]
                future_months = [(last_month + i) % 12 + 1 for i in range(1, forecast_months + 1)]
                future_names  = [month_map2[m] for m in future_months]
                fig_fc = go.Figure()
                fig_fc.add_trace(go.Scatter(x=monthly_data["Month_Name"], y=monthly_data[forecast_col],
                    mode="lines+markers", name="Actual", line=dict(color=ACCENT2, width=3),
                    marker=dict(size=8, color=ACCENT2)))
                fig_fc.add_trace(go.Scatter(x=future_names, y=future_y,
                    mode="lines+markers", name="Forecast", line=dict(color=ACCENT1, width=3, dash="dot"),
                    marker=dict(size=8, color=ACCENT1, symbol="diamond")))
                fig_fc.update_layout(title=f"{forecast_col} — {forecast_months} Month Forecast", **PLOT_TPL)
                st.plotly_chart(fig_fc, use_container_width=True)
                avg_actual   = y.mean()
                avg_forecast = future_y.mean()
                trend_dir    = "📈 Increasing" if coeffs[0] > 0 else "📉 Decreasing"
                change_pct   = ((avg_forecast - avg_actual) / avg_actual * 100) if avg_actual else 0
                fs1, fs2, fs3 = st.columns(3)
                for cw, (icon, val, lbl, clr) in zip([fs1,fs2,fs3], [
                    ("📊", f"{CURR_SYMBOL} {avg_actual:,.0f}",   "Avg Monthly (Actual)",   ACCENT2),
                    ("🔮", f"{CURR_SYMBOL} {avg_forecast:,.0f}", "Avg Monthly (Forecast)", ACCENT1),
                    ("📉", f"{change_pct:+.1f}%",     "Expected Change",        ACCENT3 if change_pct < 0 else "#f87171"),
                ]):
                    with cw:
                        st.markdown(f"""
                        <div class='metric-card' style='text-align:center;'>
                            <div style='font-size:1.5rem;margin-bottom:8px;'>{icon}</div>
                            <div style='font-size:1.4rem;font-weight:800;color:{clr};'>{val}</div>
                            <div class='metric-label'>{lbl}</div>
                        </div>
                        """, unsafe_allow_html=True)
                st.markdown(f"""
                <div class='ai-response' style='margin-top:16px;'>
                    <div style='font-weight:700;color:{ACCENT1};margin-bottom:8px;'>📊 Trend Summary</div>
                    <b>Direction:</b> {trend_dir} &nbsp;·&nbsp;
                    <b>Monthly Change:</b> {CURR_SYMBOL} {abs(coeffs[0]):,.0f}/month &nbsp;·&nbsp;
                    <b>Next Month Est.:</b> {CURR_SYMBOL} {trend(len(monthly_data)):,.0f}
                </div>
                """, unsafe_allow_html=True)
                if api_key:
                    if st.button("🤖 AI Forecast Analysis", use_container_width=True):
                        with st.spinner("Generating insights..."):
                            try:
                                fc_prompt = (f"Monthly {forecast_col} data: {dict(zip(monthly_data['Month_Name'], monthly_data[forecast_col].round(0)))}. "
                                    f"Trend: {trend_dir}. Next {forecast_months} months: {dict(zip(future_names, future_y.round(0)))}. "
                                    f"Give 3 insights in bullet points.")
                                fc_resp = ask_claude(fc_prompt, api_key)
                                st.session_state["fc_ai"] = fc_resp
                            except Exception as e:
                                st.error(str(e))
                if "fc_ai" in st.session_state:
                    st.markdown(f"""
                    <div class='ai-response' style='margin-top:10px;'>
                        <div style='font-weight:700;color:{ACCENT1};margin-bottom:8px;'>🤖 AI Forecast Insights</div>
                        {st.session_state["fc_ai"].replace(chr(10), "<br>")}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📅 Forecast ke liye kam az kam 2 months ka data chahiye.")
        else:
            st.info("📅 Date column wala CSV upload karo forecast ke liye.")

        # PDF EXPORT
        st.markdown(f"<div class='section-title'>🖨️ Export PDF Report</div>", unsafe_allow_html=True)
        if st.button("📄 Generate PDF Report", use_container_width=True):
            if not PDF_AVAILABLE:
                st.error("PDF ke liye run karo: pip install fpdf2")
            else:
                try:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    pdf.set_font("Helvetica", "B", 22)
                    pdf.set_text_color(99, 102, 241)
                    pdf.cell(0, 14, "SpendSense AI - Expense Report", ln=True, align="C")
                    pdf.set_font("Helvetica", "", 10)
                    pdf.set_text_color(120, 120, 150)
                    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}", ln=True, align="C")
                    pdf.ln(4)
                    pdf.set_draw_color(99, 102, 241)
                    pdf.set_line_width(0.8)
                    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                    pdf.ln(6)
                    pdf.set_font("Helvetica", "B", 13)
                    pdf.set_text_color(30, 30, 60)
                    pdf.cell(0, 10, "Dataset Overview", ln=True)
                    pdf.set_font("Helvetica", "", 10)
                    pdf.set_text_color(60, 60, 80)
                    pdf.cell(0, 7, f"Records: {df.shape[0]}  |  Columns: {df.shape[1]}  |  Numeric: {len(numeric_cols)}", ln=True)
                    if "Year" in df.columns:
                        pdf.cell(0, 7, f"Date Range: {int(df['Year'].min())} - {int(df['Year'].max())}", ln=True)
                    pdf.ln(4)
                    pdf.set_font("Helvetica", "B", 13)
                    pdf.set_text_color(30, 30, 60)
                    pdf.cell(0, 10, "Numeric Summary", ln=True)
                    pdf.set_font("Helvetica", "", 10)
                    pdf.set_text_color(60, 60, 80)
                    for col in numeric_cols[:6]:
                        pdf.cell(0, 7, f"{col}: Total={df[col].sum():,.0f}  Avg={df[col].mean():,.0f}  Max={df[col].max():,.0f}", ln=True)
                    pdf.ln(4)
                    if cat_cols:
                        pdf.set_font("Helvetica", "B", 13)
                        pdf.set_text_color(30, 30, 60)
                        pdf.cell(0, 10, "Category Breakdown", ln=True)
                        for col in cat_cols[:2]:
                            pdf.set_font("Helvetica", "B", 10)
                            pdf.set_text_color(60, 60, 80)
                            pdf.cell(0, 7, f"{col}:", ln=True)
                            pdf.set_font("Helvetica", "", 10)
                            for val, cnt in df[col].value_counts().head(5).items():
                                pdf.cell(0, 6, f"   {val}: {cnt} records", ln=True)
                        pdf.ln(4)
                    ai_sections = {"overview":"Overview","savings":"Savings Tips","income":"Income Ideas","warnings":"Red Flags"}
                    if any(f"ai_result_{k}" in st.session_state for k in ai_sections):
                        pdf.set_font("Helvetica", "B", 13)
                        pdf.set_text_color(30, 30, 60)
                        pdf.cell(0, 10, "AI Insights", ln=True)
                        for k, title in ai_sections.items():
                            if f"ai_result_{k}" in st.session_state:
                                pdf.set_font("Helvetica", "B", 11)
                                pdf.set_text_color(99, 102, 241)
                                pdf.cell(0, 8, title, ln=True)
                                pdf.set_font("Helvetica", "", 9)
                                pdf.set_text_color(60, 60, 80)
                                txt = st.session_state[f"ai_result_{k}"].encode("latin-1","replace").decode("latin-1")
                                pdf.multi_cell(0, 6, txt)
                                pdf.ln(2)
                    pdf.set_y(-18)
                    pdf.set_font("Helvetica", "I", 8)
                    pdf.set_text_color(150, 150, 170)
                    pdf.cell(0, 8, "Generated by SpendSense AI  |  Powered by Groq", align="C")
                    pdf_buf = io.BytesIO()
                    pdf_buf.write(pdf.output())
                    pdf_buf.seek(0)
                    st.success("✅ PDF ready!")
                    st.download_button("⬇️ Download PDF Report", pdf_buf,
                        file_name=f"spendsense_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf", use_container_width=True)
                except Exception as e:
                    st.error(f"PDF Error: {str(e)}")

    # ---- TAB 7: CHAT ----
    with tab7:
        st.markdown(f"<div class='section-title'>💬 Chat with Your Data</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='ai-response' style='margin-bottom:16px;'>
            <div style='font-weight:700;color:{ACCENT1};margin-bottom:6px;'>🤖 AI Data Assistant</div>
            <span style='color:{TEXT2};font-size:0.87rem;'>
            Apne expense data ke baare mein koi bhi sawal seedha poochein — Urdu, Hindi ya English mein.
            </span>
        </div>
        """, unsafe_allow_html=True)

        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        for msg in st.session_state["chat_history"]:
            is_ai   = msg["role"] == "assistant"
            bg      = BG3 if is_ai else BG2
            icon    = "🤖" if is_ai else "👤"
            label   = "AI" if is_ai else "You"
            clr     = ACCENT1 if is_ai else ACCENT2
            radius  = "14px 14px 14px 4px" if is_ai else "14px 14px 4px 14px"
            justify = "flex-start" if is_ai else "flex-end"
            st.markdown(f"""
            <div style='display:flex;justify-content:{justify};margin:8px 0;'>
                <div style='max-width:82%;background:{bg};border:1px solid {BORDER};
                border-radius:{radius};padding:12px 16px;'>
                    <div style='font-size:0.74rem;font-weight:700;color:{clr};margin-bottom:5px;'>{icon} {label}</div>
                    <div style='font-size:0.9rem;color:{TEXT};line-height:1.65;'>
                        {msg["content"].replace(chr(10), "<br>")}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"<div style='color:{TEXT2};font-size:0.8rem;margin:8px 0 4px;'>💡 Quick questions:</div>", unsafe_allow_html=True)
        qp1, qp2, qp3 = st.columns(3)
        quick_prompts = {
            "Sabse bada kharcha?": "Mera sabse bada kharcha kaunsi category mein hai?",
            "Best savings month?": "Kis month mein maine sabse zyada save kiya?",
            "Budget suggestion?":  "Mujhe ek simple monthly budget suggest karo.",
        }
        for col_q, (label_q, full_q) in zip([qp1,qp2,qp3], quick_prompts.items()):
            with col_q:
                if st.button(label_q, key=f"qp_{label_q}", use_container_width=True):
                    st.session_state["prefill_chat"] = full_q
                    st.rerun()

        prefill    = st.session_state.pop("prefill_chat", "")
        chat_input = st.text_input("Message:", value=prefill,
            placeholder="Koi bhi sawal poochein apne data ke baare mein...",
            label_visibility="collapsed", key="chat_input_box")

        col_send, col_clear = st.columns([5,1])
        with col_send:
            send_btn = st.button("📤 Send", use_container_width=True)
        with col_clear:
            if st.button("🗑️", use_container_width=True, help="Clear chat"):
                st.session_state["chat_history"] = []
                st.rerun()

        if send_btn and chat_input.strip():
            if not api_key:
                st.error("⚠️ Groq API key sidebar mein daalen.")
            else:
                lang      = st.session_state.get("ai_lang", "English")
                lang_note = " Reply in Urdu or Roman Urdu." if "Urdu" in lang else " Reply in Hindi." if "Hindi" in lang else ""
                cat_str2  = " ".join([f"{k}:{list(v.items())[:3]}" for k,v in list(summary["cat_summary"].items())[:2]])
                sys_msg   = (f"You are a friendly personal finance assistant. "
                    f"User's data: {summary['rows']} rows, cols: {', '.join(summary['numeric_cols'][:4])}, "
                    f"categories: {cat_str2}. Answer concisely.{lang_note}")
                st.session_state["chat_history"].append({"role":"user","content":chat_input.strip()})
                with st.spinner("Soch raha hoon..."):
                    try:
                        client  = Groq(api_key=api_key)
                        model   = st.session_state.get("groq_model","llama-3.1-8b-instant")
                        history = [{"role":"system","content":sys_msg}]
                        for m in st.session_state["chat_history"][-8:]:
                            history.append({"role":m["role"],"content":m["content"]})
                        resp  = client.chat.completions.create(model=model, messages=history, max_tokens=600)
                        reply = resp.choices[0].message.content
                        st.session_state["chat_history"].append({"role":"assistant","content":reply})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")