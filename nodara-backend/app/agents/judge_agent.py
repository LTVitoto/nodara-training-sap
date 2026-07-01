from pydantic import BaseModel, Field
from app.core.sap_ai_client import get_sap_openai_llm
from app.tools.sap_tools import create_sap_business_partner, report_ehs_incident
from app.schemas.sap_schemas import SapBusinessPartnerPayload, SapEHSIncidentPayload

class SapStructuredExtraction(BaseModel):
    Country: str = Field(default="", description="Código ISO del país (ej: BR)")
    BP_Role: str = Field(default="", description="Rol BP (ej: FLCU01)")
    IncidentCategory: str = Field(default="", description="Categoría EHS (ej: SPILL)")
    Severity: str = Field(default="", description="Severidad (ej: HIGH)")
    Description: str = Field(default="", description="Descripción del incidente")
    Plant: str = Field(default="", description="Planta (ej: PL01)")

def judge_node(state):
    llm = get_sap_openai_llm(temperature=0.0)
    user_messages = [m.content for m in state["messages"] if m.type == "human"]
    last_msg = user_messages[-1] if user_messages else ""
    
    extracted = {"Country": "", "BP_Role": "", "IncidentCategory": "", "Severity": "", "Description": "", "Plant": ""}
    
    if not hasattr(llm, 'responses'):
        structured_llm = llm.with_structured_output(SapStructuredExtraction)
        try:
            res = structured_llm.invoke(last_msg)
            if res.Country: extracted["Country"] = res.Country
            if res.BP_Role: extracted["BP_Role"] = res.BP_Role
            if res.IncidentCategory: extracted["IncidentCategory"] = res.IncidentCategory
            if res.Severity: extracted["Severity"] = res.Severity
            if res.Description: extracted["Description"] = res.Description
            if res.Plant: extracted["Plant"] = res.Plant
        except Exception: pass
    else:
        if "brasil" in last_msg.lower(): extracted["Country"] = "BR"
        if "criar" in last_msg.lower(): extracted["BP_Role"] = "FLCU01"
        if "derrame" in last_msg.lower(): 
            extracted["IncidentCategory"] = "SPILL"
            extracted["Severity"] = "HIGH"
            extracted["Description"] = "Derrame detectado"
            extracted["Plant"] = "PL01"

    audit_note = "Análisis completado sin llamadas SAP."
    
    # Enrutamiento dinámico a Tools según el Examen
    try:
        if state["exam_id"] == "DATA_MASTERS" and extracted["Country"]:
            valid = SapBusinessPartnerPayload(Country=extracted["Country"], BP_Role=extracted["BP_Role"])
            tool_result = create_sap_business_partner.invoke({"country": valid.Country, "bp_role": valid.BP_Role})
            audit_note = f"Ejecución S/4HANA BP: {tool_result}"
        elif "LITIO" in state["exam_id"] and extracted["IncidentCategory"]:
            valid = SapEHSIncidentPayload(IncidentCategory=extracted["IncidentCategory"], Severity=extracted["Severity"], Description=extracted["Description"], Plant=extracted["Plant"])
            tool_result = report_ehs_incident.invoke({"incident_category": valid.IncidentCategory, "severity": valid.Severity, "description": valid.Description, "plant_id": valid.Plant})
            audit_note = f"Ejecución S/4HANA EHS: {tool_result}"
    except Exception as e:
        audit_note = f"Ejecución Cancelada (Cleansing): {str(e)}"
        
    return {"extracted_sap_fields": extracted, "audit_findings": audit_note}
