from fastapi import APIRouter, UploadFile, File, Form
from app.services.rag_ingestion import ejecutar_chunking_y_embedding

router = APIRouter()

# 1. Asegúrate de que la función del endpoint tenga el "async"
@router.post("/rag/ingest")
async def ingest_pdf(
    exam_id: str = Form(...), 
    file: UploadFile = File(...)
):
    # 2. Asegúrate de que la llamada a la función tenga el "await"
    resultado = await ejecutar_chunking_y_embedding(exam_id=exam_id, file=file)
    return resultado