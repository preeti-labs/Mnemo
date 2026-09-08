import os
import re
import json
from datetime import datetime, date

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Mnemo",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# OPENAI
# ============================================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "page": "Today",

    # Study
    "study_material": "",
    "study_summary": "",
    "study_concepts": [],
    "study_simple_explanation": "",
    "study_flashcards": [],
    "study_topic": "",

    # Quiz
    "quiz_started": False,
    "quiz_index": 0,
    "quiz_score": 0,
    "quiz_difficulty": "Medium",
    "quiz_history": [],
    "quiz_answered": False,
    "current_question": None,
    "last_result": None,
    "last_explanation": "",

    # Academic
    "timetable": [],
    "syllabus": [],
    "teachers": [],
    "notices": [],
    "academic_ready": False,

    "raw_timetable": "",
    "raw_syllabus": "",
    "raw_teachers": "",
    "raw_notices": "",

    # Catch-up
    "missed_plan": None,

    # Progress
    "concepts_learned": 0,
    "sessions_completed": 0,

    # Atmosphere
    "study_atmosphere": "quiet morning ☕",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# COLORS
# ============================================================

CREAM = "#FFF9F4"
BERRY = "#D94F78"
DEEP_BERRY = "#351D2B"

PISTA = "#C7D9A5"
LILAC = "#C7B4DD"
BUTTER = "#F2D477"

WHITE = "#FFFFFF"

MUTED = "#806D75"

SOFT_PINK = "#F7DCE5"
SOFT_LILAC = "#EEE7F5"
SOFT_PISTA = "#E9F0DC"
SOFT_BUTTER = "#FFF3C8"


# ============================================================
# CUSTOM CSS
# ============================================================



# ============================================================
# HTML RENDERER
# ============================================================

def render_html(content, unsafe_allow_html=True):
    """Render Mnemo HTML reliably across Streamlit versions."""
    if hasattr(st, "html"):
        st.html(content)
    else:
        st.markdown(content, unsafe_allow_html=True)

