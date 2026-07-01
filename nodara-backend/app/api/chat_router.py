from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.graph import compile_nodara_graph
from app.services.hana_vector_store import engine
from langchain_core.messages import HumanMessage
from langfuse.langchain import CallbackHandler # <--- CORRECCIÓN: API V3 DE LANGFUSE
from sqlalchemy import text
import json, os
from app.core.config import settings

router = APIRouter()
nodara_graph = compile_nodara_graph()

class ChatInput(BaseModel):
    user_id: str
    exam_id: str
    company_code: str
    message: str

@router.post("/chat")
async def process_chat(payload: ChatInput):
    target_lang = "Português (Brasil)" if payload.company_code == "BR01" else "Español (Chile)"
    session_key = f"{payload.user_id}_{payload.exam_id}"
    
    with engine.connect() as conn:
        session = conn.execute(text("SELECT current_index, retry_count, messages_blob FROM graph_sessions WHERE session_key = :k;"), {"k": session_key}).fetchone()
        preguntas_db = conn.execute(text("SELECT numero_pregunta, enunciado, rubrica_json FROM preguntas WHERE exam_id = :eid ORDER BY numero_pregunta ASC;"), {"eid": payload.exam_id}).fetchall()
    
    if not preguntas_db: raise HTTPException(status_code=404, detail="Exam not found")
    
    if session:
        current_index, retry_count = session[0], session[1]
        messages = [HumanMessage(content=m["content"]) for m in json.loads(session[2])]
    else:
        current_index, retry_count, messages = 0, 0, []

    if current_index >= len(preguntas_db): return {"response": "Exame concluído com sucesso."}

    if payload.message.strip(): messages.append(HumanMessage(content=payload.message))

    inputs = {
        "messages": messages, "user_id": payload.user_id, "exam_id": payload.exam_id, "company_code": payload.company_code,
        "current_question_index": current_index, "total_questions": len(preguntas_db),
        "source_manual_language": "English", "target_training_language": target_lang,
        "target_sap_process": payload.exam_id,
        "active_question_text": preguntas_db[current_index][1], "active_rubric_json": json.loads(preguntas_db[current_index][2]),
        "extracted_sap_fields": {}, "audit_findings": "", "is_approved": False, "retry_count": retry_count
    }

    try:
        langfuse_handler = CallbackHandler()
        result = nodara_graph.invoke(inputs, config={"callbacks": [langfuse_handler], "configurable": {"thread_id": session_key}})
        
        last_content = result["messages"][-1].content
        if "is_approved" in result and len(messages) > 0:
            if result["is_approved"]:
                current_index += 1
                retry_count = 0
                if current_index < len(preguntas_db): 
                    last_content += f"\n\nPróxima questão: {preguntas_db[current_index][1]}"
            else:
                retry_count += 1
                
        formatted = [{"role": "user" if isinstance(m, HumanMessage) else "assistant", "content": m.content} for m in result["messages"]]
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO graph_sessions (session_key, current_index, retry_count, messages_blob) VALUES (:k, :i, :r, :b) ON CONFLICT (session_key) DO UPDATE SET current_index=:i, retry_count=:r, messages_blob=:b;"), {"k": session_key, "i": current_index, "r": retry_count, "b": json.dumps(formatted)})
            conn.commit()
        return {"response": last_content}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))