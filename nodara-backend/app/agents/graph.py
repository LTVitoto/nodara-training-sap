from langgraph.graph import StateGraph, END
from app.agents.state import NodaraState
from app.agents.instructor_agent import instructor_node
from app.agents.judge_agent import judge_node
from app.agents.auditor_agent import auditor_node

def router_logic(state):
    user_messages = [m.content for m in state["messages"] if m.type == "human"]
    if user_messages and len(user_messages[-1].strip()) > 3: return "judge"
    return END

def compile_nodara_graph():
    w = StateGraph(NodaraState)
    w.add_node("instructor", instructor_node)
    w.add_node("judge", judge_node)
    w.add_node("auditor", auditor_node)
    w.set_entry_point("instructor")
    w.add_conditional_edges("instructor", router_logic, {"judge": "judge", END: END})
    w.add_edge("judge", "auditor")
    w.add_edge("auditor", END)
    return w.compile()
