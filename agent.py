import streamlit as st
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph.message import add_messages
from tavily import TavilyClient

# ── Web search via Tavily (key hidden in Streamlit Secrets) ──
def web_search(query):
    client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
    response = client.search(query, max_results=5)
    return "\n".join(r.get("content", "") for r in response.get("results", []))

def get_llm(api_key):
    return ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)

class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]
    topic: str
    memory_context: str        # ← past research recalled from Mem0
    sub_questions: list
    research: str
    report: str
    reviewed_report: str

def planner_node(state, llm):
    mem = state.get("memory_context", "")
    mem_text = f"\n\nThe user has researched related topics before:\n{mem}" if mem else ""
    response = llm.invoke([
        SystemMessage(content="You are a research planner. Break the given topic into 3 specific sub-questions to research. If the user has past related research, build on it rather than repeating it."),
        HumanMessage(content=f"Topic: {state['topic']}{mem_text}")
    ])
    return {"sub_questions": [response.content], "messages": [AIMessage(content="Planning done.")]}

def researcher_node(state, llm):
    search_results = web_search(state["topic"])
    response = llm.invoke([
        SystemMessage(content="You are an expert researcher. Use the search results to find key information."),
        HumanMessage(content=f"Sub-questions: {state['sub_questions'][0]}\n\nSearch Results: {search_results}")
    ])
    return {"research": response.content, "messages": [AIMessage(content="Research complete.")]}

def writer_node(state, llm):
    mem = state.get("memory_context", "")
    mem_text = f"\n\nRelevant past research by this user (connect to it where useful):\n{mem}" if mem else ""
    response = llm.invoke([
        SystemMessage(content="You are a professional writer. Write a structured report with Introduction, Key Findings, and Conclusion."),
        HumanMessage(content=f"Topic: {state['topic']}\n\nResearch: {state['research']}{mem_text}")
    ])
    return {"report": response.content, "messages": [AIMessage(content="Report written.")]}

def reviewer_node(state, llm):
    response = llm.invoke([
        SystemMessage(content="You are an expert reviewer. Review this report and improve it. Make it more professional and complete."),
        HumanMessage(content=f"Report: {state['report']}")
    ])
    return {"reviewed_report": response.content, "messages": [AIMessage(content="Review complete.")]}

def build_graph(api_key):
    llm = get_llm(api_key)

    graph = StateGraph(ResearchState)
    graph.add_node("planner", lambda s: planner_node(s, llm))
    graph.add_node("researcher", lambda s: researcher_node(s, llm))
    graph.add_node("writer", lambda s: writer_node(s, llm))
    graph.add_node("reviewer", lambda s: reviewer_node(s, llm))

    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "reviewer")
    graph.add_edge("reviewer", END)

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)
