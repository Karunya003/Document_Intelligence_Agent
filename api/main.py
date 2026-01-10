from fastapi import FastAPI, UploadFile, File, Form
import os, shutil, json, logging
from dotenv import load_dotenv
from pydantic import ValidationError
import json, re

from agent.agent import build_agent
from langchain.output_parsers import PydanticOutputParser
from pydantic import ValidationError
from agent.schemas import DocumentInsight
from agent.tools import pdf_extractor
from evaluation.evaluator import evaluate

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY not set")

app = FastAPI(title="Document Intelligence Agent")

agent_executor = build_agent()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

parser = PydanticOutputParser(pydantic_object=DocumentInsight)

# In-memory document store
pdf_memory: dict[str, str] = {}

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_json_output(text: str) -> str:
    """Clean JSON output from markdown code blocks and other artifacts"""
    if not text:
        return ""
    
    # Remove markdown code blocks
    text = re.sub(r"```(json)?\n?", "", text)
    text = re.sub(r"\n?```", "", text)
    
    # Remove common prefixes that GPT might add
    prefixes = [
        "Here is the extracted information from the document formatted according to the specified JSON schema:",
        "Here is the JSON output:",
        "The JSON output is:",
        "I will extract the required information from the provided document and format it according to the specified JSON schema.",
        "Here's the JSON response:",
        "JSON output:"
    ]
    
    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
    
    # Find JSON content (look for { ... })
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        text = json_match.group(0)
    
    # Clean up whitespace
    text = text.strip()
    
    return text


@app.get("/")
def root():
    return {"message": "Document Intelligence Agent API is running!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat")
async def analyze_document(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

# Extract text safely
    text = pdf_extractor.invoke(file_path)
    text = text.replace("\n", " ").strip()
    pdf_memory[file.filename] = text

    # Prepare structured output parser
    task = f"""
    Here is the document to analyze:
    \"\"\"{text}\"\"\"
    Extract summary, key entities, risks, and metrics.
    Return JSON STRICTLY following this schema:
    {parser.get_format_instructions()}
    """

    result = agent_executor.invoke({"input": task})
    response_json = json.loads(result["output"])
    answer = response_json["answer"]  # Always works

    try:
        raw_output = clean_json_output(answer)

         # First, parse as plain JSON
        json_data = json.loads(raw_output)
        
        # Then create DocumentInsight from dict
        structured = DocumentInsight(
            summary=str(json_data.get("summary", "")),
            entities=list(json_data.get("entities", [])),
            risks=list(json_data.get("risks", [])),
            metrics=dict(json_data.get("metrics", {}))
        )

    except (ValidationError, json.JSONDecodeError) as e:
        return {
        "error": "Failed to parse output",
        "details": str(e),
        "raw_json": raw_output if 'raw_output' in locals() else answer[:1000],
        "json_parsed": json_data if 'json_data' in locals() else None
    }

    evaluation = evaluate(
        output=structured.model_dump(),
        meta={
            "schema_valid": True,
            "document_length": len(text),
            "confidence": 0.9
        }
    )

    logger.info("Evaluation:")
    logger.info(json.dumps(evaluation, indent=2))

    return {
        "result": structured.model_dump(),
        "evaluation": evaluation
    }


@app.post("/question")
async def question_document(
    file_name: str = Form(...),
    question: str = Form(...)
):
    if file_name not in pdf_memory:
        return {"error": "Document not found. Upload first."}

    document_text = pdf_memory[file_name]

    task = f"""
    Answer the question using ONLY the document below.

    Question:
    {question}

    Document:
    {document_text}
    """

    result = agent_executor.invoke({"input": task})

    return {"answer": result["output"]}
