import io
import re
from fastapi import UploadFile
from sqlalchemy import text
from app.services.hana_vector_store import engine
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

def limpiar_texto_binario(texto: str) -> str:
    """
    Elimina caracteres nulos (0x00) y símbolos de control binario 
    que hacen colapsar a PostgreSQL y a los tokenizers.
    """
    if not texto:
        return ""
    texto_limpio = texto.replace("\x00", "")
    texto_limpio = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', texto_limpio)
    return texto_limpio

async def ejecutar_chunking_y_embedding(exam_id: str, file: UploadFile, db=None, *args, **kwargs) -> dict:
    try:
        # 1. Leer el archivo binario cargado en memoria
        contenido_bytes = await file.read()
        
        # 2. Parsear el PDF de forma segura usando PdfReader desde memoria
        fichero_memoria = io.BytesIO(contenido_bytes)
        lector_pdf = PdfReader(fichero_memoria)
        
        texto_completo = ""
        for n_pagina, pagina in enumerate(lector_pdf.pages):
            texto_pag = pagina.extract_text() or ""
            texto_completo += f"\n--- PÁGINA {n_pagina + 1} ---\n{texto_pag}"
        
        # 3. BLINDAJE CRÍTICO: Sanitizar el texto extraído
        texto_sanitizado = limpiar_texto_binario(texto_completo)
        
        if not texto_sanitizado.strip():
            return {"status": "error", "message": "El archivo PDF no contiene texto legible."}

        # 4. Configurar el cortador de texto semántico
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=120,
            length_function=len
        )
        
        # 5. Generar los fragmentos (chunks)
        chunks = text_splitter.split_text(texto_sanitizado)
        
        # 6. Almacenamiento en Postgres vector store
        vector_ficticio = [0.0] * 1536
        
        with engine.connect() as conn:
            # --- INICIO BLOQUE NUEVO: Auto-creación de tabla vectorial ---
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS rag_documents_chunks (
                    id SERIAL PRIMARY KEY,
                    exam_id VARCHAR(50),
                    chunk_index INTEGER,
                    content_text TEXT,
                    embedding_vector vector(1536)
                );
            """))
            conn.commit()
            # --- FIN BLOQUE NUEVO ---

            for i, chunk in enumerate(chunks):
                chunk_final = limpiar_texto_binario(chunk)
                
                query = text("""
                    INSERT INTO rag_documents_chunks (exam_id, chunk_index, content_text, embedding_vector) 
                    VALUES (:eid, :idx, :content, :vec);
                """)
                conn.execute(query, {
                    "eid": exam_id,
                    "idx": i,
                    "content": chunk_final,
                    "vec": vector_ficticio
                })
            conn.commit()
            
        return {
            "status": "success", 
            "chunks_procesados": len(chunks), 
            "message": f"Se han procesado e indexado {len(chunks)} fragmentos para el examen {exam_id} de forma segura."
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}