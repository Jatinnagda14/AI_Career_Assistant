import streamlit as st
from huggingface_hub import InferenceClient
from pypdf import PdfReader
from dotenv import load_dotenv

import os
import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    st.error("HF_TOKEN missing. Create a .env file in project root and set HF_TOKEN.")
    st.stop()

client = InferenceClient(api_key=HF_TOKEN)

# ----------------------------
# Helpers
# ----------------------------
def extract_text(file):
    text = ""
    if file.type == "application/pdf":
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    elif file.type == "text/plain":
        text = file.read().decode("utf-8")
    return text

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="AI Career Assistant",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# CSS — Classical Dark-Gold Theme
# ----------------------------
st.markdown("""
<style>

/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Inter:wght@300;400;500&display=swap');

/* ── Root Tokens ── */
:root {
    --bg:         #0F0F1A;
    --surface:    #1A1A2E;
    --surface2:   #22223B;
    --gold:       #C9A84C;
    --gold-light: #E8C87A;
    --ivory:      #F5F0E8;
    --muted:      #8A8AA8;
    --border:     #2E2E4A;
    --danger:     #C0504D;
    --success:    #4A9B6F;
    --warn:       #C9903A;
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--ivory) !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--ivory) !important;
}

[data-testid="stSidebar"] .stRadio label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    padding: 6px 0 !important;
    transition: color 0.2s;
}

[data-testid="stSidebar"] .stRadio label:hover {
    color: var(--gold) !important;
}

/* Radio selected state */
[data-testid="stSidebar"] [aria-checked="true"] + label,
[data-testid="stSidebar"] .stRadio [aria-checked="true"] ~ div label {
    color: var(--gold) !important;
}

/* ── Sidebar Brand ── */
.sidebar-brand {
    padding: 24px 0 20px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 24px;
}
.sidebar-brand .monogram {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: var(--gold);
    letter-spacing: 2px;
    line-height: 1;
}
.sidebar-brand .tagline {
    font-size: 0.7rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 4px;
}

/* ── Page Header ── */
.page-header {
    padding: 48px 0 32px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 40px;
}
.page-eyebrow {
    font-size: 0.7rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 10px;
}
.page-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3rem;
    font-weight: 600;
    color: var(--ivory);
    line-height: 1.1;
    margin: 0;
}
.gold-rule {
    width: 48px;
    height: 2px;
    background: var(--gold);
    margin-top: 20px;
}

/* ── Cards / Panels ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 28px 32px;
    margin-bottom: 24px;
}
.card-label {
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 8px;
}
.card-value {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.4rem;
    font-weight: 600;
    color: var(--ivory);
}

/* ── Metrics row ── */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 40px;
}

/* ── Hero ── */
.hero-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-top: 3px solid var(--gold);
    border-radius: 4px;
    padding: 48px 48px 40px;
    margin-bottom: 40px;
    position: relative;
    overflow: hidden;
}
.hero-panel::after {
    content: '✦';
    position: absolute;
    right: 48px;
    top: 40px;
    font-size: 5rem;
    color: var(--border);
    line-height: 1;
    pointer-events: none;
}
.hero-panel h1 {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 2.8rem !important;
    font-weight: 600 !important;
    color: var(--ivory) !important;
    margin: 0 0 8px !important;
}
.hero-panel p {
    color: var(--muted) !important;
    font-size: 0.95rem !important;
    max-width: 520px !important;
    line-height: 1.7 !important;
    margin: 0 !important;
}

/* ── Section Labels ── */
.section-label {
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
    color: var(--ivory) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 12px 16px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 2px rgba(201,168,76,0.15) !important;
    outline: none !important;
}

/* ── Slider ── */
[data-testid="stSlider"] .stSlider > div > div > div > div {
    background: var(--gold) !important;
}

/* ── Buttons ── */
[data-testid="stButton"] > button {
    background: transparent !important;
    border: 1px solid var(--gold) !important;
    color: var(--gold) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    padding: 10px 28px !important;
    border-radius: 2px !important;
    transition: all 0.2s !important;
    cursor: pointer !important;
}
[data-testid="stButton"] > button:hover {
    background: var(--gold) !important;
    color: var(--bg) !important;
}

/* ── File Uploader ── */
[data-testid="stFileUploader"] {
    border: 1px dashed var(--border) !important;
    border-radius: 4px !important;
    background: var(--surface) !important;
    padding: 20px !important;
}
[data-testid="stFileUploader"] * {
    color: var(--muted) !important;
}

/* ── Alerts ── */
[data-testid="stSuccess"] {
    background: rgba(74,155,111,0.12) !important;
    border: 1px solid var(--success) !important;
    border-left: 3px solid var(--success) !important;
    border-radius: 3px !important;
    color: var(--ivory) !important;
}
[data-testid="stWarning"] {
    background: rgba(201,144,58,0.12) !important;
    border: 1px solid var(--warn) !important;
    border-left: 3px solid var(--warn) !important;
    border-radius: 3px !important;
    color: var(--ivory) !important;
}
[data-testid="stError"] {
    background: rgba(192,80,77,0.12) !important;
    border: 1px solid var(--danger) !important;
    border-left: 3px solid var(--danger) !important;
    border-radius: 3px !important;
    color: var(--ivory) !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] {
    color: var(--gold) !important;
}

/* ── Output text ── */
.output-block {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-left: 3px solid var(--gold);
    border-radius: 3px;
    padding: 28px 32px;
    margin-top: 24px;
    font-size: 0.93rem;
    line-height: 1.8;
    color: var(--ivory);
}

/* ── Labels ── */
label, [data-testid="stWidgetLabel"] {
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    font-family: 'Inter', sans-serif !important;
    margin-bottom: 6px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold); }

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 32px 0 !important;
}

/* ── Write output ── */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
    color: var(--ivory) !important;
}

[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
    font-family: 'Cormorant Garamond', serif !important;
    color: var(--gold-light) !important;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="monogram">ACA</div>
        <div class="tagline">AI Career Assistant</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Career Roadmap",
            "Placement Predictor",
            "Interview Generator",
            "Resume Analyzer"
        ],
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.68rem;letter-spacing:0.12em;color:#3A3A52;text-transform:uppercase;padding-top:16px;border-top:1px solid #2E2E4A;">
        Powered by Llama 3.1 · HF Inference
    </div>
    """, unsafe_allow_html=True)

