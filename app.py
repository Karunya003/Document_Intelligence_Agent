import streamlit as st
import requests
import os

# Configuration
API_URL = "http://localhost:8000"
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(
    page_title="Document Intelligence Agent",
    page_icon="📄"
)

# Session State Initialization
st.session_state.setdefault("pdf_uploaded", None)
st.session_state.setdefault("schema_result", None)
st.session_state.setdefault("evaluation", None)
st.session_state.setdefault("chat_history", [])

# Interface
st.title("📄 Document Intelligence Agent")
st.caption("Upload once • Ask many questions • No repeated LLM calls")

# pdf upload
pdf_file = st.file_uploader("Upload a PDF", type=["pdf"])

if pdf_file and st.session_state.pdf_uploaded != pdf_file.name:
    file_path = os.path.join(UPLOAD_DIR, pdf_file.name)

    with open(file_path, "wb") as f:
        f.write(pdf_file.getbuffer())

    st.session_state.pdf_uploaded = pdf_file.name
    st.session_state.schema_result = None
    st.session_state.evaluation = None
    st.session_state.chat_history = []


if st.session_state.pdf_uploaded and st.session_state.schema_result is None:

    st.info("PDF uploaded. Click below to extract document intelligence.")

    if st.button("🔍 Extract Document Schema"):
        with st.spinner("Extracting schema (this may take a moment)..."):
            try:
                file_path = os.path.join(
                    UPLOAD_DIR, st.session_state.pdf_uploaded
                )

                with open(file_path, "rb") as f:
                    response = requests.post(
                        f"{API_URL}/chat",
                        files={"file": f},
                        timeout=120
                    )

                data = response.json()

                if "error" in data:
                    st.error(data["error"])
                else:
                    st.session_state.schema_result = data.get("result")
                    st.session_state.evaluation = data.get("evaluation")
                    st.success("Schema extracted successfully!")

            except Exception as e:
                st.error(f"Backend error: {e}")

#Display extracted schema and evaluation
if st.session_state.schema_result:
    st.subheader("📊 Extracted Document Schema")
    st.json(st.session_state.schema_result)

    if st.session_state.evaluation:
        st.subheader("📝 Evaluation")
        st.json(st.session_state.evaluation)

#QA Section
if st.session_state.schema_result:
    st.subheader("💬 Ask Questions About This Document")

    question = st.text_input(
        "Enter your question",
        placeholder="What are the key risks mentioned?"
    )

    if st.button("Ask Question") and question:
        with st.spinner("Thinking..."):
            try:
                # FIXED: Send form data instead of file
                response = requests.post(
                    f"{API_URL}/question",
                    data={
                        "file_name": st.session_state.pdf_uploaded,
                        "question": question
                    },
                    timeout=60
                )

                data = response.json()
                
                # Check if response contains answer
                if "answer" in data:
                    answer = data["answer"]
                elif "error" in data:
                    answer = f"Error: {data['error']}"
                else:
                    answer = str(data)  # Show full response if unexpected format

                st.session_state.chat_history.append({
                    "question": question,
                    "answer": answer
                })

            except Exception as e:
                st.error(f"Backend error: {e}")


if st.session_state.chat_history:
    st.subheader("🧠 Conversation History")

    for chat in st.session_state.chat_history:
        st.markdown(f"**Q:** {chat['question']}")
        st.markdown(f"**A:** {chat['answer']}")
        st.divider()