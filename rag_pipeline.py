import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from chroma import get_vector_db

# Load environment variables
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env")


# Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    google_api_key=api_key,
    temperature=0
)


def ask_question(question):
    # Get Chroma vector database
    vector_db = get_vector_db()

    # Create retriever
    retriever = vector_db.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 5,
            "fetch_k": 15
        }
    )

    # Search relevant documents
    retrieved_docs = retriever.invoke(question)

    # If no documents found
    if not retrieved_docs:
        return {
            "answer": "I could not find the answer in the provided sources.",
            "sources": []
        }

    # Prepare context
    context_parts = []
    sources = []

    for doc in retrieved_docs:
        context_parts.append(doc.page_content)

        metadata = doc.metadata

        source = metadata.get(
            "file_name",
            metadata.get("source", "Unknown")
        )

        page = metadata.get("page", None)

        source_type = metadata.get(
            "source_type",
            "unknown"
        )

        sources.append({
            "source": source,
            "page": page,
            "type": source_type
        })

    context = "\n\n---\n\n".join(context_parts)

    # RAG prompt
    prompt = f"""
You are an AI knowledge assistant.

Answer the user's question using ONLY
the information provided in the context.

Rules:

1. Do not use outside knowledge.
2. Do not invent information.
3. If the answer is not present in the context,
   say exactly:

"I could not find the answer in the provided sources."

4. Give a clear and useful answer.
5. Stay grounded in the provided sources.

CONTEXT:

{context}

USER QUESTION:

{question}
"""

    # Generate answer using Gemini
    response = llm.invoke(prompt)

    # Extract response text
    if isinstance(response.content, str):
        answer = response.content

    else:
        answer_parts = []

        for block in response.content:

            if isinstance(block, dict):

                if block.get("type") == "text":
                    answer_parts.append(
                        block.get("text", "")
                    )

            elif isinstance(block, str):
                answer_parts.append(block)

        answer = "\n".join(answer_parts)

    # Return answer + sources
    return {
        "answer": answer,
        "sources": sources
    }