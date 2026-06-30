from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage

class NodaraState(TypedDict):
    messages: List[BaseMessage]
    scenario_id: str
    company_code: str
    audit_findings: Dict[str, Any]
    next_node: str
