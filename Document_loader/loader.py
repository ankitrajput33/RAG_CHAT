from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    CSVLoader,
    WebBaseLoader
)


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".csv",
    ".md"
}


def load_file(file_path: str):
    """
    Automatically detects the file type
    and loads the file using the appropriate loader.
    """

    path = Path(file_path)

    # Check file exists
    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    # Check it is actually a file
    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {file_path}"
        )

    extension = path.suffix.lower()
    file_name = path.name

    print(f"Loading: {file_name}")

    # Check supported extension
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Supported types: "
            f"{', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # PDF
    if extension == ".pdf":
        loader = PyPDFLoader(str(path))

    # DOCX
    elif extension == ".docx":
        loader = Docx2txtLoader(str(path))

    # TXT
    elif extension == ".txt":
        loader = TextLoader(
            str(path),
            encoding="utf-8"
        )

    # CSV
    elif extension == ".csv":
        loader = CSVLoader(str(path))

    # Markdown
    elif extension == ".md":
        loader = TextLoader(
            str(path),
            encoding="utf-8"
        )

    # Load documents
    documents = loader.load()

    # Check empty document
    if not documents:
        raise ValueError(
            f"No content could be extracted from: {file_name}"
        )

    # Add metadata
    for document in documents:

        document.metadata["file_name"] = file_name

        document.metadata["source_type"] = (
            extension.replace(".", "")
        )

    print(
        f"Successfully loaded {len(documents)} document(s)"
    )

    return documents


def load_url(url: str):
    """
    Load text from a webpage.
    """

    if not url.startswith(("http://", "https://")):
        raise ValueError(
            "URL must start with http:// or https://"
        )

    print(f"Loading URL: {url}")

    loader = WebBaseLoader(url)

    documents = loader.load()

    if not documents:
        raise ValueError(
            f"No content could be extracted from URL: {url}"
        )

    # Add metadata
    for document in documents:

        document.metadata["source_type"] = "web"
        document.metadata["source_url"] = url
        document.metadata["file_name"] = url

    print(
        f"Successfully loaded {len(documents)} document(s)"
    )

    return documents