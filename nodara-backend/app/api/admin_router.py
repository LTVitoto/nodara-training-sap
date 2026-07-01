from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.rag_ingestion import ejecutar_chunking_y_embedding
from app.services.hana_vector_store import engine
from sqlalchemy import text

router = APIRouter()

@router.post("/rag/ingest")
async def upload_manual(exam_id: str = Form(...), file: UploadFile = File(...)):
    try:
        return ejecutar_chunking_y_embedding(await file.read(), file.filename, exam_id)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
