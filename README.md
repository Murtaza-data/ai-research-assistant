🔍 AI Research Assistant
An intelligent research assistant powered by a multi-agent system built with LangGraph and Groq LLM. Give it any topic and it will research the web, analyze the information, and generate a professional structured report.

🚀 Live Demo
Click here to try the app

🤖 How it works
The app uses a 4-agent pipeline powered by LangGraph:

🧠 Planner Agent — breaks your topic into 3 specific research questions
🔍 Researcher Agent — searches the web for relevant information using DuckDuckGo
✍️ Writer Agent — writes a structured report with Introduction, Key Findings, and Conclusion
✅ Reviewer Agent — improves and polishes the final report
You can also ask follow-up questions after the report is generated — the assistant remembers the full context of the report.

💬 Features
Multi-agent research pipeline using LangGraph
Real-time web search using DuckDuckGo
Structured professional reports
Follow-up questions with full report context
Download report as text file
Clean and simple Streamlit interface
🛠️ Tech Stack
LangGraph — multi-agent workflow orchestration
Groq + LLaMA 3.1 8B — free LLM
LangChain — LLM framework
DuckDuckGo Search — real-time web search tool
Streamlit — web interface
▶️ Run Locally
Clone the repo
git clone https://github.com/Murtaza-data/ai-research-assistant.git
cd ai-research-assistant
Install dependencies
pip install -r requirements.txt
Run the app
streamlit run app.py
Enter your Groq API key in the sidebar
🔑 API Key
This app uses the Groq API which is free. Get your API key at console.groq.com

📁 Project Structure
ai-research-assistant/
├── app.py              
├── agent.py            
├── requirements.txt    
└── README.md           
👨‍💻 Author
