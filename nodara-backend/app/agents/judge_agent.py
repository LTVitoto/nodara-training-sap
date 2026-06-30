from langchain_core.messages import AIMessage

def judge_node(state):
    """
    Analiza el input del usuario y extrae entidades SAP.
    Usamos lógica hardcodeada para el esqueleto.
    """
    last_user_message = state["messages"][-2].content.lower() if len(state["messages"]) > 1 else ""
    
    # Simulación de extracción de LLM (Function Calling Mock)
    extracted_fields = {}
    if "brasil" in last_user_message or "br" in last_user_message:
        extracted_fields["Country"] = "BR"
    if "mineração" in last_user_message or "cliente" in last_user_message:
        extracted_fields["BP_Role"] = "FLCU01" # Rol de Cliente SAP
        
    audit_note = "Dados extraídos com sucesso." if extracted_fields else "Faltam dados obrigatórios do cliente."
        
    return {
        "extracted_sap_fields": extracted_fields,
        "audit_findings": audit_note
    }