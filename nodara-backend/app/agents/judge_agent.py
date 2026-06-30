from app.tools.sap_tools import create_sap_business_partner

def judge_node(state):
    """Extrae las entidades e invoca la herramienta SAP"""
    user_messages = [m.content.lower() for m in state["messages"] if m.type == "human"]
    last_user_message = user_messages[-1] if user_messages else ""
    
    extracted_fields = {}
    if "brasil" in last_user_message or "br" in last_user_message:
        extracted_fields["Country"] = "BR"
    if "mineração" in last_user_message or "cliente" in last_user_message:
        extracted_fields["BP_Role"] = "FLCU01" 
        
    audit_note = ""
    
    # Si tenemos ambos datos, intentamos crear el cliente en SAP simulado
    if "Country" in extracted_fields and "BP_Role" in extracted_fields:
        # LLAMADA A LA HERRAMIENTA ODATA
        tool_result = create_sap_business_partner.invoke({
            "country": extracted_fields["Country"],
            "bp_role": extracted_fields["BP_Role"]
        })
        audit_note = f"Ejecución S/4HANA: {tool_result}"
    else:
        audit_note = "Ejecución cancelada: Faltam dados obrigatórios."
        
    return {
        "extracted_sap_fields": extracted_fields,
        "audit_findings": audit_note
    }