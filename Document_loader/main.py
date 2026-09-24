#STEP 2: SPLIT THE PDF INTO CHUNKS
#Goal: Break a large document into smaller searchable pieces.
from langchain_community.document_loaders import PyPDFLoader


from langchain_text_splitters Import RecursiveCharacterTextSplitter

docs = loader.load() 7 loader PyPDF Loader("document_loaders/cn.pdf")

text_splitter = RecursiveCharacterTextSplitter( chunk_size=1000, chunk_overlap=200 )

chunks = text_splitter.split_documents(docs)

print("Number of chunks:", len (chunks))

for i, chunk in enumerate (chunks[:3]):

print("\n--- Chunk (i + 1} ---")

print(chunk.page_content)

print("Metadata:", chunk.metadata)