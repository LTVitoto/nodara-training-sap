import json
from app.tools.sap_tools import fetch_sap_ehs_incident_data

def judge_node(state):
    """Extrae evidencia cruda desde S/4HANA de forma autónoma"""
    datos_sap_crudos = fetch_sap_ehs_incident_data.invoke({"incident_id": "INC-QAS-9921"})
    parsed_data = json.loads(datos_sap_crudos)
    return {"audit_findings": parsed_data}
