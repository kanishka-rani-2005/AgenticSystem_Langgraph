from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
import os 

load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from pypdf import PdfReader
import docx2txt



Path("uploads").mkdir(exist_ok=True)
Path("chroma_db").mkdir(exist_ok=True)


embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)

vectorstore = Chroma(
    collection_name="agentic_chatbot_docs",
    embedding_function=embeddings,
    persist_directory="chroma_db"
)


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