import uuid
import streamlit as st
from rag_pipeline import RAGPipeline

st.set_page_config(page_title="مشاوره حقوقی سربازی", layout="centered")

st.markdown(
    """
    <style>
    html, body, [class*="css"] { direction: rtl; text-align: right; font-family: Tahoma, Arial, sans-serif; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_pipeline():
    return RAGPipeline()


if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

pipeline = load_pipeline()

st.title("مشاوره حقوقی سربازی")

if st.button("شروع مکالمه جدید"):
    pipeline.memory.sessions.pop(st.session_state.session_id, None)
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            st.caption("منابع: " + " | ".join(msg["sources"]))

query = st.chat_input("سوال حقوقی خود را درباره سربازی بنویسید...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"):
        with st.spinner("در حال بررسی منابع و نوشتن پاسخ..."):
            answer_text, sources = pipeline.answer(st.session_state.session_id, query)
        st.write(answer_text)
        if sources:
            st.caption("منابع: " + " | ".join(sources))

    st.session_state.messages.append({"role": "assistant", "content": answer_text, "sources": sources})
