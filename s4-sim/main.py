from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import uuid
import os

app = FastAPI(title="Nodara S4 Sim - Core Transaccional")

# Persistencia de datos maestros locales en SQLite
DB_DIR = "./data"
os.makedirs(DB_DIR, exist_ok=True)
engine = create_engine(f"sqlite:///{DB_DIR}/s4hana.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Material(Base):
    __tablename__ = "materials"
    ean = Column(String, primary_key=True, index=True)
    stock_transito = Column(Integer, default=10)

class EhsIncident(Base):
    __tablename__ = "ehs_incidents"
    incident_id = Column(String, primary_key=True, index=True)
    category = Column(String)
    status = Column(String)
    plant = Column(String)
    toxicidad = Column(Integer)
    distancia_agua = Column(Float, nullable=True)

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    if db.query(Material).count() == 0:
        for i in range(180):
            ean = f"779{str(i).zfill(5)}"
            db.add(Material(ean=ean, stock_transito=15))
        db.commit()
    
    # Inyectar caso base para auditoría de incidentes mineros (El error humano)
    if db.query(EhsIncident).filter(EhsIncident.incident_id == "INC-QAS-9921").first() is None:
        db.add(EhsIncident(
            incident_id="INC-QAS-9921",
            category="ENV",
            status="1",
            plant="PLN1",
            toxicidad=45,
            distancia_agua=None
        ))
        db.commit()
    db.close()

@app.get("/health")
def health():
    return {"status": "ok", "service": "s4-sim"}

# Middleware del Handshake CSRF nativo de SAP
@app.middleware("http")
async def csrf_middleware(request: Request, call_next):
    if request.url.path == "/health":
        return await call_next(request)

    if request.method == "GET" and request.headers.get("x-csrf-token") == "Fetch":
        response = await call_next(request)
        token = uuid.uuid4().hex
        response.headers["x-csrf-token"] = token
        response.set_cookie("sap_session", "session_" + token)
        return response
    
    if request.method in ["POST", "PATCH", "PUT", "DELETE"]:
        token = request.headers.get("x-csrf-token")
        cookie = request.cookies.get("sap_session")
        if not token or not cookie or cookie != "session_" + token:
            return JSONResponse(
                status_code=403,
                content={
                    "error": {
                        "code": "CX_CSRF_TOKEN_VALIDATION_FAILED",
                        "message": "CSRF token validation failed, operation rejected by S4 Security Core.",
                        "innererror": {"component_id": "BC-MID-ICF", "service_namespace": "/sap/"}
                    }
                },
                headers={"x-csrf-token": "Required"}
            )
            
    return await call_next(request)

# OData V4 Endpoints - Material Document
@app.get("/sap/opu/odata4/sap/api_material_document/srvd_a2x/sap/materialdocument/0001/MaterialDocument")
def get_material_document():
    return {
        "@odata.context": "$metadata#MaterialDocument",
        "value": [{"Material": "MOCK-LI-DLE", "StockInTransit": 15, "Plant": "PLN1"}]
    }

# OData V2 Endpoints - EHS Standard Cabecera
@app.get("/sap/opu/odata/sap/API_EHS_INCIDENT_SRV/Incidents('{incident_id}')")
def get_ehs_incident_standard(incident_id: str):
    db = SessionLocal()
    incident = db.query(EhsIncident).filter(EhsIncident.incident_id == incident_id).first()
    db.close()
    if incident:
        return {
            "d": {
                "IncidentId": incident.incident_id,
                "IncidentCategory": incident.category,
                "Status": incident.status,
                "Plant": incident.plant
            }
        }
    return JSONResponse(status_code=404, content={"error": "Incident master data header not found"})

# OData V2 Endpoints - ZAPI Clean Core Ampliación Custom
@app.get("/sap/opu/odata/sap/ZAPI_EHS_ENV_EXTENSION_SRV/IncidentExtensions('{incident_id}')")
def get_ehs_incident_extension(incident_id: str):
    db = SessionLocal()
    incident = db.query(EhsIncident).filter(EhsIncident.incident_id == incident_id).first()
    db.close()
    if incident:
        return {
            "d": {
                "IncidentId": incident.incident_id,
                "Z_Toxicidad": incident.toxicidad,
                "Z_Distancia_Agua": incident.distancia_agua,
                "Z_Tipo_Suelo": "Arcilloso"
            }
        }
    return JSONResponse(status_code=404, content={"error": "Clean Core Extension fields not found"})

# ==============================================================================
# ENDPOINTS: OData V2 - API_BUSINESS_PARTNER (POC Brasil)
# ==============================================================================
class BusinessPartner(Base):
    __tablename__ = "business_partners"
    bp_id = Column(String, primary_key=True, index=True)
    country = Column(String)
    bp_role = Column(String)

Base.metadata.create_all(bind=engine)

@app.post("/sap/opu/odata/sap/API_BUSINESS_PARTNER/A_BusinessPartner")
async def create_business_partner(request: Request):
    """
    Simula la creación de un Cliente en S/4HANA (Role FLCU01).
    Valida que vengan los datos obligatorios.
    """
    data = await request.json()
    country = data.get("Country")
    roles = data.get("to_BusinessPartnerRole", {}).get("results", [])
    
    # Validar campos obligatorios (Hardcodeado para el POC)
    if not country:
        return JSONResponse(status_code=400, content={"error": "Falta el País (Country)"})
    
    bp_role = roles[0].get("BusinessPartnerRole") if roles else None
    if bp_role != "FLCU01":
        return JSONResponse(status_code=400, content={"error": "Falta el Rol de Cliente (FLCU01)"})
    
    # Simular guardado exitoso
    new_bp_id = f"BP_{uuid.uuid4().hex[:6].upper()}"
    
    db = SessionLocal()
    db.add(BusinessPartner(bp_id=new_bp_id, country=country, bp_role=bp_role))
    db.commit()
    db.close()
    
    return {
        "d": {
            "BusinessPartner": new_bp_id,
            "Country": country,
            "to_BusinessPartnerRole": {"results": [{"BusinessPartnerRole": bp_role}]}
        }
    }
