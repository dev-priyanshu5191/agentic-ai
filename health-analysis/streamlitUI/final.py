import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import re
from PIL import Image


load_dotenv()

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BloodWork Analyzer",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── App Background ── */
.stApp {
    background: #f7f4ef;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #1a1a2e !important;
    border-right: 1px solid #2d2d4e;
}
[data-testid="stSidebar"] * {
    color: #e8e4dc !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stTextInput label {
    color: #a09898 !important;
    font-size: 11px !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #e8e4dc !important;
}

/* ── Header ── */
.hero-header {
    background: #1a1a2e;
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.8rem;
    color: #e8e4dc;
    margin: 0;
    line-height: 1.1;
}
.hero-subtitle {
    color: #7c6f8e;
    font-size: 0.95rem;
    margin-top: 0.4rem;
    font-weight: 300;
    letter-spacing: 0.04em;
}
.hero-badge {
    background: #c8a97e;
    color: #1a1a2e;
    padding: 8px 20px;
    border-radius: 100px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* ── Section Headers ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #8a7d6e;
    margin-bottom: 1rem;
    margin-top: 2rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #d9d2c7;
}

/* ── Metric Cards ── */
.metric-card {
    background: white;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    border: 1px solid #ede8e0;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: #c8a97e;
    border-radius: 4px 0 0 4px;
}
.metric-label {
    font-size: 0.75rem;
    color: #9e9083;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.metric-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #1a1a2e;
    line-height: 1.2;
    margin-top: 4px;
}
.metric-unit {
    font-size: 0.8rem;
    color: #9e9083;
    margin-left: 4px;
}
.metric-status {
    margin-top: 8px;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 3px 10px;
    border-radius: 100px;
    display: inline-block;
}
.status-normal { background: #eaf3de; color: #3b6d11; }
.status-high   { background: #fcebeb; color: #a32d2d; }
.status-low    { background: #faeeda; color: #854f0b; }

/* ── Summary Cards ── */
.summary-card {
    background: white;
    border-radius: 14px;
    padding: 1.6rem;
    border: 1px solid #ede8e0;
    height: 100%;
}
.summary-icon {
    width: 44px; height: 44px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    margin-bottom: 1rem;
}
.summary-card h4 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.15rem;
    color: #1a1a2e;
    margin: 0 0 0.5rem;
}
.summary-card p {
    font-size: 0.88rem;
    color: #6b6057;
    line-height: 1.6;
    margin: 0;
}

/* ── Diet Plan ── */
.diet-card {
    background: white;
    border-radius: 14px;
    padding: 1.5rem;
    border: 1px solid #ede8e0;
    margin-bottom: 1rem;
}
.meal-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #f0ebe4;
}
.meal-time {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #8a7d6e;
}
.meal-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.2rem;
    color: #1a1a2e;
}
.food-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px dashed #f0ebe4;
    font-size: 0.88rem;
    color: #4a3f35;
}
.food-item:last-child { border: none; }
.food-cal {
    font-size: 0.78rem;
    color: #9e9083;
    font-weight: 500;
}

/* ── Health Score Ring ── */
.score-wrapper {
    background: #1a1a2e;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    color: #e8e4dc;
}
.score-label {
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #7c6f8e;
    margin-bottom: 0.5rem;
}
.score-value {
    font-family: 'DM Serif Display', serif;
    font-size: 3.5rem;
    color: #c8a97e;
    line-height: 1;
}
.score-grade {
    font-size: 0.9rem;
    color: #a09898;
    margin-top: 0.4rem;
}

