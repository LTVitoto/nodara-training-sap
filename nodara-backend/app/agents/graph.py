import os
import json
import operator
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage, HumanMessage
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langgraph.graph import StateGraph, START, END
from sqlalchemy import text
from app.services.hana_vector_store import engine
from app.core.config import settings

# ==========================================
# 1. DEFINICIÓN DEL ESTADO DEL GRAFO (MEMORIA)
# ==========================================
class GraphState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_id: str
    exam_id: str
    company_code: str
    current_question_index: int
    total_questions: int
    source_manual_language: str
    target_training_language: str
    target_sap_process: str
    active_question_text: str
    active_rubric_json: dict
    extracted_sap_fields: dict
    audit_findings: str
    is_approved: bool
    retry_count: int
    rag_context: str  # <--- NUEVO: Almacenará el texto recuperado de la base de datos

# ==========================================
# 2. MOTOR RAG: BÚSQUEDA VECTORIAL EN PGVECTOR / HANA
# ==========================================
def retrieve_rag_context(exam_id: str, query_text: str) -> str:
    """
    Convierte el mensaje del usuario en un vector y busca los fragmentos 
    más relevantes en la base de datos para inyectarlos en el LLM.
    """
    try:
        # En dev.cloud aquí llamarías al embedding de SAP AI Hub (ej. text-embedding-3-small)
        # Para dev.local, usamos el mismo vector ficticio de 1536 ceros de la ingesta
        vector_busqueda = [0.0] * 1536 
        
        # Búsqueda de similitud Euclidiana (<->) en pgvector. 
        # (Nota: En BTP con HANA se usa COSINE_SIMILARITY)
        query = text("""
            SELECT content_text 
            FROM rag_documents_chunks 
            WHERE exam_id = :eid 
            ORDER BY embedding_vector <-> :vec 
            LIMIT 3;
        """)
        
        with engine.connect() as conn:
            resultados = conn.execute(query, {"eid": exam_id, "vec": str(vector_busqueda)}).fetchall()
            
        if not resultados:
            return "No se encontraron manuales operativos en la base de datos para este proceso."
            
        # Concatenamos los 3 mejores fragmentos encontrados
        contexto_unido = "\n\n---\n\n".join([fila[0] for fila in resultados])
        return contexto_unido
        
    except Exception as e:
        print(f"[ERROR RAG] Falla en la recuperación vectorial: {e}")
        return "Error interno al recuperar los manuales de SAP."

# ==========================================
# 3. NODOS DEL GRAFO COGNITIVO
# ==========================================
def judge_node(state: GraphState) -> dict:
    """
    Agente Juez: Recupera el contexto RAG y evalúa la respuesta del alumno.
    """
    # 1. Extraer la última respuesta del alumno
    last_user_message = state["messages"][-1].content if state["messages"] else ""
    
    # 2. DISPARO DEL RAG: Vamos a la base de datos por el manual
    contexto_recuperado = retrieve_rag_context(state["exam_id"], last_user_message)
    
    # 3. Construcción del System Prompt (El cerebro del Juez)
    system_prompt = f"""
Eres un Auditor Técnico Senior de SAP evaluando a un operador en entrenamiento.
Idioma de respuesta: {state['target_training_language']}

REGLA DE ORO: Debes evaluar la respuesta del alumno basándote ÚNICA Y EXCLUSIVAMENTE en el siguiente manual operativo de la planta. Si la respuesta contradice el manual o asume automatizaciones prohibidas, reprueba al alumno.

================ CONTEXTO DEL MANUAL (RAG) ================
{contexto_recuperado}
===========================================================

RÚBRICA DE APROBACIÓN ESPERADA:
{json.dumps(state['active_rubric_json'], indent=2)}

PREGUNTA DEL EXAMEN:
{state['active_question_text']}

RESPUESTA DEL ALUMNO:
{last_user_message}

Tu salida DEBE ser un JSON válido con esta estructura exacta, sin texto extra (Markdown permitido solo dentro de los valores):
{{
    "is_approved": true/false,
    "audit_findings": "Tu justificación técnica detallada basada en el manual."
}}
"""

    # 4. Invocación del LLM
    if os.getenv("SAP_ENV") == "dev.cloud":
        # === PRODUCCIÓN: SAP GENERATIVE AI HUB (GPT-4o) ===
        # from langchain_openai import ChatOpenAI
        # llm = ChatOpenAI(model="gpt-4o", ...) # Integración SDK SAP
        pass
    else:
        # === LOCAL: MOCK MODEL PARA NO GASTAR TOKENS ===
        # Simulamos que el LLM leyó el RAG y aprobó la respuesta retornando el JSON esperado
        mock_response = json.dumps({
            "is_approved": True,
            "audit_findings": f"[MOCK DEV.LOCAL] Avaliação da Rúbrica concluída con éxito. \nContexto RAG inyectado: {len(contexto_recuperado)} caracteres procesados."
        })
        llm = FakeMessagesListChatModel(responses=[AIMessage(content=mock_response)])

    # Ejecutamos la simulación/realidad
    respuesta_llm = llm.invoke([SystemMessage(content=system_prompt)])
    
    # 5. Parseo de la decisión
    try:
        decision = json.loads(respuesta_llm.content)
        is_approved = decision.get("is_approved", False)
        findings = decision.get("audit_findings", "Sin justificación.")
    except json.JSONDecodeError:
        is_approved = False
        findings = "Error del LLM al formatear el JSON. Intervención manual requerida."

    # Retornamos el parche para actualizar el State
    return {
        "rag_context": contexto_recuperado,
        "is_approved": is_approved,
        "audit_findings": findings,
        "messages": [AIMessage(content=findings)]
    }

# ==========================================
# 4. COMPILACIÓN Y ORQUESTACIÓN (LANGGRAPH)
# ==========================================
def compile_nodara_graph():
    """
    Construye y compila el flujo de trabajo de los Agentes.
    """
    workflow = StateGraph(GraphState)
    
    # Añadimos los nodos
    workflow.add_node("judge", judge_node)
    
    # Definimos las aristas (El flujo)
    workflow.add_edge(START, "judge")
    workflow.add_edge("judge", END)
    
    # Compilamos el grafo
    app = workflow.compile()
    
    return app