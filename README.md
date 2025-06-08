# 🤖 AI Resume Screener Dashboard with LLaMA3 + Streamlit

A smart, interactive dashboard that evaluates multiple resumes against a job description using a local LLM (LLaMA3 via Ollama) and presents a professional, HR-friendly UI for shortlisting candidates.

Built for the **Cyfuture AI Hackathon**.

---

## 🚀 Features

- 📄 Upload Job Description & multiple PDF resumes  
- 🧠 LLM-based resume scoring (0–100) with reasoning  
- 🎖️ Highlights top candidates visually  
- 📊 Resume match scores shown as horizontal progress bars  
- 🧑‍💼 Candidate info cards: Name, Email, Phone, Skills  
- 📋 Tabular summary of all applications  
- 💬 AI HR Chatbot to ask queries like:  
  - *Who is best for Data Scientist role?*  
  - *Who scored above 70%?*  
  - *List candidates with Python skills*

---

## 🧠 How It Works

1. Paste or upload the job description.  
2. Upload multiple resumes in PDF format.  
3. LLaMA3 evaluates and scores each resume against the JD.  
4. Dashboard displays:  
   - Candidate cards  
   - Resume match % with progress bar  
   - Interactive HR chatbot

---

## 📦 Setup Instructions

### 1. Clone the Repo & Setup Virtual Environment

```bash
git clone [https://github.com/your-username/llama3-resume-screener](https://github.com/sreevamsi2005/Cyfuture-AI-Hackathon).git
cd Cyfuture-AI-Hackathon
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Ollama with LLaMA3 Model

Make sure you have [Ollama](https://ollama.com/) installed.

```bash
ollama run llama3
```

### 4. Launch the Streamlit App

```bash
streamlit run resume_dashboard_app.py
```

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit  
- **LLM:** LLaMA3 via Ollama (runs locally)  
- **Backend:** Python, PyPDF2, RegEx  
- **Visualization:** Streamlit UI Components

---

## 📸 UI Preview (Key Screens)

- ✅ Candidate Resume Cards  
- 📊 Match % Score Bars  
- 💬 AI HR Chatbot Panel

---

## 🤖 Example Chatbot Prompts

- Who is best for Machine Learning role?  
- Show resumes with score above 80%.  
- List all candidates with SQL skills.  
- Which candidate has experience in TensorFlow?

---
