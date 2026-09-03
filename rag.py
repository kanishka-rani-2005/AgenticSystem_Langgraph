from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
import os 

load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage

from pypdf import PdfReader
import docx2txt



Path("uploads").mkdir(exist_ok=True)
Path("chroma_db").mkdir(exist_ok=True)


# Gemini embedding model
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)

# Vectorstore
vectorstore = Chroma(
    collection_name="agentic_chatbot_docs",
    embedding_function=embeddings,
    persist_directory="chroma_db"
)


# This function reads the content of a file based on its type (PDF, DOCX, TXT, MD, PY, CSV, JSON) and returns the text content. It raises an error for unsupported file types.
def read_file_text(file_path:str)->str:
    path=Path(file_path)
    suffix=path.suffix.lower()


    if suffix==".pdf":
        reader=PdfReader(file_path)
        text=""
        for page in reader.pages:
            text+=page.extract_text() or ""
            text+="\n"
        return text

    if suffix==".docx":
        text=docx2txt.process(file_path)
        return text
    if suffix in ['.txt','.md','.py','.csv','.json']:
        with open(file_path,'r',encoding='utf-8') as f:
            return f.read()

    raise ValueError(f"Unsupported file type: {suffix}. Supported types are PDF, DOCX, TXT, MD, PY, CSV, JSON.")



# This function adds a document to the RAG system by reading the file, splitting it into chunks, and storing those chunks in a vector store for later retrieval. 
# It returns the filename and the number of chunks created.
def add_document_to_rag(file_path:str,thread_id:str):
    text=read_file_text(file_path)


    if not text.strip():
        raise ValueError("The document is empty or could not be read.")


    splitter=RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    chunks=splitter.split_text(text)

    docs:List[Document]=[
        Document(
            page_content=chunk,
            metadata={
                "thread_id": thread_id,
                "source": Path(file_path).name
            }
        )
        for chunk in chunks
        ]
    vectorstore.add_documents(docs)

    return {
        "filename":Path(file_path).name,
        "chunks":len(docs)
    }


def thread_has_documents(thread_id: str) -> bool:
    """Return whether a conversation has at least one indexed document."""
    result = vectorstore.get(
        where={"thread_id": thread_id},
        limit=1,
        include=[]
    )
    return bool(result.get("ids"))


# This function retrieves relevant documents from the RAG(Retrieval-Augmented Generation) system based on a query and a thread ID.
# It performs a similarity search in the vector store and returns the content of the most relevant documents, along with their sources.
# If no relevant documents are found, it returns a message indicating that.
def retrieve_from_rag(query:str,thread_id:str,k:int=4)->str:
    docs=vectorstore.similarity_search(
        query,
        k=k,
        filter={"thread_id":thread_id}
    )

    if not docs:
        return "No relevant documents found for the query."

    results=[]
    for i , doc in enumerate(docs,start=1):
        source=doc.metadata.get("source","Uploaded document")
        results.append(
            f"[Source{i}: {source}] \n {doc.page_content}"
        )
    return "\n\n".join(results)