# ----------------------------
# Dashboard
# ----------------------------
if page == "Dashboard":

    st.markdown("""
    <div class="hero-panel">
        <h1>Your Career,<br>Precisely Guided.</h1>
        <p>An intelligent assistant for building careers with clarity — from roadmaps and resumes to interview preparation and placement insight.</p>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-label">Skills Analyzed</div>
            <div class="card-value">120</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-label">Jobs Matched</div>
            <div class="card-value">45</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="card">
            <div class="card-label">Interview Questions</div>
            <div class="card-value">350</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-label">Career Chat</div>', unsafe_allow_html=True)

    question = st.text_input("Ask anything about careers, skills, or the job market", label_visibility="collapsed",
                              placeholder="e.g. What skills do I need to become a data scientist?")

    if st.button("Send →"):
        with st.spinner("Consulting the oracle..."):
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.1-8B-Instruct",
                messages=[{"role": "user", "content": question}],
                max_tokens=800
            )
            answer = response.choices[0].message.content
            st.markdown(f'<div class="output-block">{answer}</div>', unsafe_allow_html=True)

# ----------------------------
# Career Roadmap
# ----------------------------
elif page == "Career Roadmap":

    st.markdown("""
    <div class="page-header">
        <div class="page-eyebrow">I — Strategic Planning</div>
        <div class="page-title">Career Roadmap</div>
        <div class="gold-rule"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Your Goal</div>', unsafe_allow_html=True)
    goal = st.text_input("What role are you aiming for?", label_visibility="collapsed",
                          placeholder="e.g. Machine Learning Engineer, Product Manager...")

    if st.button("Generate Roadmap →"):
        with st.spinner("Charting your path..."):
            prompt = f"""
            Create a complete, structured roadmap for becoming a {goal}.

            Include:
            - Core Skills Required
            - Technologies & Tools
            - Learning Path (step-by-step)
            - Recommended Projects
            - Certifications Worth Pursuing
            - Interview Preparation Strategy

            Be specific, practical, and actionable.
            """
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.1-8B-Instruct",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200
            )
            roadmap = response.choices[0].message.content
            st.markdown(f'<div class="output-block">{roadmap}</div>', unsafe_allow_html=True)

