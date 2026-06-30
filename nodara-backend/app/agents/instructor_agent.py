from langchain_core.messages import AIMessage

def instructor_node(state):
    """Guía socrático del alumno"""
    last_message = state["messages"][-1].content
    response = f"Como Instructor Nodara, analizo tu planteamiento: '{last_message}'. ¿Has revisado las métricas de toxicidad en S/4HANA antes de cerrar el caso?"
    return {"messages": [AIMessage(content=response)]}
