import streamlit as st
import PyPDF2
import os
import re
import pandas as pd
import requests

# ------------------ CONFIG ------------------
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

# ------------------ UTILITIES ------------------
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def parse_resume(text):
    lines = text.strip().split('\n')
    name_line = next((line.strip() for line in lines if line.strip()), "-")
    
    return {
        "name": name_line,
        "email": re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text),
        "phone": re.findall(r"\+?\d[\d\-\s]{8,14}\d", text),
        "skills": re.findall(r"Skills[:\-]?\s*(.*)", text, re.IGNORECASE),
        "education": re.findall(r"(B\.Tech|M\.Tech|PhD|MBA|Bachelors|Masters)", text, re.IGNORECASE),
        "experience": re.findall(r"(\d+)\+?\s+years?", text),
    }


def get_resume_score(resume_text: str, jd: str) -> dict:
    prompt = f"""You're an AI HR expert.
Evaluate the following resume against this job description.

Job Description:
{jd}

Resume:
{resume_text}

Give a score out of 100 and explain why.

Return in this format:
SCORE: <number>
REASON: <reason>
"""
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    })
    if response.status_code == 200:
        content = response.json()["response"]
        score_match = re.search(r"SCORE:\s*(\d+)", content)
        reason_match = re.search(r"REASON:\s*(.*)", content, re.DOTALL)
        score = int(score_match.group(1)) if score_match else 0
        reason = reason_match.group(1).strip() if reason_match else "No explanation."
        return {"score": score, "reason": reason}
    else:
        return {"score": 0, "reason": "Failed to fetch from LLM."}

# ------------------ UI CONFIG ------------------
st.set_page_config(page_title="LLM Resume Screener", layout="wide")
st.markdown("<h1 style='text-align: center;'>🤖 AI Resume Screener Dashboard</h1>", unsafe_allow_html=True)

# ------------------ SIDEBAR INPUTS ------------------
with st.sidebar:
    st.header("📄 Job & Resume Inputs")
    jd = st.text_area("🧾 Paste Job Description", height=200)
    uploaded_files = st.file_uploader("📤 Upload Resumes (PDF)", type=["pdf"], accept_multiple_files=True)
    process_btn = st.button("⚙️ Analyze Resumes")

# ------------------ PROCESS RESUMES ------------------
if process_btn and jd and uploaded_files:
    data = []
    for file in uploaded_files:
        resume_text = extract_text_from_pdf(file)
        parsed = parse_resume(resume_text)
        score_data = get_resume_score(resume_text, jd)

        data.append({
            "Filename": file.name,
            "Name": parsed.get("name", ["-"])[0] if parsed.get("name") else "-",
            "Email": parsed.get("email", ["-"])[0] if parsed.get("email") else "-",
            "Phone": parsed.get("phone", ["-"])[0] if parsed.get("phone") else "-",
            "Score": score_data["score"],
            "Skills": parsed.get("skills", ["-"])[0] if parsed.get("skills") else "-",
            "Reason": score_data["reason"],
        })

    df = pd.DataFrame(data).sort_values(by="Score", ascending=False)
    st.session_state["resume_df"] = df

# ------------------ DISPLAY DASHBOARD ------------------
if "resume_df" in st.session_state:
    df = st.session_state["resume_df"]
    top_score = df["Score"].max()

    st.subheader("📊 Candidate Overview (Sorted by Score)")
    styled_df = df.drop(columns=["Reason"]).copy()
    styled_df["Name"] = styled_df.apply(lambda row: f"{row['Name']} 🎖️" if row["Score"] == top_score else row["Name"], axis=1)
    st.dataframe(styled_df, use_container_width=True)

    st.subheader("🧑 Detailed Resume Cards")
    for _, row in df.iterrows():
        with st.container():
            st.markdown("---")
            col1, col2 = st.columns([1, 3])

            with col1:
                name_display = f"{row['Name']} 🎖️" if row["Score"] == top_score else row["Name"]
                st.markdown(f"### {name_display}")
                st.markdown(f"📧 **Email:** {row['Email']}")
                st.markdown(f"📞 **Phone:** {row['Phone']}")

            with col2:
                st.markdown(f"💼 **Skills:** {row['Skills']}")
                st.markdown("📊 **Resume Match Score:**")
                st.progress(row["Score"] / 100)
                st.markdown(f"**{row['Score']}% Match**")

            with st.expander("🔍 AI Feedback (Why this score?)"):
                st.markdown(row["Reason"])

# ------------------ AI CHAT HR BOT ------------------
st.subheader("💬 Ask HR AI About Candidates")
chat_query = st.text_input("🔎 Example: 'Who is best for ML role?'")

if chat_query and "resume_df" in st.session_state:
    context = st.session_state["resume_df"].to_string()
    chat_prompt = f"""You are an HR AI assistant.

You have the following candidate data:

{context}

Answer the following question using this data:

{chat_query}
"""
    chat_response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": chat_prompt,
        "stream": False
    })
    if chat_response.status_code == 200:
        st.markdown("### 🤖 AI Response:")
        with st.chat_message("ai"):
            st.markdown(chat_response.json()["response"])
    else:
        st.error("❌ Failed to get response from Ollama LLM.")
