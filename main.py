# import streamlit as st
# from langGraphFun import app

# st.title("University Support System")

# query = st.text_input("Ask something about the university:")

# if st.button("Ask") and query.strip() != "":
#     with st.spinner("Thinking..."):
#         result = app.invoke({"query": query})
    
#     st.subheader("Answer:")
#     if result["answer"] == "ESCALATE":
#         st.warning("⚠ Unable to find exact answer. Please contact school admin.")
#     else:
#         st.success(result["answer"])

import streamlit as st
from langGraphFun import app

st.set_page_config(page_title="University Support System", layout="wide")

# ---------------- Header ----------------
st.markdown(
    """
    <div style="
        background: linear-gradient(90deg, #3b82f6, #9333ea);
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    ">
        <h1 style="color: white; margin: 0; font-size: 32px;">
            🎓 University Support Chat Assistant
        </h1>
        <p style="color: #e5e7eb; font-size: 16px; margin-top: 8px;">
            Ask anything related to admissions, programs, fees, scholarships, and more.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- Custom Styles ----------------
st.markdown("""
<style>

.user-bubble {
    background: #dbeafe; /* Light Blue */
    padding: 12px 18px;
    border-radius: 15px;
    color: #1e3a8a;
    max-width: 70%;
    font-size: 15px;
}

.assistant-bubble {
    background: #f3e8ff; /* Soft Purple */
    padding: 12px 18px;
    border-radius: 15px;
    color: #581c87;
    max-width: 70%;
    font-size: 15px;
}

.thinking-bubble .assistant-bubble {
    background: #f1f5f9; /* Light Gray */
    color: #475569;
}

.right {
    text-align: right;
    margin-bottom: 12px;
}

.left {
    text-align: left;
    margin-bottom: 12px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- Initialize chat ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# ---------------- Display Chat ----------------
for msg in st.session_state.messages:

    if msg["role"] == "user":
        st.markdown(
            f"""
            <div class="right">
                <div style="display:flex; justify-content:flex-end; align-items:center; gap:10px;">
                    <div class="user-bubble">{msg["content"]}</div>
                    <img src="https://cdn-icons-png.flaticon.com/512/149/149071.png" width="20">
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    elif msg["role"] == "assistant":
        st.markdown(
            f"""
            <div class="left">
                <div style="display:flex; align-items:center; gap:10px;">
                    <img src="https://cdn-icons-png.flaticon.com/512/4711/4711987.png" width="20">
                    <div class="assistant-bubble">{msg["content"]}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    elif msg["role"] == "thinking":
        st.markdown(
            f"""
            <div class="left thinking-bubble">
                <div style="display:flex; align-items:center; gap:10px;">
                    <img src="https://cdn-icons-png.flaticon.com/512/4711/4711987.png" width="20">
                    <div class="assistant-bubble">Thinking…</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown('</div>', unsafe_allow_html=True)


# ---------------- User Input ----------------
query = st.chat_input("Ask something about the university...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    st.session_state.messages.append({"role": "thinking", "content": "Thinking…"})
    st.rerun()


# ---------------- AI Response ----------------
if st.session_state.messages and st.session_state.messages[-1]["role"] == "thinking":

    last_user_msg = next(
        (m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"),
        None
    )

    result = app.invoke({"query": last_user_msg})

    answer = (
        "⚠ Unable to find exact answer. Please contact school admin."
        if result["answer"] == "ESCALATE"
        else result["answer"]
    )

    st.session_state.messages.pop()
    st.session_state.messages.append({"role": "assistant", "content": answer})

    st.rerun()
