from langchain_core.messages import AIMessage

def auditor_node(state):
    """Emite el dictamen final basado en la respuesta de la herramienta SAP"""
    audit_findings = state.get("audit_findings", "")
    
    if "SUCCESS" in audit_findings:
        dictamen = f"Parabéns! {audit_findings} O fluxo de criação de clientes australiano foi cumprido no Brasil."
    else:
        dictamen = f"Atenção: A transação falhou. Motivo: {audit_findings} Por favor, revise o procedimento."
        
    return {"messages": [AIMessage(content=dictamen)]}