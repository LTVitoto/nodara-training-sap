import os, json
from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

def init_database_tables():
    with engine.connect() as conn:
        if settings.SAP_ENV == "dev.local":
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()

        conn.execute(text("CREATE TABLE IF NOT EXISTS examenes (exam_id VARCHAR(50) PRIMARY KEY, nombre VARCHAR(100), proceso_sap VARCHAR(100));"))
        conn.execute(text("CREATE TABLE IF NOT EXISTS preguntas (id SERIAL PRIMARY KEY, exam_id VARCHAR(50), numero_pregunta INT, enunciado TEXT, rubrica_json TEXT);"))
        tipo_vector = "VECTOR(1536)" if settings.SAP_ENV == "dev.local" else "REAL_VECTOR"
        conn.execute(text(f"CREATE TABLE IF NOT EXISTS documentos_rag (id SERIAL PRIMARY KEY, exam_id VARCHAR(50), filename VARCHAR(255), chunk_text TEXT, embedding {tipo_vector});"))
        conn.execute(text("CREATE TABLE IF NOT EXISTS graph_sessions (session_key VARCHAR(100) PRIMARY KEY, current_index INT, retry_count INT, messages_blob TEXT);"))
        conn.commit()
        
        res = conn.execute(text("SELECT COUNT(*) FROM examenes;")).fetchone()
        if res[0] == 0:
            examenes = [
                ("LITIO_DLE", "Planta Litio DLE - Dosificación HCl", "EHS & Process Control"),
                ("CU_LIX", "Planta Cobre - Lixiviación", "EHS & Process Control"),
                ("DATA_MASTERS", "SAP MDG - Datos Maestros", "Creation of Business Partner")
            ]
            for eid, name, proc in examenes:
                conn.execute(text("INSERT INTO examenes VALUES (:id, :name, :proc);"), {"id": eid, "name": name, "proc": proc})
            
            preguntas_data = [
                (1, "LITIO_DLE", "Antes de iniciar HCl para desorción, ¿qué verificas en la columna?", {"criterios": ["Verificar pH base", "Válvula abierta", "EPI"], "fail_conditions": ["No mencionar EPI"]}),
                (2, "LITIO_DLE", "Detectas caída brusca de presión en la bomba de HCl. ¿Qué haces?", {"criterios": ["Detener bomba", "Aislar válvulas"], "fail_conditions": ["Aumentar potencia"]}),
                (3, "LITIO_DLE", "La resina se expande 45% (límite 30%). ¿Qué ajuste realizas?", {"criterios": ["Reducir flujo"], "fail_conditions": ["Drenar columna"]}),
                (4, "LITIO_DLE", "¿Cómo aseguras neutralización antes del ciclo de adsorción?", {"criterios": ["Lavado con agua DI", "pH neutro"], "fail_conditions": ["Salmuera"]}),
                (5, "LITIO_DLE", "Derrame de 50L de HCl fuera del dique. Describe tu accionar.", {"criterios": ["Evacuar", "Absorbente", "Reportar EHS en SAP"], "fail_conditions": ["Lavar con agua"]}),
                (1, "DATA_MASTERS", "Paso CERO obligatorio antes de crear BP en SAP.", {"criterios": ["Buscar por RUT"], "fail_conditions": ["Crearlo directo"]}),
                (2, "DATA_MASTERS", "Roles para módulo de Ventas.", {"criterios": ["FLCU01"], "fail_conditions": ["Solo General"]}),
                (3, "DATA_MASTERS", "Impacto de Account Group.", {"criterios": ["Cuenta asociada FI"], "fail_conditions": ["Agrupar"]}),
                (4, "DATA_MASTERS", "Campos obligatorios cliente Australia.", {"criterios": ["Country AU", "Moneda"], "fail_conditions": ["País en blanco"]}),
                (5, "DATA_MASTERS", "Resolución de Falta Cuenta Asociada.", {"criterios": ["Company Code"], "fail_conditions": ["General"]})
            ]
            for num, eid, enunciado, rubrica in preguntas_data:
                conn.execute(text("INSERT INTO preguntas (exam_id, numero_pregunta, enunciado, rubrica_json) VALUES (:eid, :num, :en, :rub);"), {"eid": eid, "num": num, "en": enunciado, "rub": json.dumps(rubrica)})
            conn.commit()
