from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.graph import compile_nodara_graph
from langchain_core.messages import HumanMessage
from langfuse.callback import CallbackHandler
import os

router = APIRouter()
nodara_graph = compile_nodara_graph()

# Estructura del JSON que enviará el Frontend (Fiori/UI5)
class ChatInput(BaseModel):
    user_id: str
    scenario_id: str
    company_code: str
    message: str

@router.post("/chat")
async def process_chat_message(payload: ChatInput):
    # 1. Instanciamos el espía de Langfuse
    langfuse_handler = CallbackHandler(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST")
    )
    
    # 2. Lógica Dinámica de Inyección de Contexto 
    # (En producción esto vendría de S/4HANA, aquí lo simulamos por el código de empresa)
    if payload.company_code == "BR01":  # Filial Brasil
        target_lang = "Português (Brasil)"
    elif payload.company_code == "CL01": # Filial Chile
        target_lang = "Español (Chile)"
    else:
        target_lang = "English"

    # 3. Armamos el Estado Inicial (NodaraState)
    inputs = {
        "messages": [HumanMessage(content=payload.message)],
        "scenario_id": payload.scenario_id,
        "company_code": payload.company_code,
        
        # --- NUEVAS VARIABLES DE CONTEXTO ---
        "source_manual_language": "English (Australia)",
        "target_training_language": target_lang,
        "target_sap_process": "Creation of Business Partner (Customer Role)",
        
        # --- MEMORIA VACÍA PARA LOS AGENTES ---
        "extracted_sap_fields": {},
        "audit_findings": "",
        "next_node": ""
    }
    
    try:
        # 4. Inyectamos Langfuse y Ejecutamos el Grafo
        config = {
            "callbacks": [langfuse_handler], 
            "configurable": {"thread_id": payload.user_id}
        }
        
        # invoke() hace correr a los agentes (Instructor -> Juez -> Auditor)
        result = nodara_graph.invoke(inputs, config=config)
        
        return {"response": result["messages"][-1].content}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph Execution Failed: {str(e)}")