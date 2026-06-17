import streamlit as st
from agent import build_graph
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import uuid

# ── Mem0 — long-term, cross-session memory (hosted) ──
# Key stored in Streamlit Secrets. Wrapped so the app still works if Mem0 is unavailable.
def get_memory():
    try:
        from mem0 import MemoryClient
        return MemoryClient(api_key=st.secrets["MEM0_API_KEY"])
    except Exception:
        return None

mem_client = get_memory()

def save_memory(messages, user_id):
    if mem_client and user_id:
        try:
            mem_client.add(messages, user_id=user_id)
        except Exception:
            pass

def recall_memory(query, user_id):
    if mem_client and user_id:
        try:
            results = mem_client.search(query, user_id=user_id)
            return "\n".join(m.get("memory", "") for m in results)
        except Exception:
            return ""
    return ""

st.set_page_config(page_title="AI Research Assistant", page_icon="🔍", layout="wide")
st.title("🔍 AI Research Assistant")
st.caption("Powered by LangGraph + Groq + Mem0")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Groq API Key", type="password")
    username = st.text_input("Your name (for memory)", placeholder="e.g. mohammad")
    st.markdown("---")
    st.markdown("### How it works")
    st.markdown("1. 🧠 Planner breaks topic into questions")
    st.markdown("2. 🔍 Researcher searches the web (Tavily)")
    st.markdown("3. ✍️ Writer creates structured report")
    st.markdown("4. ✅ Reviewer improves the report")
    st.markdown("---")
    st.markdown("🧠 **Mem0** remembers your research across sessions")
    st.markdown("---")
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

# ── Welcome back — show what Mem0 remembers about this user ──
if username and mem_client:
    past = recall_memory("past research topics and interests", username)
    if past:
        with st.expander(f"📚 What I remember about {username}", expanded=False):
            st.markdown(past)

# ════════════════════════════════════════════════════════
# 1. GENERATE A REPORT (the 4-agent pipeline)
# ════════════════════════════════════════════════════════

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

            # Save this research to long-term memory
            save_memory([
                {"role": "user", "content": f"Researched the topic: {topic}"},
                {"role": "assistant", "content": result["reviewed_report"][:2000]}
            ], username)

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

    # ── Follow-up (short-term: uses this session's report + history) ──
    st.markdown("---")
    st.subheader("💬 Ask a follow-up question")
    follow_up = st.text_input("Your question:", placeholder="e.g. What are the limitations?", key="followup_input")

    if st.button("Ask", key="ask_btn"):
        if not follow_up:
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking..."):
                history = f"Main Report about {st.session_state.topic}:\n\n{st.session_state.report}\n\n"
                if st.session_state.followup_answers:
                    history += "Previous Follow-up Conversation:\n"
                    for item in st.session_state.followup_answers:
                        history += f"Q: {item['question']}\n"
                        history += f"A: {item['answer']}\n\n"
                history += f"New Question: {follow_up}"

                llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)
                response = llm.invoke([
                    SystemMessage(content="You are a helpful assistant. Answer the follow-up question based on the research report and previous conversation history. Be concise and relevant."),
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

# ════════════════════════════════════════════════════════
# 2. MEMORY CHAT — talk to your long-term memory (cross-session)
# ════════════════════════════════════════════════════════
# This works even in a brand-new session: it retrieves what Mem0
# stored about you in the past and answers from it.

st.markdown("---")
st.subheader("🧠 Memory Chat — continue from past sessions")
st.caption("Ask about anything you researched before, even on a previous day.")

mem_question = st.text_input("Ask your memory:", placeholder="e.g. Summarize what we discussed about machine learning", key="mem_input")

if st.button("Ask Memory", key="mem_btn"):
    if not api_key:
        st.error("Please enter your Groq API key.")
    elif not username:
        st.error("Please enter your name in the sidebar so I know whose memory to use.")
    elif not mem_question:
        st.warning("Please enter a question.")
    elif not mem_client:
        st.error("Memory service is unavailable right now.")
    else:
        with st.spinner("Recalling your past research..."):
            memories = recall_memory(mem_question, username)
            llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)
            response = llm.invoke([
                SystemMessage(content="You are a helpful assistant with memory of the user's past research. Use the remembered information below to answer. If the memory doesn't cover it, say so honestly."),
                HumanMessage(content=f"What I remember about {username}:\n{memories}\n\nQuestion: {mem_question}")
            ])
            st.markdown("### 🧠 From your memory:")
            st.markdown(response.content)
            if memories:
                with st.expander("🔍 Raw memories used"):
                    st.text(memories)
