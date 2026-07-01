import os, requests, backoff
from langchain_core.tools import tool
from app.core.config import settings

@backoff.on_exception(backoff.expo, (requests.exceptions.Timeout, requests.exceptions.HTTPError), max_tries=3)
def _ejecutar_handshake_sap(session: requests.Session, url_base: str) -> str:
    url_fetch = f"{url_base}/sap/opu/odata4/sap/api_material_document/srvd_a2x/sap/materialdocument/0001/MaterialDocument"
    headers = {"x-csrf-token": "Fetch", "Accept": "application/json"}
    try:
        res = session.get(url_fetch, headers=headers, timeout=5)
        return res.headers.get("x-csrf-token", "")
    except Exception:
        return "local_dev_token"

@tool
def create_sap_business_partner(country: str, bp_role: str) -> str:
    """
    Herramienta transaccional para crear un Business Partner en SAP S/4HANA.
    Requiere obligatoriamente el código del País (Country) y el Rol del BP (BP_Role).
    """
    base_url = settings.SAP_IS_BASE_URL
    session = requests.Session()
    token_csrf = _ejecutar_handshake_sap(session, base_url)
    headers = {"x-csrf-token": token_csrf, "Accept": "application/json", "Content-Type": "application/json"}
    payload = {"Country": country, "to_BusinessPartnerRole": {"results": [{"BusinessPartnerRole": bp_role}]}}
    url_post = f"{base_url}/sap/opu/odata/sap/API_BUSINESS_PARTNER/A_BusinessPartner"
    try:
        res = session.post(url_post, headers=headers, json=payload, timeout=5)
        if res.status_code in [200, 201]: return f"SUCCESS BP: {res.json().get('d', {}).get('BusinessPartner')}"
        return f"ERROR SAP: {res.text}"
    except Exception as e: return f"ERROR: {str(e)}"

@tool
def report_ehs_incident(incident_category: str, severity: str, description: str, plant_id: str) -> str:
    """
    Herramienta transaccional para reportar un Incidente Ambiental o de Seguridad en SAP EHS.
    Úsala cuando el alumno identifique correctamente un derrame o accidente y decida reportarlo.
    Requiere: Categoría (IncidentCategory), Severidad (Severity), Descripción y Planta (Plant).
    """
    base_url = settings.SAP_IS_BASE_URL
    session = requests.Session()
    token_csrf = _ejecutar_handshake_sap(session, base_url)
    headers = {"x-csrf-token": token_csrf, "Accept": "application/json", "Content-Type": "application/json"}
    payload = {"IncidentCategory": incident_category, "Severity": severity, "Description": description, "Plant": plant_id}
    url_post = f"{base_url}/sap/opu/odata/sap/API_EHS_INCIDENT_SRV/Incidents"
    try:
        res = session.post(url_post, headers=headers, json=payload, timeout=5)
        if res.status_code in [200, 201]: return f"SUCCESS EHS: {res.json().get('d', {}).get('IncidentId')}"
        return f"ERROR SAP: {res.text}"
    except Exception as e: return f"ERROR: {str(e)}"