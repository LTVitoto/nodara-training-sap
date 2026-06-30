from fastapi import FastAPI
from app.api.chat_router import router as chat_router
from app.api.admin_router import router as admin_router

app = FastAPI(title="Nodara AI Brain - Core Gateway", version="1.0.0")

app.include_router(chat_router, prefix="/api")
app.include_router(admin_router, prefix="/api/admin")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "nodara-backend-ai"}
