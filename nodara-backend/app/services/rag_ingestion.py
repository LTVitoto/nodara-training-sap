import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.hana_vector_store import engine
from sqlalchemy import text
from app.core.config import settings

def obtener_embedding(texto: str) -> list:
    if settings.SAP_ENV == "dev.local":
        import random
        random.seed(hash(texto))
        return [random.uniform(-1, 1) for _ in range(1536)]
    from generative_ai_hub_sdk.core.client import HubClient
    from langchain_openai import OpenAIEmbeddings
    HubClient.init()
    return OpenAIEmbeddings(model="text-embedding-3-small").embed_query(texto)

def ejecutar_chunking_y_embedding(file_content: bytes, filename: str, exam_id: str):
    texto_completo = file_content.decode("utf-8", errors="ignore")
    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_text(texto_completo)
    with engine.connect() as conn:
        for chunk in chunks:
            vec = obtener_embedding(chunk)
            conn.execute(text("INSERT INTO documentos_rag (exam_id, filename, chunk_text, embedding) VALUES (:eid, :f, :t, :e);"), {"eid": exam_id, "f": filename, "t": chunk, "e": str(vec) if settings.SAP_ENV=="dev.local" else vec})
        conn.commit()
    return {"status": "success", "chunks": len(chunks), "db": settings.SAP_ENV}
