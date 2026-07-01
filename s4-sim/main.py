from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nodara_user:NodaraPass2026!@postgres-service:5432/nodara_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BusinessPartner(Base):
    __tablename__ = "sap_business_partners"
    bp_id = Column(String, primary_key=True, index=True)
    country = Column(String)
    bp_role = Column(String)

class EHSIncident(Base):
    __tablename__ = "sap_ehs_incidents"
    incident_id = Column(String, primary_key=True, index=True)
    category = Column(String)
    severity = Column(String)
    plant = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SAP S/4HANA OData Core Simulator v2.0")

@app.get("/health")
def health():
    return {"status": "S/4HANA Security Core Operational"}

@app.get("/sap/opu/odata4/sap/api_material_document/srvd_a2x/sap/materialdocument/0001/MaterialDocument")
def odata_handshake(request: Request):
    response = JSONResponse(content={"d": "Handshake successful"})
    response.headers["x-csrf-token"] = "CSRF_TOKEN_VALID_SAP_BTP_2026"
    return response

@app.post("/sap/opu/odata/sap/API_BUSINESS_PARTNER/A_BusinessPartner")
async def create_bp(request: Request):
    if request.headers.get("x-csrf-token") != "CSRF_TOKEN_VALID_SAP_BTP_2026":
        return JSONResponse(status_code=403, content={"error": "CX_CSRF_TOKEN_VALIDATION_FAILED"})
    data = await request.json()
    country = data.get("Country")
    roles = data.get("to_BusinessPartnerRole", {}).get("results", [])
    bp_role = roles[0].get("BusinessPartnerRole") if roles else None
    if not country or not bp_role:
        return JSONResponse(status_code=400, content={"error": "Missing mandatory BP fields."})
    new_id = f"BP_{uuid.uuid4().hex[:6].upper()}"
    db = SessionLocal()
    db.add(BusinessPartner(bp_id=new_id, country=country, bp_role=bp_role))
    db.commit()
    db.close()
    return {"d": {"BusinessPartner": new_id, "Country": country}}

@app.post("/sap/opu/odata/sap/API_EHS_INCIDENT_SRV/Incidents")
async def create_ehs_incident(request: Request):
    if request.headers.get("x-csrf-token") != "CSRF_TOKEN_VALID_SAP_BTP_2026":
        return JSONResponse(status_code=403, content={"error": "CX_CSRF_TOKEN_VALIDATION_FAILED"})
    data = await request.json()
    category = data.get("IncidentCategory")
    severity = data.get("Severity")
    plant = data.get("Plant")
    if not category or not severity:
        return JSONResponse(status_code=400, content={"error": "Faltan campos obligatorios EHS."})
    new_id = f"INC_{uuid.uuid4().hex[:6].upper()}"
    db = SessionLocal()
    db.add(EHSIncident(incident_id=new_id, category=category, severity=severity, plant=plant))
    db.commit()
    db.close()
    return {"d": {"IncidentId": new_id, "Status": "Created", "Severity": severity}}
