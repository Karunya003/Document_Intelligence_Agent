import streamlit as st
import requests
from agent.schemas import DocumentInsight
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
st.session_state.setdefault("extracted_insights", None)
st.session_state.setdefault("chat_history", [])

# Interface
st.title("📄 Document Intelligence Agent")
st.caption("Upload once • Ask many questions • Smart extraction + conversation")

# PDF upload
pdf_file = st.file_uploader("Upload a PDF", type=["pdf"])

if pdf_file and st.session_state.pdf_uploaded != pdf_file.name:
    file_path = os.path.join(UPLOAD_DIR, pdf_file.name)
    
    with open(file_path, "wb") as f:
        f.write(pdf_file.getbuffer())
    
    st.session_state.pdf_uploaded = pdf_file.name
    st.session_state.extracted_insights = None
    st.session_state.chat_history = []
    
# Extraction Section (direct LLM call, no tools)
if st.session_state.pdf_uploaded and not st.session_state.extracted_insights:
    st.success("PDF uploaded. Click below to extract structured insights.")
    
    if st.button("🔍 Extract Document Insights"):
        with st.spinner("Extracting insights (it may take a while)..."):
            file_path = os.path.join(UPLOAD_DIR, st.session_state.pdf_uploaded)
            
            with open(file_path, "rb") as f:
                response = requests.post(
                    f"{API_URL}/extract",
                    files={"file": f},
                    timeout=120
                )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.extracted_insights = data.get("result", {})
                st.success("Extracted successfully!")
            else:
                st.error(f"Error: {response.status_code}")

# Display extracted insights
if st.session_state.extracted_insights:
    st.subheader("📊 Extracted Document Insights")
    try:
        insights = st.session_state.extracted_insights
        validated_insights = DocumentInsight(**insights)
        
        # Display structured insights
        st.markdown("### 📝 Summary")
        st.write(validated_insights.summary)
        
        st.markdown("### 🏢 Key Entities")
        for entity in validated_insights.entities:
            st.write(f"- {entity}")
            
        st.markdown("### ⚠️ Risks Identified")
        for risk in validated_insights.risks:
            st.write(f"- {risk}")
            
        st.markdown("### 📈 Key Metrics")
        for key, value in validated_insights.metrics.items():
            st.write(f"**{key}**: {value}")
            
    except Exception as e:
        st.error(f"Validation error: {e}")
        st.json(insights)  # Fallback to JSON

# QA Section (with tools)
if st.session_state.extracted_insights:
    st.subheader("💬 Ask Questions (Uses Tools)")
    
    question = st.text_input(
        "Ask a question about the document",
        placeholder="What are the action items?",
        key="question_input"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Ask", type="primary"):
            if question:
                with st.spinner("Thinking (using tools)..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/chat",
                            data={
                                "file_name": st.session_state.pdf_uploaded,
                                "question": question
                            },
                            timeout=60
                        )
                        
                        data = response.json()
                        
                        if "answer" in data:
                            answer = data["answer"]
                        elif "error" in data:
                            answer = f"Error: {data['error']}"
                        else:
                            answer = str(data)
                        
                        st.session_state.chat_history.append({
                            "question": question,
                            "answer": answer
                        })
                        
                        # Clear input
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error: {e}")

# Display conversation history
if st.session_state.chat_history:
    st.subheader("🧠 Conversation History")
    
    for i, chat in enumerate(st.session_state.chat_history):
        st.markdown(f"**Q{i+1}:** {chat['question']}")
        st.markdown(f"**A{i+1}:** {chat['answer']}")
        st.divider()