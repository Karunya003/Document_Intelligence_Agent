from langchain.tools import tool
from pypdf import PdfReader
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Ensure API key
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY not set")

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, timeout=300)

# Memory for multi-turn conversation
PDF_MEMORY = {}

def store_pdf_text(file_path: str, text: str):
    PDF_MEMORY[file_path] = text

def get_pdf_text(file_path: str) -> str:
    return PDF_MEMORY.get(file_path, "")

# Pdf extractor tool
@tool
def pdf_extractor(file_path: str) -> str:
    """
    Extract text from a PDF and return it for analysis.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found: {file_path}"

    try:
        reader = PdfReader(file_path)
        text = "".join(page.extract_text() or "" for page in reader.pages).strip()
        if not text:
            return "Error: No text found in PDF."

        # store in memory
        store_pdf_text(file_path, text)

        return text

    except Exception as e:
        return f"Error extracting PDF: {str(e)}"
    
# Summarization tool
@tool
def summarize(file_path: str) -> str:
    """
    Summarize the PDF stored in memory.
    """
    text = get_pdf_text(file_path)
    if not text:
        return "No PDF loaded. Please upload the document first."

    prompt = f"Summarize the following document in 3-5 concise sentences:\n{text}"
    return llm.predict(prompt)

# Entity extraction tool
@tool
def extract_entities(file_path: str) -> str:
    """
    Extract key entities from the PDF.
    """
    text = get_pdf_text(file_path)
    if not text:
        return "No PDF loaded. Please upload the document first."

    prompt = f"Extract key entities such as companies, dates, products, and financial terms from the text:\n{text}"
    return llm.predict(prompt)

# Risk extraction tool
@tool
def extract_risks(file_path: str) -> str:
    """
    Extract potential risks mentioned in the PDF.
    """
    text = get_pdf_text(file_path)
    if not text:
        return "No PDF loaded. Please upload the document first."

    prompt = f"Identify potential risks from the following document:\n{text}"
    return llm.predict(prompt)

# Metrics extraction tool
@tool
def extract_metrics(file_path: str) -> str:
    """
    Extract important metrics (financial figures, performance indicators) from the PDF.
    """
    text = get_pdf_text(file_path)
    if not text:
        return "No PDF loaded. Please upload the document first."

    prompt = f"Extract important metrics (financial figures, KPIs, percentages) from the following document:\n{text}"
    return llm.predict(prompt)

# Question answering tool
@tool
def answer_question(file_path: str, question: str) -> str:
    """
    Answer any question about the PDF document.
    """
    text = get_pdf_text(file_path)
    if not text:
        return "No PDF loaded. Please upload the document first."

    prompt = f"Document text:\n{text}\n\nQuestion: {question}\nAnswer concisely."
    return llm.predict(prompt)

# Action items extraction tool
@tool
def extract_action_items(text: str) -> str:
    """Extract action items or next steps from a document"""
    prompt = f"Extract all action items or next steps from the following text:\n{text}"
    return llm.predict(prompt)

# Sentiment analysis tool
@tool
def sentiment_analysis(text: str) -> str:
    """Perform sentiment analysis on the text"""
    prompt = f"Analyze the sentiment of the following text and label it as Positive, Negative, or Neutral:\n{text}"
    return llm.predict(prompt)

# Trend analysis tool without llm usage
@tool
def analyze_trend(values: list[float]) -> str:
    """
    Analyze numeric data and predict trend: upward, downward, stable.
    """
    if not values:
        return "No data provided."
    if len(values) < 2:
        return "Not enough data to determine trend."
    
    diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
    avg_diff = sum(diffs)/len(diffs)
    
    if avg_diff > 0:
        return "Overall trend is upward."
    elif avg_diff < 0:
        return "Overall trend is downward."
    else:
        return "Trend is stable."



# List of core tools
core_tools = [
    pdf_extractor,
    summarize,
    extract_entities,
    extract_risks,
    extract_metrics
]

# Additional analysis tools
dynamic_tools = [
    answer_question,
    extract_action_items,
    sentiment_analysis,
    analyze_trend
]