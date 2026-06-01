import streamlit as st
from agent import build_graph
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import uuid

st.set_page_config(page_title="AI Research Assistant", page_icon="🔍", layout="wide")
st.title("🔍 AI Research Assistant")
st.caption("Powered by LangGraph + Groq")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Groq API Key", type="password")
    st.markdown("---")
    st.markdown("### How it works")
    st.markdown("1. 🧠 Planner breaks topic into questions")
    st.markdown("2. 🔍 Researcher searches the web")
    st.markdown("3. ✍️ Writer creates structured report")
    st.markdown("4. ✅ Reviewer improves the report")
    st.markdown("---")
    st.markdown("Built by **Mohammad Murtaza**")
    st.markdown("Powered by LangGraph + Groq + Streamlit")

if "graph_app" not in st.session_state:
    st.session_state.graph_app = None
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "report" not in st.session_state:
    st.session_state.report = ""
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "followup_answers" not in st.session_state:
    st.session_state.followup_answers = []

if api_key and st.session_state.graph_app is None:
    st.session_state.graph_app = build_graph(api_key)

topic = st.text_input("Enter a research topic:", placeholder="e.g. What is Machine Learning?", key="topic_input")

if st.button("Generate Report", type="primary", key="generate_btn"):
    if not api_key:
        st.error("Please enter your Groq API key in the sidebar.")
    elif not topic:
        st.error("Please enter a research topic.")
    else:
        with st.spinner("Researching and writing report... please wait..."):
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            result = st.session_state.graph_app.invoke({
                "topic": topic,
                "messages": [HumanMessage(content=f"Research topic: {topic}")],
                "sub_questions": [],
                "research": "",
                "report": "",
                "reviewed_report": ""
            }, config=config)
            st.session_state.report = result["reviewed_report"]
            st.session_state.topic = topic
            st.session_state.followup_answers = []
            st.rerun()

if st.session_state.report:
    st.markdown("---")
    st.subheader(f"Report: {st.session_state.topic}")
    st.markdown(st.session_state.report)

    st.download_button(
        label="📄 Download Report",
        data=st.session_state.report,
        file_name="research_report.txt",
        mime="text/plain",
        key="download_btn"
    )

    if st.session_state.followup_answers:
        st.markdown("### Follow-up Answers")
        for i, item in enumerate(st.session_state.followup_answers):
            st.markdown(f"**Q: {item['question']}**")
            st.markdown(item["answer"])
            st.markdown("---")

    st.markdown("---")
    st.subheader("💬 Ask a follow-up question")
    follow_up = st.text_input("Your question:", placeholder="e.g. What are the limitations?", key="followup_input")

    if st.button("Ask", key="ask_btn"):
        if not follow_up:
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking..."):
                # Build full conversation history
                history = f"Main Report about {st.session_state.topic}:\n\n{st.session_state.report}\n\n"
                if st.session_state.followup_answers:
                    history += "Previous Follow-up Conversation:\n"
                    for item in st.session_state.followup_answers:
                        history += f"Q: {item['question']}\n"
                        history += f"A: {item['answer']}\n\n"
                history += f"New Question: {follow_up}"

                llm = ChatGroq(model="llama-3.1-8b-instant", api_key=api_key)
                response = llm.invoke([
                    SystemMessage(content="You are a helpful assistant. Answer the follow-up question based on the research report and previous conversation history. Be concise and relevant."),
                    HumanMessage(content=history)
                ])
                st.session_state.followup_answers.append({
                    "question": follow_up,
                    "answer": response.content
                })
                st.rerun()