/* ── Alert Boxes ── */
.alert-box {
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-size: 0.88rem;
    line-height: 1.6;
    margin-bottom: 0.75rem;
    border-left: 4px solid;
}
.alert-warn { background: #faeeda; border-color: #ef9f27; color: #633806; }
.alert-danger { background: #fcebeb; border-color: #e24b4a; color: #501313; }
.alert-good { background: #eaf3de; border-color: #639922; color: #173404; }

/* ── Upload Area ── */
.upload-hint {
    background: white;
    border: 2px dashed #d9d2c7;
    border-radius: 14px;
    padding: 2.5rem;
    text-align: center;
    color: #8a7d6e;
    font-size: 0.9rem;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: white;
    border-radius: 10px;
    padding: 4px;
    border: 1px solid #ede8e0;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 500;
    color: #8a7d6e;
    padding: 8px 20px;
}
.stTabs [aria-selected="true"] {
    background: #1a1a2e !important;
    color: #e8e4dc !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding: 1.5rem 0 0;
}

/* ── Buttons ── */
.stButton > button {
    background: #1a1a2e;
    color: #e8e4dc;
    border: none;
    border-radius: 10px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.9rem;
    padding: 0.7rem 2rem;
    letter-spacing: 0.02em;
    transition: background 0.2s;
}
.stButton > button:hover {
    background: #2d2d4e;
    color: #e8e4dc;
}

/* ── Inputs ── */
.stNumberInput input, .stTextInput input, .stSelectbox select {
    border-radius: 8px !important;
    border: 1px solid #d9d2c7 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Plotly chart background ── */
.js-plotly-plot .plotly { background: transparent !important; }

/* ── Scroll Box ── */
.scroll-box {
    height: 300px;
    overflow-y: auto;
    padding: 1rem;
    border: 1px solid #d9d2c7;
    border-radius: 10px;
    background-color: #f9f7f4;
    font-size: 0.9rem;
    line-height: 1.6;
    color: #4a3f35;
}

/* ── Divider ── */
hr { border-color: #d9d2c7; opacity: 0.5; }
</style>
""", unsafe_allow_html=True)


# ─── Initialize LLM ─────────────────────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(model="gemma-4-31b-it")


# ─── File Processing Functions ──────────────────────────────────────────────────
@st.cache_resource
def get_tesseract_path():
    """Get Tesseract path - adjust if needed for your system"""
    try:
        return pytesseract.pytesseract.pytesseract_cmd
    except:
        return None


def extract_text_from_image(image_file):
    """Extract text from image using OCR (Tesseract)"""
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        st.warning(f"⚠️ OCR extraction failed: {str(e)}\nPlease ensure Tesseract is installed.")
        return None


def extract_text_from_file(uploaded_file):
    """Extract text from various file formats"""
    file_ext = uploaded_file.name.split('.')[-1].lower()
    
    try:
        if file_ext in ['txt', 'text']:
            return uploaded_file.read().decode('utf-8')
        elif file_ext in ['png', 'jpg', 'jpeg']:
            return extract_text_from_image(uploaded_file)
        elif file_ext == 'pdf':
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
            except ImportError:
                st.warning("⚠️ PyPDF2 not installed. Please install it: pip install PyPDF2")
                return None
        else:
            return None
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None


def parse_report_with_ai(report_text):
    """Use AI to extract patient info and blood parameters from report"""
    extraction_prompt = f"""
You are a medical data extraction assistant. From the blood report below, extract:

1. Patient Information: name, age, gender
2. All test values with their status (HIGH, LOW, or NORMAL based on reference ranges)

Format your response as JSON:
{{
    "patient": {{"name": "...", "age": ..., "gender": "..."}},
    "tests": [
        {{"name": "test_name", "value": number, "unit": "...", "status": "HIGH/LOW/NORMAL", "reference": "range"}}
    ]
}}

Blood Report:
{report_text}
"""
    try:
        response = llm.invoke(extraction_prompt)
        # Try to parse JSON from response
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    return None


def generate_health_analysis(extracted_values_text):
    """Generate health summary and diet plan using AI"""
    diet_prompt = f"""
You are a clinical nutritionist specializing in Indian dietary habits.

Based on the blood work analysis below, provide a response with these two sections clearly separated by "---SECTION_BREAK---":

HEALTH SUMMARY (4-5 lines):
Explain the patient's condition in simple, non-technical language.

---SECTION_BREAK---

INDIAN DIET PLAN:
List foods to eat more of and foods to avoid, using commonly available Indian foods.
Keep it practical and concise.

Blood Work Analysis:
{extracted_values_text}
"""
    try:
        response = llm.invoke(diet_prompt)
        parts = response.text.split("---SECTION_BREAK---")
        health_summary = parts[0].replace("HEALTH SUMMARY", "").strip() if len(parts) > 0 else ""
        diet_plan = parts[1].strip() if len(parts) > 1 else ""
        return health_summary, diet_plan
    except Exception as e:
        st.error(f"Error generating analysis: {str(e)}")
        return "", ""


# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1.5rem 0 2rem;">
        <div style="font-size: 2.2rem; margin-bottom: 0.4rem;">🩸</div>
        <div style="font-family:'DM Serif Display',serif; font-size:1.3rem; color:#e8e4dc;">BloodWork AI</div>
        <div style="font-size:0.75rem; color:#7c6f8e; margin-top:4px;">Smart health analyzer</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Patient Profile**")
    patient_name = st.text_input("Full Name", placeholder="e.g. Arjun Sharma")
    col_a, col_b = st.columns(2)
    with col_a:
        age = st.number_input("Age", 1, 120, 35)
    with col_b:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])

    weight = st.number_input("Weight (kg)", 20.0, 300.0, 70.0, step=0.5)
    height = st.number_input("Height (cm)", 100.0, 250.0, 170.0, step=0.5)

    bmi = weight / ((height / 100) ** 2)
    if bmi < 18.5:
        bmi_status = "Underweight"
    elif bmi < 25:
        bmi_status = "Normal"
    elif bmi < 30:
        bmi_status = "Overweight"
    else:
        bmi_status = "Obese"

    st.markdown(f"""
    <div style="background:#2d2d4e; border-radius:10px; padding:1rem; margin:1rem 0; text-align:center;">
        <div style="font-size:0.7rem; color:#7c6f8e; text-transform:uppercase; letter-spacing:0.1em;">BMI</div>
        <div style="font-family:'DM Serif Display',serif; font-size:2rem; color:#c8a97e;">{bmi:.1f}</div>
        <div style="font-size:0.8rem; color:#a09898;">{bmi_status}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Report Date**")
    report_date = st.date_input("Report Date", date.today(), label_visibility="collapsed")

    st.markdown("**Dietary Preference**")
    diet_pref = st.selectbox("Dietary Preference", ["No Restriction", "Vegetarian", "Vegan", "Diabetic-Friendly", "Low-Sodium", "Heart-Healthy"], label_visibility="collapsed")

    st.markdown("**Allergies / Avoid**")
    allergies = st.multiselect("Allergies / Avoid", ["Dairy", "Gluten", "Nuts", "Seafood", "Eggs", "Soy"], label_visibility="collapsed")


# ─── Hero Header ───────────────────────────────────────────────────────────────
display_name = patient_name if patient_name else "Patient"
st.markdown(f"""
<div class="hero-header">
    <div>
        <h1 class="hero-title">Blood Report<br><i style="color:#c8a97e;">& Diet Planner</i></h1>
        <div class="hero-subtitle">Comprehensive analysis · Personalised nutrition · Health insights</div>
    </div>
    <div style="text-align:right;">
        <div class="hero-badge">🩺 {display_name}</div>
        <div style="color:#4a4464; font-size:0.8rem; margin-top:0.75rem;">{report_date.strftime('%d %B %Y')}</div>
        <div style="color:#4a4464; font-size:0.75rem; margin-top:0.2rem;">{age} yrs · {gender} · {weight} kg</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─── Main Tabs ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🔬 Blood Parameters", "📊 Health Summary", "🥗 Diet Plan", "📁 Upload Report"])


# ══════════════════════════════════════════════════════════════════════
# TAB 1 — BLOOD PARAMETERS
# ══════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-label">Complete Blood Count (CBC)</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    params = {
        "Hemoglobin": {"default": 13.5, "min": 3.0,  "max": 25.0,  "unit": "g/dL",
                       "normal_m": (13.5, 17.5), "normal_f": (12.0, 15.5)},
        "WBC Count":  {"default": 7.5,  "min": 0.5,  "max": 20.0,  "unit": "×10³/µL",
                       "normal_m": (4.5, 11.0), "normal_f": (4.5, 11.0)},
        "Platelet":   {"default": 250.0,"min": 50.0, "max": 800.0, "unit": "×10³/µL",
                       "normal_m": (150, 400), "normal_f": (150, 400)},
        "RBC":        {"default": 4.8,  "min": 1.0,  "max": 8.0,   "unit": "×10⁶/µL",
                       "normal_m": (4.7, 6.1), "normal_f": (4.2, 5.4)},
    }

    values = {}
    cols = [col1, col2, col3, col4]
    for i, (name, p) in enumerate(params.items()):
        with cols[i]:
            val = st.number_input(f"{name} ({p['unit']})", float(p["min"]), float(p["max"]), float(p["default"]), step=0.1, key=f"cbc_{name}")
            values[name] = val
            lo, hi = p["normal_m"] if gender == "Male" else p["normal_f"]
            status = "Normal" if lo <= val <= hi else ("High" if val > hi else "Low")
            cls = {"Normal": "status-normal", "High": "status-high", "Low": "status-low"}[status]
            st.markdown(f'<div class="metric-card" style="margin-top:0.5rem;"><div class="metric-label">{name}</div><div class="metric-value">{val:.1f}<span class="metric-unit">{p["unit"]}</span></div><span class="metric-status {cls}">{status}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Metabolic Panel</div>', unsafe_allow_html=True)

    col5, col6, col7, col8 = st.columns(4)
    meta_params = {
        "Glucose (FBS)":   {"default": 95.0,  "min": 40.0, "max": 500.0, "unit": "mg/dL", "lo": 70.0, "hi": 100.0},
        "HbA1c":           {"default": 5.4,   "min": 3.0,  "max": 15.0,  "unit": "%",     "lo": 4.0,  "hi": 5.6},
        "Creatinine":      {"default": 1.0,   "min": 0.1,  "max": 15.0,  "unit": "mg/dL", "lo": 0.7,  "hi": 1.3},
        "Uric Acid":       {"default": 5.5,   "min": 1.0,  "max": 15.0,  "unit": "mg/dL", "lo": 3.5,  "hi": 7.2},
    }

    for i, (name, p) in enumerate(meta_params.items()):
        with [col5, col6, col7, col8][i]:
            val = st.number_input(f"{name} ({p['unit']})", float(p["min"]), float(p["max"]), float(p["default"]), step=0.1, key=f"meta_{name}")
            values[name] = val
            status = "Normal" if p["lo"] <= val <= p["hi"] else ("High" if val > p["hi"] else "Low")
            cls = {"Normal": "status-normal", "High": "status-high", "Low": "status-low"}[status]
            st.markdown(f'<div class="metric-card" style="margin-top:0.5rem;"><div class="metric-label">{name}</div><div class="metric-value">{val:.1f}<span class="metric-unit">{p["unit"]}</span></div><span class="metric-status {cls}">{status}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Lipid Profile</div>', unsafe_allow_html=True)

    col9, col10, col11, col12 = st.columns(4)
    lipid_params = {
        "Total Cholesterol": {"default": 185.0, "min": 50.0, "max": 500.0,  "unit": "mg/dL", "lo": 0.0,  "hi": 200.0},
        "LDL":               {"default": 110.0, "min": 10.0, "max": 300.0,  "unit": "mg/dL", "lo": 0.0,  "hi": 130.0},
        "HDL":               {"default": 52.0,  "min": 10.0, "max": 100.0,  "unit": "mg/dL", "lo": 40.0, "hi": 100.0},
        "Triglycerides":     {"default": 140.0, "min": 30.0, "max": 1000.0, "unit": "mg/dL", "lo": 0.0,  "hi": 150.0},
    }

    for i, (name, p) in enumerate(lipid_params.items()):
        with [col9, col10, col11, col12][i]:
            val = st.number_input(f"{name} ({p['unit']})", float(p["min"]), float(p["max"]), float(p["default"]), step=1.0, key=f"lipid_{name}")
            values[name] = val
            status = "Normal" if p["lo"] <= val <= p["hi"] else ("High" if val > p["hi"] else "Low")
            cls = {"Normal": "status-normal", "High": "status-high", "Low": "status-low"}[status]
            st.markdown(f'<div class="metric-card" style="margin-top:0.5rem;"><div class="metric-label">{name}</div><div class="metric-value">{val:.0f}<span class="metric-unit">{p["unit"]}</span></div><span class="metric-status {cls}">{status}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Liver & Thyroid</div>', unsafe_allow_html=True)

    col13, col14, col15, col16 = st.columns(4)
    liver_params = {
        "ALT (SGPT)": {"default": 28.0,  "min": 1.0,  "max": 500.0,  "unit": "U/L",     "lo": 7.0,  "hi": 56.0},
        "AST (SGOT)": {"default": 25.0,  "min": 1.0,  "max": 500.0,  "unit": "U/L",     "lo": 10.0, "hi": 40.0},
        "TSH":        {"default": 2.5,   "min": 0.01, "max": 50.0,   "unit": "µIU/mL",  "lo": 0.4,  "hi": 4.0},
        "Vitamin D":  {"default": 28.0,  "min": 1.0,  "max": 150.0,  "unit": "ng/mL",   "lo": 30.0, "hi": 100.0},
    }

    for i, (name, p) in enumerate(liver_params.items()):
        with [col13, col14, col15, col16][i]:
            val = st.number_input(f"{name} ({p['unit']})", float(p["min"]), float(p["max"]), float(p["default"]), step=0.1, key=f"liver_{name}")
            values[name] = val
            status = "Normal" if p["lo"] <= val <= p["hi"] else ("High" if val > p["hi"] else "Low")
            cls = {"Normal": "status-normal", "High": "status-high", "Low": "status-low"}[status]
            st.markdown(f'<div class="metric-card" style="margin-top:0.5rem;"><div class="metric-label">{name}</div><div class="metric-value">{val:.1f}<span class="metric-unit">{p["unit"]}</span></div><span class="metric-status {cls}">{status}</span></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# TAB 2 — HEALTH SUMMARY
# ══════════════════════════════════════════════════════════════════════
with tab2:
    # Health Score Calculation
    scores = {
        "Hemoglobin":        (values.get("Hemoglobin", 13.5),       (12.0, 17.5)),
        "Glucose (FBS)":     (values.get("Glucose (FBS)", 95),      (70, 100)),
        "Total Cholesterol": (values.get("Total Cholesterol", 185), (0, 200)),
        "LDL":               (values.get("LDL", 110),              (0, 130)),
        "HDL":               (values.get("HDL", 52),               (40, 100)),
        "Triglycerides":     (values.get("Triglycerides", 140),    (0, 150)),
        "HbA1c":             (values.get("HbA1c", 5.4),            (4.0, 5.6)),
        "Vitamin D":         (values.get("Vitamin D", 28),         (30, 100)),
    }

    def score_param(val, lo, hi):
        if lo <= val <= hi:
            return 100
        elif val < lo:
            gap = lo - val
            ref = lo - lo * 0.3 if lo > 0 else 10
            return max(0, 100 - (gap / max(lo * 0.5, 1)) * 50)
        else:
            gap = val - hi
            return max(0, 100 - (gap / max(hi * 0.2, 1)) * 50)

    param_scores = {k: score_param(v, lo, hi) for k, (v, (lo, hi)) in scores.items()}
    overall_score = int(sum(param_scores.values()) / len(param_scores))

    if overall_score >= 85:
        grade, grade_color, grade_text = "A", "#639922", "Excellent"
    elif overall_score >= 70:
        grade, grade_color, grade_text = "B", "#ba7517", "Good"
    elif overall_score >= 55:
        grade, grade_color, grade_text = "C", "#ef9f27", "Fair"
    else:
        grade, grade_color, grade_text = "D", "#e24b4a", "Needs Attention"

    # ── Row 1: Score + Radar ──
    left, right = st.columns([1, 2])

    with left:
        st.markdown(f"""
        <div class="score-wrapper">
            <div class="score-label">Overall Health Score</div>
            <div class="score-value">{overall_score}</div>
            <div style="font-size:0.7rem; color:#7c6f8e; margin:4px 0 12px;">out of 100</div>
            <div style="background:#2d2d4e; border-radius:100px; height:6px; overflow:hidden; margin-bottom:1rem;">
                <div style="width:{overall_score}%; height:100%; background:#c8a97e; border-radius:100px;"></div>
            </div>
            <div style="font-family:'DM Serif Display',serif; font-size:1.8rem; color:{grade_color};">{grade}</div>
            <div style="font-size:0.85rem; color:#a09898; margin-top:2px;">{grade_text}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # BMI card
        bmi_color = "#639922" if 18.5 <= bmi < 25 else ("#ba7517" if bmi < 18.5 else "#e24b4a")
        st.markdown(f"""
        <div class="metric-card" style="border-left-color:{bmi_color};">
            <div class="metric-label">Body Mass Index</div>
            <div class="metric-value">{bmi:.1f}<span class="metric-unit">kg/m²</span></div>
            <span class="metric-status" style="background:{'#eaf3de' if 18.5<=bmi<25 else '#faeeda'}; color:{'#3b6d11' if 18.5<=bmi<25 else '#854f0b'};">{bmi_status}</span>
        </div>
        """, unsafe_allow_html=True)

    with right:
        # Radar / Spider Chart
        categories = list(param_scores.keys())
        score_vals = list(param_scores.values())
        categories += [categories[0]]
        score_vals += [score_vals[0]]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=score_vals, theta=categories,
            fill='toself',
            fillcolor='rgba(200,169,126,0.18)',
            line=dict(color='#c8a97e', width=2),
            name='Your Score'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=[100]*len(categories), theta=categories,
            fill='toself',
            fillcolor='rgba(26,26,46,0.04)',
            line=dict(color='#d9d2c7', width=1, dash='dot'),
            name='Ideal'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10)),
                angularaxis=dict(tickfont=dict(size=11)),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=40, t=40, b=40),
            height=320,
        )
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

    # ── Row 2: Parameter Bar Chart ──
    st.markdown('<div class="section-label">Parameter Scores Breakdown</div>', unsafe_allow_html=True)

    bar_colors = ['#639922' if s >= 80 else ('#ef9f27' if s >= 55 else '#e24b4a') for s in list(param_scores.values())]
    fig_bar = go.Figure(go.Bar(
        x=list(param_scores.keys()),
        y=list(param_scores.values()),
        marker_color=bar_colors,
        marker_line_width=0,
        text=[f"{v:.0f}" for v in param_scores.values()],
        textposition='outside',
        textfont=dict(size=11),
    ))
    fig_bar.add_hline(y=80, line_dash="dot", line_color="#d9d2c7", annotation_text="Target 80", annotation_position="right")
    fig_bar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(range=[0, 115], showgrid=True, gridcolor='#f0ebe4', title='Score'),
        xaxis=dict(showgrid=False),
        margin=dict(l=10, r=10, t=20, b=10),
        height=280,
        font=dict(family="DM Sans, sans-serif", size=12),
    )
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    # ── Row 3: Insights ──
    st.markdown('<div class="section-label">Health Insights</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="summary-card">
            <div class="summary-icon" style="background:#eaf3de;">🫀</div>
            <h4>Cardiovascular Risk</h4>
            <p>Your lipid profile indicates <strong>low-to-moderate</strong> cardiovascular risk. LDL is within acceptable limits. Maintain a low-saturated-fat diet and regular aerobic exercise.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="summary-card">
            <div class="summary-icon" style="background:#faeeda;">🩸</div>
            <h4>Blood Sugar Control</h4>
            <p>Fasting glucose is at <strong>{values.get('Glucose (FBS)', 95):.0f} mg/dL</strong> and HbA1c at <strong>{values.get('HbA1c', 5.4):.1f}%</strong>. Blood sugar is {'well-controlled' if values.get('Glucose (FBS)', 95) < 100 else 'slightly elevated'}. Monitor carbohydrate intake carefully.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        vd = values.get("Vitamin D", 28)
        st.markdown(f"""
        <div class="summary-card">
            <div class="summary-icon" style="background:#{'fcebeb' if vd < 30 else 'eaf3de'};">☀️</div>
            <h4>Vitamin D Status</h4>
            <p>Vitamin D at <strong>{vd:.0f} ng/mL</strong> is {'<strong style="color:#a32d2d;">deficient</strong>. Supplement with 2000–4000 IU/day and increase sun exposure. Add fatty fish and fortified foods to your diet.' if vd < 30 else 'within the normal range. Maintain sun exposure and dietary sources.'}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    with c4:
        hgb = values.get("Hemoglobin", 13.5)
        lo_hgb = 13.5 if gender == "Male" else 12.0
        st.markdown(f"""
        <div class="summary-card">
            <div class="summary-icon" style="background:#{'fcebeb' if hgb < lo_hgb else 'eaf3de'};">🔴</div>
            <h4>Hemoglobin & Iron</h4>
            <p>Hemoglobin is <strong>{hgb:.1f} g/dL</strong> — {'<strong style="color:#a32d2d;">below normal</strong>. Consider iron-rich foods and consult your physician about supplementation.' if hgb < lo_hgb else 'normal. Maintain iron-rich foods in your diet.'}</p>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        alt = values.get("ALT (SGPT)", 28)
        st.markdown(f"""
        <div class="summary-card">
            <div class="summary-icon" style="background:#{'faeeda' if alt > 56 else 'eaf3de'};">🫁</div>
            <h4>Liver Function</h4>
            <p>ALT at <strong>{alt:.0f} U/L</strong> — {'<strong style="color:#854f0b;">mildly elevated</strong>. Limit alcohol, processed foods and fried items. Consult a gastroenterologist if persistent.' if alt > 56 else 'within normal limits, indicating healthy liver function.'}</p>
        </div>
        """, unsafe_allow_html=True)
    with c6:
        tsh = values.get("TSH", 2.5)
        st.markdown(f"""
        <div class="summary-card">
            <div class="summary-icon" style="background:#{'fcebeb' if tsh > 4 or tsh < 0.4 else 'eaf3de'};">🦋</div>
            <h4>Thyroid Function</h4>
            <p>TSH at <strong>{tsh:.2f} µIU/mL</strong> — {'within normal range, indicating balanced thyroid activity.' if 0.4 <= tsh <= 4.0 else '<strong style="color:#a32d2d;">outside normal range</strong>. Please consult an endocrinologist for further evaluation.'}</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Alerts ──
    st.markdown('<div class="section-label">Flags & Recommendations</div>', unsafe_allow_html=True)

    alerts = []
    if values.get("Glucose (FBS)", 95) > 100:
        alerts.append(("warn", "⚠️ Fasting glucose is above the optimal threshold of 100 mg/dL. Pre-diabetic range detected. Reduce refined sugar, white rice and processed carbohydrates."))
    if values.get("LDL", 110) > 130:
        alerts.append(("danger", "🔴 LDL cholesterol is elevated. Reduce saturated fats (red meat, full-fat dairy). Increase oats, nuts, and olive oil in your diet."))
    if values.get("Vitamin D", 28) < 30:
        alerts.append(("warn", "⚠️ Vitamin D deficiency detected. Spend 20–30 minutes in sunlight daily. Consider supplementation (2000–4000 IU/day) after consulting your doctor."))
    if values.get("Hemoglobin", 13.5) < (13.5 if gender == "Male" else 12.0):
        alerts.append(("warn", "⚠️ Low hemoglobin suggests possible anaemia. Include spinach, lentils, red meat (if non-vegetarian), and iron-fortified cereals."))
    if not alerts:
        alerts.append(("good", "✅ All critical parameters are within acceptable ranges. Maintain your healthy lifestyle!"))

    for atype, msg in alerts:
        st.markdown(f'<div class="alert-box alert-{atype}">{msg}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# TAB 3 — DIET PLAN
# ══════════════════════════════════════════════════════════════════════
with tab3:
    # Calculate estimated calories
    if gender == "Male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    tdee = int(bmr * 1.4)

    st.markdown('<div class="section-label">Personalised Calorie Target</div>', unsafe_allow_html=True)

    mc1, mc2, mc3, mc4 = st.columns(4)
    for col, label, val, unit in zip(
        [mc1, mc2, mc3, mc4],
        ["Daily Calories", "Protein", "Carbs", "Fats"],
        [tdee, int(weight * 1.2), int(tdee * 0.45 / 4), int(tdee * 0.30 / 9)],
        ["kcal", "g", "g", "g"]
    ):
        with col:
            st.markdown(f"""
            <div style="background:#1a1a2e; border-radius:12px; padding:1.2rem; text-align:center;">
                <div style="font-size:0.7rem; color:#7c6f8e; text-transform:uppercase; letter-spacing:0.1em;">{label}</div>
                <div style="font-family:'DM Serif Display',serif; font-size:1.8rem; color:#c8a97e;">{val}</div>
                <div style="font-size:0.75rem; color:#4a4464;">{unit}/day</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">7-Day Meal Plan</div>', unsafe_allow_html=True)

    # Diet plan based on conditions
    glucose = values.get("Glucose (FBS)", 95)
    ldl = values.get("LDL", 110)
    hgb = values.get("Hemoglobin", 13.5)
    vd = values.get("Vitamin D", 28)

    is_diabetic = glucose > 100 or diet_pref == "Diabetic-Friendly"
    is_low_iron = hgb < (13.5 if gender == "Male" else 12.0)
    is_heart = ldl > 130 or diet_pref == "Heart-Healthy"
    is_veg = diet_pref in ["Vegetarian", "Vegan"]

    def meal_html(time, emoji, title, items):
        rows = "".join([f'<div class="food-item"><span>{f}</span><span class="food-cal">{c}</span></div>' for f, c in items])
        return f"""
        <div class="diet-card">
            <div class="meal-header">
                <span style="font-size:1.5rem;">{emoji}</span>
                <div>
                    <div class="meal-time">{time}</div>
                    <div class="meal-title">{title}</div>
                </div>
            </div>
            {rows}
        </div>"""

    col_diet1, col_diet2 = st.columns(2)

    if is_diabetic or is_heart:
        breakfast_items = [
            ("Oatmeal with chia seeds & berries", "~280 kcal"),
            ("2 boiled eggs / paneer cubes", "~140 kcal"),
            ("Green tea (unsweetened)", "~5 kcal"),
        ]
        lunch_items = [
            ("Brown rice (1 cup cooked)", "~215 kcal"),
            ("Dal / Moong lentil soup", "~150 kcal"),
            ("Stir-fried vegetables (no oil)", "~80 kcal"),
            ("Cucumber-tomato salad", "~30 kcal"),
        ]
    else:
        breakfast_items = [
            ("Whole-wheat toast with avocado", "~310 kcal"),
            ("2 scrambled eggs" if not is_veg else "Tofu scramble", "~150 kcal"),
            ("1 medium banana", "~90 kcal"),
            ("Milk / almond milk (200 ml)", "~120 kcal"),
        ]
        lunch_items = [
            ("Mixed grain rice (1 cup)", "~220 kcal"),
            ("Rajma / Chickpea curry", "~180 kcal"),
            ("Sautéed greens (spinach/kale)", "~60 kcal"),
            ("Curd / Yoghurt (100 g)", "~60 kcal"),
        ]

    snack_items = [
        ("Handful of walnuts + almonds", "~160 kcal"),
        ("Apple / Guava (1 medium)", "~80 kcal"),
        ("Green tea or lemon water", "~5 kcal"),
    ]

    if is_low_iron:
        dinner_items = [
            ("Spinach + lentil khichdi", "~320 kcal"),
            ("Grilled chicken / tofu" if not is_veg else "Paneer tikka (2 pcs)", "~180 kcal"),
            ("Beetroot salad with lime", "~60 kcal"),
        ]
    elif is_heart:
        dinner_items = [
            ("Quinoa or barley (¾ cup)", "~190 kcal"),
            ("Grilled salmon / baked tofu", "~200 kcal"),
            ("Steamed broccoli & carrots", "~70 kcal"),
        ]
    else:
        dinner_items = [
            ("Whole-wheat roti (2 pcs)", "~200 kcal"),
            ("Mixed vegetable sabzi", "~120 kcal"),
            ("Dal (1 bowl)", "~140 kcal"),
            ("Small bowl curd", "~60 kcal"),
        ]

    with col_diet1:
        st.markdown(meal_html("Early Morning · 6–7 AM", "🌅", "Wake-Up Ritual",
            [("Warm lemon water (1 glass)", "~5 kcal"),
             ("Soaked almonds (5–6)", "~40 kcal"),
             ("1 tsp methi seeds (fenugreek) in water" if is_diabetic else "Amla juice (30 ml)", "~5 kcal")]),
            unsafe_allow_html=True)
        st.markdown(meal_html("Breakfast · 8–9 AM", "🍳", "Morning Fuel", breakfast_items), unsafe_allow_html=True)
        st.markdown(meal_html("Mid-Morning · 11 AM", "🍎", "Light Snack", snack_items), unsafe_allow_html=True)

    with col_diet2:
        st.markdown(meal_html("Lunch · 1–2 PM", "🥗", "Main Meal", lunch_items), unsafe_allow_html=True)
        st.markdown(meal_html("Evening Snack · 5 PM", "🫖", "Refreshment",
            [("Herbal tea / green tea", "~5 kcal"),
             ("Makhana (fox nuts) – 1 cup", "~100 kcal"),
             ("1 seasonal fruit", "~70 kcal")]),
            unsafe_allow_html=True)
        st.markdown(meal_html("Dinner · 7–8 PM", "🌙", "Light Dinner", dinner_items), unsafe_allow_html=True)

    # ── Foods to Avoid & Foods to Eat ──
    st.markdown('<div class="section-label">Tailored Nutrition Guidance</div>', unsafe_allow_html=True)

    avoid_col, eat_col = st.columns(2)
    with avoid_col:
        st.markdown("""
        <div class="diet-card">
            <div class="meal-title" style="margin-bottom:1rem;">🚫 Foods to Limit / Avoid</div>
        """, unsafe_allow_html=True)
        avoid_list = ["Refined sugar & sugary beverages", "White rice & maida (refined flour)",
                      "Deep-fried & processed foods", "Red meat (limit to 2×/week)",
                      "Full-fat dairy if LDL is high", "Excess salt (>5g/day)"]
        for item in avoid_list:
            st.markdown(f'<div class="food-item">❌ {item}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with eat_col:
        st.markdown("""
        <div class="diet-card">
            <div class="meal-title" style="margin-bottom:1rem;">✅ Recommended Superfoods</div>
        """, unsafe_allow_html=True)
        eat_list = ["Leafy greens (spinach, kale, methi)", "Fatty fish (salmon, sardines) or flaxseeds",
                    "Berries, citrus fruits & guava", "Legumes (lentils, chickpeas, rajma)",
                    "Nuts & seeds (walnuts, chia, almonds)", "Whole grains (oats, quinoa, barley)"]
        for item in eat_list:
            st.markdown(f'<div class="food-item">✅ {item}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Hydration & Supplements ──
    st.markdown('<div class="section-label">Hydration & Supplements</div>', unsafe_allow_html=True)
    h1, h2, h3 = st.columns(3)
    water_need = round(weight * 0.033, 1)
    with h1:
        st.markdown(f"""<div class="summary-card"><div class="summary-icon" style="background:#e6f1fb;">💧</div><h4>Daily Water Intake</h4><p>Aim for <strong>{water_need} litres/day</strong> based on your body weight. Increase by 500 ml on days with exercise. Avoid beverages with added sugar.</p></div>""", unsafe_allow_html=True)
    with h2:
        supps = []
        if vd < 30: supps.append("Vitamin D3 (2000 IU/day)")
        if is_low_iron: supps.append("Iron + Vitamin C supplement")
        supps.append("Omega-3 (fish oil / flaxseed)")
        if is_diabetic: supps.append("Chromium picolinate (consult doctor)")
        st.markdown(f"""<div class="summary-card"><div class="summary-icon" style="background:#faeeda;">💊</div><h4>Suggested Supplements</h4><p>{'<br>• '.join([''] + supps)}</p><p style="margin-top:8px; font-size:0.78rem; color:#9e9083;">Always consult your physician before starting supplements.</p></div>""", unsafe_allow_html=True)
    with h3:
        st.markdown("""<div class="summary-card"><div class="summary-icon" style="background:#eaf3de;">🏃</div><h4>Exercise Prescription</h4><p><strong>150 min/week</strong> of moderate aerobic activity (brisk walking, cycling, swimming). Add 2 sessions of strength training. Morning exercise helps insulin sensitivity.</p></div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# TAB 4 — UPLOAD REPORT
# ══════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-label">Upload Blood Report</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload your blood report (PDF or image)",
        type=["pdf", "png", "jpg", "jpeg", "txt"],
        help="Upload a scanned or digital copy of your blood report for auto-parsing."
    )

    if uploaded_file:
        st.markdown(f"""
        <div class="alert-box alert-good">
            ✅ File <strong>{uploaded_file.name}</strong> uploaded successfully ({uploaded_file.size / 1024:.1f} KB).
        </div>
        """, unsafe_allow_html=True)
        
        # Extract text from file
        with st.spinner("📖 Extracting text from your report..."):
            extracted_text = extract_text_from_file(uploaded_file)
        
        if extracted_text and len(extracted_text.strip()) > 0:
            st.success("✅ Text extracted successfully!")
            
            # Show extracted text
            with st.expander("📄 View Extracted Text"):
                st.text_area("Extracted Report", value=extracted_text, height=200, disabled=True)
            
            # Parse with AI
            if st.button("🤖 Analyze Report with AI", type="primary", use_container_width=True):
                with st.spinner("🔍 Analyzing your blood report using AI..."):
                    
                    # Stage 1: Extract structured data
                    parsed_data = parse_report_with_ai(extracted_text)
                    
                    if parsed_data:
                        # Update sidebar with extracted patient info
                        st.session_state['extracted_patient'] = parsed_data.get('patient', {})
                        patient_info = parsed_data.get('patient', {})
                        
                        st.markdown("### 📋 Extracted Patient Information")
                        info_col1, info_col2, info_col3 = st.columns(3)
                        
                        with info_col1:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">Patient Name</div>
                                <div class="metric-value" style="color:#c8a97e;">{patient_info.get('name', 'N/A')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with info_col2:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">Age</div>
                                <div class="metric-value" style="color:#c8a97e;">{patient_info.get('age', 'N/A')} years</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with info_col3:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">Gender</div>
                                <div class="metric-value" style="color:#c8a97e;">{patient_info.get('gender', 'N/A')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Show extracted tests
                        st.markdown("### 🧪 Extracted Blood Parameters")
                        tests = parsed_data.get('tests', [])
                        
                        if tests:
                            test_cols = st.columns(4)
                            for i, test in enumerate(tests[:4]):
                                with test_cols[i % 4]:
                                    status_color = {"HIGH": "#e24b4a", "LOW": "#ef9f27", "NORMAL": "#639922"}
                                    color = status_color.get(test.get('status', 'NORMAL'), "#639922")
                                    st.markdown(f"""
                                    <div class="metric-card" style="border-left-color:{color};">
                                        <div class="metric-label">{test.get('name', 'Unknown')}</div>
                                        <div class="metric-value">{test.get('value', 0)}<span class="metric-unit">{test.get('unit', '')}</span></div>
                                        <span class="metric-status" style="background:{'#eaf3de' if test.get('status')=='NORMAL' else '#faeeda' if test.get('status')=='LOW' else '#fcebeb'}; color:{'#173404' if test.get('status')=='NORMAL' else '#633806' if test.get('status')=='LOW' else '#501313'};">{test.get('status', 'N/A')}</span>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            # Show remaining tests if any
                            if len(tests) > 4:
                                st.markdown(f"**+ {len(tests) - 4} more tests extracted**")
                        
                        # Stage 2: Generate health analysis
                        st.markdown("### 📊 Generating Health Analysis...")
                        with st.spinner("Generating health summary and diet recommendations..."):
                            
                            # Create formatted test summary for analysis
                            test_summary = "\n".join([
                                f"- {t.get('name', 'Unknown')}: {t.get('value', 0)} | Status: {t.get('status', 'UNKNOWN')} | Reference: {t.get('reference', 'N/A')}"
                                for t in tests
                            ])
                            
                            health_summary, diet_plan = generate_health_analysis(test_summary)
                            
                            if health_summary or diet_plan:
                                st.success("✅ Analysis Complete!")
                                
                                # Display results
                                ana_col1, ana_col2 = st.columns(2)
                                
                                with ana_col1:
                                    st.markdown("#### 💊 Health Summary")
                                    st.markdown(f'<div class="scroll-box">{health_summary}</div>', unsafe_allow_html=True)
                                
                                with ana_col2:
                                    st.markdown("#### 🍽️ Diet Plan")
                                    st.markdown(f'<div class="scroll-box">{diet_plan}</div>', unsafe_allow_html=True)
                                
                                # Option to auto-fill form
                                if st.button("✅ Auto-fill Sidebar Parameters", type="secondary"):
                                    if patient_info.get('name'):
                                        st.session_state['patient_name'] = patient_info.get('name')
                                    if patient_info.get('age'):
                                        st.session_state['age'] = patient_info.get('age')
                                    if patient_info.get('gender'):
                                        st.session_state['gender'] = patient_info.get('gender')
                                    st.success("✅ Sidebar parameters updated! Go to Tab 1 to see your data.")
                    else:
                        st.warning("⚠️ Could not parse structured data from report. Please check the report format.")
        else:
            st.error("❌ Failed to extract text from the uploaded file. Please ensure the file is readable.")
    else:
        st.markdown("""
        <div class="upload-hint">
            <div style="font-size:2.5rem; margin-bottom:0.75rem;">📄</div>
            <div style="font-weight:500; color:#4a3f35; margin-bottom:0.5rem;">Drop your blood report here</div>
            <div style="font-size:0.82rem;">Supported: PDF, PNG, JPG, TXT · Max 200 MB</div>
            <div style="font-size:0.78rem; color:#b0a898; margin-top:0.5rem;">AI-powered extraction · Auto-fills patient info & test parameters</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Export Report</div>', unsafe_allow_html=True)
    ecol1, ecol2, ecol3 = st.columns(3)
    with ecol1:
        st.button("📄 Export Health Summary (PDF)")
    with ecol2:
        st.button("🥗 Export Diet Plan (PDF)")
    with ecol3:
        st.button("📊 Export Full Report (Excel)")

    st.markdown("""
    <div style="margin-top:2rem; padding:1.5rem; background:white; border-radius:14px; border:1px solid #ede8e0;">
        <div style="font-family:'DM Serif Display',serif; font-size:1.1rem; color:#1a1a2e; margin-bottom:0.75rem;">⚕️ Medical Disclaimer</div>
        <div style="font-size:0.82rem; color:#8a7d6e; line-height:1.7;">
            This tool is intended for informational and educational purposes only. 
            It does <strong>not</strong> constitute medical advice, diagnosis, or treatment. 
            Always consult a qualified healthcare professional before making any changes to your diet, 
            medication, or treatment plan. Blood parameter interpretations may vary based on laboratory 
            reference ranges, individual health conditions, and clinical context.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:2.5rem 0 1rem; color:#b0a898; font-size:0.78rem;">
    BloodWork Analyzer · Powered by AI · For educational use only<br>
    <span style="color:#d9d2c7;">──────────────────────────────────────────</span>
</div>
""", unsafe_allow_html=True)
