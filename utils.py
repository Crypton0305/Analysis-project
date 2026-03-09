import pandas as pd
import numpy as np
import streamlit as st
from groq import Groq

# ==============================
# DATA LOGIC
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
    skip = ["Year", "Month", "Day", "Row_Total", "Row_Mean"]
    return [c for c in df.select_dtypes(include=np.number).columns if c not in skip]

def generate_summary_stats(df):
    numeric_cols = get_numeric_cols(df)
    cat_cols     = df.select_dtypes(include=["object"]).columns.tolist()
    summary = {
        "rows":         len(df),
        "columns":      len(df.columns),
        "numeric_cols": numeric_cols,
        "cat_cols":     cat_cols,
        "describe":     df[numeric_cols].describe().to_string() if numeric_cols else "N/A",
        "corr":         df[numeric_cols].corr().to_string() if len(numeric_cols) > 1 else "N/A",
        "cat_summary":  {}
    }
    for col in cat_cols[:3]:
        summary["cat_summary"][col] = df[col].value_counts().head(5).to_dict()
    return summary

# ==============================
# AI LOGIC
# ==============================

def ask_groq(prompt, api_key):
    client = Groq(api_key=api_key)
    model  = st.session_state.get("groq_model", "llama-3.1-8b-instant")
    resp   = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
    )
    return resp.choices[0].message.content

def chat_with_groq(api_key, messages):
    client = Groq(api_key=api_key)
    model  = st.session_state.get("groq_model", "llama-3.1-8b-instant")
    resp   = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=600,
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
    lang_note = " Respond in Urdu or Roman Urdu. Be friendly." if "Urdu" in lang else ""

    prompts = {
        "overview": base + "Give a 3-sentence overview of this spending data and financial health." + lang_note,
        "savings":  base + "Give 4 specific savings tips. Use bullet points. Be concise." + lang_note,
        "income":   base + "Suggest 4 ways to grow income or optimize finances. Bullet points." + lang_note,
        "warnings": base + "List 3 spending red flags from this data. Be direct and brief." + lang_note,
        "monthly":  base + "Analyze monthly pattern. Recommend a budget split. Keep it short." + lang_note,
        "custom":   base + f"Answer this: {extra_short}" + lang_note,
    }
    return prompts.get(analysis_type, prompts["overview"])

def build_forecast_prompt(forecast_col, monthly_data, trend_dir, coeffs, forecast_months, future_names, future_y):
    return (
        f"Monthly {forecast_col} data: {dict(zip(monthly_data['Month_Name'], monthly_data[forecast_col].round(0)))}. "
        f"Trend: {trend_dir}, Rs {coeffs[0]:,.0f}/month. "
        f"Next {forecast_months} months forecast: {dict(zip(future_names, future_y.round(0)))}. "
        f"Give 3 specific insights and recommendations in bullet points."
    )


def get_outliers(df, col):
    q1  = df[col].quantile(0.25)
    q3  = df[col].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outliers = df[(df[col] < lower) | (df[col] > upper)]
    return outliers, lower, upper

def generate_pdf(df, numeric_cols, cat_cols):
    from fpdf import FPDF
    from datetime import datetime
    import io

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

    ai_sections = {"overview": "Overview", "savings": "Savings Tips", "income": "Income Ideas", "warnings": "Red Flags"}
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
                txt = st.session_state[f"ai_result_{k}"].encode("latin-1", "replace").decode("latin-1")
                pdf.multi_cell(0, 6, txt)
                pdf.ln(2)

    pdf.set_y(-18)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 170)
    pdf.cell(0, 8, "Generated by SpendSense AI  |  Powered by Groq", align="C")

    pdf_buf = io.BytesIO()
    pdf_buf.write(pdf.output())
    pdf_buf.seek(0)
    return pdf_buf