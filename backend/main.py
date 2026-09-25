from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import tempfile
import os

from rag_pipeline import ask_question
from Document_loader.loader import load_file, load_url
from chroma import add_documents, get_document_count


app = FastAPI(
    title="AI Knowledge Assistant API",
    description="Backend API for the RAG-based AI Knowledge Assistant",
    version="1.0.0"
)


class ChatRequest(BaseModel):
    question: str


class URLRequest(BaseModel):
    url: str


@app.get("/")
def root():
    return {
        "message": "AI Knowledge Assistant Backend is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# -------------------------
# CHAT
# -------------------------

@app.post("/chat")
def chat(request: ChatRequest):
    result = ask_question(request.question)

    return result


# -------------------------
# UPLOAD DOCUMENT
# -------------------------

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt",
        ".csv",
        ".md"
    }

    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. "
                   "Allowed: PDF, DOCX, TXT, CSV, MD"
        )

    try:
        file_content = await file.read()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_extension
        ) as temp_file:

            temp_file.write(file_content)
            temp_file_path = temp_file.name

        documents = load_file(temp_file_path)

        # Keep original filename in metadata
        for document in documents:
            document.metadata["file_name"] = file.filename

        chunks_added = add_documents(documents)

        os.remove(temp_file_path)

        return {
            "message": "Document uploaded successfully!",
            "file_name": file.filename,
            "chunks_added": chunks_added,
            "total_chunks": get_document_count()
        }

    except Exception as e:

        if "temp_file_path" in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# -------------------------
# ADD WEBSITE
# -------------------------

@app.post("/add-url")
def add_url(request: URLRequest):

    try:
        documents = load_url(request.url)

        chunks_added = add_documents(documents)

        return {
            "message": "Website added successfully!",
            "url": request.url,
            "chunks_added": chunks_added,
            "total_chunks": get_document_count()
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# -------------------------
# KNOWLEDGE BASE COUNT
# -------------------------

@app.get("/knowledge-base")
def knowledge_base():

    return {
        "total_chunks": get_document_count()
    }

