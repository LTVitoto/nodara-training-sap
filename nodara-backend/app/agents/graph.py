from langgraph.graph import StateGraph, END
from app.agents.state import NodaraState
from app.agents.instructor_agent import instructor_node
from app.agents.judge_agent import judge_node
from app.agents.auditor_agent import auditor_node

def router_logic(state):
    """
    Enrutador semántico: Decide el siguiente paso basado en la intención del usuario.
    """
    last_message = state["messages"][-1].content.lower()
    
    # Si el usuario intenta enviar datos o dice "criar", pasamos al Juez
    if "criar" in last_message or "dados" in last_message or "cliente" in last_message:
        return "judge"
    
    # Si es solo una charla, se queda con el instructor
    return END

def compile_nodara_graph():
    workflow = StateGraph(NodaraState)
    
    workflow.add_node("instructor", instructor_node)
    workflow.add_node("judge", judge_node)
    workflow.add_node("auditor", auditor_node)
    
    workflow.set_entry_point("instructor")
    
    workflow.add_conditional_edges("instructor", router_logic, {"judge": "judge", END: END})
    workflow.add_edge("judge", "auditor")
    workflow.add_edge("auditor", END)
    
    return workflow.compile()