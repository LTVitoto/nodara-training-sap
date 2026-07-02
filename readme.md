# 🚀 Nodara Enterprise AI - SAP BTP Integration

![Version](https://img.shields.io/badge/Version-2.0%20(PoC%20to%20MVP)-blue)
![Architecture](https://img.shields.io/badge/Architecture-Cloud%20Native-success)
![Platform](https://img.shields.io/badge/Platform-SAP%20BTP%20Kyma-orange)
![AI Framework](https://img.shields.io/badge/AI-LangGraph%20%7C%20GenAI%20Hub-purple)

## 📌 Introducción y Estado del Proyecto

Este repositorio contiene el núcleo transaccional y cognitivo de **Nodara**, una plataforma de entrenamiento y auditoría basada en Inteligencia Artificial Generativa. 

Actualmente, **hemos superado la Prueba de Concepto (PoC) al 100% en un entorno local seguro (`dev.local`)**, logrando la orquestación de agentes cognitivos, ingesta documental (RAG) y telemetría avanzada. Ahora, el proyecto se encuentra en la fase de transición hacia un **MVP (Producto Mínimo Viable) en la nube corporativa de SAP BTP**, utilizando el clúster de Kubernetes (Kyma) y los servicios nativos de SAP.

El objetivo central es proporcionar un sistema de evaluación que audite el conocimiento técnico y procedimental de los operadores de planta (ej. *Extracción de Litio DLE*), validando no solo su conocimiento, sino el estricto cumplimiento del **SAP Clean Core 2026** y los protocolos de contingencia en sistemas ERP.

---

## 🏗️ Arquitectura Técnica y Flujo de Trabajo

El proyecto está diseñado bajo el estándar **Twelve-Factor App**, lo que permite que el mismo código que corre en una laptop de desarrollo se ejecute en la nube de SAP sin modificaciones.

1. **Backend API:** Construido en Python con **FastAPI** para manejo asíncrono de alto rendimiento.
2. **Motor Cognitivo (LangGraph):** Orquesta tres agentes secuenciales:
   * *Instructor Node:* Maneja el flujo del examen.
   * *Judge Node:* Evalúa la respuesta mediante Retrieval-Augmented Generation (RAG).
   * *Auditor Node:* Valida reglas de negocio críticas (ej. Reversión Manual SAP).
3. **Capa de Persistencia y Vectores:** Utiliza PostgreSQL con `pgvector` en local, y está programado para conectarse a **SAP HANA Cloud Vector Engine** en producción.
4. **Telemetría y Observabilidad:** Integración asíncrona con **Langfuse** para registrar cada token, costo y razonamiento del LLM sin afectar la latencia del usuario.
5. **Simulador ERP:** Un microservicio que emula el entorno transaccional OData de SAP S/4HANA para pruebas locales.

---

## 🔄 El Cambio de Paradigma: `dev.local` vs `dev.cloud`

El sistema es "consciente de su entorno" gracias a la variable de infraestructura `SAP_ENV`. El código no requiere modificaciones manuales antes de subirse a Docker Hub; su comportamiento es dictado en tiempo de ejecución (Runtime) por el clúster.

* **Modo `dev.local`:** * Activa la base de datos PostgreSQL local y `pgvector`.
  * Utiliza modelos LLM "Fake/Mock" de LangChain para emular respuestas y no consumir créditos reales.
  * Habilita la telemetría local hacia el contenedor de Langfuse.
* **Modo `dev.cloud`:** * Se activa automáticamente al ser inyectado por Kubernetes en SAP Kyma.
  * Cambia los strings de conexión para utilizar **SAP HANA Cloud** mediante los drivers `hdbcli` y `sqlalchemy-hana`.
  * Activa el SDK nativo de SAP (`generative-ai-hub-sdk`) para orquestar llamadas seguras a los modelos corporativos (GPT-4o) alojados en **SAP AI Core**.

---

## ⚙️ Configuración y Variables de Entorno

### 1. Entorno Local (`.env`)
No se sube al repositorio. Contiene las credenciales para levantar el ecosistema en Docker Compose:
```env
# Telemetría Local
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=http://langfuse-service:3000

# Base de datos transaccional simulada
DATABASE_URL=postgresql://nodara_user:NodaraPass2026!@postgres-service:5432/nodara_db
2. Entorno Cloud (SAP Kyma / Kubernetes)
En el archivo de manifiesto k8s/k8s-nodara-mvp.yaml, se definen las variables definitivas inyectadas como ConfigMap y Secret:

ConfigMap (Variables Públicas):

SAP_ENV: "dev.cloud" -> Dispara la transición a SAP HANA y AI Hub.

Secrets (Credenciales de SAP Generative AI Hub): Para conectarse a los LLMs reales y cumplir con el escudo de privacidad de SAP, se deben inyectar las Service Keys obtenidas en BTP:

AICORE_CLIENT_ID

AICORE_CLIENT_SECRET

AICORE_AUTH_URL

AICORE_BASE_URL

AICORE_RESOURCE_GROUP

🧪 Validación y Endpoints Principales
Con el ecosistema local corriendo (docker compose up -d), se puede acceder a la interfaz interactiva de Swagger UI en: http://localhost:8001/docs.

1. Ingesta de Manuales (RAG)
Endpoint: POST /api/admin/rag/ingest

Objetivo: Recibe un documento PDF (ej. Manual de Operaciones Litio DLE), lo corta en fragmentos semánticos (RecursiveCharacterTextSplitter), los sanitiza eliminando caracteres nulos y los vectoriza en la base de datos.

Validación:

En Swagger, buscar el endpoint.

Enviar exam_id (ej. LITIO_DLE) y subir un archivo .pdf.

Resultado esperado: 200 OK con un JSON confirmando la cantidad de chunks indexados de forma segura.

2. Motor de Evaluación Cognitiva (Chat)
Endpoint: POST /api/chat

Objetivo: Recibe la respuesta del alumno, invoca al LangGraph (Instructor -> Judge -> Auditor) y devuelve la calificación basada en rúbricas y en el contexto de los documentos RAG.

Payload de Ejemplo:

JSON
{
  "user_id": "U001",
  "exam_id": "LITIO_DLE",
  "company_code": "CL01",
  "message": "En caso de falla, realizaré la reversión manual en SAP S/4HANA de inmediato."
}
Validación: 1. Enviar el Payload en Swagger.
2. Verificar el retorno HTTP 200 OK con el mensaje evaluativo del Asistente.
3. Abrir el Dashboard de Langfuse (localhost:3000) y comprobar que la Traza (Trace) del razonamiento cognitivo se guardó correctamente.

🚀 Pasos para Despliegue en Producción
Compilar y subir las imágenes agnósticas a Docker Hub usando arquitectura Cloud:
docker build --platform linux/amd64 -t [USUARIO]/nodara-backend-ai:v2.0 ./nodara-backend
docker push [USUARIO]/nodara-backend-ai:v2.0

Configurar las Service Keys de SAP BTP en k8s/k8s-nodara-mvp.yaml.

Aplicar la infraestructura en Kyma:
kubectl apply -f k8s/k8s-nodara-mvp.yaml