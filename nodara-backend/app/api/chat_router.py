from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.graph import compile_nodara_graph
from langchain_core.messages import HumanMessage
from langfuse.callback import CallbackHandler
import os

router = APIRouter()
nodara_graph = compile_nodara_graph()

class ChatInput(BaseModel):
    user_id: str
    scenario_id: str
    company_code: str
    message: str

@router.post("/chat")
async def process_chat_message(payload: ChatInput):
    langfuse_handler = CallbackHandler(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST")
    )
    
    inputs = {
        "messages": [HumanMessage(content=payload.message)],
        "scenario_id": payload.scenario_id,
        "company_code": payload.company_code,
        "audit_findings": {},
        "next_node": ""
    }
    
    try:
        config = {"callbacks": [langfuse_handler], "configurable": {"thread_id": payload.user_id}}
        result = nodara_graph.invoke(inputs, config=config)
        return {"response": result["messages"][-1].content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph Execution Failed: {str(e)}")
