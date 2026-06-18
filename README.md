# 🔍 AI Research Assistant

An intelligent research assistant powered by a multi-agent system built with LangGraph and Groq LLM. Give it any topic and it will research the web, analyze the information, and generate a professional structured report — and it remembers your research across sessions.

## 🚀 Live Demo
**👉 [Click here to try the app](https://ai-research-assistant-i2ep8ufovhkbpcxnrzawdy.streamlit.app/)**

## 🤖 How it works
The app uses a 4-agent pipeline powered by LangGraph:

- 🧠 **Planner Agent** — breaks your topic into 3 specific research questions
- 🔍 **Researcher Agent** — searches the web for relevant information using Tavily
- ✍️ **Writer Agent** — writes a structured report with Introduction, Key Findings, and Conclusion
- ✅ **Reviewer Agent** — improves and polishes the final report

You can ask follow-up questions after the report is generated, and thanks to **Mem0**, the assistant remembers your past research even across different sessions.

## 💬 Features
- Multi-agent research pipeline using LangGraph
- **Persistent long-term memory (Mem0)** — remembers your research across sessions, even on different days
- Real-time web search using Tavily
- Follow-up questions with full report context
- Structured professional reports
- Download report as text file
- Clean and simple Streamlit interface

## 🧠 Two Memory Layers
- **Short-term** — within a session, follow-ups have the full report context (LangGraph checkpointer)
- **Long-term (Mem0)** — research is saved per user and recalled in future sessions, so reports build on your past work

## 🛠️ Tech Stack
- **LangGraph** — multi-agent workflow orchestration
- **Groq + LLaMA 3.3 70B** — free LLM
- **LangChain** — LLM framework
- **Mem0** — persistent cross-session memory
- **Tavily** — real-time web search
- **Streamlit** — web interface


## ▶️ Run Locally

1. Clone the repo
git clone https://github.com/Murtaza-data/ai-research-assistant.git
cd ai-research-assistant

2. Install dependencies
pip install -r requirements.txt

3. Add your keys (Tavily and Mem0 in `.streamlit/secrets.toml`, Groq in the sidebar):

TAVILY_API_KEY = "your-tavily-key"
MEM0_API_KEY = "your-mem0-key"

4. Run the app
streamlit run app.py




