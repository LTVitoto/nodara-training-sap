import random
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from app.core.sap_ai_client import get_sap_openai_llm

def instructor_node(state):
    llm = get_sap_openai_llm(temperature=0.7)
    random_seed = random.randint(10, 90)
    
    system_prompt = (
        "Eres el Ingeniero Jefe e Instructor de Operaciones de Nodara AI. Tu objetivo es evaluar al alumno "
        "en el proceso industrial crítico: {target_sap_process}.\n\n"
        "REGLAS DE IDIOMA Y COMUNICACIÓN:\n"
        "TODA tu interacción, preguntas y feedback hacia el usuario deben generarse estrictamente en: {target_training_language}.\n\n"
        "REGLAS ANTI-FRAUDE:\n"
        "1. Nunca hagas la pregunta base '{question_text}' de forma literal.\n"
        "2. Transforma la pregunta en un Escenario Práctico Operacional.\n"
        "3. Inventa parámetros numéricos aleatorios usando la semilla ({random_seed}) para que cada alumno enfrente un problema único.\n\n"
        "Status del Examen:\n"
        "- Pregunta actual ({current_index} de {total_questions}).\n"
        "- Intentos fallidos en esta pregunta: {retry_count}.\n\n"
        "Si 'retry_count' > 0, el alumno cometió un error grave según la rúbrica. Dale un feedback constructivo y exige la respuesta correcta."
    )
    
    prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("placeholder", "{messages}")])
    
    if hasattr(llm, 'responses'):
        return {"messages": [AIMessage(content=f"[MOCK] Escenario Anti-Copia ({random_seed}): {state['active_question_text']}")]}
        
    chain = prompt | llm
    response = chain.invoke({
        "target_sap_process": state["target_sap_process"],
        "target_training_language": state["target_training_language"],
        "current_index": state["current_question_index"] + 1,
        "total_questions": state["total_questions"],
        "question_text": state["active_question_text"],
        "retry_count": state["retry_count"],
        "random_seed": random_seed,
        "messages": state["messages"]
    })
    return {"messages": [response]}