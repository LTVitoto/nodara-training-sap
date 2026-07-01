from langchain_core.messages import AIMessage
from app.core.sap_ai_client import get_sap_openai_llm
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class RubricEvaluationOutput(BaseModel):
    is_approved: bool = Field(description="True si aprueba la rúbrica, False si falla")
    feedback: str = Field(description="Feedback detallado en el idioma objetivo")

def auditor_node(state):
    llm = get_sap_openai_llm(temperature=0.0)
    user_messages = [m.content for m in state["messages"] if m.type == "human"]
    last_msg = user_messages[-1] if user_messages else ""
    
    is_approved, feedback_text = False, ""
    
    if not hasattr(llm, 'responses'):
        structured_llm = llm.with_structured_output(RubricEvaluationOutput)
        
        # Formateado de manera segura para evitar quiebres de línea en Python
        system_prompt = (
            "Evalúa la respuesta del alumno contra la Rúbrica Oficial:\n"
            "{rubric}\n"
            "Resultados SAP: {audit}. Responde en {idioma}."
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{user_answer}")
        ])
        
        chain = prompt | structured_llm
        try:
            res = chain.invoke({
                "rubric": str(state["active_rubric_json"]), 
                "audit": state["audit_findings"], 
                "idioma": state["target_training_language"], 
                "user_answer": last_msg
            })
            is_approved, feedback_text = res.is_approved, res.feedback
        except Exception:
            is_approved = "SUCCESS" in state["audit_findings"]
            feedback_text = state["audit_findings"]
    else:
        is_approved = "SUCCESS" in state["audit_findings"] or "derrame" in last_msg.lower()
        feedback_text = "[MOCK] Avaliação da Rúbrica concluída."

    return {
        "is_approved": is_approved, 
        "messages": [AIMessage(content=feedback_text)]
    }