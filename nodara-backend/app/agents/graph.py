from langgraph.graph import StateGraph, END
from app.agents.state import NodaraState
from app.agents.instructor_agent import instructor_node
from app.agents.judge_agent import judge_node
from app.agents.auditor_agent import auditor_node

def router_logic(state):
    if "auditar" in state["messages"][-1].content.lower():
        return "judge"
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
