from typing import TypedDict, List, Dict, Any, Annotated
from langchain_core.messages import BaseMessage
import operator

class NodaraState(TypedDict):
    # LA MAGIA ESTÁ AQUÍ: operator.add le dice a LangGraph que ACUMULE los mensajes
    messages: Annotated[List[BaseMessage], operator.add]
    scenario_id: str
    company_code: str
    
    # Contexto Operativo
    source_manual_language: str
    target_training_language: str
    target_sap_process: str
    
    # Memoria de Auditoría (Estos NO llevan operator.add porque sí queremos que se sobrescriban)
    extracted_sap_fields: Dict[str, Any]
    audit_findings: str
    next_node: str