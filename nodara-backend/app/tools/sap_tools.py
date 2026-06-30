import os
import requests
import json
from typing import Dict, Any
from langchain_core.tools import tool

def _ejecutar_handshake_sap(session: requests.Session, url_base: str) -> str:
    """Simula o ejecuta el handshake CSRF Token nativo de SAP S/4HANA o API Management"""
    url_fetch = f"{url_base}/sap/opu/odata/sap/API_EHS_INCIDENT_SRV/Incidents('INC-QAS-9921')"
    headers = {"x-csrf-token": "Fetch", "Accept": "application/json"}
    try:
        res = session.get(url_fetch, headers=headers, timeout=5)
        return res.headers.get("x-csrf-token", "local_dev_token")
    except Exception:
        return "local_dev_token"

@tool
def fetch_sap_ehs_incident_data(incident_id: str) -> str:
    """Consulta datos transaccionales y de Clean Core en S/4HANA para auditar incidentes ambientales."""
    base_url = os.getenv("SAP_IS_BASE_URL", "http://s4-sim:8000")
    session = requests.Session()
    
    api_key = os.getenv("SAP_IS_API_KEY", "")
    token_csrf = _ejecutar_handshake_sap(session, base_url)
    
    headers = {
        "x-csrf-token": token_csrf,
        "APIKey": api_key,
        "Accept": "application/json"
    }
    
    url_std = f"{base_url}/sap/opu/odata/sap/API_EHS_INCIDENT_SRV/Incidents('{incident_id}')"
    url_ext = f"{base_url}/sap/opu/odata/sap/ZAPI_EHS_ENV_EXTENSION_SRV/IncidentExtensions('{incident_id}')"
    
    try:
        res_std = session.get(url_std, headers=headers, timeout=5).json()
        res_ext = session.get(url_ext, headers=headers, timeout=5).json()
        return json.dumps({"Standard_Header": res_std, "Clean_Core_Extension": res_ext})
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch data from SAP core: {str(e)}"})

sap_tools_list = [fetch_sap_ehs_incident_data]
