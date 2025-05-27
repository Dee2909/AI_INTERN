from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np

app = FastAPI()
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = None

class IndexRequest(BaseModel):
    documents: list[str]

class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/index_documents")
async def index_documents(request: IndexRequest):
    """Index documents into FAISS vector store."""
    global vector_store
    vector_store = FAISS.from_texts(request.documents, embeddings)
    return {"status": "Documents indexed"}

@app.post("/retrieve")
async def retrieve(request: RetrieveRequest):
    """Retrieve top-k relevant documents."""
    if vector_store is None:
        return {"error": "Vector store not initialized"}
    
    docs = vector_store.similarity_search(request.query, k=request.top_k)
    return {"retrieved_docs": [doc.page_content for doc in docs]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)