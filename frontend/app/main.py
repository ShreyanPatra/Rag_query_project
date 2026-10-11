import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load frontend environment variables
load_dotenv()

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

# Page Configuration
st.set_page_config(
    page_title="LocalRAG Engine",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🤖 LocalRAG Engine")
st.caption("Private Document Intelligence Powered by FastAPI & Local Ollama")

# Initialize Chat History in Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False

# Sidebar for PDF Upload & Status
with st.sidebar:
    st.header("📄 Document Upload")
    uploaded_file = st.file_uploader(
        "Upload a PDF document to query:", type=["pdf"], accept_multiple_files=False
    )

    if uploaded_file is not None:
        if st.button("Index Document", type="primary"):
            with st.spinner("Processing & indexing PDF..."):
                try:
                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf",
                        )
                    }
                    response = requests.post(
                        f"{BACKEND_API_URL}/upload", files=files, timeout=120
                    )

                    if response.status_code == 201:
                        data = response.json()
                        st.success(
                            f"✅ **{data['filename']}** indexed! ({data['chunks_created']} chunks)"
                        )
                        st.session_state.pdf_uploaded = True
                    else:
                        st.error(
                            f"Error ({response.status_code}): {response.json().get('detail', 'Failed to upload')}"
                        )
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to reach FastAPI backend: {str(e)}")

    st.markdown("---")
    st.markdown("### ⚙️ Engine Status")
    try:
        health_resp = requests.get(f"{BACKEND_API_URL}/", timeout=5)
        if health_resp.status_code == 200:
            st.success("Backend: Connected 🟢")
        else:
            st.warning("Backend: Unhealthy 🟡")
    except Exception:
        st.error("Backend: Disconnected 🔴")

# Main Chat Interface
st.subheader("💬 Chat with your PDF")

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Prompt
# if user_query := st.chat_input("Ask a question about your uploaded document..."):
    # Render User Message
    # st.session_state.messages.append({"role": "user", "content": user_query})
    # with st.chat_message("user"):
    #     st.markdown(user_query)

    # # Call Backend Query API
    # with st.chat_message("assistant"):
    #     with st.spinner("Retrieving context & generating answer..."):
    #         try:
    #             payload = {"question": user_query}
    #             response = requests.post(
    #                 f"{BACKEND_API_URL}/query", json=payload, timeout=180
    #             )

    #             if response.status_code == 200:
    #                 answer = response.json().get("answer", "No answer received.")
    #                 st.markdown(answer)
    #                 st.session_state.messages.append(
    #                     {"role": "assistant", "content": answer}
    #                 )
    #             else:
    #                 error_msg = response.json().get("detail", "Error processing request")
    #                 st.error(f"Backend Error: {error_msg}")
    #         except requests.exceptions.RequestException as e:
    #             st.error(f"API Connection Failed: {str(e)}")

    # Replace your current assistant chat-input handling code with this:

if user_query := st.chat_input("Ask a question about your uploaded document..."):
    # Render User Message
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Render Assistant Streaming Response
    with st.chat_message("assistant"):
        def response_generator():
            payload = {"question": user_query}
            with requests.post(
                f"{BACKEND_API_URL}/stream-query",
                json=payload,
                stream=True,
                timeout=180,
            ) as response:
                if response.status_code == 200:
                    for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                        if chunk:
                            yield chunk
                else:
                    yield f"⚠️ Backend Error ({response.status_code})"

        # Streamlit natively handles live text streaming
        full_response = st.write_stream(response_generator)
        
        # Save complete generated message to session history
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