render_html(
    f"""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* ========================================================
       GLOBAL
       ======================================================== */

    html, body, [class*="css"] {{
        font-family: "Plus Jakarta Sans", sans-serif !important;
    }}

    .stApp {{
        background:
            radial-gradient(
                circle at 90% 5%,
                rgba(199, 180, 221, 0.16),
                transparent 25%
            ),
            {CREAM};
        color: {DEEP_BERRY};
    }}

    .main .block-container {{
        max-width: 1450px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
        padding-left: 4rem;
        padding-right: 4rem;
    }}

    /* Remove Streamlit branding */
    #MainMenu {{
        visibility: hidden;
    }}

    footer {{
        visibility: hidden;
    }}

    header {{
        background: transparent !important;
    }}

    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {{
        background: {WHITE};
        border-right: 1px solid rgba(53, 29, 43, 0.07);
    }}

    section[data-testid="stSidebar"] > div {{
        padding: 2rem 1.25rem;
    }}

    .sidebar-logo {{
        font-size: 1.65rem;
        font-weight: 800;
        letter-spacing: -0.05em;
        color: {DEEP_BERRY};
        margin-bottom: 0.2rem;
    }}

    .sidebar-tagline {{
        font-size: 0.78rem;
        color: {MUTED};
        line-height: 1.5;
        margin-bottom: 2rem;
    }}

    .sidebar-section {{
        font-size: 0.68rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #A9939D;
        margin-top: 1.4rem;
        margin-bottom: 0.55rem;
    }}

    .setup-box {{
        background: {SOFT_PISTA};
        border-radius: 18px;
        padding: 1rem;
        margin-top: 1rem;
        border: 1px solid rgba(53,29,43,0.05);
    }}

    .setup-status {{
        font-size: 0.74rem;
        font-weight: 700;
        color: {DEEP_BERRY};
    }}

    .setup-small {{
        font-size: 0.72rem;
        color: {MUTED};
        margin-top: 0.25rem;
        line-height: 1.45;
    }}

    /* ========================================================
       STREAMLIT CONTROLS
       ======================================================== */

    div[data-testid="stRadio"] label {{
        font-family: "Plus Jakarta Sans", sans-serif !important;
        font-weight: 600 !important;
        color: {DEEP_BERRY} !important;
    }}

    .stButton > button {{
        border-radius: 14px !important;
        border: 1px solid rgba(53,29,43,0.08) !important;
        font-family: "Plus Jakarta Sans", sans-serif !important;
        font-weight: 700 !important;
        min-height: 44px;
        transition: all 0.18s ease;
    }}

    .stButton > button:hover {{
        transform: translateY(-1px);
        border-color: {BERRY} !important;
    }}

    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"],
    .stDateInput input {{
        border-radius: 13px !important;
        border-color: rgba(53,29,43,0.12) !important;
        font-family: "Plus Jakarta Sans", sans-serif !important;
    }}

    /* ========================================================
       PAGE HEADER
       ======================================================== */

    .eyebrow {{
        font-size: 0.76rem;
        font-weight: 700;
        color: {MUTED};
        margin-bottom: 0.7rem;
        letter-spacing: 0.02em;
    }}

    .page-title {{
        font-size: clamp(2.5rem, 5vw, 4.2rem);
        line-height: 1.02;
        letter-spacing: -0.065em;
        font-weight: 800;
        color: {DEEP_BERRY};
        margin: 0;
    }}

    .page-subtitle {{
        max-width: 670px;
        font-size: 1.03rem;
        line-height: 1.65;
        color: {MUTED};
        margin-top: 1rem;
    }}

    .hero-chip {{
        display: inline-flex;
        align-items: center;
        padding: 0.42rem 0.72rem;
        border-radius: 999px;
        background: {SOFT_PINK};
        color: {BERRY};
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        margin-bottom: 1rem;
    }}

    /* ========================================================
       CARDS
       ======================================================== */

    .mnemo-card {{
        background: {WHITE};
        border: 1px solid rgba(53,29,43,0.07);
        border-radius: 24px;
        padding: 1.5rem;
        height: 100%;
        box-shadow: 0 10px 35px rgba(53,29,43,0.035);
    }}

    .mnemo-card.pink {{
        background: {SOFT_PINK};
    }}

    .mnemo-card.pista {{
        background: {SOFT_PISTA};
    }}

    .mnemo-card.lilac {{
        background: {SOFT_LILAC};
    }}

    .mnemo-card.butter {{
        background: {SOFT_BUTTER};
    }}

    .card-kicker {{
        font-size: 0.68rem;
        font-weight: 800;
        color: {BERRY};
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.6rem;
    }}

    .card-heading {{
        font-size: 1.2rem;
        line-height: 1.25;
        font-weight: 800;
        letter-spacing: -0.035em;
        color: {DEEP_BERRY};
        margin-bottom: 0.65rem;
    }}

    .card-text {{
        font-size: 0.88rem;
        line-height: 1.65;
        color: {MUTED};
    }}

    .card-icon {{
        font-size: 1.45rem;
        margin-bottom: 0.85rem;
    }}

    /* ========================================================
       BIG EMPTY STATE
       ======================================================== */

    .empty-state {{
        background: {WHITE};
        border: 1px dashed rgba(53,29,43,0.14);
        border-radius: 26px;
        padding: 2.5rem;
        text-align: center;
    }}

    .empty-icon {{
        font-size: 2.4rem;
        margin-bottom: 0.8rem;
    }}

    .empty-title {{
        font-size: 1.25rem;
        font-weight: 800;
        letter-spacing: -0.035em;
        color: {DEEP_BERRY};
    }}

    .empty-text {{
        max-width: 560px;
        margin: 0.6rem auto 0;
        color: {MUTED};
        line-height: 1.6;
        font-size: 0.9rem;
    }}

    /* ========================================================
       METRICS
       ======================================================== */

    .metric-card {{
        background: {WHITE};
        border: 1px solid rgba(53,29,43,0.07);
        border-radius: 20px;
        padding: 1.25rem;
    }}

    .metric-label {{
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 800;
        color: {MUTED};
    }}

    .metric-number {{
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.06em;
        margin-top: 0.25rem;
        color: {DEEP_BERRY};
    }}

    /* ========================================================
       TABLE / CLASS ITEMS
       ======================================================== */

    .class-item {{
        background: {WHITE};
        border: 1px solid rgba(53,29,43,0.07);
        border-radius: 18px;
        padding: 1rem 1.15rem;
        margin-bottom: 0.65rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    }}

    .class-time {{
        min-width: 85px;
        font-size: 0.76rem;
        font-weight: 800;
        color: {BERRY};
    }}

    .class-subject {{
        font-weight: 800;
        font-size: 0.92rem;
        color: {DEEP_BERRY};
    }}

    .class-topic {{
        font-size: 0.76rem;
        color: {MUTED};
        margin-top: 0.2rem;
    }}

    .class-teacher {{
        font-size: 0.72rem;
        color: {MUTED};
        text-align: right;
    }}

    /* ========================================================
       STUDY / RECALL
       ======================================================== */

    .section-title {{
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -0.045em;
        color: {DEEP_BERRY};
        margin-bottom: 0.4rem;
    }}

    .section-subtitle {{
        color: {MUTED};
        font-size: 0.84rem;
        margin-bottom: 1.2rem;
    }}

    .concept-pill {{
        display: inline-block;
        background: {SOFT_LILAC};
        color: {DEEP_BERRY};
        padding: 0.48rem 0.75rem;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 700;
        margin: 0.2rem;
    }}

    .flashcard {{
        background: {DEEP_BERRY};
        color: {WHITE};
        border-radius: 22px;
        padding: 1.6rem;
        margin-bottom: 0.8rem;
    }}

    .flashcard-label {{
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 800;
        opacity: 0.65;
        margin-bottom: 0.65rem;
    }}

    .flashcard-question {{
        font-size: 1rem;
        line-height: 1.5;
        font-weight: 700;
    }}

    .flashcard-answer {{
        margin-top: 0.8rem;
        padding-top: 0.8rem;
        border-top: 1px solid rgba(255,255,255,0.15);
        font-size: 0.85rem;
        line-height: 1.6;
        opacity: 0.85;
    }}

    .question-box {{
        background: {WHITE};
        border: 1px solid rgba(53,29,43,0.08);
        border-radius: 26px;
        padding: 2rem;
    }}

    .question-number {{
        font-size: 0.68rem;
        font-weight: 800;
        text-transform: uppercase;
        color: {BERRY};
        letter-spacing: 0.1em;
    }}

    .question-text {{
        font-size: 1.45rem;
        line-height: 1.4;
        font-weight: 800;
        letter-spacing: -0.04em;
        margin-top: 0.65rem;
        color: {DEEP_BERRY};
    }}

    .result-good {{
        background: {SOFT_PISTA};
        border-radius: 20px;
        padding: 1.2rem;
    }}

    .result-close {{
        background: {SOFT_BUTTER};
        border-radius: 20px;
        padding: 1.2rem;
    }}

    .result-bad {{
        background: {SOFT_PINK};
        border-radius: 20px;
        padding: 1.2rem;
    }}

    .result-title {{
        font-size: 1rem;
        font-weight: 800;
        color: {DEEP_BERRY};
    }}

    .result-text {{
        font-size: 0.82rem;
        line-height: 1.55;
        color: {MUTED};
        margin-top: 0.35rem;
    }}

    /* ========================================================
       ATMOSPHERE
       ======================================================== */

    .atmosphere {{
        background: {SOFT_LILAC};
        border-radius: 18px;
        padding: 0.85rem 1rem;
        margin-top: 1rem;
    }}

    .atmosphere-label {{
        font-size: 0.65rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: {MUTED};
    }}

    .atmosphere-text {{
        font-size: 0.82rem;
        font-weight: 700;
        color: {DEEP_BERRY};
        margin-top: 0.2rem;
    }}

    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {{
        text-align: center;
        color: #A9939D;
        font-size: 0.72rem;
        padding-top: 3rem;
        padding-bottom: 1rem;
    }}

    /* ========================================================
       MOBILE
       ======================================================== */

    @media (max-width: 900px) {{
        .main .block-container {{
            padding-left: 1.2rem;
            padding-right: 1.2rem;
        }}

        .page-title {{
            font-size: 2.6rem;
        }}
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# PREMIUM HOME STYLES
# ============================================================

render_html(
    """
    <style>
    .premium-hero {
        padding: 0.6rem 0 0.35rem;
    }
    .premium-kicker {
        display: inline-flex;
        align-items: center;
        padding: .38rem .7rem;
        border: 1px solid rgba(53,29,43,.08);
        border-radius: 999px;
        background: rgba(255,255,255,.78);
        color: #806D75;
        font-size: .64rem;
        font-weight: 800;
        letter-spacing: .11em;
        text-transform: uppercase;
    }
    .premium-date {
        margin-top: 1.25rem;
        color: #806D75;
        font-size: .76rem;
        font-weight: 700;
    }
    .premium-title {
        margin: .38rem 0 0;
        max-width: 900px;
        font-size: clamp(3rem, 5.2vw, 5rem);
        line-height: .95;
        letter-spacing: -.078em;
        color: #351D2B;
        font-weight: 800;
    }
    .premium-subtitle {
        margin-top: .8rem;
        max-width: 650px;
        color: #806D75;
        font-size: .98rem;
        line-height: 1.6;
    }
    .focus-panel {
        margin-top: 1.15rem;
        padding: 1rem 1.1rem;
        border: 1px solid rgba(53,29,43,.07);
        border-radius: 18px;
        background: rgba(255,255,255,.78);
        box-shadow: 0 10px 34px rgba(53,29,43,.025);
    }
    .focus-label {
        color: #A9939D;
        font-size: .62rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .11em;
    }
    .focus-copy {
        margin-top: .32rem;
        color: #351D2B;
        font-size: .9rem;
        font-weight: 700;
        line-height: 1.45;
    }
    .stat-strip {
        margin: 1rem 0 1.25rem;
        display: flex;
        flex-wrap: wrap;
        gap: .55rem;
    }
    .stat-chip {
        padding: .48rem .7rem;
        border-radius: 11px;
        background: #FFFFFF;
        border: 1px solid rgba(53,29,43,.07);
        color: #806D75;
        font-size: .7rem;
        font-weight: 700;
    }
    .stat-chip strong {
        color: #351D2B;
        font-size: .82rem;
    }
    .premium-section-intro {
        margin-top: 1rem;
    }
    .today-card {
        padding: 1.05rem 1.15rem;
        border-radius: 18px;
        border: 1px solid rgba(53,29,43,.07);
        background: #FFFFFF;
        margin-bottom: .6rem;
        box-shadow: 0 8px 26px rgba(53,29,43,.025);
    }
    .today-card-top {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        align-items: center;
    }
    .today-time {
        color: #D94F78;
        font-size: .64rem;
        font-weight: 800;
        letter-spacing: .08em;
        text-transform: uppercase;
    }
    .today-subject {
        margin-top: .3rem;
        color: #351D2B;
        font-size: .96rem;
        font-weight: 800;
        letter-spacing: -.02em;
    }
    .today-topic {
        margin-top: .16rem;
        color: #806D75;
        font-size: .75rem;
    }
    .today-teacher {
        color: #806D75;
        font-size: .68rem;
        text-align: right;
    }
    .premium-note {
        padding: 1rem 1.05rem;
        border-radius: 18px;
        background: rgba(247,220,229,.75);
        border: 1px solid rgba(217,79,120,.07);
    }
    .premium-note-title {
        margin-top: .25rem;
        color: #351D2B;
        font-size: .98rem;
        font-weight: 800;
    }
    .premium-note-text {
        margin-top: .3rem;
        color: #806D75;
        font-size: .77rem;
        line-height: 1.55;
    }
    .setup-hero {
        padding: 1.25rem 1.25rem 1.1rem;
        border-radius: 20px;
        background: linear-gradient(135deg, rgba(247,220,229,.88), rgba(238,231,245,.72));
        border: 1px solid rgba(53,29,43,.06);
    }
    .setup-hero .setup-kicker {
        color: #D94F78;
        font-size: .63rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .1em;
    }
    .setup-hero .setup-title {
        margin-top: .35rem;
        color: #351D2B;
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -.04em;
    }
    .setup-hero .setup-copy {
        margin-top: .4rem;
        max-width: 760px;
        color: #806D75;
        font-size: .82rem;
        line-height: 1.55;
    }
    .quiet-control {
        display: flex;
        justify-content: flex-end;
        margin: .7rem 0 .9rem;
    }
    @media (max-width: 900px) {
        .premium-title { font-size: 3.1rem; }
        .today-card-top { align-items: flex-start; }
        .today-teacher { text-align: left; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HELPERS
# ============================================================


def go_to(page):
    st.session_state.page = page
    st.rerun()


def clean_json(text):
    if not text:
        return ""

    text = text.strip()

    text = re.sub(r"^```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)

    return text.strip()


def safe_list(value):
    return value if isinstance(value, list) else []


def esc(value):
    """Basic HTML escaping for AI/user-generated text."""
    value = "" if value is None else str(value)

    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#039;")
    )


def ask_mnemo(instructions, input_text):
    if not client:
        return None

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            instructions=instructions,
            input=input_text,
        )

        return response.output_text

    except Exception as e:
        st.error(f"Mnemo couldn't connect right now: {e}")
        return None


def ask_json(instructions, input_text):
    result = ask_mnemo(instructions, input_text)

    if not result:
        return None

    try:
        return json.loads(clean_json(result))

    except json.JSONDecodeError:
        st.error("Mnemo returned something unexpected. Please try again.")
        return None


def today_name():
    return datetime.now().strftime("%A")


def format_today():
    return datetime.now().strftime("%A, %d %B %Y")


def parse_time(value):
    if not value:
        return datetime.max

    try:
        return datetime.strptime(value, "%H:%M")
    except Exception:
        return datetime.max


def read_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return ""

    name = uploaded_file.name.lower()

    try:
        if name.endswith(".txt"):
            return uploaded_file.read().decode("utf-8", errors="ignore")

        if name.endswith(".pdf"):
            from pypdf import PdfReader

            reader = PdfReader(uploaded_file)

            pages = []

            for page in reader.pages:
                pages.append(page.extract_text() or "")

            return "\n".join(pages)

        if name.endswith(".docx"):
            from docx import Document

            document = Document(uploaded_file)

            return "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
            )

    except Exception as e:
        st.error(f"Couldn't read this file: {e}")
        return ""

    return ""


# ============================================================
# AI — ACADEMIC PROFILE
# ============================================================

def build_academic_profile():
    combined = f"""
TIMETABLE:
{st.session_state.raw_timetable}

SYLLABUS:
{st.session_state.raw_syllabus}

TEACHER REFERENCES:
{st.session_state.raw_teachers}

NOTICES:
{st.session_state.raw_notices}
"""

    instructions = """
You are Mnemo, a student academic organization assistant.

Convert the student's raw academic information into structured JSON.

Rules:
- Never invent facts.
- If information is missing, use "Unknown".
- Preserve exact subject names where possible.
- Keep timetable days as Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday.
- Extract teacher references only when actually provided.
- Extract notices only from supplied text.

Return ONLY valid JSON:

{
  "timetable": [
    {
      "day": "Monday",
      "start": "09:00",
      "end": "10:00",
      "subject": "Physics",
      "topic": "Vectors",
      "teacher": "Unknown",
      "room": "Unknown"
    }
  ],
  "syllabus": [
    {
      "subject": "Physics",
      "topics": ["Vectors", "Kinematics"]
    }
  ],
  "teachers": [
    {
      "name": "Teacher name",
      "subject": "Physics",
      "contact": "Unknown",
      "reference": "Any provided reference"
    }
  ],
  "notices": [
    {
      "date": "YYYY-MM-DD",
      "subject": "Physics",
      "text": "Notice text"
    }
  ]
}
"""

    result = ask_json(instructions, combined)

    if not result:
        return False

    st.session_state.timetable = safe_list(result.get("timetable"))
    st.session_state.syllabus = safe_list(result.get("syllabus"))
    st.session_state.teachers = safe_list(result.get("teachers"))
    st.session_state.notices = safe_list(result.get("notices"))

    st.session_state.academic_ready = True

    return True


# ============================================================
# AI — CATCH UP
# ============================================================

def generate_catchup(subject, missed_date, extra_context=""):

    academic_context = f"""
TIMETABLE:
{json.dumps(st.session_state.timetable, indent=2)}

SYLLABUS:
{json.dumps(st.session_state.syllabus, indent=2)}

TEACHERS:
{json.dumps(st.session_state.teachers, indent=2)}

NOTICES:
{json.dumps(st.session_state.notices, indent=2)}
"""

    instructions = """
You are Mnemo's missed-class recovery engine.

The student missed a class.

Use only the provided academic context.

Do not pretend that something is confirmed if it is not.

Return ONLY valid JSON:

{
  "scheduled_topic": "",
  "confidence": "High / Medium / Low",
  "what_is_confirmed": "",
  "what_to_learn": [],
  "catch_up_steps": [],
  "quick_check_questions": [],
  "teacher": "",
  "note": ""
}
"""

    input_text = f"""
SUBJECT:
{subject}

MISSED DATE:
{missed_date}

STUDENT CONTEXT:
{extra_context}

ACADEMIC CONTEXT:
{academic_context}
"""

    result = ask_json(instructions, input_text)

    if result:
        st.session_state.missed_plan = result

    return result


# ============================================================
# AI — STUDY PACK
# ============================================================

def generate_study_pack(material):

    instructions = """
You are Mnemo's study engine.

Turn the student's material into a useful study pack.

Do not add facts that are not supported by the material unless needed
for a very simple explanation.

Return ONLY valid JSON:

{
  "summary": "",
  "simple_explanation": "",
  "concepts": [],
  "flashcards": [
    {
      "question": "",
      "answer": ""
    }
  ]
}
"""

    return ask_json(instructions, material)


# ============================================================
# AI — QUIZ QUESTION
# ============================================================

def generate_question():

    material = st.session_state.study_material
    difficulty = st.session_state.quiz_difficulty

    instructions = """
You are Mnemo's adaptive recall engine.

Create one multiple-choice question based ONLY on the supplied study material.

Difficulty should match the requested level.

Return ONLY valid JSON:

{
  "question": "",
  "options": ["", "", "", ""],
  "answer": 0,
  "explanation": ""
}

The answer must be the zero-based index of the correct option.
"""

    input_text = f"""
DIFFICULTY:
{difficulty}

STUDY MATERIAL:
{material}
"""

    return ask_json(instructions, input_text)


# ============================================================
# QUIZ CONTROL
# ============================================================

def start_quiz():

    st.session_state.quiz_started = True
    st.session_state.quiz_index = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_history = []
    st.session_state.quiz_answered = False
    st.session_state.last_result = None
    st.session_state.last_explanation = ""

    question = generate_question()

    st.session_state.current_question = question


def finish_quiz():

    st.session_state.quiz_started = False
    st.session_state.current_question = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    render_html(
        """
        <div class="sidebar-logo">
            mnemo 🧠
        </div>

        <div class="sidebar-tagline">
            your study space, not another dashboard
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_html(
        '<div class="sidebar-section">your space</div>',
        unsafe_allow_html=True,
    )

    pages = [
        "Today",
        "Classes",
        "Catch-up",
        "Study",
        "Recall",
        "Progress",
    ]

    current_index = pages.index(st.session_state.page)

    selected_page = st.radio(
        "Navigate",
        pages,
        index=current_index,
        label_visibility="collapsed",
    )

    if selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.rerun()

    render_html(
        '<div class="sidebar-section">academic setup</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.academic_ready:

        render_html(
            """
            <div class="setup-box">
                <div class="setup-status">
                    ● setup ready
                </div>
                <div class="setup-small">
                    Mnemo knows your academic context.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        render_html(
            """
            <div class="setup-box">
                <div class="setup-status">
                    ○ setup incomplete
                </div>
                <div class="setup-small">
                    Give Mnemo a little context first.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.button(
        "⚙️ Set up Mnemo",
        use_container_width=True,
    ):
        go_to("Classes")

    render_html(
        """
        <div class="sidebar-section">
            the idea
        </div>

        <div class="sidebar-tagline">
            Mnemo connects your timetable,
            syllabus and study material so
            you spend less time figuring out
            what to do next.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# TODAY
# ============================================================

def render_today():

    hour = datetime.now().hour

    if hour < 12:
        greeting = "good morning."
        emoji = "☀️"
    elif hour < 18:
        greeting = "good afternoon."
        emoji = "🌷"
    else:
        greeting = "good evening."
        emoji = "🌙"

    today = today_name()
    todays_classes = [
        item
        for item in st.session_state.timetable
        if str(item.get("day", "")).lower() == today.lower()
    ]
    todays_classes.sort(key=lambda x: parse_time(x.get("start", "")))

    class_count = len(todays_classes)
    concept_count = st.session_state.concepts_learned
    recall_questions = len(st.session_state.quiz_history)

    if not st.session_state.academic_ready:
        focus_line = "Start by giving Mnemo the context it needs to make your day useful."
    elif todays_classes:
        focus_line = f"You have {class_count} scheduled {'class' if class_count == 1 else 'classes'} today. Start with the first one."
    elif st.session_state.study_material:
        focus_line = "Your timetable is quiet today. A good day to turn study material into memory."
    else:
        focus_line = "Nothing is demanding your attention yet. Set up your academic space and let Mnemo take it from there."

    render_html(
        f"""
        <div class="premium-hero">
            <div class="premium-kicker">MNEMO · ACADEMIC SPACE</div>
            <div class="premium-date">{format_today()}</div>
            <h1 class="premium-title">{greeting} {emoji}</h1>
            <div class="premium-subtitle">
                Here's what deserves your attention today — without the noise.
            </div>

            <div class="focus-panel">
                <div class="focus-label">today's focus</div>
                <div class="focus-copy">{esc(focus_line)}</div>
            </div>

            <div class="stat-strip">
                <div class="stat-chip"><strong>{class_count}</strong> classes</div>
                <div class="stat-chip"><strong>{concept_count}</strong> concepts</div>
                <div class="stat-chip"><strong>{recall_questions}</strong> recall questions</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    atmosphere_options = [
        "quiet morning ☕",
        "locked in 🎯",
        "low-energy but trying 🌱",
        "exam mode 🫡",
        "soft study evening 🌙",
    ]

    control_col1, control_col2 = st.columns([1, 0.55])
    with control_col2:
        atmosphere = st.selectbox(
            "study atmosphere",
            atmosphere_options,
            index=atmosphere_options.index(st.session_state.study_atmosphere),
            label_visibility="collapsed",
        )
    st.session_state.study_atmosphere = atmosphere

    if not st.session_state.academic_ready:
        render_html(
            """
            <div class="setup-hero">
                <div class="setup-kicker">your academic space</div>
                <div class="setup-title">Give Mnemo the semester. We'll handle the organization.</div>
                <div class="setup-copy">
                    Upload your timetable, syllabus, teacher references or notices.
                    Mnemo turns that information into structured context you can actually use.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        col1, col2 = st.columns(2, gap="large")
        with col1:
            render_html(
                """
                <div class="mnemo-card pista">
                    <div class="card-kicker">what happens next</div>
                    <div class="card-heading">less searching. more doing.</div>
                    <div class="card-text">
                        Today's classes, missed-class recovery, study packs and active recall — connected in one place.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            render_html(
                """
                <div class="mnemo-card lilac">
                    <div class="card-kicker">your first move</div>
                    <div class="card-heading">build your academic space.</div>
                    <div class="card-text">
                        Add a little context now. Update it whenever your semester changes.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")
        if st.button("build my academic space →", type="primary", use_container_width=True):
            go_to("Classes")
        return

    st.write("")
    col1, col2 = st.columns([1.5, 0.85], gap="large")

    with col1:
        render_html(
            """
            <div class="premium-section-intro">
                <div class="section-title">today</div>
                <div class="section-subtitle">Your schedule, distilled to what matters.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not todays_classes:
            render_html(
                """
                <div class="empty-state">
                    <div class="empty-icon">🌿</div>
                    <div class="empty-title">A quiet academic day.</div>
                    <div class="empty-text">
                        Nothing is scheduled today. Review a topic or build a study pack instead.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for item in todays_classes:
                render_html(
                    f"""
                    <div class="today-card">
                        <div class="today-card-top">
                            <div>
                                <div class="today-time">{esc(item.get("start", ""))} — {esc(item.get("end", ""))}</div>
                                <div class="today-subject">{esc(item.get("subject", "Unknown"))}</div>
                                <div class="today-topic">{esc(item.get("topic", "Topic not specified"))}</div>
                            </div>
                            <div class="today-teacher">{esc(item.get("teacher", "Unknown"))}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with col2:
        render_html(
            """
            <div class="premium-section-intro">
                <div class="section-title">your space</div>
                <div class="section-subtitle">A small snapshot of your learning system.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        render_html(
            f"""
            <div class="premium-note">
                <div class="card-kicker">memory</div>
                <div class="premium-note-title">{concept_count} concepts explored</div>
                <div class="premium-note-text">Keep turning material into things you can actually retrieve.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        if st.button("recover a missed class →", use_container_width=True):
            go_to("Catch-up")

    st.write("")
    render_html(
        f"""
        <div class="atmosphere">
            <div class="atmosphere-label">today's study atmosphere</div>
            <div class="atmosphere-text">{esc(st.session_state.study_atmosphere)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CLASSES
# ============================================================

def render_classes():

    render_html(
        """
        <div class="hero-chip">
            YOUR ACADEMIC SPACE
        </div>

        <div class="eyebrow">
            setup · context · reference
        </div>

        <h1 class="page-title">
            classes.
        </h1>

        <p class="page-subtitle">
            Give Mnemo the information it needs to understand
            your academic world.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    tabs = st.tabs(
        [
            "timetable",
            "syllabus",
            "teachers",
            "notices",
        ]
    )

    # --------------------------------------------------------
    # TIMETABLE
    # --------------------------------------------------------

    with tabs[0]:

        render_html(
            """
            <div class="section-title">
                your timetable 🗓️
            </div>

            <div class="section-subtitle">
                Upload a file or paste the timetable here.
            </div>
            """,
            unsafe_allow_html=True,
        )

        uploaded = st.file_uploader(
            "Upload timetable",
            type=["txt", "pdf", "docx"],
            key="timetable_upload",
        )

        pasted = st.text_area(
            "Or paste it here",
            height=180,
            placeholder="Monday 9:00–10:00 Physics — Vectors...",
            key="timetable_paste",
        )

        if uploaded:
            st.session_state.raw_timetable = read_uploaded_file(uploaded)

        elif pasted.strip():
            st.session_state.raw_timetable = pasted

    # --------------------------------------------------------
    # SYLLABUS
    # --------------------------------------------------------

    with tabs[1]:

        render_html(
            """
            <div class="section-title">
                your syllabus 📚
            </div>

            <div class="section-subtitle">
                Give Mnemo the topics you're expected to learn.
            </div>
            """,
            unsafe_allow_html=True,
        )

        uploaded = st.file_uploader(
            "Upload syllabus",
            type=["txt", "pdf", "docx"],
            key="syllabus_upload",
        )

        pasted = st.text_area(
            "Or paste it here",
            height=180,
            placeholder="Physics: Vectors, Kinematics...",
            key="syllabus_paste",
        )

        if uploaded:
            st.session_state.raw_syllabus = read_uploaded_file(uploaded)

        elif pasted.strip():
            st.session_state.raw_syllabus = pasted

    # --------------------------------------------------------
    # TEACHERS
    # --------------------------------------------------------

    with tabs[2]:

        render_html(
            """
            <div class="section-title">
                teacher references 👩‍🏫
            </div>

            <div class="section-subtitle">
                Names, subjects, references or contact information.
            </div>
            """,
            unsafe_allow_html=True,
        )

        uploaded = st.file_uploader(
            "Upload teacher references",
            type=["txt", "pdf", "docx"],
            key="teacher_upload",
        )

        pasted = st.text_area(
            "Or paste them here",
            height=180,
            placeholder="Dr. Sharma — Physics — Room 204...",
            key="teacher_paste",
        )

        if uploaded:
            st.session_state.raw_teachers = read_uploaded_file(uploaded)

        elif pasted.strip():
            st.session_state.raw_teachers = pasted

    # --------------------------------------------------------
    # NOTICES
    # --------------------------------------------------------

    with tabs[3]:

        render_html(
            """
            <div class="section-title">
                notices 📌
            </div>

            <div class="section-subtitle">
                Paste important announcements so Mnemo can keep
                them alongside your academic context.
            </div>
            """,
            unsafe_allow_html=True,
        )

        uploaded = st.file_uploader(
            "Upload notices",
            type=["txt", "pdf", "docx"],
            key="notice_upload",
        )

        pasted = st.text_area(
            "Or paste them here",
            height=180,
            placeholder="Internal assessment on Friday...",
            key="notice_paste",
        )

        if uploaded:
            st.session_state.raw_notices = read_uploaded_file(uploaded)

        elif pasted.strip():
            st.session_state.raw_notices = pasted

    st.write("")

    if st.button(
        "build / update my academic space →",
        type="primary",
        use_container_width=True,
    ):

        if not any(
            [
                st.session_state.raw_timetable.strip(),
                st.session_state.raw_syllabus.strip(),
                st.session_state.raw_teachers.strip(),
                st.session_state.raw_notices.strip(),
            ]
        ):

            st.warning(
                "Give Mnemo at least a little academic context first 🌷"
            )

        else:

            with st.spinner("putting your academic world together..."):

                success = build_academic_profile()

            if success:
                st.success("Your academic space is ready ✨")
                st.rerun()

    # --------------------------------------------------------
    # EXISTING DATA
    # --------------------------------------------------------

    if st.session_state.academic_ready:

        st.write("")

        render_html(
            """
            <div class="section-title">
                what Mnemo knows
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2, c3, c4 = st.columns(4)

        metrics = [
            ("classes", len(st.session_state.timetable)),
            ("syllabus areas", len(st.session_state.syllabus)),
            ("teachers", len(st.session_state.teachers)),
            ("notices", len(st.session_state.notices)),
        ]

        for col, (label, value) in zip(
            [c1, c2, c3, c4],
            metrics,
        ):

            with col:

                render_html(
                    f"""
                    <div class="metric-card">

                        <div class="metric-label">
                            {label}
                        </div>

                        <div class="metric-number">
                            {value}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.write("")

        if st.session_state.timetable:

            render_html(
                """
                <div class="section-title">
                    timetable
                </div>
                """,
                unsafe_allow_html=True,
            )

            for item in st.session_state.timetable:

                render_html(
                    f"""
                    <div class="class-item">

                        <div class="class-time">
                            {esc(item.get("day", ""))}
                        </div>

                        <div style="flex:1;">
                            <div class="class-subject">
                                {esc(item.get("subject", "Unknown"))}
                            </div>

                            <div class="class-topic">
                                {esc(item.get("topic", "Topic not specified"))}
                            </div>
                        </div>

                        <div class="class-teacher">
                            {esc(item.get("start", ""))}
                            –
                            {esc(item.get("end", ""))}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ============================================================
# CATCH-UP
# ============================================================

def render_catchup():

    render_html(
        """
        <div class="hero-chip">
            MISSED CLASS RECOVERY
        </div>

        <div class="eyebrow">
            no guilt · just the next step
        </div>

        <h1 class="page-title">
            missed something?
        </h1>

        <p class="page-subtitle">
            Tell Mnemo what you missed and we'll work backwards
            from your academic context.
        </p>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.academic_ready:

        st.write("")

        render_html(
            """
            <div class="empty-state">

                <div class="empty-icon">
                    🧭
                </div>

                <div class="empty-title">
                    Mnemo needs your academic context first.
                </div>

                <div class="empty-text">
                    Add your timetable and syllabus so Mnemo
                    can figure out what happened in the missed class.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        if st.button("set up academic space →"):
            go_to("Classes")

        return

    st.write("")

    subjects = sorted(
        set(
            item.get("subject", "Unknown")
            for item in st.session_state.timetable
            if item.get("subject")
        )
    )

    if not subjects:

        subjects = [
            item.get("subject", "Unknown")
            for item in st.session_state.syllabus
            if item.get("subject")
        ]

    if not subjects:

        subjects = ["Your subject"]

    subject = st.selectbox(
        "Which subject did you miss?",
        subjects,
    )

    missed_date = st.date_input(
        "Which day?",
        value=date.today(),
    )

    context = st.text_area(
        "Anything else you remember? optional",
        placeholder="Teacher mentioned something about a test...",
        height=120,
    )

    if st.button(
        "figure out what I missed →",
        type="primary",
    ):

        with st.spinner("tracing the class..."):

            plan = generate_catchup(
                subject,
                missed_date.isoformat(),
                context,
            )

        if plan:
            st.rerun()

    plan = st.session_state.missed_plan

    if not plan:
        return

    st.write("")

    confidence = esc(plan.get("confidence", "Unknown"))

    render_html(
        f"""
        <div class="mnemo-card lilac">

            <div class="card-kicker">
                scheduled topic
            </div>

            <div class="card-heading">
                {esc(plan.get("scheduled_topic", "Unknown"))}
            </div>

            <div class="card-text">
                Confidence: <strong>{confidence}</strong>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    col1, col2 = st.columns(2)

    with col1:

        render_html(
            f"""
            <div class="mnemo-card pista">

                <div class="card-kicker">
                    what is confirmed
                </div>

                <div class="card-text">
                    {esc(plan.get("what_is_confirmed", "Unknown"))}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:

        render_html(
            f"""
            <div class="mnemo-card butter">

                <div class="card-kicker">
                    teacher
                </div>

                <div class="card-heading">
                    {esc(plan.get("teacher", "Unknown"))}
                </div>

                <div class="card-text">
                    {esc(plan.get("note", ""))}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    what_to_learn = safe_list(plan.get("what_to_learn"))
    steps = safe_list(plan.get("catch_up_steps"))
    questions = safe_list(plan.get("quick_check_questions"))

    if what_to_learn:

        render_html(
            """
            <div class="section-title">
                what to learn
            </div>
            """,
            unsafe_allow_html=True,
        )

        for item in what_to_learn:

            render_html(
                f"""
                <div class="mnemo-card">
                    <div class="card-text">
                        • {esc(item)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.write("")

    if steps:

        render_html(
            """
            <div class="section-title">
                your catch-up route
            </div>
            """,
            unsafe_allow_html=True,
        )

        for index, step in enumerate(steps, start=1):

            render_html(
                f"""
                <div class="class-item">

                    <div class="class-time">
                        {index:02d}
                    </div>

                    <div style="flex:1;">
                        <div class="class-subject">
                            {esc(step)}
                        </div>
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    if questions:

        st.write("")

        render_html(
            """
            <div class="section-title">
                quick check 👀
            </div>
            """,
            unsafe_allow_html=True,
        )

        for question in questions:

            render_html(
                f"""
                <div class="mnemo-card pink">
                    <div class="card-text">
                        {esc(question)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.write("")


# ============================================================
# STUDY
# ============================================================

def render_study():

    render_html(
        """
        <div class="hero-chip">
            STUDY ENGINE
        </div>

        <div class="eyebrow">
            material → understanding → memory
        </div>

        <h1 class="page-title">
            let's study.
        </h1>

        <p class="page-subtitle">
            Give Mnemo your material and we'll turn it into
            something much easier to work with.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    topic = st.text_input(
        "What are you studying?",
        value=st.session_state.study_topic,
        placeholder="e.g. vectors, cell division, thermodynamics...",
    )

    st.session_state.study_topic = topic

    uploaded = st.file_uploader(
        "Upload your material",
        type=["txt", "pdf", "docx"],
        key="study_upload",
    )

    material = st.text_area(
        "Or paste your study material",
        height=260,
        placeholder="Paste notes, lecture text, textbook material, etc.",
        value=st.session_state.study_material,
    )

    if uploaded:

        material = read_uploaded_file(uploaded)

    if st.button(
        "build my study pack →",
        type="primary",
        use_container_width=True,
    ):

        if not material.strip():

            st.warning(
                "Give Mnemo some material first 📚"
            )

        else:

            with st.spinner(
                "turning this into something your brain can actually use..."
            ):

                result = generate_study_pack(material)

            if result:

                st.session_state.study_material = material
                st.session_state.study_summary = result.get(
                    "summary",
                    "",
                )
                st.session_state.study_simple_explanation = result.get(
                    "simple_explanation",
                    "",
                )
                st.session_state.study_concepts = safe_list(
                    result.get("concepts")
                )
                st.session_state.study_flashcards = safe_list(
                    result.get("flashcards")
                )

                st.session_state.concepts_learned = len(
                    st.session_state.study_concepts
                )

                st.session_state.sessions_completed += 1

                st.rerun()

    if not st.session_state.study_summary:
        return

    st.write("")

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    render_html(
        """
        <div class="section-title">
            the big picture
        </div>

        <div class="section-subtitle">
            If you remember nothing else, start here.
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_html(
        f"""
        <div class="mnemo-card pink">

            <div class="card-text">
                {esc(st.session_state.study_summary)}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    # --------------------------------------------------------
    # SIMPLE EXPLANATION
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        render_html(
            """
            <div class="section-title">
                explain it simply 🌱
            </div>
            """,
            unsafe_allow_html=True,
        )

        render_html(
            f"""
            <div class="mnemo-card pista">

                <div class="card-text">
                    {esc(st.session_state.study_simple_explanation)}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:

        render_html(
            """
            <div class="section-title">
                key concepts
            </div>
            """,
            unsafe_allow_html=True,
        )

        concepts_html = ""

        for concept in st.session_state.study_concepts:

            concepts_html += (
                f'<span class="concept-pill">'
                f'{esc(concept)}'
                f'</span>'
            )

        render_html(
            f"""
            <div class="mnemo-card lilac">
                {concepts_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # --------------------------------------------------------
    # MEMORY MAP
    # --------------------------------------------------------

    render_html(
        """
        <div class="section-title">
            memory map 🧠
        </div>

        <div class="section-subtitle">
            Think of this as the skeleton of the topic.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.study_concepts:

        for index, concept in enumerate(
            st.session_state.study_concepts,
            start=1,
        ):

            render_html(
                f"""
                <div class="class-item">

                    <div class="class-time">
                        {index:02d}
                    </div>

                    <div style="flex:1;">
                        <div class="class-subject">
                            {esc(concept)}
                        </div>

                        <div class="class-topic">
                            one piece of the bigger picture
                        </div>
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    # --------------------------------------------------------
    # FLASHCARDS
    # --------------------------------------------------------

    st.write("")

    render_html(
        """
        <div class="section-title">
            memory cards 🃏
        </div>

        <div class="section-subtitle">
            Read the question first. Try to answer before revealing it.
        </div>
        """,
        unsafe_allow_html=True,
    )

    for card in st.session_state.study_flashcards:

        question = esc(card.get("question", ""))
        answer = esc(card.get("answer", ""))

        render_html(
            f"""
            <div class="flashcard">

                <div class="flashcard-label">
                    remember this
                </div>

                <div class="flashcard-question">
                    {question}
                </div>

                <div class="flashcard-answer">
                    {answer}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    if st.button(
        "⚡ test myself now",
        type="primary",
        use_container_width=True,
    ):

        st.session_state.page = "Recall"
        start_quiz()
        st.rerun()


# ============================================================
# RECALL
# ============================================================

def render_recall():

    render_html(
        """
        <div class="hero-chip">
            ACTIVE RECALL
        </div>

        <div class="eyebrow">
            don't just reread it.
        </div>

        <h1 class="page-title">
            what do you actually remember?
        </h1>

        <p class="page-subtitle">
            Mnemo adjusts the next question based on how you're doing.
        </p>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.study_material:

        st.write("")

        render_html(
            """
            <div class="empty-state">

                <div class="empty-icon">
                    🧠
                </div>

                <div class="empty-title">
                    nothing to recall yet.
                </div>

                <div class="empty-text">
                    Build a study pack first.
                    Then Mnemo can test what actually stuck.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        if st.button("go study →"):
            go_to("Study")

        return

    # --------------------------------------------------------
    # START
    # --------------------------------------------------------

    if not st.session_state.quiz_started:

        st.write("")

        render_html(
            """
            <div class="mnemo-card lilac">

                <div class="card-kicker">
                    ready?
                </div>

                <div class="card-heading">
                    let's see what's actually in there 👀
                </div>

                <div class="card-text">
                    Five questions. Adaptive difficulty.
                    No judgment if your brain decides to disappear.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        if st.button(
            "start recall →",
            type="primary",
            use_container_width=True,
        ):

            start_quiz()
            st.rerun()

        return

    # --------------------------------------------------------
    # FINISHED
    # --------------------------------------------------------

    if st.session_state.quiz_index >= 5:

        score = st.session_state.quiz_score

        percentage = round(
            (score / 5) * 100
        )

        render_html(
            f"""
            <div class="mnemo-card pista">

                <div class="card-kicker">
                    session complete
                </div>

                <div class="card-heading">
                    {percentage}% recall
                </div>

                <div class="card-text">
                    You got {score} out of 5 questions right.
                    The important part is what you learned from the misses.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "try again",
                use_container_width=True,
            ):

                start_quiz()
                st.rerun()

        with col2:

            if st.button(
                "back to study",
                use_container_width=True,
            ):

                finish_quiz()
                go_to("Study")

        return

    # --------------------------------------------------------
    # QUESTION
    # --------------------------------------------------------

    question_data = st.session_state.current_question

    if not question_data:

        question_data = generate_question()
        st.session_state.current_question = question_data

    if not question_data:

        st.error(
            "Mnemo couldn't make a question right now."
        )
        return

    question_number = st.session_state.quiz_index + 1

    render_html(
        f"""
        <div class="question-box">

            <div class="question-number">
                question {question_number} / 5
            </div>

            <div class="question-text">
                {esc(question_data.get("question", ""))}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    options = safe_list(
        question_data.get("options")
    )

    answer = st.radio(
        "Choose an answer",
        options,
        index=None,
        key=f"quiz_answer_{st.session_state.quiz_index}",
    )

    if not st.session_state.quiz_answered:

        if st.button(
            "lock it in →",
            type="primary",
        ):

            if answer is None:

                st.warning(
                    "Pick an answer first 👀"
                )

            else:

                selected_index = options.index(answer)
                correct_index = int(
                    question_data.get("answer", 0)
                )

                correct = (
                    selected_index == correct_index
                )

                if correct:
                    st.session_state.quiz_score += 1

                    st.session_state.quiz_difficulty = (
                        "Hard"
                        if st.session_state.quiz_difficulty == "Medium"
                        else "Medium"
                    )

                else:

                    st.session_state.quiz_difficulty = (
                        "Easy"
                        if st.session_state.quiz_difficulty == "Medium"
                        else "Medium"
                    )

                st.session_state.quiz_history.append(
                    {
                        "question": question_data.get(
                            "question",
                            "",
                        ),
                        "correct": correct,
                    }
                )

                st.session_state.last_result = correct
                st.session_state.last_explanation = question_data.get(
                    "explanation",
                    "",
                )

                st.session_state.quiz_answered = True

                st.rerun()

    else:

        correct = st.session_state.last_result

        if correct:

            render_html(
                f"""
                <div class="result-good">

                    <div class="result-title">
                        nailed it. 🌱
                    </div>

                    <div class="result-text">
                        {esc(st.session_state.last_explanation)}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            render_html(
                f"""
                <div class="result-bad">

                    <div class="result-title">
                        oop — almost. 👀
                    </div>

                    <div class="result-text">
                        {esc(st.session_state.last_explanation)}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")

        if st.button(
            "next question →",
            type="primary",
        ):

            st.session_state.quiz_index += 1
            st.session_state.quiz_answered = False
            st.session_state.current_question = None
            st.session_state.last_result = None
            st.session_state.last_explanation = ""

            st.rerun()


# ============================================================
# PROGRESS
# ============================================================

def render_progress():

    render_html(
        """
        <div class="hero-chip">
            YOUR PROGRESS
        </div>

        <div class="eyebrow">
            useful numbers only
        </div>

        <h1 class="page-title">
            getting somewhere.
        </h1>

        <p class="page-subtitle">
            Mnemo tracks learning activity, not fake productivity points.
        </p>
        """,
        unsafe_allow_html=True,
    )

    history = st.session_state.quiz_history

    total_questions = len(history)

    if total_questions:

        correct_answers = sum(
            1
            for item in history
            if item.get("correct")
        )

        recall_percentage = round(
            (correct_answers / total_questions) * 100
        )

    else:

        recall_percentage = 0

    st.write("")

    c1, c2, c3, c4 = st.columns(4)

    metrics = [
        ("recall", f"{recall_percentage}%"),
        ("questions", total_questions),
        (
            "concepts",
            len(st.session_state.study_concepts),
        ),
        (
            "study sessions",
            st.session_state.sessions_completed,
        ),
    ]

    for col, (label, value) in zip(
        [c1, c2, c3, c4],
        metrics,
    ):

        with col:

            render_html(
                f"""
                <div class="metric-card">

                    <div class="metric-label">
                        {label}
                    </div>

                    <div class="metric-number">
                        {value}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    col1, col2 = st.columns(2)

    with col1:

        render_html(
            """
            <div class="section-title">
                study pattern
            </div>
            """,
            unsafe_allow_html=True,
        )

        if total_questions == 0:

            pattern = """
            You haven't done a recall session yet.
            That's okay. Start with one study pack.
            """

        elif recall_percentage >= 80:

            pattern = """
            Your recall is looking strong.
            Time to make the questions harder.
            """

        elif recall_percentage >= 50:

            pattern = """
            You're getting there.
            A little more retrieval practice should help.
            """

        else:

            pattern = """
            The material probably needs another pass.
            Try studying the concepts, then recall them again.
            """

        render_html(
            f"""
            <div class="mnemo-card pista">

                <div class="card-text">
                    {pattern}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:

        render_html(
            """
            <div class="section-title">
                recent recall
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not history:

            render_html(
                """
                <div class="mnemo-card lilac">

                    <div class="card-text">
                        Nothing here yet.
                        Your first recall session will show up here.
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            recent = history[-5:][::-1]

            for item in recent:

                if item.get("correct"):
                    label = "✓ remembered"
                    background = SOFT_PISTA
                else:
                    label = "↗ revisit this"
                    background = SOFT_PINK

                render_html(
                    f"""
                    <div style="
                        background:{background};
                        border-radius:16px;
                        padding:0.8rem 1rem;
                        margin-bottom:0.55rem;
                        font-size:0.78rem;
                        font-weight:700;
                        color:{DEEP_BERRY};
                    ">
                        {label}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.write("")

    render_html(
        """
        <div class="mnemo-card butter">

            <div class="card-kicker">
                little reminder
            </div>

            <div class="card-heading">
                studying isn't supposed to look productive.
            </div>

            <div class="card-text">
                If you understand more than you did yesterday,
                Mnemo considers that a win.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PAGE ROUTER
# ============================================================

if st.session_state.page == "Today":
    render_today()

elif st.session_state.page == "Classes":
    render_classes()

elif st.session_state.page == "Catch-up":
    render_catchup()

elif st.session_state.page == "Study":
    render_study()

elif st.session_state.page == "Recall":
    render_recall()

elif st.session_state.page == "Progress":
    render_progress()


# ============================================================
# FOOTER
# ============================================================

render_html(
    """
    <div class="footer">
        mnemo 🧠 · made for the days when your brain has 47 tabs open
    </div>
    """,
    unsafe_allow_html=True,
)