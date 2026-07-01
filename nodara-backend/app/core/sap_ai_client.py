import os
from langchain_openai import ChatOpenAI
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage
from app.core.config import settings

def get_sap_openai_llm(temperature: float = 0.0):
    if settings.SAP_ENV == "dev.local" and (not settings.SAP_AICORE_CLIENT_ID or "xxxx" in settings.SAP_AICORE_CLIENT_ID):
        return FakeMessagesListChatModel(responses=[
            AIMessage(content="[MOCK LLM - DEV.LOCAL. Simulando processamento NLP.]")
        ])
    
    os.environ["AICORE_LLM_CLIENT_ID"] = settings.SAP_AICORE_CLIENT_ID
    os.environ["AICORE_LLM_CLIENT_SECRET"] = settings.SAP_AICORE_CLIENT_SECRET
    os.environ["AICORE_LLM_AUTH_URL"] = settings.SAP_AICORE_AUTH_URL
    os.environ["AICORE_LLM_BASE_URL"] = settings.SAP_AICORE_BASE_URL
    os.environ["AICORE_LLM_RESOURCE_GROUP"] = settings.SAP_AICORE_RESOURCE_GROUP
    
    from generative_ai_hub_sdk.core.client import HubClient
    HubClient.init()
    return ChatOpenAI(model_name=settings.SAP_OPENAI_DEPLOYMENT_ID, temperature=temperature)
