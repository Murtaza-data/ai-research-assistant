# 🔍 AI Research Assistant

An intelligent research assistant powered by a **multi-agent system** built with LangGraph and Groq LLM. Give it any topic and it will research the web, analyze the information, and generate a professional structured report.

## 🚀 Live Demo
[Click here to try the app](https://ai-research-assistant-i2ep8ufovhkbpcxnrzawdy.streamlit.app/)

## 🤖 How it works
The app uses a **4-agent pipeline** powered by LangGraph:

1. 🧠 **Planner Agent** — breaks your topic into 3 specific research questions
2. 🔍 **Researcher Agent** — searches the web for relevant information using DuckDuckGo
3. ✍️ **Writer Agent** — writes a structured report with Introduction, Key Findings, and Conclusion
4. ✅ **Reviewer Agent** — improves and polishes the final report

You can also ask **follow-up questions** after the report is generated — the assistant remembers the full context of the report.

## 💬 Features
- Multi-agent research pipeline using LangGraph
- Real-time web search using DuckDuckGo
- Structured professional reports
- Follow-up questions with full report context
- Download report as text file
- Clean and simple Streamlit interface

## 🛠️ Tech Stack
- **LangGraph** — multi-agent workflow orchestration
- **Groq + LLaMA 3.1 8B** — free LLM
- **LangChain** — LLM framework
- **DuckDuckGo Search** — real-time web search tool
- **Streamlit** — web interface

## ▶️ Run Locally

1. Clone the repo
git clone https://github.com/Murtaza-data/ai-research-assistant.git
cd ai-research-assistant

2. Install dependencies
pip install -r requirements.txt

3. Run the app
streamlit run app.py

4. Enter your Groq API key in the sidebar


