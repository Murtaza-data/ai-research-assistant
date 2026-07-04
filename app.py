import streamlit as st
from agent import build_graph
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import uuid

# ════════════════════════════════════════════════════════
# MEM0 — long-term memory (errors are VISIBLE for debugging)
# ════════════════════════════════════════════════════════

def get_memory():
    try:
        from mem0 import MemoryClient
        return MemoryClient(api_key=st.secrets["MEM0_API_KEY"])
    except Exception as e:
        st.session_state["mem_error"] = str(e)
        return None

mem_client = get_memory()

def save_memory(messages, user_id):
    if not mem_client or not user_id:
        return
    try:
        mem_client.add(messages, user_id=user_id)
    except Exception as e:
        st.error(f"Mem0 SAVE error: {e}")

def recall_memory(query, user_id):
    if not mem_client or not user_id:
        return ""
    try:
        # Newer Mem0 API: user_id goes inside filters={}
        results = mem_client.search(query, filters={"user_id": user_id})
        # Handle both possible response shapes (list, or dict with "results")
        if isinstance(results, dict):
            results = results.get("results", [])
        mems = [m.get("memory", "") for m in results if isinstance(m, dict)]
        return "\n".join(mems)
    except Exception as e:
        st.error(f"Mem0 SEARCH error: {e}")
        return ""

# ════════════════════════════════════════════════════════
# UI SETUP
# ════════════════════════════════════════════════════════

st.set_page_config(page_title="AI Research Assistant", page_icon="🔍", layout="wide")
st.title("🔍 AI Research Assistant")
st.caption("Powered by LangGraph + Groq + Mem0")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Groq API Key", type="password")
    username = st.text_input("Username", placeholder="e.g. mohammad")

    # Memory connection status (visible diagnostic)
    if mem_client:
        st.success("🧠 Memory connected")
    else:
        st.error("🧠 Memory NOT connected")
        if st.session_state.get("mem_error"):
            st.caption(st.session_state["mem_error"])

    st.markdown("---")
    st.markdown("### How it works")
    st.markdown("1. 🧠 Planner breaks topic into questions")
    st.markdown("2. 🔍 Researcher searches the web (Tavily)")
    st.markdown("3. ✍️ Writer creates structured report")
    st.markdown("4. ✅ Reviewer improves the report")
    st.markdown("---")
    st.markdown("🧠 **Mem0** remembers your research across sessions")
    st.markdown("Built by **Mohammad Murtaza**")

# ── Session state ─────────────────────────────────────
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

# ── Welcome back — show what Mem0 remembers (proof it works) ──
if username and mem_client:
    past = recall_memory("past research topics and interests", username)
    if past:
        with st.expander(f"📚 What I remember about {username}", expanded=True):
            st.markdown(past)

# ════════════════════════════════════════════════════════
# 1. MAIN — generate a report (remembers past sessions)
# ════════════════════════════════════════════════════════

topic = st.text_input("Enter a research topic:", placeholder="e.g. What is Machine Learning?", key="topic_input")

if st.button("Generate Report", type="primary", key="generate_btn"):
    if not api_key:
        st.error("Please enter your Groq API key in the sidebar.")
    elif not topic:
        st.error("Please enter a research topic.")
    else:
        with st.spinner("Researching and writing report... please wait..."):
            # Recall related past research → feed it into the pipeline
            memory_context = recall_memory(topic, username)

            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            result = st.session_state.graph_app.invoke({
                "topic": topic,
                "memory_context": memory_context,
                "messages": [HumanMessage(content=f"Research topic: {topic}")],
                "sub_questions": [],
                "research": "",
                "report": "",
                "reviewed_report": ""
            }, config=config)

            st.session_state.report = result["reviewed_report"]
            st.session_state.topic = topic
            st.session_state.followup_answers = []

            # Save this research to long-term memory
            save_memory([
                {"role": "user", "content": f"Researched the topic: {topic}"},
                {"role": "assistant", "content": result["reviewed_report"][:1500]}
            ], username)

            st.rerun()

# ════════════════════════════════════════════════════════
# 2. REPORT + FOLLOW-UP (appears after a report exists)
# ════════════════════════════════════════════════════════

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
        for item in st.session_state.followup_answers:
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
                # Short-term: this session's report + follow-up history
                history = f"Main Report about {st.session_state.topic}:\n\n{st.session_state.report}\n\n"
                if st.session_state.followup_answers:
                    history += "Previous Follow-up Conversation:\n"
                    for item in st.session_state.followup_answers:
                        history += f"Q: {item['question']}\nA: {item['answer']}\n\n"

                # Long-term: relevant memories from past sessions
                past_mem = recall_memory(follow_up, username)
                if past_mem:
                    history += f"Relevant memory from past sessions:\n{past_mem}\n\n"

                history += f"New Question: {follow_up}"

                llm = ChatGroq(model="openai/gpt-oss-120b", api_key=api_key)
                response = llm.invoke([
                    SystemMessage(content="You are a helpful assistant. Answer the follow-up question using the research report, this session's conversation, and any relevant past-session memory. Be concise and relevant."),
                    HumanMessage(content=history)
                ])
                st.session_state.followup_answers.append({
                    "question": follow_up,
                    "answer": response.content
                })

                # Save the follow-up to long-term memory
                save_memory([
                    {"role": "user", "content": follow_up},
                    {"role": "assistant", "content": response.content}
                ], username)

                st.rerun()
