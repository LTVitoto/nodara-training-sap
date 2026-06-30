from fastapi import APIRouter
from app.core import config

router = APIRouter()

@router.post("/upload-pdf")
async def upload_mining_manual():
    return {
        "status": "success",
        "detail": f"Manual recibido. Entorno activo: {config.ENVIRONMENT}. Ingestando a HANA Vector Store."
    }

@router.get("/kpis")
def get_dashboard_kpis():
    # FORMATO COMPATIBLE NATIVO CON SAP FIORI ELEMENTS OVERVIEW PAGE
    return {
        "d": {
            "results": [
                {
                    "__metadata": {
                        "id": "ResilienceKPISet('1')",
                        "uri": "/api/kpis('1')",
                        "type": "NodaraModel.ResilienceKPI"
                    },
                    "ID": "1",
                    "CompanyCode": "1000",
                    "Filial": "Australia Principal",
                    "TasaResiliencia": 92.4,
                    "ErroresEvitados": 42,
                    "MitigacionFinancieraUSD": 840000.00
                },
                {
                    "__metadata": {
                        "id": "ResilienceKPISet('2')",
                        "uri": "/api/kpis('2')",
                        "type": "NodaraModel.ResilienceKPI"
                    },
                    "ID": "2",
                    "CompanyCode": "2000",
                    "Filial": "Brasil Operaciones",
                    "TasaResiliencia": 78.1,
                    "ErroresEvitados": 19,
                    "MitigacionFinancieraUSD": 310000.00
                }
            ]
        }
    }
