from langchain_core.messages import AIMessage
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel

def instructor_node(state):
    """
    Simula la ingesta del manual en Inglés (Australia) 
    y responde educando en Portugués (Brasil).
    """
    # En la Fase 2, este FakeChatModel se reemplazará por SAP Generative AI Hub
    mock_llm = FakeMessagesListChatModel(
        responses=[
            AIMessage(content="Olá! Bem-vindo ao treinamento de operações. Segundo o manual da matriz na Austrália, para criar um Cliente SAP (Business Partner), precisamos do Nome, Termo de Pesquisa (Search Term) e País. Quais dados você vai inserir no sistema hoje?")
        ]
    )
    
    # Simulamos que el LLM lee el último mensaje del usuario y responde
    response = mock_llm.invoke(state["messages"])
    
    return {"messages": [response]}