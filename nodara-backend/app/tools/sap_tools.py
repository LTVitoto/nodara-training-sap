import os
import requests
import json
from langchain_core.tools import tool

def _ejecutar_handshake_sap(session: requests.Session, url_base: str) -> str:
    """Simula el handshake CSRF Token nativo de SAP S/4HANA"""
    # Cambiamos /health por un endpoint OData real que SÍ genera token
    url_fetch = f"{url_base}/sap/opu/odata4/sap/api_material_document/srvd_a2x/sap/materialdocument/0001/MaterialDocument"
    headers = {"x-csrf-token": "Fetch", "Accept": "application/json"}
    try:
        # Al usar session.get, requests guarda automáticamente la cookie 'sap_session'
        res = session.get(url_fetch, headers=headers, timeout=5)
        # Y aquí extraemos el token que viene en la cabecera
        return res.headers.get("x-csrf-token", "")
    except Exception as e:
        print(f"Handshake failed: {e}")
        return ""

@tool
def create_sap_business_partner(country: str, bp_role: str) -> str:
    """
    Herramienta que crea un Cliente (Business Partner) en SAP S/4HANA.
    Requiere obligatoriamente el código del País y el Rol del BP.
    """
    base_url = os.getenv("SAP_IS_BASE_URL", "http://s4-sim:8000")
    session = requests.Session()
    
    # 1. Obtener Token de Seguridad
    token_csrf = _ejecutar_handshake_sap(session, base_url)
    
    headers = {
        "x-csrf-token": token_csrf,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # 2. Armar el payload OData
    payload = {
        "Country": country,
        "to_BusinessPartnerRole": {
            "results": [
                {"BusinessPartnerRole": bp_role}
            ]
        }
    }
    
    # 3. Disparar a SAP
    url_post = f"{base_url}/sap/opu/odata/sap/API_BUSINESS_PARTNER/A_BusinessPartner"
    
    try:
        res = session.post(url_post, headers=headers, json=payload, timeout=5)
        if res.status_code == 200 or res.status_code == 201:
            data = res.json()
            bp_id = data.get("d", {}).get("BusinessPartner")
            return f"SUCCESS: Business Partner {bp_id} creado correctamente en S/4HANA."
        else:
            return f"ERROR SAP: {res.text}"
    except Exception as e:
        return f"CRITICAL ERROR: No se pudo conectar a S/4HANA - {str(e)}"

# Lista exportable de herramientas
sap_tools_list = [create_sap_business_partner]