from fastapi import FastAPI, UploadFile, File, Form
import os, shutil, logging
from dotenv import load_dotenv
from agent.agent import extract_document_insights, conversation_agent
from agent.tools import pdf_extractor

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY not set")

app = FastAPI(title="Document Intelligence Agent")

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory document store
pdf_memory: dict[str, str] = {}

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
def root():
    return {"message": "Document Intelligence Agent API is running!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/extract")
async def extract_document(file: UploadFile = File(...)):
    """Direct extraction endpoint (no tools)"""
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text from PDF
    text = pdf_extractor.invoke(file_path)
    text = text.replace("\n", " ").strip()
    
    # Store in memory for Q&A
    pdf_memory[file.filename] = text
    
    # Use direct LLM extraction (no tools)
    insights = extract_document_insights(text)
    
    return {"result": insights}

@app.post("/chat")
async def question_document(
    file_name: str = Form(...),
    question: str = Form(...)
):
    """Conversation endpoint (with tools)"""
    if file_name not in pdf_memory:
        return {"error": "Document not found. Upload first via /extract endpoint."}

    # Get the file path for tools
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    # Create context for conversation
    task = f"""
    File: {file_name}
    File path: {file_path}
    
    User question: {question}
    
    You have access to tools to help answer this question.
    Use the appropriate tools if needed.
    """
    
    try:
        result = conversation_agent.invoke({"input": task})
        return {"answer": result["output"]}
    except Exception as e:
        logger.error(f"Conversation agent error: {e}")
        return {"error": f"Agent error: {str(e)}"}