# ----------------------------
# Placement Predictor
# ----------------------------
elif page == "Placement Predictor":

    st.markdown("""
    <div class="page-header">
        <div class="page-eyebrow">II — Assessment</div>
        <div class="page-title">Placement Predictor</div>
        <div class="gold-rule"></div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1], gap="large")

    with col_a:
        st.markdown('<div class="section-label">Academic Score</div>', unsafe_allow_html=True)
        cgpa = st.slider("CGPA", 0.0, 10.0, 7.0, step=0.1, label_visibility="collapsed")
        st.markdown(f"""
        <div style="font-family:'Cormorant Garamond',serif;font-size:3rem;color:var(--gold);line-height:1;margin:8px 0 0;">
            {cgpa:.1f}<span style="font-size:1rem;color:#8A8AA8;margin-left:6px;">/ 10.0</span>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="section-label">Your Skills</div>', unsafe_allow_html=True)
        skills = st.text_input("List your skills", label_visibility="collapsed",
                                placeholder="Python, SQL, Machine Learning, React...")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Predict Placement →"):

        if cgpa >= 8:
            st.success("High Placement Probability — Strong academic foundation detected.")
        elif cgpa >= 6:
            st.warning("Moderate Placement Probability — Skill development can strengthen your profile.")
        else:
            st.error("Improvement Needed — Focus on fundamentals and hands-on projects.")

        with st.spinner("Generating personalised advice..."):
            prompt = f"""
            Student CGPA: {cgpa}
            Skills: {skills}

            Provide structured placement advice covering:
            - Strengths to leverage
            - Gaps to close
            - Specific action items for the next 3 months
            - Companies to target given this profile
            """
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.1-8B-Instruct",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            st.markdown(f'<div class="output-block">{response.choices[0].message.content}</div>',
                        unsafe_allow_html=True)

# ----------------------------
# Interview Generator
# ----------------------------
elif page == "Interview Generator":

    st.markdown("""
    <div class="page-header">
        <div class="page-eyebrow">III — Preparation</div>
        <div class="page-title">Interview Generator</div>
        <div class="gold-rule"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Technology or Role</div>', unsafe_allow_html=True)
    tech = st.text_input("Enter a technology, language, or job role", label_visibility="collapsed",
                          placeholder="e.g. Python, System Design, React, Data Structures...")

    if st.button("Generate Questions →"):
        with st.spinner("Composing interview set..."):
            prompt = f"""
            Generate exactly 10 interview questions with detailed answers for: {tech}.

            Format each as:
            Q[N]. [Question]
            A[N]. [Answer]

            Make questions range from foundational to advanced.
            """
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.1-8B-Instruct",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
            result = response.choices[0].message.content
            st.markdown(f'<div class="output-block">{result}</div>', unsafe_allow_html=True)

# ----------------------------
# Resume Analyzer
# ----------------------------
elif page == "Resume Analyzer":

    st.markdown("""
    <div class="page-header">
        <div class="page-eyebrow">IV — Document Analysis</div>
        <div class="page-title">ATS Resume Analyzer</div>
        <div class="gold-rule"></div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown('<div class="section-label">Upload Resume</div>', unsafe_allow_html=True)
        file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"],
                                 label_visibility="collapsed")
        if file:
            st.success(f"✦ {file.name} uploaded successfully")

    with col_right:
        st.markdown('<div class="section-label">Job Description</div>', unsafe_allow_html=True)
        job_description = st.text_area("Paste the target job description here", height=180,
                                        label_visibility="collapsed",
                                        placeholder="Paste the full job description to get an ATS match analysis...")

    st.markdown("<br>", unsafe_allow_html=True)

    if file and st.button("Analyze Resume →"):
        resume_text = extract_text(file)

        with st.spinner("Running ATS analysis..."):
            prompt = f"""
            You are an expert ATS Resume Scanner.

            Compare the Resume with the Job Description and provide:

            ## ATS Match Score
            Score out of 100 with brief justification.

            ## Matching Skills
            Skills present in both resume and JD.

            ## Missing Skills
            Skills in JD not found in resume.

            ## Missing Keywords
            Important ATS keywords absent from resume.

            ## Resume Strengths
            What the resume does well.

            ## Resume Weaknesses
            Areas that need improvement.

            ## Actionable Recommendations
            Specific, numbered improvements to make.

            ## Interview Readiness
            Rate readiness for this role and why.

            Resume:
            {resume_text}

            Job Description:
            {job_description}
            """

            response = client.chat.completions.create(
                model="meta-llama/Llama-3.1-8B-Instruct",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )

        st.markdown('<div class="section-label" style="margin-top:32px;">Analysis Report</div>',
                    unsafe_allow_html=True)
        st.markdown(f'<div class="output-block">{response.choices[0].message.content}</div>',
                    unsafe_allow_html=True)

        with st.expander("View Extracted Resume Text"):
            st.text_area("", resume_text, height=300, label_visibility="collapsed")