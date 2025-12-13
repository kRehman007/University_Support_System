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
from langGraphFun import app, State

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

/* Reference Links Box Styles */
.references-box {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border: 1px solid #7dd3fc;
    border-radius: 12px;
    padding: 16px;
    margin-top: 8px;
    margin-left: 30px;
    max-width: 65%;
}

.references-title {
    font-size: 13px;
    font-weight: 600;
    color: #0369a1;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.reference-link {
    display: block;
    background: white;
    border: 1px solid #bae6fd;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
    text-decoration: none;
    transition: all 0.2s ease;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.reference-link:hover {
    border-color: #0ea5e9;
    box-shadow: 0 4px 12px rgba(14, 165, 233, 0.15);
    transform: translateY(-1px);
}

.reference-link:last-child {
    margin-bottom: 0;
}

.reference-title {
    font-size: 14px;
    font-weight: 500;
    color: #0c4a6e;
    margin-bottom: 4px;
    line-height: 1.3;
}

.reference-url {
    font-size: 11px;
    color: #0891b2;
    word-break: break-all;
}

/* Loading States */
.loading-state {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 18px;
    border-radius: 15px;
    max-width: 70%;
    font-size: 14px;
    animation: pulse 1.5s ease-in-out infinite;
}

.loading-vector {
    background: linear-gradient(90deg, #ddd6fe, #e9d5ff);
    color: #6b21a8;
}

.loading-web {
    background: linear-gradient(90deg, #bfdbfe, #ddd6fe);
    color: #1e40af;
}

.loading-generating {
    background: linear-gradient(90deg, #bbf7d0, #d9f99d);
    color: #166534;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

.loading-icon {
    display: inline-block;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

</style>
""", unsafe_allow_html=True)

# ---------------- Initialize chat ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown('<div class="chat-container">', unsafe_allow_html=True)


# ---------------- Helper function for reference links ----------------
def render_references(web_results):
    """Render styled reference links box."""
    if not web_results:
        return ""
    
    links_html = ""
    for r in web_results:
        title = r.get("title", "Source")
        url = r.get("url", "#")
        links_html += f'''
        <a href="{url}" target="_blank" class="reference-link">
            <div class="reference-title">📄 {title}</div>
            <div class="reference-url">{url}</div>
        </a>
        '''
    
    return f'''
    <div class="references-box">
        <div class="references-title">
            🔗 Sources from University Website
        </div>
        {links_html}
    </div>
    '''


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
        content = msg["content"]
        web_results = msg.get("web_results", [])
        
        # Build the HTML for the message
        html_parts = [
            '<div class="left">',
            '<div style="display:flex; align-items:flex-start; gap:10px;">',
            '<img src="https://cdn-icons-png.flaticon.com/512/4711/4711987.png" width="20" style="margin-top: 4px;">',
            '<div>',
            f'<div class="assistant-bubble">{content}</div>',
        ]
        
        # Add references if there are web results
        if web_results:
            html_parts.append('<div class="references-box">')
            html_parts.append('<div class="references-title">🔗 Sources from University Website</div>')
            for r in web_results:
                title = r.get("title", "Source")
                url = r.get("url", "#")
                
                # Extract domain for display to prevent markdown auto-linking issues
                display_url = url
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    display_url = parsed.netloc
                except:
                    pass
                    
                html_parts.append(f'<a href="{url}" target="_blank" class="reference-link">')
                html_parts.append(f'<div class="reference-title">📄 {title}</div>')
                html_parts.append(f'<div class="reference-url">{display_url}</div>')
                html_parts.append('</a>')
            html_parts.append('</div>')
        
        html_parts.extend(['</div>', '</div>', '</div>'])
        
        st.markdown(''.join(html_parts), unsafe_allow_html=True)

    elif msg["role"] == "loading":
        # Dynamic loading states
        loading_type = msg.get("loading_type", "thinking")
        
        if loading_type == "classifying":
            st.markdown(
                """
                <div class="left">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/4711/4711987.png" width="20">
                        <div class="loading-state loading-vector">
                            <span class="loading-icon">🔍</span> Analyzing your question...
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        elif loading_type == "retrieving":
            st.markdown(
                """
                <div class="left">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/4711/4711987.png" width="20">
                        <div class="loading-state loading-vector">
                            <span class="loading-icon">📚</span> Retrieving information from knowledge base...
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        elif loading_type == "web_search":
            st.markdown(
                """
                <div class="left">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/4711/4711987.png" width="20">
                        <div class="loading-state loading-web">
                            <span class="loading-icon">🌐</span> Fetching latest data from university website...
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        elif loading_type == "generating":
            st.markdown(
                """
                <div class="left">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/4711/4711987.png" width="20">
                        <div class="loading-state loading-generating">
                            <span class="loading-icon">✨</span> Generating response...
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class="left">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/4711/4711987.png" width="20">
                        <div class="loading-state loading-vector">
                            <span class="loading-icon">⏳</span> Processing...
                        </div>
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
    st.session_state.messages.append({"role": "loading", "loading_type": "classifying"})
    st.rerun()


# ---------------- AI Response ----------------
if st.session_state.messages and st.session_state.messages[-1]["role"] == "loading":

    last_user_msg = next(
        (m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"),
        None
    )
    
    current_loading = st.session_state.messages[-1]
    loading_type = current_loading.get("loading_type", "classifying")
    
    # Progress through loading states
    if loading_type == "classifying":
        st.session_state.messages[-1] = {"role": "loading", "loading_type": "retrieving"}
        st.rerun()
    
    elif loading_type == "retrieving":
        # Run the graph and get the result
        try:
            result = app.invoke({"query": last_user_msg})
            
            answer = (
                "⚠️ Unable to find exact answer. Please contact the university administration."
                if result.get("answer") == "ESCALATE"
                else result.get("answer", "Sorry, I couldn't process your request.")
            )
            
            # Get web results for references
            web_results = result.get("web_results", [])
            
            # Remove loading and add assistant message
            st.session_state.messages.pop()
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "web_results": web_results
            })
            
            st.rerun()
                
        except Exception as e:
            st.session_state.messages.pop()
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ An error occurred: {str(e)}"
            })
            st.rerun()

