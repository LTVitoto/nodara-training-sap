from langchain_core.messages import AIMessage

def auditor_node(state):
    """Aplica la rúbrica corporativa Clean Core y emite el dictamen final"""
    findings = state.get("audit_findings", {})
    ext_fields = findings.get("Clean_Core_Extension", {}).get("d", {})
    
    toxicidad = ext_fields.get("Z_Toxicidad", 0)
    distancia = ext_fields.get("Z_Distancia_Agua", None)
    
    if toxicidad > 30 and distancia is None:
        dictamen = "CRÍTICO: El Auditor detectó violación de Clean Core. Toxicidad alta sin distancia a fuentes hídricas registrada. Alumno reprobado por omisión regulatoria."
    else:
        dictamen = "CUMPLIMIENTO TOTAL: Los datos en S/4HANA satisfacen los controles de la minera."
        
    return {"messages": [AIMessage(content=dictamen)]}
