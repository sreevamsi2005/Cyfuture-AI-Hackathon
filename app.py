# resume_screening_app.py

import streamlit as st
import PyPDF2
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Resume Parsing Functions ---
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def parse_resume(text):
    return {
        "name": re.findall(r"Name[:\-]?\s*(\w+\s*\w+)", text),
        "email": re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text),
        "phone": re.findall(r"\+?\d[\d -]{8,12}\d", text),
        "skills": re.findall(r"Skills[:\-]?\s*(.*)", text, re.IGNORECASE),
        "education": re.findall(r"(B\.Tech|Bachelors|Masters|Ph\.D|M\.Tech)", text, re.IGNORECASE),
        "experience": re.findall(r"(\d+)\+?\s+years?", text),
    }

# --- JD Matching ---
def match_resume_to_jd(resume_text, jd_text):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_text, jd_text])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])
    return float(similarity[0][0])

# --- Chat Screening ---
screening_questions = [
    "Tell me briefly about yourself.",
    "What are your top 3 technical skills?",
    "Do you have experience working in teams?",
    "Are you open to relocation?",
]

def get_next_question(index):
    if index < len(screening_questions):
        return screening_questions[index]
    else:
        return None

# --- Scoring Logic ---
def calculate_score(jd_score, answers):
    chat_score = sum(1 for ans in answers if len(ans) > 20) / len(answers)
    final_score = (0.7 * jd_score) + (0.3 * chat_score)
    status = "Shortlisted" if final_score >= 0.5 else "Rejected"
    return round(final_score, 2), status

# --- Streamlit UI ---
st.set_page_config(page_title="AI Resume Screener", layout="centered")
st.title("🧠 AI Resume Screening Chatbot")

if "chat_index" not in st.session_state:
    st.session_state.chat_index = 0
    st.session_state.answers = []
    st.session_state.resume_data = {}
    st.session_state.jd_score = 0.0

uploaded_resume = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])
jd_input = st.text_area("📝 Paste Job Description")

if uploaded_resume and jd_input and st.button("Start Screening"):
    resume_text = extract_text_from_pdf(uploaded_resume)
    st.session_state.resume_data = parse_resume(resume_text)
    st.session_state.jd_score = match_resume_to_jd(resume_text, jd_input)
    st.success("Resume parsed & matched. Let’s start chat screening!")

if st.session_state.resume_data:
    question = get_next_question(st.session_state.chat_index)
    if question:
        user_response = st.text_input(f"Q{st.session_state.chat_index+1}: {question}")
        if st.button("Submit Answer"):
            st.session_state.answers.append(user_response)
            st.session_state.chat_index += 1
            st.experimental_rerun()
    else:
        score, status = calculate_score(st.session_state.jd_score, st.session_state.answers)
        st.subheader(f"✅ Final Score: {score}")
        st.success(f"Candidate Status: {status}")
        st.json(st.session_state.resume_data)
